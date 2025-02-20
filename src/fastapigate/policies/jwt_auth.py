import jwt
from jwt import PyJWKClient
from dataclasses import dataclass
from typing import Optional, Any

from fastapi import Request, Response
from pydantic import BaseModel

from fastapigate.core.types import BasePolicy

class JWTAuthPolicyConfig(BaseModel):
    jwk_url: str
    audience: str
    issuer: str
    algorithms: list[str] = ["RS256"]

@dataclass
class JWTAuthPolicy(BasePolicy[JWTAuthPolicyConfig]):
    """
    A JWT authentication policy that verifies the Bearer token from the Authorization header.
    On successful validation, the decoded token is attached to `request.state.jwt_payload`.
    If verification fails, a 401 Unauthorized response is returned.
    """
    _jwk_client: Optional[PyJWKClient] = None

    def _get_jwk_client(self) -> PyJWKClient:
        if self._jwk_client is None:
            self._jwk_client = PyJWKClient(self.config.jwk_url)
        return self._jwk_client

    async def inbound(self, request: Request) -> Optional[Response]:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                content="Missing or invalid Authorization header"
            )
        token = auth_header[len("Bearer "):].strip()
        try:
            jwk_client = self._get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token).key
            decoded = jwt.decode(
                token,
                signing_key,
                algorithms=self.config.algorithms,
                audience=self.config.audience,
                issuer=self.config.issuer,
            )
            # Attach the decoded payload to the request for later use.
            request.state.jwt_payload = decoded
        except Exception as e:
            return Response(
                status_code=401,
                content=f"Invalid token: {str(e)}"
            )
        return None


