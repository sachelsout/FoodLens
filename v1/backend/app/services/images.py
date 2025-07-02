import os
import httpx
from dotenv import load_dotenv

load_dotenv()
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

async def get_image_for_dish(dish_name: str) -> str:
    query = dish_name + " food"
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "client_id": UNSPLASH_ACCESS_KEY
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        results = data.get("results")
        if results:
            return results[0]["urls"]["small"]  # return small image URL
        return "Image not found"
