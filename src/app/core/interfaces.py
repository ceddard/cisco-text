from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate_response(
        self, system_prompt: str, user_message: str, **kwargs
    ) -> str:
        """Generate a response using the LLM provider."""
        pass

    @abstractmethod
    async def generate_streaming_response(
        self, system_prompt: str, user_message: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the LLM provider."""
        pass


class ChatService(ABC):
    """Abstract interface for chat services."""

    @abstractmethod
    async def process_query(self, query: str) -> str:
        """Process a user query and return a response."""
        pass

    @abstractmethod
    async def process_query_stream(self, query: str) -> AsyncGenerator[str, None]:
        """Process a user query and yield streaming response chunks."""
        pass

    @property
    @abstractmethod
    def service_type(self) -> str:
        """Return the service type identifier."""
        pass


class ServiceFactory(ABC):
    """Abstract interface for service factories."""

    @abstractmethod
    def create_service(self, service_type: str, config: Dict[str, Any]) -> ChatService:
        """Create a service instance."""
        pass

    @abstractmethod
    def get_available_services(self) -> list:
        """Get list of available services."""
        pass
