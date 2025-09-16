import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_vision_llm(img_b64: str):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        # TODO: Replace with a valid OpenRouter vision model slug configured for your account
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict JSON formatter. Respond with ONLY compact JSON with keys: "
                    "restaurant_name (string), categories (array of {name, items}), and items (array of {name, description, price})."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract structured menu from this image. Return only JSON."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                ],
            },
        ],
        "temperature": 0.2,
    }
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        detail = e.response.text if e.response is not None else str(e)
        status = e.response.status_code if e.response is not None else "?"
        raise RuntimeError(f"OpenRouter HTTP {status}: {detail}")
    except httpx.RequestError as e:
        raise RuntimeError(f"OpenRouter request failed: {e}")
