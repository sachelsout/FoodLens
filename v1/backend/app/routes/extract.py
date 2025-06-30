from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.ocr import extract_text_from_image
from ..services.llm import extract_structured_menu

router = APIRouter()

@router.post("/extract")
async def extract_menu(file: UploadFile = File(...)):
    try:
        text = await extract_text_from_image(file)
        # structured = await extract_structured_menu(text)
        return {
            "raw_ocr": text,
            "structured": {}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))