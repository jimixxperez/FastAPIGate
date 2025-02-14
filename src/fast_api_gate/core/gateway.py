import logging 

from core.policy import PolicyRegistry
from core.types import BasePolicy
from core.config import GatewayConfig
from dataclasses import dataclass, field
from fastapi import Request

logger = logging.getLogger(__name__)

@dataclass
class Gateway:
    config: GatewayConfig
    policy_registry: PolicyRegistry
    inbound_policies: list[BasePolicy] = field(default_factory=list)
    backend_policies: list[BasePolicy] = field(default_factory=list)
    outbound_policies: list[BasePolicy] = field(default_factory=list)
    on_error_policies: list[BasePolicy] = field(default_factory=list)

    
    def __post_init__(self):
        logger.info("Initializing Gateway")
        logger.debug(f"Gateway config: {self.config.model_dump_json(indent=2)}")
        
        logger.debug("Register inbound policies")
        for inbound_policy in self.config.global_policies.inbound:
            policy_registry_entry = self.policy_registry.get(inbound_policy.id)
            policy_config = policy_registry_entry.config_model(**inbound_policy.config)

        logger.debug("Register inbound policies")
        for backend_policy in self.config.global_policies.backend:
            self.policy_registry.register(backend_policy.id, backend_policy.config, backend_policy.policy)


        logger.debug("Register outbound policies")
        for outbound_policy in self.config.global_policies.outbound:
            self.policy_registry.register(outbound_policy.id, outbound_policy.config, outbound_policy.policy)

        logger.debug("Register onError policies")
        for on_error_policy in self.config.global_policies.onError:
            self.policy_registry.register(on_error_policy.id, on_error_policy.config, on_error_policy.policy)

    async def run(self, request: Request):
        ...

