#!/bin/bash

GATEWAY_URL="https://syntrix-gateway-541833001986.asia-south1.run.app"

echo "Simulating traffic to generate logs..."

for i in {1..20}; do
  echo "Request $i..."
  
  # Catalog
  curl -s "$GATEWAY_URL/api/products" > /dev/null
  curl -s "$GATEWAY_URL/api/products/1" > /dev/null
  curl -s "$GATEWAY_URL/api/categories" > /dev/null
  
  # Cart
  curl -s "$GATEWAY_URL/api/cart/1" > /dev/null
  curl -s -X POST "$GATEWAY_URL/api/cart/1/items" -H "Content-Type: application/json" -d '{"product_id": 1, "quantity": 1}' > /dev/null
  
  # Inventory
  curl -s "$GATEWAY_URL/api/inventory/health" > /dev/null
  
  # Order
  curl -s -X POST "$GATEWAY_URL/api/checkout" -H "Content-Type: application/json" -d '{"cart_id": 1, "customer_id": 1}' > /dev/null
  
  # Random delay
  sleep $((RANDOM % 3))
done

echo "Traffic simulation complete."
curl -s "$GATEWAY_URL/api/inventory/1" > /dev/null
curl -s -X POST "$GATEWAY_URL/api/payment" -H "Content-Type: application/json" -d "{\"order_id\": 1, \"amount\": 10.0}" > /dev/null
