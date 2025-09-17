from flask import Flask, Response

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=["GET"]) 
@app.route("/<path:path>", methods=["GET"]) 
def test(path: str = ""):
    return Response("ok", mimetype="text/plain")


