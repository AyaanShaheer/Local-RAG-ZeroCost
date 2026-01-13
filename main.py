from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY

app = FastAPI()

# Expose /metrics
app.mount("/metrics", make_asgi_app())

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    endpoint = request.url.path
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        response = await call_next(request)
    return response
