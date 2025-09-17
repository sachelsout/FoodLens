import os
import httpx

UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")


def fetch_unsplash_images(structured: dict) -> dict:
    if not structured or "categories" not in structured:
        return structured

    if not UNSPLASH_API_KEY:
        # Fallback: use Unsplash Source (no API key required) to provide a best-effort image URL
        for category in structured.get("categories", []):
            for item in category.get("items", []) or []:
                query = (item.get("name") or "food").strip()
                # 600x400 random image related to the query
                item["image_url"] = f"https://source.unsplash.com/600x400/?{query}"
        return structured

    for category in structured.get("categories", []):
        for item in category.get("items", []):
            query = item.get("name")
            if not query:
                continue
            try:
                url = "https://api.unsplash.com/search/photos"
                params = {"query": query, "per_page": 1}
                headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}

                with httpx.Client(timeout=10) as client:
                    resp = client.get(url, headers=headers, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    if data.get("results"):
                        item["image_url"] = data["results"][0]["urls"]["small"]
            except Exception as e:
                item["image_url"] = None
                print(f"Unsplash fetch failed for {query}: {e}")
    return structured
