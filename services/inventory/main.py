import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from shared.logging.logger import get_logger
from shared.middleware.tracing import TracingMiddleware
from shared.utils.database import get_db
from shared.models.models import Product, InventoryTransaction, SimulationConfig
from google.cloud import pubsub_v1
import json
from shared.logging.logger import get_logger, request_id_var, trace_id_var

logger = get_logger("inventory-service")
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = "project-4e3f1563-833a-4721-bf7"
INVENTORY_TOPIC_PATH = publisher.topic_path(PROJECT_ID, "inventory-events")
app = FastAPI(title="Inventory Service")
app.add_middleware(TracingMiddleware)

class ReserveItem(BaseModel):
    product_id: int
    quantity: int

class ReserveRequest(BaseModel):
    items: List[ReserveItem]

@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    logger.info("Inventory checked", extra={"event": "inventory_checked"})
    return [{"product_id": p.id, "stock": p.stock} for p in products]

@app.post("/inventory/reserve")
def reserve_inventory(req: ReserveRequest, db: Session = Depends(get_db)):
    config = db.query(SimulationConfig).filter(SimulationConfig.key == "inventory_mode").first()
    mode = config.value if config else "healthy"
    
    # Process reserve
    for item in req.items:
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
        stock_before = product.stock
        
        # apply simulation
        if mode == "out_of_stock":
            logger.warning("Inventory insufficient (simulated)", extra={"event": "inventory_insufficient", "product_id": item.product_id})
            raise HTTPException(status_code=400, detail="Insufficient stock (simulated)")
        elif mode == "low_stock" and product.stock > 5:
            # act as if stock is 2
            product.stock = 2
            
        if product.stock < item.quantity:
            logger.warning("Inventory insufficient", extra={"event": "inventory_insufficient", "product_id": item.product_id})
            db.rollback()
            try:
                publisher.publish(INVENTORY_TOPIC_PATH, data=json.dumps({"event_type": "inventory.insufficient", "product_id": item.product_id}).encode("utf-8"))
            except: pass
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")
            
        product.stock -= item.quantity
        
        txn = InventoryTransaction(product_id=item.product_id, quantity=-item.quantity, transaction_type="RESERVE")
        db.add(txn)
        
        logger.info("Inventory reserved", extra={
            "event": "inventory_reserved", 
            "product_id": item.product_id, 
            "stock_before": stock_before, 
            "stock_after": product.stock,
            "quantity": item.quantity
        })
        
    db.commit()
    
    try:
        publisher.publish(INVENTORY_TOPIC_PATH, data=json.dumps({"event_type": "inventory.reserved", "items": [{"product_id": i.product_id, "qty": i.quantity} for i in req.items]}).encode("utf-8"))
    except: pass
    
    return {"status": "success"}

@app.post("/inventory/release")
def release_inventory(req: ReserveRequest, db: Session = Depends(get_db)):
    for item in req.items:
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        if product:
            stock_before = product.stock
            product.stock += item.quantity
            txn = InventoryTransaction(product_id=item.product_id, quantity=item.quantity, transaction_type="RELEASE")
            db.add(txn)
            logger.info("Inventory released", extra={
                "event": "inventory_updated", 
                "product_id": item.product_id, 
                "stock_before": stock_before, 
                "stock_after": product.stock
            })
    db.commit()
    return {"status": "success"}
