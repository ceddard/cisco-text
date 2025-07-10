from abc import abstractmethod
from typing import Dict, Any, AsyncGenerator
import logging

from app.core.interfaces import ChatService
from app.services.llm.llm_service_manager import LLMServiceManager

logger = logging.getLogger(__name__)


class BaseChatService(ChatService):
    """Base implementation for chat services."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_manager = LLMServiceManager(config)
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this service."""
        pass

    @property
    @abstractmethod
    def service_type(self) -> str:
        """Return the service type identifier."""
        pass

    async def process_query(self, query: str) -> str:
        """
        Process a user query and return a response.

        Args:
            query: The user's query

        Returns:
            str: The processed response or a dict with response and image_url for services that support images
        """
        try:
            user_message = self._format_user_message(query)
            kwargs = self._get_llm_kwargs()

            response = await self.llm_manager.generate_response(
                system_prompt=self.system_prompt, user_message=user_message, **kwargs
            )

            return response

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return self._get_error_message(str(e))

    async def process_query_stream(self, query: str) -> AsyncGenerator[str, None]:
        """
        Process a user query and yield streaming response chunks.

        Args:
            query: The user's query

        Yields:
            str: Chunks of the processed response
        """
        try:
            user_message = self._format_user_message(query)
            kwargs = self._get_llm_kwargs()

            async for chunk in self.llm_manager.generate_streaming_response(
                system_prompt=self.system_prompt, user_message=user_message, **kwargs
            ):
                yield chunk

        except Exception as e:
            self.logger.error(f"Error in streaming response: {e}")
            yield self._get_error_message(str(e))

    def _format_user_message(self, query: str) -> str:
        """Format the user message. Override in subclasses if needed."""
        return query

    def _get_llm_kwargs(self) -> Dict[str, Any]:
        """Get LLM kwargs using service configuration."""
        from app.config import settings

        service_settings = settings.AVAILABLE_SERVICES.get(self.service_type, {})

        temperature = service_settings.get(
            "temperature", self.config.get("temperature", 0.7)
        )

        return {"temperature": temperature}

    def _get_error_message(self, error: str) -> str:
        """Get error message for the user. Override in subclasses if needed."""
        return (
            f"Sorry, I couldn't process your request right now. Please try again later."
        )
