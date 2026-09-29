import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.models.models import Base, Product, SimulationConfig
from shared.utils.database import engine, SessionLocal
from shared.logging.logger import get_logger

logger = get_logger("seed-script")

products_data = [
    {"sku": f"SKU-{i:03d}", "name": f"Cloud Product {i}", "category": "Compute" if i % 3 == 0 else "Storage" if i % 3 == 1 else "Networking", "price": round(10.0 + i * 2.5, 2), "stock": 100, "rating": 4.5}
    for i in range(1, 51)
]

def seed_db():
    logger.info("Starting database seed...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        from shared.models.models import Customer
        if db.query(Customer).count() == 0:
            logger.info("Inserting dummy customer...")
            db.add(Customer(name="John Doe", email="john@example.com"))
            db.commit()

        # Check if already seeded
        if db.query(Product).count() == 0:
            logger.info("Inserting products...")
            for p in products_data:
                db.add(Product(**p))
            db.commit()
            
        # Init simulation config
        if db.query(SimulationConfig).count() == 0:
            logger.info("Inserting default simulation configs...")
            configs = [
                SimulationConfig(key="payment_mode", value="normal"),
                SimulationConfig(key="inventory_mode", value="healthy"),
                SimulationConfig(key="db_mode", value="normal")
            ]
            for c in configs:
                db.add(c)
            db.commit()
            
        logger.info("Database seed complete.")
    except Exception as e:
        logger.error(f"Error during seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
