from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

from core.gateway import Gateway

class GatewayMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, gateway: Gateway):
        super().__init__(app)
        self.gateway = gateway

    async def dispatch(self, request: Request, call_next) -> Response:
        async with self.gateway as ctx:
            response = await ctx.call_before(request)
            if response:
                return response
            response = await call_next(request)
            response = await ctx.call_after(request, response)
        return response
