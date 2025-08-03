import base64
import httpx
import os
import json

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openrouter/horizon-beta"

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
    Output JSON like:
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

    # Prepare payload for OpenRouter
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

    # Send request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )

    # Parse result
    if response.status_code != 200:
        return {"error": f"OpenRouter API error: {response.text}"}

    data = response.json()
    try:
        raw_output = data["choices"][0]["message"]["content"]
        structured_json = json.loads(raw_output)
        return structured_json
    except Exception as e:
        return {"error": f"Failed to parse JSON: {str(e)}", "raw": data}
