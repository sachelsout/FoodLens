import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3-4b-it:free")


def call_vision_llm(img_b64: str):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract a structured menu from this image and respond with ONLY compact JSON. "
                            "Required shape: {\"restaurant_name\": string, \"categories\": [{\"name\": string, \"items\": [{\"name\": string, \"description\": string, \"price\": string}]}]}. "
                            "For every item, description must be 2 to 4 words. "
                            "Do not include markdown, explanations, or extra keys."
                        ),
                    },
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
        raise RuntimeError(
            f"OpenRouter HTTP {status} (model={OPENROUTER_MODEL}): {detail}"
        )
    except httpx.RequestError as e:
        raise RuntimeError(f"OpenRouter request failed: {e}")
