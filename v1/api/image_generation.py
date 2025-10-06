import httpx
from urllib.parse import quote

# --- Pollinations API (free, no key required) ---
POLLINATIONS_API_URL = "https://image.pollinations.ai/prompt/"

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

def build_pollinations_prompt(item: dict, category: dict) -> str:
    """Build a general prompt for Pollinations image generation."""
    name = item.get("name") or "Delicious dish"
    description = item.get("description") or "Tasty and visually appealing"
    category_name = category.get("name") or "Dish"

    item_type = detect_item_type(name, description)

    # General plating and background hints
    if item_type == "drink":
        serving = "served in a glass, realistic, high quality photo"
        background = "café, bar, or home kitchen, natural lighting"
    elif item_type == "dessert":
        serving = "served on a dessert plate, close-up, high quality photo"
        background = "cozy café or dessert table, natural lighting"
    else:  # food
        serving = "served on a plate or traditional dishware, appetizing presentation, high quality photo"
        background = "restaurant or home kitchen, natural lighting"

    prompt_parts = [name, description, category_name, item_type, serving, background]
    prompt = ", ".join([p for p in prompt_parts if p])
    return quote(prompt)

def generate_image_url(item: dict, category: dict) -> str:
    """Generate an image URL for a menu item using Pollinations."""
    prompt = build_pollinations_prompt(item, category)
    return f"{POLLINATIONS_API_URL}{prompt}"

def fetch_pollinations_images(structured: dict) -> dict:
    """Update menu items with Pollinations-generated images (fully general)."""
    if not structured or "categories" not in structured:
        return structured

    for category in structured.get("categories", []):
        for item in category.get("items", []):
            # Skip if image already exists
            if item.get("image_url"):
                continue
            try:
                item["image_url"] = generate_image_url(item, category)
            except Exception as e:
                item["image_url"] = None
                print(f"Image generation failed for {item.get('name')}: {e}")

    return structured