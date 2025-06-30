import httpx
import os
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Load from env var

async def extract_structured_menu(text: str) -> dict:
    prompt = f"""
You are a helpful assistant that extracts structured data from restaurant menus.

Given the following raw text from a scanned menu, output a JSON object with:
- restaurant_name (if available)
- a list of categories (e.g., Breakfast, Appetizers)
- each category contains items with name, price, and description (if available)

Text:
{text}

Output:
"""

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
            json=body,
            headers={"Content-Type": "application/json"}
        )
        res.raise_for_status()
        data = res.json()
        text_output = data["candidates"][0]["content"]["parts"][0]["text"]

        try:
            structured_data = json.loads(text_output)
        except json.JSONDecodeError:
            raise ValueError("Gemini response is not valid JSON.\n\n" + text_output)

        return structured_data