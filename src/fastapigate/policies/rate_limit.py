import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Any

from fastapi import Request, Response
from pydantic import BaseModel

from fastapigate.core.types import BasePolicy

class RateLimitPolicyConfig(BaseModel):
    requests_per_minute: Optional[int] = None
    requests_per_minute_per_ip: Optional[int] = None
    requests_per_minute_per_user: Optional[int] = None
    requests_per_minute_per_user_per_ip: Optional[int] = None

@dataclass
class RateLimitPolicy(BasePolicy[RateLimitPolicyConfig]):
    """
    A rate limiting policy enforcing limits at multiple levels:
      - Global requests per minute
      - Requests per minute per IP
      - Requests per minute per user (if provided via "X-User" header)
      - Requests per minute per user per IP

    This implementation uses a fixed 60-second window and
    maintains a dedicated asyncio.Lock for each key to reduce contention.
    """
    _counters: dict[str, tuple[float, int]] = field(default_factory=dict, init=False)
    _locks: dict[str, asyncio.Lock] = field(default_factory=dict, init=False)
    _locks_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    async def inbound(self, request: Request) -> Optional[Response]:
        now = time.time()

        # Global rate limit
        requests_per_minute = self.config.requests_per_minute
        if requests_per_minute is not None and requests_per_minute > 0:
            if await self._update_and_check("global", self.config.requests_per_minute, now):
                return Response(
                    status_code=429,
                    content="Global rate limit exceeded"
                )

        # Per-IP rate limit
        ip = request.client.host if request.client else "unknown"
        requests_per_minute_per_ip = self.config.requests_per_minute_per_ip
        if requests_per_minute_per_ip is not None and requests_per_minute_per_ip > 0:
            ip_key = f"ip:{ip}"
            if await self._update_and_check(ip_key, requests_per_minute_per_ip, now):
                return Response(
                    status_code=429,
                    content=f"Rate limit exceeded for IP {ip}"
                )

        # Per-user rate limit (if provided via "X-User" header)
        user = request.headers.get("X-User")
        requests_per_minute_per_user = self.config.requests_per_minute_per_user
        if user and requests_per_minute_per_user is not None and requests_per_minute_per_user > 0:
            user_key = f"user:{user}"
            if await self._update_and_check(user_key, requests_per_minute_per_user, now):
                return Response(
                    status_code=429,
                    content=f"Rate limit exceeded for user {user}"
                )

        # Per-user-per-IP rate limit
        requests_per_minute_per_user_per_ip = self.config.requests_per_minute_per_user_per_ip
        if user and requests_per_minute_per_user_per_ip is not None and requests_per_minute_per_user_per_ip > 0:
            user_ip_key = f"user_ip:{user}:{ip}"
            if await self._update_and_check(user_ip_key, requests_per_minute_per_user_per_ip, now):
                return Response(
                    status_code=429,
                    content=f"Rate limit exceeded for user {user} from IP {ip}"
                )

        return None

    async def _update_and_check(self, key: str, limit: int, now: float) -> bool:
        """
        Update the counter for the given key and return True if the limit has been reached.
        Uses a fixed window of 60 seconds.
        """
        lock = await self._get_lock(key)
        async with lock:
            timestamp, count = self._counters.get(key, (now, 0))
            # Reset counter if the window has passed
            if now - timestamp > 60:
                timestamp, count = now, 0
            if count >= limit:
                return True
            self._counters[key] = (timestamp, count + 1)
            return False

    async def _get_lock(self, key: str) -> asyncio.Lock:
        """
        Return the asyncio.Lock for a specific key, creating one if necessary.
        """
        if key not in self._locks:
            async with self._locks_lock:
                if key not in self._locks:
                    self._locks[key] = asyncio.Lock()
        return self._locks[key]


