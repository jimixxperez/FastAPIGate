import logging 
from contextvars import ContextVar
from typing import AsyncIterable, Awaitable, Callable, Iterable, Optional, Type, get_args, cast, Any
from typing import AsyncIterable, Iterable, Optional, Type, get_args, cast, Any

from core.policy import PolicyRegistry
from core.types import BasePolicy
from core.config import GatewayConfig
from dataclasses import dataclass, field

from fastapi import Request
from fastapi.responses import Response
from pydantic import BaseModel

logger = logging.getLogger(__name__)

gateway_context: ContextVar[dict[str, Any]] = ContextVar("GatewayContextVar")

def _get_policy_config_class_from_generic(policy: Type[BasePolicy]) -> Type[BaseModel]:
    policy_class = cast(Type[BaseModel], get_args(policy.__orig_bases__[0])[0])
    return policy_class

@dataclass
class GatewayContext:
    gateway: "Gateway"
    call_next: Callable[[Request], Awaitable[Response]]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: Optional[TracebackType]):
        ...

    
    async def call_before(self, request: Request) -> Optional[Response]:
        for policy in self.gateway._inbound_policies:
            response = await policy.inbound(request)
            if response:
                return response
        for policy in self.gateway._backend_policies:
            response = await policy.backend(request)
            if response:
                return response
        return None
    
    async def call_after(self, request: Request, backend_response: Response) -> Optional[Response]:
        for policy in self.gateway._outbound_policies:
            response = await policy.outbound(request, backend_response)
            return response
        return None

    async def call_on_error(self, request: Request, exc: Exception, context: dict[str, Any]) -> Optional[Response]:
        for policy in self.gateway._on_error_policies:
            response = await policy.on_error(request, exc, context)
            return response
        return None
    
    async def run(self, request: Request) -> Response:
        try: 
            response = await self.call_before(request)
            if response:
                return response
            backend_response = await self.call_next(request)
            response = await self.call_after(request, backend_response)
            if response:
                return response
            return backend_response
        except Exception as exc:
            response = await self.call_on_error(request, exc, context)
            if response:
                return response
            raise exc

@dataclass
class Gateway:
    gateway_config: GatewayConfig
    policy_registry: PolicyRegistry

    _inbound_policies: list[BasePolicy] = field(default_factory=list)
    _backend_policies: list[BasePolicy] = field(default_factory=list)
    _outbound_policies: list[BasePolicy] = field(default_factory=list)
    _on_error_policies: list[BasePolicy] = field(default_factory=list)

    def _setup_policies(self, policy_id: str, policy_config: dict[str, Any]) -> BasePolicy:
        PolicyClass = self.policy_registry.get(policy_id)
        PolicyConfig = _get_policy_config_class_from_generic(PolicyClass)
        policy_config_instance = PolicyConfig(**policy_config)
        return PolicyClass(config=policy_config_instance)
    
    def __post_init__(self):
        logger.info("Initializing Gateway")
        logger.debug(f"Gateway config: {self.gateway_config.model_dump_json(indent=2)}")
        global_policies = self.gateway_config.global_policies
        logger.debug("Initializing global policies")
        logger.debug("Inbound policies")
        for inbound_policy_config in global_policies.inbound:
            policy_id = list(inbound_policy_config.keys())[0]
            policy_config = inbound_policy_config[policy_id]
            base_policy = self._setup_policies(policy_id, policy_config)
            self._inbound_policies.append(base_policy)

        logger.debug("Backend policies")
        for backend_policy_config in global_policies.backend:
            policy_id = list(backend_policy_config.keys())[0]
            policy_config = backend_policy_config[policy_id]
            base_policy = self._setup_policies(policy_id, policy_config)
            self._backend_policies.append(base_policy)

        logger.debug("Outbound policies")
        for outbound_policy_config in global_policies.outbound:
            policy_id = list(outbound_policy_config.keys())[0]
            policy_config = outbound_policy_config[policy_id]
            base_policy = self._setup_policies(policy_id, policy_config)
            self._outbound_policies.append(base_policy)

        logger.debug("On Error policies")
        for on_error_policy_config in global_policies.on_error:
            policy_id = list(on_error_policy_config.keys())[0]
            policy_config = on_error_policy_config[policy_id]
            base_policy = self._setup_policies(policy_id, policy_config)
            self._on_error_policies.append(base_policy)

    def __call__(self, call_next: Callable[[Request], Awaitable[Response]]) -> GatewayContext:
        return GatewayContext(self, call_next)


