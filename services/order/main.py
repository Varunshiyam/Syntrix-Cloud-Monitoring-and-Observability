import os
import sys
import httpx

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.logging.logger import get_logger, request_id_var, trace_id_var
from shared.middleware.tracing import TracingMiddleware
from shared.utils.database import get_db
from shared.models.models import Order
from google.cloud import pubsub_v1
import json

logger = get_logger("order-service")
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = "project-4e3f1563-833a-4721-bf7"
ORDER_TOPIC_PATH = publisher.topic_path(PROJECT_ID, "order-events")
app = FastAPI(title="Order Service")
app.add_middleware(TracingMiddleware)

CART_URL = os.getenv("CART_URL", "http://cart:8000")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory:8000")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment:8000")

class CheckoutRequest(BaseModel):
    cart_id: int
    customer_id: int = 1

def get_headers():
    return {
        "X-Request-Id": request_id_var.get(),
        "X-Trace-Id": trace_id_var.get()
    }

@app.post("/checkout")
async def checkout(req: CheckoutRequest, db: Session = Depends(get_db)):
    logger.info("Checkout started", extra={"event": "checkout_started", "cart_id": req.cart_id})
    
    async with httpx.AsyncClient() as client:
        # 1. Validate Cart
        cart_resp = await client.get(f"{CART_URL}/cart/{req.cart_id}", headers=get_headers())
        if cart_resp.status_code != 200:
            logger.error("Order failed: Cart not found", extra={"event": "order_failed", "reason": "cart_not_found"})
            raise HTTPException(status_code=400, detail="Cart not found or empty")
            
        cart_data = cart_resp.json()
        items = cart_data.get("items", [])
        if not items:
            logger.error("Order failed: Cart empty", extra={"event": "order_failed", "reason": "cart_empty"})
            raise HTTPException(status_code=400, detail="Cart is empty")
            
        total_amount = cart_data.get("total", 0.0)
        
        # 2. Reserve Inventory
        reserve_payload = {
            "items": [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in items]
        }
        inv_resp = await client.post(f"{INVENTORY_URL}/inventory/reserve", json=reserve_payload, headers=get_headers())
        if inv_resp.status_code != 200:
            logger.error("Order failed: Inventory reservation failed", extra={"event": "order_failed", "reason": "inventory_insufficient"})
            raise HTTPException(status_code=400, detail="Inventory reservation failed")
            
        # Create Order in DB (Pending)
        order = Order(customer_id=req.customer_id, total_amount=total_amount, payment_status="PENDING", order_status="CREATED")
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Publish to Pub/Sub
        try:
            event_data = {
                "event_type": "order.created",
                "order_id": order.id,
                "customer_id": order.customer_id,
                "total_amount": order.total_amount,
                "items": items,
                "trace_id": trace_id_var.get()
            }
            publisher.publish(ORDER_TOPIC_PATH, data=json.dumps(event_data).encode("utf-8"))
            logger.info("Published order.created event")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            
        logger.info("Order created", extra={"event": "order_created", "order_id": order.id, "total_amount": total_amount})
        
        # 3. Process Payment
        pay_payload = {"order_id": order.id, "amount": total_amount}
        pay_resp = await client.post(f"{PAYMENT_URL}/payments", json=pay_payload, headers=get_headers())
        
        if pay_resp.status_code != 200:
            order.payment_status = "FAILED"
            order.order_status = "FAILED"
            db.commit()
            
            # Release inventory
            await client.post(f"{INVENTORY_URL}/inventory/release", json=reserve_payload, headers=get_headers())
            
            logger.error("Order failed: Payment processing failed", extra={"event": "order_failed", "order_id": order.id, "reason": "payment_failed"})
            raise HTTPException(status_code=400, detail="Payment failed")
            
        # 4. Confirmation
        order.payment_status = "SUCCESS"
        order.order_status = "COMPLETED"
        db.commit()
        
        logger.info("Order completed", extra={"event": "order_completed", "order_id": order.id, "total_amount": total_amount})
        
        # Clear cart
        for item in items:
            await client.delete(f"{CART_URL}/cart/items/{item['item_id']}", headers=get_headers())
            
        return {"order_id": order.id, "status": "COMPLETED", "total": total_amount}

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders

@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
