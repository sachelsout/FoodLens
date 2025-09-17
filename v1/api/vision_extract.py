import json
from api.vision_llm import call_vision_llm
from api.images import fetch_unsplash_images
from api.vision_response import structure_response


def handler(request):
    try:
        body = getattr(request, "body", b"")
        if not body:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "No file uploaded"})}

        data = json.loads(body.decode("utf-8"))
        img_b64 = data.get("image_base64")
        if not img_b64:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing image_base64 field"})}

        llm_result = call_vision_llm(img_b64)
        structured = structure_response(llm_result)
        structured = fetch_unsplash_images(structured)

        return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"structured": structured})}

    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})}


def app(environ, start_response):
    try:
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except (ValueError, TypeError):
            length = 0
        body = environ.get("wsgi.input").read(length) if length > 0 else b""

        class _Req:
            pass

        req = _Req()
        req.body = body

        resp = handler(req)
        status_code = int(resp.get("statusCode", 200))
        reason = "OK" if status_code < 400 else "ERROR"
        status_line = f"{status_code} {reason}"
        headers = [("Content-Type", "application/json")]
        start_response(status_line, headers)
        return [resp.get("body", "{}").encode("utf-8")]
    except Exception as e:
        start_response("500 INTERNAL SERVER ERROR", [("Content-Type", "application/json")])
        return [json.dumps({"error": str(e)}).encode("utf-8")]
