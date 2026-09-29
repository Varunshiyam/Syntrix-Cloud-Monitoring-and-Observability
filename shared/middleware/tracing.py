import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from shared.logging.logger import request_id_var, trace_id_var, get_logger

logger = get_logger(__name__)

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        req_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        
        request_id_var.set(req_id)
        trace_id_var.set(trace_id)
        
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        latency_ms = int(process_time * 1000)
        
        response.headers["X-Request-Id"] = req_id
        response.headers["X-Trace-Id"] = trace_id
        
        # Log every request to ensure all environments (GKE, GCE, Cloud Run) produce latency logs
        if not request.url.path.startswith("/health") and not request.url.path.startswith("/frontend"):
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
