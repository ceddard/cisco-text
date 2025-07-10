from typing import Dict, Any, AsyncGenerator, AsyncGenerator
import logging

from app.core.interfaces import ChatService, ServiceFactory
from app.services.chat import (
    InventorChatService,
    TranslatorChatService,
    CuratorChatService,
)
from app.exceptions import InvalidServiceTypeError

logger = logging.getLogger(__name__)


class ChatServiceFactory(ServiceFactory):
    """Factory for creating chat service instances."""

    def __init__(self):
        self._SERVICE_REGISTRY = {
            "inventor": InventorChatService,
            "translator": TranslatorChatService,
            "curator": CuratorChatService,
        }

    def create_service(self, service_type: str, config: Dict[str, Any]) -> ChatService:
        """
        Create a chat service instance.

        Args:
            service_type: The type of service to create
            config: Configuration for the service

        Returns:
            ChatService: The created service instance

        Raises:
            InvalidServiceTypeError: If the service type is not supported
        """
        if service_type not in self._SERVICE_REGISTRY:
            available_services = ", ".join(self._SERVICE_REGISTRY.keys())
            raise InvalidServiceTypeError(
                f"Service type '{service_type}' not supported. "
                f"Available services: {available_services}"
            )

        service_class = self._SERVICE_REGISTRY[service_type]
        logger.info(f"Creating service: {service_type}")

        return service_class(config)

    def get_available_services(self) -> list:
        """
        Get list of available service types.

        Returns:
            list: List of available service type names
        """
        return list(self._SERVICE_REGISTRY.keys())

    async def process_query(
        self, service_type: str, query: str, config: Dict[str, Any]
    ) -> str:
        """
        Create service and process query in one call.

        Args:
            service_type: The type of service to use
            query: The user's query
            config: Configuration for the service

        Returns:
            str: The processed response
        """
        service = self.create_service(service_type, config)
        return await service.process_query(query)

    async def process_query_stream(
        self, service_type: str, query: str, config: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Create service and process streaming query in one call.

        Args:
            service_type: The type of service to use
            query: The user's query
            config: Configuration for the service

        Yields:
            str: Chunks of the processed response
        """
        service = self.create_service(service_type, config)
        async for chunk in service.process_query_stream(query):
            yield chunk
