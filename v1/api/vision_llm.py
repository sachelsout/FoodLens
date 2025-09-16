import os
import httpx
import json

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def call_vision_llm(img_b64: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": "Extract restaurant name, categories, and items with description and price from menu image."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Here is the menu image:"},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}
                ]
            }
        ]
    }

    with httpx.Client(timeout=60) as client:
        res = client.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()
