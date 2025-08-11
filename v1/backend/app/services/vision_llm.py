import base64
import httpx
import os
import json
import re
from pydantic import ValidationError
from app.models.vision_response import OpenRouterResponse

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL_NAME = "meta-llama/llama-3.2-11b-vision-instruct:free"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

async def extract_menu_with_vision(image_bytes: bytes):
    # Convert image to base64 string
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Prepare prompt
    prompt = """
    You are an assistant that extracts structured menu data from a restaurant menu image.
    ONLY OUTPUT raw JSON. Do NOT include any text before or after. No explanations.

    Each menu item must have its own description.
    If the menu does not include a description, generate a concise 5-6 word description that relates only to that specific menu item’s name.
    Do NOT use other menu item names in a description.
    Use the format:
    {
      "restaurant_name": "...",
      "categories": [
        {
          "name": "...",
          "items": [
            {
              "name": "...",
              "description": "...",
              "price": "..."
            }
          ]
        }
      ]
    }
    """


    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"}
                ]
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_BASE_URL,
            headers=headers,
            json=payload
        )

    if response.status_code != 200:
        return {"error": f"OpenRouter API error: {response.text}"}

    data = response.json()

    try:
        parsed_response = OpenRouterResponse.parse_obj(data)
        raw_output = parsed_response.choices[0].message.content

        # Try to extract JSON block from the full text
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not json_match:
            return {"error": "Failed to locate JSON in LLM response", "raw": raw_output}

        json_string = json_match.group(0)
        structured_json = json.loads(json_string)
        return structured_json
    
    except ValidationError as ve:
        return {"error": f"Pydantic validation error: {ve}"}

    except Exception as e:
        return {"error": f"Failed to parse JSON: {str(e)}", "raw": raw_output}
