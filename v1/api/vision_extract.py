import base64
import json
from .vision_llm import call_vision_llm
from .images import fetch_unsplash_images
from .vision_response import structure_response

def handler(request, response):
    try:
        # Vercel passes the request body as bytes
        body = request.body
        if not body:
            response.status_code = 400
            return {"error": "No file uploaded"}

        # Expect JSON payload with base64 image
        data = json.loads(body.decode("utf-8"))
        img_b64 = data.get("image_base64")
        if not img_b64:
            response.status_code = 400
            return {"error": "Missing image_base64 field"}

        # Call vision LLM
        llm_result = call_vision_llm(img_b64)
        structured = structure_response(llm_result)

        # Fetch Unsplash images
        structured = fetch_unsplash_images(structured)

        return {"structured": structured}

    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}
