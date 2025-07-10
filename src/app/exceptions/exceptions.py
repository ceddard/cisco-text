class ChatServiceError(Exception):
    """Base exception for chat service errors."""

    pass


class LLMServiceError(ChatServiceError):
    """Exception raised when LLM service fails."""

    pass


class InvalidServiceTypeError(ChatServiceError):
    """Exception raised when an invalid service type is requested."""

    pass


class ConfigurationError(ChatServiceError):
    """Exception raised when configuration is invalid."""

    pass


class APIError(LLMServiceError):
    """Exception raised when external API calls fail."""

    pass


class AuthenticationError(APIError):
    """Exception raised when API authentication fails."""

    pass


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""

    pass


class AsyncProcessingError(ChatServiceError):
    """Exception raised when asynchronous processing fails."""

    pass


class StreamingError(AsyncProcessingError):
    """Exception raised when streaming operations fail."""

    pass


class ConnectionClosedError(AsyncProcessingError):
    """Exception raised when a connection is unexpectedly closed during streaming."""

    pass


class TimeoutError(AsyncProcessingError):
    """Exception raised when an asynchronous operation times out."""

    pass


class ImageGenerationError(APIError):
    """Exception raised when image generation fails."""

    pass
