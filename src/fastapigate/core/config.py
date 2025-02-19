import yaml
from typing import Any, Optional, Protocol, TypeVar, Generic, TypeAlias
from pydantic import BaseModel, Field, ConfigDict, TypeAdapter
from pydantic.alias_generators import to_camel


PolicyId: TypeAlias = str
PolicyConfig: TypeAlias = dict[str, Any]
RawPolicyEntry: TypeAlias = dict[PolicyId, PolicyConfig]

class PhasePolicies(BaseModel):
    inbound: list[RawPolicyEntry] = Field(default_factory=list)
    backend: list[RawPolicyEntry] = Field(default_factory=list) 
    outbound: list[RawPolicyEntry] = Field(default_factory=list)
    on_error: list[RawPolicyEntry] = Field(default_factory=list)

    model_config = ConfigDict(alias_generator=to_camel)

def load_config():
    with open("config.yaml", "r") as f:
        config_dict = yaml.safe_load(f)
    return config_dict

class GatewayConfig(BaseModel):
    global_policies: PhasePolicies 

    model_config = ConfigDict(alias_generator=to_camel)

    @classmethod
    def from_file(cls, path: str):
        with open(path, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)

