from typing import Dict, Any, AsyncGenerator
import logging

from app.core.interfaces import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class LLMServiceManager:
    """Manager class for LLM provider interactions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = self._create_provider()

    def _create_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider based on configuration."""
        provider_type = self.config.get("provider", "openai")

        if provider_type == "openai":
            return OpenAIProvider(self.config)
        else:
            raise ConfigurationError(f"Unsupported LLM provider: {provider_type}")

    async def generate_response(
        self, system_prompt: str, user_message: str, **kwargs
    ) -> str:
        """
        Generate a response using the configured LLM provider.

        Args:
            system_prompt: The system prompt to set the context
            user_message: The user's message
            **kwargs: Additional parameters for the provider

        Returns:
            str: The generated response
        """
        return await self.provider.generate_response(
            system_prompt=system_prompt, user_message=user_message, **kwargs
        )

    async def generate_streaming_response(
        self, system_prompt: str, user_message: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using the configured LLM provider.

        Args:
            system_prompt: The system prompt to set the context
            user_message: The user's message
            **kwargs: Additional parameters for the provider

        Yields:
            str: Chunks of the generated response
        """
        async for chunk in self.provider.generate_streaming_response(
            system_prompt=system_prompt, user_message=user_message, **kwargs
        ):
            yield chunk
