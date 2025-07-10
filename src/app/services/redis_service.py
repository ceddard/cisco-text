import json
import redis.asyncio as redis
import logging
from typing import Dict, Any, Optional
import datetime

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self, redis_url: str, ttl: int = 604800, optional: bool = True):
        self.redis_url = redis_url
        self.redis = None
        self.ttl = ttl
        self.optional = optional
        self.connection_error = False

    async def initialize(self):
        """Initialize the Redis connection."""
        try:
            self.redis = await redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
            logger.info(f"Connected to Redis at {self.redis_url}")
            self.connection_error = False
        except Exception as e:
            self.connection_error = True
            if not self.optional:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
            else:
                logger.warning(f"Redis connection failed: {e}. Running in reduced functionality mode.")

    async def store_log(self, key: str, data: Dict[str, Any]) -> bool:
        """Store a log entry in Redis with TTL."""
        if self.connection_error:
            return False
        
        if not self.redis:
            return False
        
        try:
            serializable_data = self._prepare_for_serialization(data)
            json_data = json.dumps(serializable_data)
            
            await self.redis.set(key, json_data, ex=self.ttl)
            return True
        except Exception as e:
            if not self.connection_error:
                logger.warning(f"Failed to store log in Redis: {e}. Further Redis errors will be suppressed.")
                self.connection_error = True
            return False
    
    async def get_log(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a log entry from Redis."""
        if self.connection_error or not self.redis:
            return None
        
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            if not self.connection_error:
                logger.warning(f"Failed to retrieve log from Redis: {e}")
                self.connection_error = True
            return None
    
    async def get_logs_by_pattern(self, pattern: str) -> list:
        """Retrieve logs matching a pattern."""
        if self.connection_error or not self.redis:
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
            if not self.connection_error:
                logger.warning(f"Failed to retrieve logs by pattern from Redis: {e}")
                self.connection_error = True
            return []
    
    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
    
    async def clear_all_logs(self) -> bool:
        """Clear all logs stored in Redis."""
        if self.connection_error or not self.redis:
            return False
        
        try:
            keys = await self.redis.keys("request:*") + await self.redis.keys("response:*")
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} log entries from Redis")
            return True
        except Exception as e:
            if not self.connection_error:
                logger.warning(f"Failed to clear logs from Redis: {e}")
                self.connection_error = True
            return False
    
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
