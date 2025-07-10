import os
from typing import Dict, Any, ClassVar
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with type validation."""

    APP_NAME: str = "Cisco Chat API"
    APP_DESCRIPTION: str = "i dont know what to write here"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_LOG_TTL: int = int(os.getenv("REDIS_LOG_TTL", 604800))  # 7 days in seconds

    @property
    def LLM_CONFIG(self) -> Dict[str, Any]:
        """LLM configuration with proper defaults."""
        return {
            "provider": "openai",
            "api_key": self.OPENAI_API_KEY,
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1500,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "timeout": 60,
            "retry_attempts": 3,
            "image_api_key": self.OPENAI_API_KEY,
            "image_model": "dall-e-3", 
            "image_size": "1024x1024",
            "image_quality": "standard",
            "image_style": "vivid"
        }

    AVAILABLE_SERVICES: ClassVar[Dict[str, Dict[str, Any]]] = {
        "inventor": {
            "name": "Inventor of Imaginary Tools",
            "description": "Creates whimsical inventions to solve problems",
            "temperature": 0.8,
        },
        "translator": {
            "name": "Translator of Unspoken Feelings",
            "description": "Interprets subtext and emotions in messages",
            "temperature": 0.7,
        },
        "curator": {
            "name": "Dream Healer and Curator of Surreal Art",
            "description": "Transforms dreams into surreal art and stories",
            "temperature": 0.9,
        },
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
