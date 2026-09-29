import os

filepath = '/Users/varunshiyam/Desktop/CTS_HACKATHON/SYNTRIX/gateway/main.py'
with open(filepath, 'r') as f:
    content = f.read()

# Insert ContextVar setting at the start of gateway_logging_and_routing
new_content = content.replace(
    'async def gateway_logging_and_routing(request: Request, call_next):\n    # This middleware',
    '''async def gateway_logging_and_routing(request: Request, call_next):
    import uuid
    req_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    request_id_var.set(req_id)
    trace_id_var.set(trace_id)
    
    # This middleware'''
)

with open(filepath, 'w') as f:
    f.write(new_content)
