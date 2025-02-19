from typing import Any, Optional, Protocol, TypeVar, Generic, runtime_checkable
from dataclasses import dataclass
from fastapi import Request, Response
from pydantic import BaseModel

PolicyConfig = TypeVar("PolicyConfig", bound=BaseModel)

@runtime_checkable
class InboundPolicy(Protocol[PolicyConfig]):
    config: PolicyConfig
    async def inbound(self, request: Request) -> Optional[Response]:
        ...

@runtime_checkable
class BackendPolicy(Protocol[PolicyConfig]):
    config: PolicyConfig
    async def backend(self, request: Request) -> Optional[Response]:
        ...

@runtime_checkable
class OutboundPolicy(Protocol[PolicyConfig]):
    config: PolicyConfig
    async def outbound(self, request: Request, response: Response) -> Optional[Response]:
        ...

@runtime_checkable
class OnErrorPolicy(Protocol[PolicyConfig]):
    config: PolicyConfig
    async def on_error(self, request: Request, exc: Exception, context: dict[str, Any]) -> Optional[Response]:
        ...

Policy = InboundPolicy[PolicyConfig] | BackendPolicy[PolicyConfig] | OutboundPolicy[PolicyConfig] | OnErrorPolicy[PolicyConfig]

@dataclass
class BasePolicy(Generic[PolicyConfig]):
    config: PolicyConfig

#@dataclass
#class BasePolicy(Generic[PolicyConfig]):
#    config: PolicyConfig
#
#    """A simple multi-phase policy base with default no-ops."""
#    async def inbound(self, request: Request) -> Optional[Response]:
#        ...
#    async def backend(self, request: Request) -> Optional[Response]:
#        ...
#    async def outbound(self, request: Request, response: Response) -> Optional[Response]:
#        ...
#    async def on_error(self, request: Request, exc: Exception, context: dict[str, Any]) -> Optional[Response]:
#        ...
