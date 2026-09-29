import logging
import json
import datetime
import os
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

# Context variables for tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            created_time = datetime.datetime.utcfromtimestamp(record.created)
            log_record['timestamp'] = created_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if log_record.get('level'):
            log_record['severity'] = log_record['level'].upper()
            del log_record['level']
        else:
            log_record['severity'] = record.levelname
            
        log_record['service'] = os.getenv("SERVICE_NAME", "unknown-service")
        log_record['environment'] = os.getenv("ENVIRONMENT", "local")
        
        # Inject correlation IDs from context
        req_id = request_id_var.get()
        if req_id:
            log_record['request_id'] = req_id
        
        trace_id = trace_id_var.get()
        if trace_id:
            log_record['trace_id'] = trace_id
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "project-4e3f1563-833a-4721-bf7")
            # Google Cloud Logging structured payload format
            log_record['logging.googleapis.com/trace'] = f"projects/{project_id}/traces/{trace_id}"
            log_record['logging.googleapis.com/spanId'] = trace_id[:16] # Simplified span ID

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        logHandler = logging.StreamHandler()
        formatter = CustomJsonFormatter('%(timestamp)s %(severity)s %(message)s')
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
        logger.propagate = False
    return logger
