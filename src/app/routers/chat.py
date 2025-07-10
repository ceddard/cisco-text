from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.chat_service_factory import ChatServiceFactory
from app.services.llm.openai_provider import OpenAIProvider
from app.config import settings
from app.exceptions import (
    InvalidServiceTypeError,
    ChatServiceError,
    AsyncProcessingError
)
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

factory = ChatServiceFactory()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the chatbot and get a response.

    Args:
        request: ChatRequest containing prompt type and query
        background_tasks: FastAPI background tasks

    Returns:
        ChatResponse: The chatbot's response
    """

    try:
        service = factory.create_service(request.prompt, settings.LLM_CONFIG)
        result = await service.process_query(query=request.query)
        
        # Handle both string and dict responses (for services with images, ok? in future, i will add more types, maybe...)
        if isinstance(result, dict):
            return ChatResponse(
                response=result.get("response", ""),
                chat_type=request.prompt,
                image_url=result.get("image_url")
            )
        else:
            return ChatResponse(response=result, chat_type=request.prompt, image_url=None)

    except InvalidServiceTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/message/stream")
async def stream_message(request: ChatRequest):
    """
    Send a message to the chatbot and get a streaming response.

    Args:
        request: ChatRequest containing prompt type and query

    Returns:
        StreamingResponse: The chatbot's response as a stream of data
    """

    try:
        service = factory.create_service(request.prompt, settings.LLM_CONFIG)

        async def response_generator():
            try:
                response_stream = await service.process_query_stream(request.query)

                async for chunk in response_stream:
                    yield json.dumps(
                        {"chunk": chunk, "chat_type": request.prompt}
                    ) + "\n"

            except AsyncProcessingError as e:
                logger.error(f"Async processing error: {e}")
                yield json.dumps({"error": f"Processing error: {str(e)}"}) + "\n"
            except Exception as e:
                logger.error(f"Unexpected error during streaming: {e}")
                yield json.dumps(
                    {"error": f"An unexpected error occurred: {str(e)}"}
                ) + "\n"

        return StreamingResponse(
            response_generator(), media_type="application/x-ndjson"
        )

    except InvalidServiceTypeError as e:
        logger.warning(f"Invalid service type requested: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ChatServiceError as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/services")
async def get_available_services():
    """
    Get a list of available chat services.

    Returns:
        dict: List of available service types
    """
    return {
        "services": factory.get_available_services(),
        "service_details": settings.AVAILABLE_SERVICES,
    }


@router.get("/health")
async def health_check():
    """
    Perform a health check on the chat services and LLM provider.

    Returns:
        dict: Health status
    """
    try:
        provider = OpenAIProvider(settings.LLM_CONFIG)
        llm_health = await provider.health_check()

        services = factory.get_available_services()

        return {
            "status": "healthy",
            "llm_provider": llm_health,
            "available_services": services,
            "service_count": len(services),
        }

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the current LLM model.

    Returns:
        dict: Model information
    """
    try:
        provider = OpenAIProvider(settings.LLM_CONFIG)
        model_info = await provider.get_model_info()

        return {
            "model_info": model_info,
            "config": {
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
                "debug": settings.DEBUG,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get model info: {str(e)}"
        )
