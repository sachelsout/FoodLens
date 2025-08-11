from .images import get_image_for_dish
import httpx
import os
from dotenv import load_dotenv
import json, re
from pydantic import ValidationError
from app.models.vision_response import OpenRouterResponse

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL_NAME = "mistralai/mistral-nemo:free"

def extract_json_from_string(text):
    try:
        cleaned = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("No valid JSON object found in LLM reply.")
    except Exception as e:
        raise ValueError(f"Failed to parse LLM JSON: {e}")

async def extract_structured_menu(text: str) -> dict:
    prompt = f"""
You are a helpful assistant that extracts structured data from restaurant menus.

Given the following raw OCR text, return a JSON with:
- restaurant_name (if available)
- categories: list of sections like 'Cocktails', 'Appetizers', etc.
- each category has a list of items with name, price (if available), and description (if available)

Raw OCR Text:
{text}

Return only JSON, no explanation.
"""

    body = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(
            OPENROUTER_BASE_URL,
            json=body,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        res.raise_for_status()
        data = res.json()
        try:
            parsed_response = OpenRouterResponse.parse_obj(data)
            reply = parsed_response.choices[0].message.content
        except ValidationError as ve:
            raise ValueError(f"Pydantic validation error: {ve}")

        menu = extract_json_from_string(reply)

    # 🔗 Add image URLs to each menu item
    for category in menu.get("categories", []):
        for item in category.get("items", []):
            dish_name = item.get("name", "")
            image_url = await get_image_for_dish(dish_name)
            item["image_url"] = image_url or "Image not found"
    return menu
