from typing import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.gateway import Gateway

class GatewayMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, gateway: Gateway):
        super().__init__(app)
        self.gateway = gateway

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        async with self.gateway(call_next) as ctx:
            response = await ctx.run(request, call_next)
            return response

            response = await ctx.call_before(request)
            if response:
                return response
            response = await call_next(request)
            response = await ctx.call_after(request, response)
        return response
