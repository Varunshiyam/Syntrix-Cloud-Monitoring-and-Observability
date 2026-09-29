import requests
BASE = "https://syntrix-gateway-541833001986.asia-south1.run.app"
res = requests.post(f"{BASE}/api/cart")
cart_id = res.json()["cart_id"]
res = requests.post(f"{BASE}/api/cart/items", json={"cart_id": cart_id, "product_id": 1, "quantity": 1})
res = requests.post(f"{BASE}/api/checkout", json={"cart_id": cart_id, "customer_id": 1})
print("Checkout:", res.status_code, res.text)
