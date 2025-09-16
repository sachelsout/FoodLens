import base64
import json
import os
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from PIL import Image
from .vision_llm import call_vision_llm
from .images import fetch_unsplash_images
from .vision_response import structure_response

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # Parse multipart form-data manually
            boundary = self.headers['Content-Type'].split("boundary=")[-1]
            parts = body.split(b"--" + boundary.encode())
            file_bytes = None
            for part in parts:
                if b"Content-Disposition" in part and b"filename=" in part:
                    file_bytes = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
                    break

            if not file_bytes:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "No file uploaded"}')
                return

            # Convert to base64
            img_b64 = base64.b64encode(file_bytes).decode("utf-8")

            # Call vision LLM
            llm_result = call_vision_llm(img_b64)

            # Structure response
            structured = structure_response(llm_result)

            # Fetch Unsplash images for dishes
            structured = fetch_unsplash_images(structured)

            # Respond
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"structured": structured}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
