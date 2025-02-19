import asyncio
from dataclasses import dataclass
from typing import Optional

from fastapigate.core.types import BasePolicy
from fastapi import Request, Response
from pydantic import BaseModel

class RetryPolicyConfig(BaseModel):
    max_attempts: int = 3
    backoff_seconds: float = 1.0

@dataclass
class RetryPolicy(BasePolicy[RetryPolicyConfig]):

    async def on_error(self, request: Request, exc: Exception, context: dict) -> Optional[Response]:
        """
        If the exception occurred during the backend or outbound phase,
        we attempt to re-invoke the backend call up to `max_attempts` times.
        
        The 'context' dict can store details like the function needed
        to call the backend, the previously failed attempt count, etc.
        """
        phase = context.get("phase")  
        # We'll only retry if the error happened in the 'backend' or 'outbound' phase.
        if phase not in ("backend", "outbound"):
            return None

        # Grab the call_backend function or response from context
        call_backend_fn = context.get("call_backend_fn")
        if not call_backend_fn:
            return None  # can't retry if we don't know how to call the backend

        attempt_count = context.get("attempt_count", 1)

        if attempt_count >= self.config.max_attempts:
            # Already tried enough times, give up
            return None

        # Wait some backoff time
        await asyncio.sleep(self.config.backoff_seconds)

        # Increment attempt count
        context["attempt_count"] = attempt_count + 1

        # Re-invoke the backend call, returning its result or raising again
        try:
            backend_response = await call_backend_fn()
            return backend_response  # If successful, we have a new response
        except Exception as e:
            # If it fails again, we do nothing here. Possibly the next on-error policy can handle it,
            # or the same RetryPolicy might get invoked again if it's configured in sequence.
            return None
