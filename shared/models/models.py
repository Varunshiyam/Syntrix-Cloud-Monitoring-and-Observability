from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class SimulationConfig(Base):
    __tablename__ = 'simulation_config'
    key = Column(String, primary_key=True)
    value = Column(String)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String)
    price = Column(Float)
    stock = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)

class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    total_amount = Column(Float)
    payment_status = Column(String)  # PENDING, SUCCESS, FAILED
    order_status = Column(String)    # CREATED, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    amount = Column(Float)
    status = Column(String) # SUCCESS, DECLINED, TIMEOUT, RETRY
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryTransaction(Base):
    __tablename__ = 'inventory_transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    transaction_type = Column(String) # RESERVE, RELEASE, RESTOCK
    created_at = Column(DateTime, default=datetime.utcnow)
