from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"]) 
def ping():
    return jsonify({"ok": True})
