from typing import Any, Optional, Protocol, TypeVar, Generic
from dataclasses import dataclass
from fastapi import Request, Response

PolicyConfig = TypeVar("PolicyConfig", bound=BaseModel)

@dataclass
class BasePolicy(Generic[PolicyConfig]):
    config: PolicyConfig

    """A simple multi-phase policy base with default no-ops."""
    async def inbound(self, request: Request) -> Optional[Response]:
        ...
    async def backend(self, request: Request) -> Optional[Response]:
        ...
    async def outbound(self, request: Request, response: Response) -> Optional[Response]:
        ...
    async def on_error(self, request: Request, exc: Exception, context: dict[str, Any]) -> Optional[Response]:
        ...
