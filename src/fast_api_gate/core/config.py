from typing import Any, Optional, Protocol, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

class RawPolicyEntry(BaseModel):
    id: str
    config: dict[str, Any] 

class PhasePolicies(BaseModel):
    inbound: list[RawPolicyEntry] = Field(default_factory=list)
    backend: list[RawPolicyEntry] = Field(default_factory=list) 
    outbound: list[RawPolicyEntry] = Field(default_factory=list)
    on_error: list[RawPolicyEntry] = Field(default_factory=list)

    ConfigDict = ConfigDict(alias_generator=to_camel)

class GatewayConfig(BaseModel):
    global_policies: PhasePolicies 

    ConfigDict = ConfigDict(alias_generator=to_camel)


