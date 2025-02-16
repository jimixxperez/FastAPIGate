from typing import Any, Optional, Protocol, TypeVar, Generic
from pydantic import BaseModel, Field
from fastapi import Request, Response
from core.types import BasePolicy


class RawPolicyEntry(BaseModel):
    id: str
    config: dict[str, Any] 

class PhasePolicies(BaseModel):
    inbound: list[RawPolicyEntry] = Field(default_factory=list)
    backend: list[RawPolicyEntry] = Field(default_factory=list) 
    outbound: list[RawPolicyEntry] = Field(default_factory=list)
    onError: list[RawPolicyEntry] = Field(default_factory=list)

class GatewayConfig(BaseModel):
    globalPolicies: PhasePolicies = PhasePolicies()
    # For brevity, skipping workspace/products/APIs. We'll just do global in this snippet.
    #
PolicyConfig = TypeVar("PolicyConfig", bound=BaseModel)

from dataclasses import dataclass

#@dataclass
#class BasePolicy(Generic[PolicyConfig]):
#    config: PolicyConfig
#
#    """A simple multi-phase policy base with default no-ops."""
#    async def inbound(self, request: Request) -> Optional[Response]:
#        return None
#        
#    async def backend(self, request: Request) -> Optional[Response]:
#        return None
#
#    async def outbound(self, request: Request, response: Response) -> Optional[Response]:
#        return None
#
#    async def on_error(self, request: Request, exc: Exception, context: dict[str, Any]) -> Optional[Response]:
#        return None

from dataclasses import dataclass, field
from typing import NamedTuple, Type


@dataclass
class PolicyRegistry:
    _registry: dict[str, Type[BasePolicy]] = field(default_factory=dict)

    def register(self, id: str,  policy: Type[BasePolicy]):
        self._registry[id] = policy

    def get(self, id: str) -> Type[BasePolicy[Any]]:
        if id not in self._registry:
            raise ValueError(f"Unknown policy id: {id}")
        return self._registry[id]


