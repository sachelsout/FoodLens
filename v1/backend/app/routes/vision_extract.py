from fastapi import APIRouter, UploadFile, File, HTTPException
import traceback
from ..services.vision_llm import extract_menu_with_vision
from ..services.images import get_image_for_dish  # your Unsplash fetch function

router = APIRouter()

@router.post("/vision-extract")
async def vision_extract(file: UploadFile = File(...)):
    try:
        print("🔹 Reading uploaded file bytes...")
        image_bytes = await file.read()
        print(f"🔹 Read {len(image_bytes)} bytes from uploaded file")

        print("🔹 Calling Vision LLM service...")
        structured_menu = await extract_menu_with_vision(image_bytes)
        print("🔹 Vision LLM response received")

        if "error" in structured_menu:
            print(f"⚠️ Vision LLM returned error: {structured_menu['error']}")
            raise HTTPException(status_code=500, detail=structured_menu["error"])

        print("🔹 Enriching menu items with images from Unsplash...")
        for category in structured_menu.get("categories", []):
            for item in category.get("items", []):
                dish_name = item.get("name")
                if dish_name:
                    try:
                        image_url = await get_image_for_dish(dish_name)
                        if image_url:
                            item["image_url"] = image_url
                    except Exception as e:
                        print(f"⚠️ Failed to get image for '{dish_name}': {e}")
                        # Optional: assign None or skip image_url on failure
                        item["image_url"] = None

        print("🔹 Returning structured menu")
        return {"structured": structured_menu}

    except Exception as e:
        tb = traceback.format_exc()
        print(f"🔥 Unhandled error in /vision-extract:\n{tb}")
        raise HTTPException(status_code=500, detail=str(e))
