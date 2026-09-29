import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from shared.logging.logger import get_logger
from shared.middleware.tracing import TracingMiddleware
from shared.utils.database import get_db
from shared.models.models import Cart, CartItem, Product, SimulationConfig

logger = get_logger("cart-service")
app = FastAPI(title="Cart Service")
app.add_middleware(TracingMiddleware)

def check_db_delay(db: Session):
    config = db.query(SimulationConfig).filter(SimulationConfig.key == "db_mode").first()
    if config and config.value == "slow_queries":
        time.sleep(1.5)
        logger.warning("Simulated slow query delay", extra={"event": "slow_query"})

@app.get("/health")
def health_check():
    return {"status": "ok"}

class AddItemRequest(BaseModel):
    cart_id: int
    product_id: int
    quantity: int

class UpdateItemRequest(BaseModel):
    quantity: int

@app.post("/cart")
def create_cart(db: Session = Depends(get_db)):
    check_db_delay(db)
    # create anonymous cart
    cart = Cart(customer_id=1) # Assume customer 1 exists from seed
    db.add(cart)
    db.commit()
    db.refresh(cart)
    logger.info("Cart created", extra={"event": "cart_created", "cart_id": cart.id})
    return {"cart_id": cart.id}

@app.get("/cart/{cart_id}")
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    check_db_delay(db)
    cart = db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.product)).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = []
    total = 0.0
    for item in cart.items:
        items.append({
            "item_id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity
        })
        total += item.product.price * item.quantity
        
    return {"cart_id": cart.id, "items": items, "total": total}

@app.post("/cart/items")
def add_item(req: AddItemRequest, db: Session = Depends(get_db)):
    check_db_delay(db)
    cart = db.query(Cart).filter(Cart.id == req.cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = db.query(CartItem).filter(CartItem.cart_id == req.cart_id, CartItem.product_id == req.product_id).first()
    if item:
        item.quantity += req.quantity
    else:
        item = CartItem(cart_id=req.cart_id, product_id=req.product_id, quantity=req.quantity)
        db.add(item)
    
    db.commit()
    logger.info("Item added to cart", extra={"event": "item_added", "cart_id": req.cart_id, "product_id": req.product_id, "quantity": req.quantity})
    return {"status": "success"}

@app.put("/cart/items/{item_id}")
def update_item(item_id: int, req: UpdateItemRequest, db: Session = Depends(get_db)):
    check_db_delay(db)
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.quantity = req.quantity
    db.commit()
    logger.info("Cart updated", extra={"event": "cart_updated", "cart_id": item.cart_id, "product_id": item.product_id, "quantity": req.quantity})
    return {"status": "success"}

@app.delete("/cart/items/{item_id}")
def remove_item(item_id: int, db: Session = Depends(get_db)):
    check_db_delay(db)
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    cart_id = item.cart_id
    product_id = item.product_id
    
    db.delete(item)
    db.commit()
    logger.info("Item removed from cart", extra={"event": "item_removed", "cart_id": cart_id, "product_id": product_id})
    return {"status": "success"}
