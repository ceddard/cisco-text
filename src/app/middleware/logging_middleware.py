import time
import json
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.services.redis_service import RedisService
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, redis_service: RedisService):
        super().__init__(app)
        self.redis_service = redis_service

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        request_body = await self._get_request_body(request)
        request_log = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "body": request_body,
            "timestamp": start_time,
        }
        
        if not self.redis_service.connection_error:
            await self.redis_service.store_log(f"request:{request_id}", request_log)
        
        response = await self._get_response(request, call_next)
        
        process_time = time.time() - start_time
        if not self.redis_service.connection_error:
            response_body = response.body.decode() if hasattr(response, "body") else ""
            response_log = {
                "request_id": request_id,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": self._parse_response_body(response_body),
                "process_time": process_time,
                "timestamp": time.time(),
            }
            
            await self.redis_service.store_log(f"response:{request_id}", response_log)
        
        logger.info(
            f"RequestID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {process_time:.3f}s"
        )
        
        return response
    
    async def _get_request_body(self, request: Request) -> dict:
        """Extract and parse request body."""
        try:
            body = await request.body()
            body_str = body.decode()
            if body_str:
                try:
                    return json.loads(body_str)
                except json.JSONDecodeError:
                    return {"raw": body_str}
            return {}
        except Exception as e:
            logger.error(f"Error parsing request body: {e}")
            return {"error": "Failed to parse request body"}
    
    async def _get_response(self, request: Request, call_next):
        """Get response with body preserved."""
        response = await call_next(request)
        
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
    
    def _parse_response_body(self, body: str) -> dict:
        """Parse response body to JSON if possible."""
        if not body:
            return {}
        
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body[:1000] + ("..." if len(body) > 1000 else "")}
