from dotenv import load_dotenv
import os

load_dotenv()
print("GEMINI_API_KEY =", os.getenv("GEMINI_API_KEY"))  # you can remove this after testing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.extract import router as extract_router

app = FastAPI()

# CORS settings...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extract_router, prefix="/api")
