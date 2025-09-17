import json
from flask import Flask, request, jsonify
from api.vision_llm import call_vision_llm
from api.images import fetch_unsplash_images
from api.vision_response import structure_response

app = Flask(__name__)


@app.route("/", methods=["POST"]) 
def vision_extract():
    try:
        data = request.get_json(silent=True) or {}
        img_b64 = data.get("image_base64")
        if not img_b64:
            return jsonify({"error": "Missing image_base64 field"}), 400

        llm_result = call_vision_llm(img_b64)
        structured = structure_response(llm_result)
        structured = fetch_unsplash_images(structured)

        return jsonify({"structured": structured}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
