import json
import redis.asyncio as redis
import logging
from typing import Dict, Any, Optional
import datetime

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self, redis_url: str, ttl: int = 604800):
        self.redis_url = redis_url
        self.redis = None
        self.ttl = ttl

    async def initialize(self):
        """Initialize the Redis connection."""
        try:
            self.redis = await redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def store_log(self, key: str, data: Dict[str, Any]) -> bool:
        """Store a log entry in Redis with TTL."""
        if not self.redis:
            logger.error("Redis not initialized")
            return False
        
        try:
            serializable_data = self._prepare_for_serialization(data)
            json_data = json.dumps(serializable_data)
            
            await self.redis.set(key, json_data, ex=self.ttl)
            return True
        except Exception as e:
            logger.error(f"Failed to store log in Redis: {e}")
            return False
    
    async def get_log(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a log entry from Redis."""
        if not self.redis:
            logger.error("Redis not initialized")
            return None
        
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve log from Redis: {e}")
            return None
    
    async def get_logs_by_pattern(self, pattern: str) -> list:
        """Retrieve logs matching a pattern."""
        if not self.redis:
            logger.error("Redis not initialized")
            return []
        
        try:
            keys = await self.redis.keys(pattern)
            if not keys:
                return []
            
            logs = []
            for key in keys:
                log = await self.get_log(key)
                if log:
                    logs.append({"key": key, "data": log})
            
            return logs
        except Exception as e:
            logger.error(f"Failed to retrieve logs by pattern from Redis: {e}")
            return []
    
    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
    
    def _prepare_for_serialization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for JSON serialization by converting non-serializable types."""
        serializable_data = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                serializable_data[key] = self._prepare_for_serialization(value)
            elif isinstance(value, (datetime.datetime, datetime.date)):
                serializable_data[key] = value.isoformat()
            else:
                serializable_data[key] = value
        
        return serializable_data
