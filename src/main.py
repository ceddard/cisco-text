import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI
from app.routers import chat
from app.config import settings
import time

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Asynchronous Chat API!",
        "description": """
        🚀 Creative Prompt API — A lightweight and expressive interface to interact with three imaginative LLM-powered assistants:

        🎨 • Tool Inventor — Generates magical or futuristic products based on everyday problems  
        🧠 • Subtext Translator — Interprets the hidden emotional meaning behind ambiguous messages  
        🌙 • Dream Curator — Transforms surreal dream descriptions into artwork and micro-stories

        Just provide a prompt type and your input — and receive a structured, creative response.

        Perfect for applications in storytelling, emotion analysis, idea generation, or just playful AI-powered creativity.
        """,
        "docs_url": "/docs",
        "version": settings.APP_VERSION,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration systems."""
    health = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION
    }
    return health


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
