import logging 
from contextvars import ContextVar
from types import TracebackType
from typing import AsyncIterable, Iterable, Optional, Type, get_args, cast, Any

from core.policy import PolicyRegistry
from core.types import BasePolicy
from core.config import GatewayConfig
from dataclasses import dataclass, field

from fastapi import Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

gateway_context: ContextVar[dict[str, Any]] = ContextVar("GatewayContextVar")

def _get_policy_config_class_from_generic(policy: Type[BasePolicy]) -> Type[BaseModel]:
    policy_class = cast(Type[BaseModel], get_args(policy.__orig_bases__[0])[0])
    return policy_class

class GatewayContext:
    def __init__(self, gateway: "Gateway"):
        self.gateway = gateway
    
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
    
    async def call_after(self, request: Request, response: Response) -> Optional[Response]:
        for policy in self.gateway._outbound_policies:
            response = await policy.outbound(request, response)
            if response:
                return response
        return response


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
            base_policy = self._setup_policies(inbound_policy_config.id, inbound_policy_config.config)
            self._inbound_policies.append(base_policy)

        logger.debug("Backend policies")
        for backend_policy_config in global_policies.backend:
            base_policy = self._setup_policies(backend_policy_config.id, backend_policy_config.config)
            self._backend_policies.append(base_policy)

        logger.debug("Outbound policies")
        for outbound_policy_config in global_policies.outbound:
            base_policy = self._setup_policies(outbound_policy_config.id, outbound_policy_config.config)
            self._outbound_policies.append(base_policy)

        logger.debug("On Error policies")
        for on_error_policy_config in global_policies.on_error:
            base_policy = self._setup_policies(on_error_policy_config.id, on_error_policy_config.config)
            self._on_error_policies.append(base_policy)

    async def __aenter__(self):
        return GatewayContext(self)
    
    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: Optional[TracebackType]):
        for on_error_policy in self._on_error_policies:
            await on_error_policy.on_error(None, exc_val, context)


    async def run(self, request: Request) -> AsyncIterable[Response]:
    #    """Run the gateway"""
    #    try:
    #        for policy in self._inbound_policies:
    #            response = await policy.inbound(request)
    #            if response:
    #                yield response
    #                return

    #        for policy in self._backend_policies:
    #            response = await policy.backend(request)
    #            if response:
    #                yield response
    #                return

    #        # Forward the request to the next middleware
    #        # TODO: Forward the request to the next middleware
    #        yield

    #        for policy in self._outbound_policies:
    #            response = await policy.outbound(request, response)
    #            if response:
    #                yield response
    #                return
    #    except Exception as exc:
    #        for policy in self._on_error_policies:
    #            response = await policy.on_error(request, exc, context)
    #            if response:
    #                yield response
    #                return
