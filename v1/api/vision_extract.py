import json
from .vision_llm import call_vision_llm
from .images import fetch_unsplash_images
from .vision_response import structure_response

def handler(request):
    try:
        # Expect JSON payload with base64 image
        body = request.body
        if not body:
            return {"statusCode": 400, "body": json.dumps({"error": "No file uploaded"})}

        data = json.loads(body.decode("utf-8"))
        img_b64 = data.get("image_base64")
        if not img_b64:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing image_base64 field"})}

        # Call vision LLM
        llm_result = call_vision_llm(img_b64)
        structured = structure_response(llm_result)

        # Fetch Unsplash images
        structured = fetch_unsplash_images(structured)

        return {"statusCode": 200, "body": json.dumps({"structured": structured})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
