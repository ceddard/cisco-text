from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.redis_service import RedisService
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)

async def get_redis_service():
    from app.main import redis_service
    return redis_service

@router.get("/")
async def get_logs(
    request_id: Optional[str] = Query(None, description="Filter by specific request ID"),
    path: Optional[str] = Query(None, description="Filter by API path"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Get API logs from Redis with optional filtering.
    """
    try:
        if request_id:
            request_log = await redis_service.get_log(f"request:{request_id}")
            response_log = await redis_service.get_log(f"response:{request_id}")
            
            if not request_log:
                raise HTTPException(status_code=404, detail=f"No logs found for request ID: {request_id}")
                
            return {
                "request": request_log,
                "response": response_log
            }
        
        pattern = "request:*"
        all_requests = await redis_service.get_logs_by_pattern(pattern)
        
        if path:
            all_requests = [
                req for req in all_requests 
                if req["data"].get("path") and path in req["data"].get("path")
            ]
        
        all_requests.sort(key=lambda x: x["data"].get("timestamp", 0), reverse=True)
        all_requests = all_requests[:limit]
        
        result = []
        for req in all_requests:
            request_id = req["data"].get("request_id")
            if request_id:
                response_log = await redis_service.get_log(f"response:{request_id}")
                result.append({
                    "request": req["data"],
                    "response": response_log
                })
        
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@router.delete("/")
async def clear_logs(redis_service: RedisService = Depends(get_redis_service)):
    """
    Clear all logs from Redis.
    """
    try:
        request_keys = await redis_service.redis.keys("request:*")
        response_keys = await redis_service.redis.keys("response:*")
        
        if request_keys:
            await redis_service.redis.delete(*request_keys)
        if response_keys:
            await redis_service.redis.delete(*response_keys)
        
        return {"message": f"Cleared {len(request_keys) + len(response_keys)} log entries"}
    
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {str(e)}")
