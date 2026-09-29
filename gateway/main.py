import os
import httpx
from fastapi import FastAPI, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.logging.logger import get_logger, request_id_var, trace_id_var
from shared.middleware.tracing import TracingMiddleware
from shared.utils.database import get_db
from shared.models.models import SimulationConfig
from sqlalchemy.orm import Session

logger = get_logger("gateway")
app = FastAPI(title="CloudMart Gateway")

app.add_middleware(TracingMiddleware)

# Services map
SERVICES = {
    "products": os.getenv("CATALOG_URL", "http://catalog:8000"),
    "categories": os.getenv("CATALOG_URL", "http://catalog:8000"),
    "search": os.getenv("CATALOG_URL", "http://catalog:8000"),
    "cart": os.getenv("CART_URL", "http://cart:8000"),
    "checkout": os.getenv("ORDER_URL", "http://order:8000"),
    "orders": os.getenv("ORDER_URL", "http://order:8000"),
    "payments": os.getenv("PAYMENT_URL", "http://payment:8000"),
    "inventory": os.getenv("INVENTORY_URL", "http://inventory:8000"),
}

async def get_identity_token(audience: str) -> str:
    if os.getenv("ENVIRONMENT") != "cloud":
        return ""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience={audience}",
                headers={"Metadata-Flavor": "Google"},
                timeout=2.0
            )
            if resp.status_code == 200:
                return resp.text
    except Exception as e:
        logger.error("Failed to fetch identity token", extra={"error": str(e)})
    return ""

@app.middleware("http")
async def gateway_logging_and_routing(request: Request, call_next):
    import uuid
    req_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    request_id_var.set(req_id)
    trace_id_var.set(trace_id)
    
    # This middleware handles the access logging and dynamic proxying
    # if the path starts with /api/
    
    start_time = time.time()
    
    if request.url.path.startswith("/api/simulation"):
        return await call_next(request)
        
    if request.url.path.startswith("/api/"):
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 2:
            service_key = path_parts[1]
            if service_key in SERVICES:
                # Proxy the request
                base_url = SERVICES[service_key]
                # rebuild the path without /api/
                target_path = "/" + "/".join(path_parts[1:])
                target_url = f"{base_url}{target_path}"
                if request.url.query:
                    target_url += f"?{request.url.query}"
                
                headers = dict(request.headers)
                headers.pop("host", None)
                headers["X-Request-Id"] = request_id_var.get()
                headers["X-Trace-Id"] = trace_id_var.get()
                
                if os.getenv("ENVIRONMENT") == "cloud":
                    token = await get_identity_token(base_url)
                    if token:
                        headers["Authorization"] = f"Bearer {token}"
                
                body = await request.body()
                
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        proxy_req = client.build_request(
                            method=request.method,
                            url=target_url,
                            headers=headers,
                            content=body
                        )
                        proxy_resp = await client.send(proxy_req)
                        
                        latency_ms = int((time.time() - start_time) * 1000)
                        
                        logger.info(
                            "Request completed",
                            extra={
                                "event": "request_completed",
                                "endpoint": request.url.path,
                                "method": request.method,
                                "status_code": proxy_resp.status_code,
                                "latency_ms": latency_ms,
                                "upstream": target_url
                            }
                        )
                        
                        return Response(
                            content=proxy_resp.content,
                            status_code=proxy_resp.status_code,
                            headers=dict(proxy_resp.headers)
                        )
                except Exception as e:
                    logger.error("Gateway proxy error", extra={"event": "gateway_error", "error": str(e)})
                    return JSONResponse(status_code=502, content={"error": "Bad Gateway"})

    # For all other requests (like static files or simulation endpoint)
    response = await call_next(request)
    latency_ms = int((time.time() - start_time) * 1000)
    
    if not request.url.path.startswith("/frontend"):
        logger.info(
            "Request completed",
            extra={
                "event": "request_completed",
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "latency_ms": latency_ms
            }
        )
    return response

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/simulation")
async def update_simulation_config(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    for key, value in data.items():
        config = db.query(SimulationConfig).filter(SimulationConfig.key == key).first()
        if config:
            config.value = str(value)
        else:
            config = SimulationConfig(key=key, value=str(value))
            db.add(config)
    db.commit()
    return {"status": "updated"}

@app.get("/api/simulation")
async def get_simulation_config(db: Session = Depends(get_db)):
    configs = db.query(SimulationConfig).all()
    return {c.key: c.value for c in configs}

# Serve frontend
# app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
# The mount path needs to be correct relative to where gateway runs.
# It will run from /app/gateway in docker.
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), '..', 'frontend'), html=True), name="frontend")

