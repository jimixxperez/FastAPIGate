from typing import Any, Optional, Protocol, TypeVar, Generic
from pydantic import BaseModel, Field
from fastapi import Request, Response


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

from dataclasses import dataclass, field
from typing import NamedTuple, Type

class PolicyRegistryEntry(NamedTuple):
    config_model: Type[BaseModel]
    policy: BasePolicy

@dataclass
class PolicyRegistry:
    _registry: dict[str, PolicyRegistryEntry] = field(default_factory=dict)

    def register(self, id: str, config: Type[BaseModel], policy: BasePolicy):
        self._registry[id] = PolicyRegistryEntry(config, policy)

    def get(self, id: str) -> PolicyRegistryEntry:
        if id not in self._registry:
            raise ValueError(f"Unknown policy id: {id}")
        return self._registry[id]

     


