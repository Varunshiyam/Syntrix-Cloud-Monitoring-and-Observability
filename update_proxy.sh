sed -i '/if target_url.startswith('\''https:\/\/'\''):/,/new_headers\['\''Authorization'\''\] = f'\''Bearer {TOKEN}'\''/d' /tmp/proxy.py
sudo pkill -f /tmp/proxy.py
sudo nohup python3 /tmp/proxy.py > /tmp/proxy.log 2>&1 &
