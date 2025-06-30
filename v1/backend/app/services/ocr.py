import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

async def extract_text_from_image(file):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    raw_text = pytesseract.image_to_string(image)
    return raw_text