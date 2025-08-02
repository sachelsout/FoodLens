from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.vision_llm import extract_menu_with_vision
from ..services.images import get_image_for_dish  # your Unsplash fetch function

router = APIRouter()

@router.post("/vision-extract")
async def vision_extract(file: UploadFile = File(...)):
    try:
        # Read uploaded image as bytes
        image_bytes = await file.read()

        # Call Vision LLM service
        structured_menu = await extract_menu_with_vision(image_bytes)

        if "error" in structured_menu:
            raise HTTPException(status_code=500, detail=structured_menu["error"])

        # Enrich menu items with images from Unsplash
        for category in structured_menu.get("categories", []):
            for item in category.get("items", []):
                dish_name = item.get("name")
                if dish_name:
                    image_url = await get_image_for_dish(dish_name)
                    if image_url:
                        item["image_url"] = image_url

        return {"structured": structured_menu}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
