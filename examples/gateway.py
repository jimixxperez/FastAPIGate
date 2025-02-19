from fastapigate import GatewayMiddleware, GatewayConfig
from fastapi import FastAPI

app = FastAPI()

config = GatewayConfig.from_file("./gate_config.yaml")

app.add_middleware(
    GatewayMiddleware.from_gateway_config, 
    gateway_config=config,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
