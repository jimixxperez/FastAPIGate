from typing import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from fastapigate.core.config import GatewayConfig
from fastapigate.core.gateway import Gateway
from fastapigate.default_policy_registry import default_policy_registry
from starlette.middleware.trustedhost import TrustedHostMiddleware

class GatewayMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, gateway: Gateway):
        super().__init__(app)
        self.gateway = gateway

    @classmethod
    def from_gateway_config(cls, app, gateway_config: GatewayConfig):
        gateway = Gateway(gateway_config, default_policy_registry())
        return cls(app, gateway)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        async with self.gateway(call_next) as ctx:
            response = await ctx.run(request)
            return response

            response = await ctx.call_before(request)
            if response:
                return response
            response = await call_next(request)
            response = await ctx.call_after(request, response)
        return response
