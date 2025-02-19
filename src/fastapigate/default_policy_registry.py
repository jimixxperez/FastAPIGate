from fastapigate.core.policy import PolicyRegistry
#from fastapigate.policies.jwt_auth import JWTAuth
#from fastapigate.policies.rate_limit import RateLimit
from fastapigate.policies.retry import RetryPolicy

def default_policy_registry() -> PolicyRegistry:
    registry = PolicyRegistry()
    #registry.register("jwt_auth", JWTAuth)
    #registry.register("rate_limit", RateLimit)
    registry.register("retry", RetryPolicy)
    return registry
