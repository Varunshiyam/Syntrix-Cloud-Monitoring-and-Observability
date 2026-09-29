import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from shared.logging.logger import get_logger, request_id_var, trace_id_var
from shared.middleware.tracing import TracingMiddleware
from shared.utils.database import get_db
from shared.models.models import Product, SimulationConfig

logger = get_logger("catalog-service")
app = FastAPI(title="Catalog Service")
app.add_middleware(TracingMiddleware)

def check_db_delay(db: Session):
    config = db.query(SimulationConfig).filter(SimulationConfig.key == "db_mode").first()
    if config and config.value == "slow_queries":
        time.sleep(1.5)
        logger.warning("Simulated slow query delay", extra={"event": "slow_query"})

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    check_db_delay(db)
    products = db.query(Product).all()
    logger.info("Catalog loaded", extra={"event": "catalog_loaded", "count": len(products)})
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    check_db_delay(db)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.info("Product not found", extra={"event": "product_not_found", "product_id": product_id})
        raise HTTPException(status_code=404, detail="Product not found")
    
    logger.info("Product viewed", extra={"event": "product_viewed", "product_id": product_id, "category": product.category})
    return product

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    check_db_delay(db)
    categories = db.query(Product.category).distinct().all()
    categories_list = [c[0] for c in categories]
    return categories_list

@app.get("/search")
def search_products(q: str = Query(...), db: Session = Depends(get_db)):
    check_db_delay(db)
    products = db.query(Product).filter(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.category.ilike(f"%{q}%")
        )
    ).all()
    logger.info("Search performed", extra={"event": "search_performed", "query": q, "results_count": len(products)})
    return products
