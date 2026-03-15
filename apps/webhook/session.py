# apps/webhook/session.py
# Session management for WhatsApp conversations.
# Uses Redis when available, falls back to a thread-safe in-memory store.

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class InMemorySessionBackend:
    """Simple in-memory session store with TTL expiration."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._expires: Dict[str, datetime] = {}

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id in self._expires and datetime.utcnow() > self._expires[session_id]:
            self._sessions.pop(session_id, None)
            self._expires.pop(session_id, None)
            return None
        return self._sessions.get(session_id)

    async def save(self, session_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        self._sessions[session_id] = data
        self._expires[session_id] = datetime.utcnow() + timedelta(seconds=ttl_seconds)

    async def delete(self, session_id: str):
        self._sessions.pop(session_id, None)
        self._expires.pop(session_id, None)


class RedisSessionBackend:
    """Redis-backed session store. Requires the redis async client."""

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(self._redis_url, decode_responses=True)
        return self._client

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            client = await self._get_client()
            raw = await client.get(f"session:{session_id}")
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Redis GET failed for session %s: %s", session_id, exc)
            return None

    async def save(self, session_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        try:
            client = await self._get_client()
            await client.set(f"session:{session_id}", json.dumps(data, default=str), ex=ttl_seconds)
        except Exception as exc:
            logger.warning("Redis SET failed for session %s: %s", session_id, exc)

    async def delete(self, session_id: str):
        try:
            client = await self._get_client()
            await client.delete(f"session:{session_id}")
        except Exception as exc:
            logger.warning("Redis DELETE failed for session %s: %s", session_id, exc)


class SessionManager:
    """
    Facade that picks the best available backend.
    Tries Redis first; falls back to in-memory if Redis is unreachable.
    """

    def __init__(self):
        self._backend = None

    def _ensure_backend(self):
        if self._backend is not None:
            return
        from apps.webhook.config import get_settings
        settings = get_settings()
        if settings.redis_url:
            try:
                self._backend = RedisSessionBackend(settings.redis_url)
                logger.info("Session backend: Redis (%s)", settings.redis_url)
            except Exception:
                self._backend = InMemorySessionBackend()
                logger.info("Session backend: InMemory (Redis unavailable)")
        else:
            self._backend = InMemorySessionBackend()
            logger.info("Session backend: InMemory (no REDIS_URL)")

    async def get_session(self, wa_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_backend()
        return await self._backend.get(wa_id)

    async def save_session(self, wa_id: str, state: Dict[str, Any], ttl_seconds: int = 86400):
        self._ensure_backend()
        await self._backend.save(wa_id, state, ttl_seconds)

    async def clear_session(self, wa_id: str):
        self._ensure_backend()
        await self._backend.delete(wa_id)


# Singleton used across the application.
session_manager = SessionManager()
