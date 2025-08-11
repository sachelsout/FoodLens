from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.extract import router as extract_router
from .routes.vision_extract import router as vision_extract_router

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
app.include_router(vision_extract_router, prefix="/api")