from typing import Any, Optional, Protocol, TypeVar, Generic
from pydantic import BaseModel, Field

class RawPolicyEntry(BaseModel):
    id: str
    config: dict[str, Any] 

class PhasePolicies(BaseModel):
    inbound: list[RawPolicyEntry] = Field(default_factory=list)
    backend: list[RawPolicyEntry] = Field(default_factory=list) 
    outbound: list[RawPolicyEntry] = Field(default_factory=list)
    onError: list[RawPolicyEntry] = Field(default_factory=list)

class GatewayConfig(BaseModel):
    globalPolicies: PhasePolicies
