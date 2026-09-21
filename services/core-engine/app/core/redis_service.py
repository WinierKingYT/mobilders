"""
Redis Service for Personal Learning Engine.
Provides atomic rate limiting, distributed idempotency caching,
and graceful offline in-memory fallback.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import redis

from app.core.config import settings

logger = logging.getLogger("core.redis")


class RedisService:
    """
    Manages Redis connection, loads redis_init.lua for atomic rate limiting
    and idempotency checking, and gracefully falls back when Redis is offline.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._client: Optional[redis.Redis] = None
        self._lua_script_sha: Optional[str] = None
        self._is_connected: bool = False
        self._init_client()

    def _init_client(self) -> None:
        try:
            client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )
            # Test connection with ping
            client.ping()
            self._client = client
            self._is_connected = True
            self._load_lua_script()
            logger.info("Redis connection established successfully.")
        except Exception as e:
            self._is_connected = False
            self._client = None
            logger.info(
                f"Redis server not available at {self.redis_url} ({e}). "
                "Operating in resilient offline in-memory mode."
            )

    def _load_lua_script(self) -> None:
        if not self._client:
            return
        try:
            base_dir = Path(__file__).resolve().parent.parent.parent
            lua_file = base_dir / "redis_init.lua"
            if lua_file.exists():
                with open(lua_file, "r", encoding="utf-8") as f:
                    lua_code = f.read()
                self._lua_script_sha = self._client.script_load(lua_code)
                logger.debug(f"Loaded redis_init.lua with SHA: {self._lua_script_sha}")
        except Exception as e:
            logger.warning(f"Failed to load redis_init.lua into Redis: {e}")
            self._lua_script_sha = None

    @property
    def is_connected(self) -> bool:
        if not self._client:
            return False
        try:
            self._client.ping()
            self._is_connected = True
            return True
        except Exception:
            self._is_connected = False
            return False

    def check_idempotency_and_rate_limit(
        self,
        rate_key: str,
        idemp_key: str,
        max_requests: int = 2,
        window_seconds: int = 1,
        idemp_ttl: int = 86400,
        client_msg_id: str = "",
    ) -> Tuple[str, Optional[str]]:
        """
        Executes redis_init.lua atomically.
        Returns:
            ("CACHED", cached_data_str)
            ("RATE_LIMITED", current_count_str)
            ("ALLOWED", current_count_str)
        If Redis is offline, returns ("ALLOWED", "1") to allow local processing.
        """
        if not self.is_connected or not self._client or not self._lua_script_sha:
            return ("ALLOWED", "1")

        try:
            result = self._client.evalsha(
                self._lua_script_sha,
                2,
                rate_key,
                idemp_key,
                max_requests,
                window_seconds,
                idemp_ttl,
                client_msg_id,
            )
            if isinstance(result, list) and len(result) >= 2:
                status, data = str(result[0]), str(result[1])
                return (status, data)
            elif isinstance(result, list) and len(result) == 1:
                return (str(result[0]), None)
            return ("ALLOWED", "1")
        except Exception as e:
            logger.warning(f"Redis Lua script execution error: {e}. Falling back.")
            return ("ALLOWED", "1")

    def store_idempotent_response(
        self,
        idemp_key: str,
        response_data: Any,
        ttl_seconds: int = 86400,
    ) -> None:
        """Stores serialized response in Redis with TTL."""
        if not self.is_connected or not self._client or not idemp_key:
            return

        try:
            if isinstance(response_data, str):
                serialized = response_data
            elif hasattr(response_data, "model_dump_json"):
                serialized = response_data.model_dump_json()
            elif hasattr(response_data, "json"):
                serialized = response_data.json()
            else:
                serialized = json.dumps(response_data, ensure_ascii=False, default=str)

            self._client.setex(idemp_key, ttl_seconds, serialized)
        except Exception as e:
            logger.warning(f"Failed to store idempotent response in Redis: {e}")

    def get_idempotent_response(self, idemp_key: str) -> Optional[str]:
        """Retrieves cached response from Redis if present."""
        if not self.is_connected or not self._client or not idemp_key:
            return None

        try:
            return self._client.get(idemp_key)
        except Exception as e:
            logger.warning(f"Failed to get idempotent response from Redis: {e}")
            return None

    def close(self) -> None:
        """Closes the Redis client connection pool."""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            finally:
                self._client = None
                self._is_connected = False

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
