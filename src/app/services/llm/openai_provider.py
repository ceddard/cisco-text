import openai
from typing import Dict, Any, Optional, AsyncGenerator
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.interfaces import LLMProvider
from app.exceptions import (
    LLMServiceError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    APIError,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider."""

    def __init__(self, config: Dict[str, Any]):
        self._validate_config(config)
        self.config = config
        self.client = openai.AsyncOpenAI(
            api_key=config.get("api_key", ""), timeout=config.get("timeout", 60)
        )

        self.model = config.get("model", "gpt-4")
        self.default_temperature = config.get("temperature", 0.7)
        self.default_max_tokens = config.get("max_tokens", 1500)
        self.top_p = config.get("top_p", 1.0)
        self.frequency_penalty = config.get("frequency_penalty", 0.0)
        self.presence_penalty = config.get("presence_penalty", 0.0)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration."""
        if not config.get("api_key"):
            raise ConfigurationError("OpenAI API key is required")

        if not config.get("model"):
            raise ConfigurationError("OpenAI model is required")

    async def validate_connection(self) -> bool:
        """
        Validate the OpenAI API connection asynchronously.

        Returns:
            bool: True if connection is valid

        Raises:
            ConfigurationError: If connection fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except openai.AuthenticationError:
            raise ConfigurationError("Invalid OpenAI API key")
        except openai.APIError as e:
            raise ConfigurationError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Connection test failed: {str(e)}")

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model asynchronously.

        Returns:
            Dict with model information
        """
        try:
            return {
                "model": self.model,
                "temperature": self.default_temperature,
                "max_tokens": self.default_max_tokens,
                "provider": "openai",
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            raise LLMServiceError(f"Failed to get model info: {str(e)}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self, system_prompt: str, user_message: str, **kwargs
    ) -> str:
        """
        Generate a response using OpenAI's API.

        Args:
            system_prompt: The system prompt to set the context
            user_message: The user's message
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            str: The generated response

        Raises:
            LLMServiceError: If the API call fails
        """
        try:
            temperature = kwargs.get("temperature", self.default_temperature)
            max_tokens = kwargs.get("max_tokens", self.default_max_tokens)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
            )

            content = response.choices[0].message.content
            if not content:
                raise LLMServiceError("Empty response from OpenAI")

            return content.strip()

        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise RateLimitError("Rate limit exceeded. Please try again later.")

        except openai.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Invalid API key")

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"API error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {e}")
            raise LLMServiceError(f"Failed to generate response: {str(e)}")

    async def generate_streaming_response(
        self, system_prompt: str, user_message: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using OpenAI's API.

        Args:
            system_prompt: The system prompt to set the context
            user_message: The user's message
            **kwargs: Additional parameters

        Yields:
            str: Chunks of the generated response
        """
        try:
            temperature = kwargs.get("temperature", self.default_temperature)
            max_tokens = kwargs.get("max_tokens", self.default_max_tokens)

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise RateLimitError("Rate limit exceeded. Please try again later.")

        except openai.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Invalid API key")

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"API error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in streaming: {e}")
            raise LLMServiceError(f"Failed to generate streaming response: {str(e)}")

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate).

        Args:
            text: Text to count tokens for

        Returns:
            int: Approximate token count
        """
        try:
            return len(text) // 4
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the OpenAI service.

        Returns:
            Dict with health status
        """
        try:
            start_time = time.time()

            await self.validate_connection()

            end_time = time.time()
            response_time = end_time - start_time

            return {
                "status": "healthy",
                "provider": "openai",
                "model": self.model,
                "response_time": response_time,
                "timestamp": start_time,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "openai",
                "error": str(e),
                "timestamp": time.time(),
            }
