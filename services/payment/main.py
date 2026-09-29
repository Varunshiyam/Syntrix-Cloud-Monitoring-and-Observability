import os
import sys
import time
import random
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.logging.logger import get_logger
from shared.middleware.tracing import TracingMiddleware
from shared.utils.database import get_db
from shared.models.models import Payment, SimulationConfig
from google.cloud import pubsub_v1
import json
from shared.logging.logger import get_logger, request_id_var, trace_id_var

logger = get_logger("payment-service")
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = "project-4e3f1563-833a-4721-bf7"
PAYMENT_TOPIC_PATH = publisher.topic_path(PROJECT_ID, "payment-events")
app = FastAPI(title="Payment Service")
app.add_middleware(TracingMiddleware)

class PaymentRequest(BaseModel):
    order_id: int
    amount: float

@app.post("/payments")
async def process_payment(req: PaymentRequest, db: Session = Depends(get_db)):
    logger.info("Payment started", extra={"event": "payment_started", "order_id": req.order_id, "amount": req.amount})
    
    config = db.query(SimulationConfig).filter(SimulationConfig.key == "payment_mode").first()
    mode = config.value if config else "normal"
    
    # Process simulation modes
    if mode == "20_timeout":
        if random.random() < 0.2:
            logger.error("Payment timeout", extra={"event": "payment_timeout", "order_id": req.order_id})
            await asyncio.sleep(2)
            raise HTTPException(status_code=504, detail="Payment Gateway Timeout")
    elif mode == "50_timeout":
        if random.random() < 0.5:
            logger.error("Payment timeout", extra={"event": "payment_timeout", "order_id": req.order_id})
            await asyncio.sleep(2)
            raise HTTPException(status_code=504, detail="Payment Gateway Timeout")
    elif mode == "declined":
        if random.random() < 0.3:
            payment = Payment(order_id=req.order_id, amount=req.amount, status="DECLINED")
            db.add(payment)
            db.commit()
            logger.warning("Payment declined", extra={"event": "payment_declined", "order_id": req.order_id, "amount": req.amount})
            
            try:
                event_data = {"event_type": "payment.failed", "order_id": req.order_id, "amount": req.amount, "reason": "declined"}
                publisher.publish(PAYMENT_TOPIC_PATH, data=json.dumps(event_data).encode("utf-8"))
            except: pass
            
            raise HTTPException(status_code=402, detail="Payment Declined")

    # Success path
    payment = Payment(order_id=req.order_id, amount=req.amount, status="SUCCESS")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    try:
        event_data = {"event_type": "payment.completed", "order_id": req.order_id, "amount": req.amount}
        publisher.publish(PAYMENT_TOPIC_PATH, data=json.dumps(event_data).encode("utf-8"))
    except: pass
    
    logger.info("Payment processed", extra={"event": "payment_processed", "payment_id": payment.id, "order_id": req.order_id, "amount": req.amount, "payment_status": "SUCCESS"})
    return {"payment_id": payment.id, "status": "SUCCESS"}

@app.get("/payments/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
