from flask import Flask, request, jsonify

from api.image_generation import build_image_prompt, generate_cloudflare_image

app = Flask(__name__)


def _handle_generate_item_image():
    try:
        data = request.get_json(silent=True) or {}
        item = data.get("item") or {}
        category_name = data.get("category_name")

        if not isinstance(item, dict):
            return jsonify({"error": "Invalid item payload"}), 400

        item_name = item.get("name")
        if not item_name:
            return jsonify({"error": "Missing item name"}), 400

        category = {"name": category_name} if category_name else {}
        prompt = build_image_prompt(item, category)
        image_url = generate_cloudflare_image(prompt)

        return jsonify({"image_url": image_url}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/", methods=["POST"])
@app.route("/api/generate_item_image", methods=["POST"])
def generate_item_image():
    return _handle_generate_item_image()
