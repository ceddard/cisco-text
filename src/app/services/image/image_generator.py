import os
import logging
import re
import aiohttp
import base64
from typing import Optional, Dict, Any
from app.exceptions.exceptions import ImageGenerationError

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Service for generating images from text prompts using OpenAI DALL-E."""

    def __init__(self, config: Dict[str, Any]):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.model = config.get("image_model", "dall-e-3")
        self.size = config.get("image_size", "1024x1024")
        self.quality = config.get("image_quality", "standard")
        self.style = config.get("image_style", "vivid")
        
        
    async def generate_image(self, prompt: str) -> Optional[str]:
        """
        Generate an image from a text prompt using DALL-E.
        
        Args:
            prompt: Text description of the desired image
            
        Returns:
            Optional[str]: URL of the generated image, or None if generation failed
        """
        if not prompt or not self.api_key:
            logger.warning("Missing prompt or API key for image generation")
            return None
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            formatted_prompt = self._format_prompt(prompt)
            
            payload = {
                "model": self.model,
                "prompt": formatted_prompt,
                "size": self.size,
                "quality": self.quality,
                "style": self.style,
                "n": 1,
            }
            
            logger.debug(f"Sending image generation request with prompt: {formatted_prompt[:50]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    headers=headers, 
                    json=payload
                ) as response:
                    response_text = await response.text()
                    
                    if response.status != 200:
                        error_detail = "Unknown error"
                        try:
                            error_data = await response.json()
                            if isinstance(error_data, dict) and "error" in error_data:
                                error_msg = error_data["error"].get("message")
                                error_type = error_data["error"].get("type")
                                error_detail = f"{error_type}: {error_msg}" if error_msg else error_type
                        except Exception:
                            pass
                            
                        logger.error(f"Image generation failed: {error_detail}")
                        logger.debug(f"Full error response: {response_text}")
                        raise ImageGenerationError(f"Failed to generate image: {error_detail}")
                    
                    try:    
                        data = await response.json()
                        
                        if "data" in data and len(data["data"]) > 0 and "url" in data["data"][0]:
                            return data["data"][0]["url"]
                        else:
                            logger.warning(f"No image URL in the response: {response_text}")
                            raise ImageGenerationError("No image URL in the response")
                    except Exception as e:
                        logger.error(f"Error parsing response: {str(e)}")
                        logger.debug(f"Response content: {response_text}")
                        raise ImageGenerationError(f"Error parsing API response")
                        
        except ImageGenerationError:
            raise
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise ImageGenerationError(f"Unexpected error: {str(e)}")
            
    def _format_prompt(self, prompt: str) -> str:
        """Format the prompt to get better results from the image generation model."""
        image_prompt_match = re.search(r'🌠 Image Prompt: (.*?)(?:\n\n|$)', prompt, re.DOTALL)
        if image_prompt_match:
            prompt = image_prompt_match.group(1).strip()
        
        if len(prompt) > 3800:
            logger.warning(f"Prompt too long ({len(prompt)} chars), truncating")
            prompt = prompt[:3800]
        
        if prompt and prompt[-1] not in ['.', '!', '?']:
            prompt = prompt + '.'

        return f"{prompt} Surreal dreamlike quality, detailed, fantasy art style, 4K resolution."
