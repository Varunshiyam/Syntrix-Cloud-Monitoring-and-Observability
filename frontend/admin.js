// Admin Panel Toggle
document.getElementById('dev-panel-toggle').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('dev-panel').classList.toggle('hidden');
    fetchSimulationConfig();
});

document.getElementById('close-dev-panel').addEventListener('click', () => {
    document.getElementById('dev-panel').classList.add('hidden');
});

// Simulation API
async function fetchSimulationConfig() {
    try {
        const res = await fetch(`${API_BASE}/simulation`);
        const data = await res.json();
        if (data.payment_mode) document.getElementById('sim-payment').value = data.payment_mode;
        if (data.inventory_mode) document.getElementById('sim-inventory').value = data.inventory_mode;
        if (data.db_mode) document.getElementById('sim-db').value = data.db_mode;
    } catch (e) { console.error(e); }
}

document.getElementById('apply-sim-btn').addEventListener('click', async () => {
    const payload = {
        payment_mode: document.getElementById('sim-payment').value,
        inventory_mode: document.getElementById('sim-inventory').value,
        db_mode: document.getElementById('sim-db').value
    };
    try {
        await fetch(`${API_BASE}/simulation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        document.getElementById('sim-status').innerText = 'Settings applied!';
        setTimeout(() => document.getElementById('sim-status').innerText = '', 2000);
    } catch (e) {
        document.getElementById('sim-status').innerText = 'Failed to apply settings.';
    }
});

// Traffic Simulator
let trafficInterval = null;

async function simulateTrafficUser() {
    try {
        // 1. Browse catalog
        const catRes = await fetch(`${API_BASE}/products`);
        const products = await catRes.json();
        
        // 2. Select random product
        const p = products[Math.floor(Math.random() * products.length)];
        await fetch(`${API_BASE}/products/${p.id}`); // view product
        
        // 3. Create Cart
        const cartRes = await fetch(`${API_BASE}/cart`, { method: 'POST' });
        const cartData = await cartRes.json();
        
        // 4. Add to Cart
        await fetch(`${API_BASE}/cart/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cart_id: cartData.cart_id, product_id: p.id, quantity: Math.floor(Math.random() * 3) + 1 })
        });
        
        // 5. Checkout (70% probability to attempt checkout)
        if (Math.random() < 0.7) {
            await fetch(`${API_BASE}/checkout`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cart_id: cartData.cart_id, customer_id: 1 })
            });
        }
    } catch (e) {
        // Silently fail for traffic simulator
    }
}

document.getElementById('start-traffic-btn').addEventListener('click', () => {
    const users = parseInt(document.getElementById('sim-traffic-users').value);
    
    document.getElementById('start-traffic-btn').classList.add('hidden');
    document.getElementById('stop-traffic-btn').classList.remove('hidden');
    document.getElementById('traffic-status').innerText = `Running ${users} users...`;
    
    // Calculate interval to generate roughly X users per second
    const delay = 1000 / users;
    
    trafficInterval = setInterval(() => {
        simulateTrafficUser();
    }, delay);
});

document.getElementById('stop-traffic-btn').addEventListener('click', () => {
    clearInterval(trafficInterval);
    document.getElementById('start-traffic-btn').classList.remove('hidden');
    document.getElementById('stop-traffic-btn').classList.add('hidden');
    document.getElementById('traffic-status').innerText = 'Idle';
});
