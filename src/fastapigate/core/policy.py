from typing import Any, Optional, Protocol, TypeVar, Generic
from pydantic import BaseModel, Field
from fastapi import Request, Response
from fastapigate.core.types import BasePolicy



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


