from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=["GET"]) 
@app.route("/<path:path>", methods=["GET"]) 
def ping(path: str = ""):
    return jsonify({"ok": True})
