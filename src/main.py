import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI
from app.routers import chat, logs
from app.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.services.redis_service import RedisService
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

redis_service = RedisService(redis_url=settings.REDIS_URL)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

@app.on_event("startup")
async def startup_event():
    await redis_service.initialize()
    logger.info("Application startup: Redis service initialized")

@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.close()
    logger.info("Application shutdown: Redis service closed")

app.add_middleware(LoggingMiddleware, redis_service=redis_service)

app.include_router(chat.router)
app.include_router(logs.router)


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
        "version": settings.APP_VERSION,
        "services": {
            "redis": "unknown"
        }
    }
    
    try:
        if redis_service and redis_service.redis:
            await redis_service.redis.ping()
            health["services"]["redis"] = "healthy"
        else:
            health["services"]["redis"] = "not initialized"
    except Exception as e:
        health["services"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    return health


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
