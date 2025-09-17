import json
from api.vision_llm import call_vision_llm
from api.images import fetch_unsplash_images
from api.vision_response import structure_response

def handler(request):
    try:
        body = request.body
        if not body:
            return (400, {"Content-Type": "application/json"},
                    json.dumps({"error": "No file uploaded"}))

        data = json.loads(body.decode("utf-8"))
        img_b64 = data.get("image_base64")
        if not img_b64:
            return (400, {"Content-Type": "application/json"},
                    json.dumps({"error": "Missing image_base64"}))

        # LLM + Unsplash
        llm_result = call_vision_llm(img_b64)
        structured = structure_response(llm_result)
        structured = fetch_unsplash_images(structured)

        return (200, {"Content-Type": "application/json"},
                json.dumps({"structured": structured}))

    except Exception as e:
        return (500, {"Content-Type": "application/json"},
                json.dumps({"error": str(e)}))
