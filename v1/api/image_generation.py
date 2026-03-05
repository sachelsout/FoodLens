import os
import base64
from pathlib import Path

import httpx

def _load_dotenv_fallback() -> None:
    """Load .env values if process env vars are missing (local dev fallback)."""
    candidate_paths = [
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]

    for env_path in candidate_paths:
        if not env_path.exists():
            continue

        for line in env_path.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue

            key, value = raw.split("=", 1)
            env_key = key.strip()
            env_value = value.strip().strip('"').strip("'")
            if env_key and env_key not in os.environ:
                os.environ[env_key] = env_value

        break


_load_dotenv_fallback()


def _get_cloudflare_api_url() -> str | None:
    return os.getenv("CLOUDFLARE_IMAGE_API_URL")


def _get_cloudflare_api_key() -> str | None:
    return os.getenv("API_KEY") or os.getenv("CLOUDFLARE_IMAGE_API_KEY")

# Keywords to detect drinks or desserts
DRINK_KEYWORDS = ["juice", "coffee", "tea", "latte", "milkshake", "soda", "cocktail", "wine", "beer", "smoothie"]
DESSERT_KEYWORDS = ["ice cream", "cake", "dessert", "sweet", "pastry", "pudding", "tart", "gulab jamun", "rasgulla"]

def detect_item_type(name: str, description: str = "") -> str:
    """Detect if the menu item is food, drink, or dessert."""
    text = (name + " " + (description or "")).lower()
    if any(k in text for k in DRINK_KEYWORDS):
        return "drink"
    if any(k in text for k in DESSERT_KEYWORDS):
        return "dessert"
    return "food"

def build_image_prompt(item: dict, category: dict) -> str:
    name = item.get("name") or "Delicious dish"
    description = item.get("description") or "Tasty and visually appealing"
    category_name = category.get("name") or "Dish"

    item_type = detect_item_type(name, description)
    style = "realistic food photography, natural lighting, high detail"
    return ", ".join([name, description, category_name, item_type, style])


def generate_cloudflare_image(prompt: str) -> str | None:
    cloudflare_image_api_url = _get_cloudflare_api_url()
    cloudflare_image_api_key = _get_cloudflare_api_key()

    if not cloudflare_image_api_url:
        return None

    headers = {"Content-Type": "application/json"}
    if cloudflare_image_api_key:
        headers["Authorization"] = f"Bearer {cloudflare_image_api_key}"
        headers["x-api-key"] = cloudflare_image_api_key

    payload = {"prompt": prompt}

    with httpx.Client(timeout=60) as client:
        response = client.post(cloudflare_image_api_url, headers=headers, json=payload)
        response.raise_for_status()

        content_type = (response.headers.get("content-type") or "").lower()
        if content_type.startswith("image/"):
            encoded = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type.split(';')[0]};base64,{encoded}"

        if "application/json" in content_type:
            data = response.json()
            if isinstance(data, dict):
                for key in ("image_url", "url", "image", "data_url"):
                    value = data.get(key)
                    if isinstance(value, str) and value:
                        return value

                base64_data = data.get("base64")
                if isinstance(base64_data, str) and base64_data:
                    return f"data:image/png;base64,{base64_data}"
            return None

        text = response.text.strip()
        if text.startswith("http") or text.startswith("data:"):
            return text

    return None

def attach_generated_images(structured: dict) -> dict:
    """Attach Cloudflare Worker generated image URLs directly in backend response."""
    if not structured or "categories" not in structured:
        return structured

    for category in structured.get("categories", []):
        for item in category.get("items", []):
            if not item.get("image_url"):
                try:
                    prompt = build_image_prompt(item, category)
                    item["image_url"] = generate_cloudflare_image(prompt)
                except Exception as error:
                    item["image_url"] = None
                    print(f"Cloudflare image generation failed for {item.get('name')}: {error}")

    return structured