import json


def handler(request):
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"ok": True})}


def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"ok": True}).encode("utf-8")]
