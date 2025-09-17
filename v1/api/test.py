from flask import Flask, Response

app = Flask(__name__)


@app.route("/", methods=["GET"]) 
def test():
    return Response("ok", mimetype="text/plain")


