const API_BASE = '/api';
let currentCartId = null;

// Routing
function navigate(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
    
    // Update nav active state
    document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
    const activeLink = document.querySelector(`.nav-links a[href="#${viewId}"]`);
    if (activeLink) activeLink.classList.add('active');

    // Load data based on view
    if (viewId === 'catalog') loadCatalog();
    if (viewId === 'cart') loadCart();
    if (viewId === 'orders') loadOrders();
    if (viewId === 'dashboard') loadDashboard();
}

window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    navigate(hash);
});

// Initialization
async function init() {
    // Try to get or create cart
    currentCartId = localStorage.getItem('cart_id');
    if (!currentCartId) {
        try {
            const res = await fetch(`${API_BASE}/cart`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                currentCartId = data.cart_id;
                localStorage.setItem('cart_id', currentCartId);
            }
        } catch (e) { console.error('Failed to init cart', e); }
    }
    
    // Trigger initial route
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    navigate(hash);
}

// Data Loaders
async function loadCatalog(query = '') {
    const url = query ? `${API_BASE}/search?q=${encodeURIComponent(query)}&_t=${Date.now()}` : `${API_BASE}/products?_t=${Date.now()}`;
    try {
        const res = await fetch(url);
        const products = await res.json();
        const grid = document.getElementById('product-grid');
        grid.innerHTML = '';
        products.forEach(p => {
            grid.innerHTML += `
                <div class="glass-card product-card">
                    <div>
                        <span class="category">${p.category}</span>
                        <h3>${p.name}</h3>
                        <p class="price">$${p.price.toFixed(2)}</p>
                        <p style="color: ${p.stock < 10 ? 'var(--warning-color)' : 'var(--text-secondary)'}">Stock: ${p.stock}</p>
                    </div>
                    <button class="btn" onclick="addToCart(${p.id})">Add to Cart</button>
                </div>
            `;
        });
    } catch (e) { console.error(e); }
}

async function addToCart(productId) {
    if (!currentCartId) return;
    try {
        await fetch(`${API_BASE}/cart/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cart_id: parseInt(currentCartId), product_id: productId, quantity: 1 })
        });
        // update cart count visually (mock)
        const countSpan = document.getElementById('cart-count');
        countSpan.innerText = parseInt(countSpan.innerText) + 1;
        alert('Added to cart!');
    } catch (e) { console.error(e); }
}

async function loadCart() {
    if (!currentCartId) return;
    try {
        const res = await fetch(`${API_BASE}/cart/${currentCartId}?_t=${Date.now()}`);
        if (!res.ok) {
            document.getElementById('cart-content').innerHTML = '<p>Cart is empty</p>';
            return;
        }
        const cart = await res.json();
        const content = document.getElementById('cart-content');
        if (cart.items.length === 0) {
            content.innerHTML = '<p>Cart is empty</p>';
            document.getElementById('cart-total').innerText = 'Total: $0.00';
            return;
        }
        
        let html = '';
        cart.items.forEach(item => {
            html += `
                <div class="cart-item">
                    <div>
                        <h4>${item.name}</h4>
                        <p>$${item.price.toFixed(2)} x ${item.quantity}</p>
                    </div>
                    <button class="btn error" onclick="removeFromCart(${item.item_id})">Remove</button>
                </div>
            `;
        });
        content.innerHTML = html;
        document.getElementById('cart-total').innerText = `Total: $${cart.total.toFixed(2)}`;
        
        // update count
        document.getElementById('cart-count').innerText = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    } catch (e) { console.error(e); }
}

async function removeFromCart(itemId) {
    try {
        await fetch(`${API_BASE}/cart/items/${itemId}`, { method: 'DELETE' });
        loadCart();
    } catch (e) { console.error(e); }
}

async function checkout() {
    document.getElementById('checkout-status').innerText = 'Processing...';
    try {
        const res = await fetch(`${API_BASE}/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cart_id: parseInt(currentCartId), customer_id: 1 })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('checkout-status').innerHTML = `<span style="color: var(--secondary-color)">Success! Order #${data.order_id} created.</span>`;
            localStorage.removeItem('cart_id');
            currentCartId = null;
            document.getElementById('cart-count').innerText = '0';
            setTimeout(() => { window.location.hash = '#orders'; init(); }, 2000);
        } else {
            document.getElementById('checkout-status').innerHTML = `<span style="color: var(--error-color)">Error: ${data.detail}</span>`;
        }
    } catch (e) {
        document.getElementById('checkout-status').innerHTML = `<span style="color: var(--error-color)">Network Error</span>`;
    }
}

async function loadOrders() {
    try {
        const res = await fetch(`${API_BASE}/orders?_t=${Date.now()}`);
        const orders = await res.json();
        const list = document.getElementById('orders-list');
        if (orders.length === 0) {
            list.innerHTML = '<p>No orders found.</p>';
            return;
        }
        let html = '<table><tr><th>Order ID</th><th>Amount</th><th>Status</th><th>Payment</th><th>Date</th></tr>';
        orders.sort((a,b) => b.id - a.id).forEach(o => {
            html += `<tr>
                <td>#${o.id}</td>
                <td>$${o.total_amount.toFixed(2)}</td>
                <td><span style="color: ${o.order_status === 'COMPLETED' ? 'var(--secondary-color)' : (o.order_status === 'FAILED' ? 'var(--error-color)' : 'white')}">${o.order_status}</span></td>
                <td>${o.payment_status}</td>
                <td>${new Date(o.created_at).toLocaleString()}</td>
            </tr>`;
        });
        html += '</table>';
        list.innerHTML = html;
    } catch (e) { console.error(e); }
}

async function loadDashboard() {
    try {
        const oRes = await fetch(`${API_BASE}/orders?_t=${Date.now()}`);
        const pRes = await fetch(`${API_BASE}/products?_t=${Date.now()}`);
        if(oRes.ok && pRes.ok) {
            const orders = await oRes.json();
            const products = await pRes.json();
            
            document.getElementById('dash-products').innerText = products.length;
            document.getElementById('dash-orders').innerText = orders.length;
            
            const revenue = orders.filter(o => o.order_status === 'COMPLETED').reduce((sum, o) => sum + o.total_amount, 0);
            document.getElementById('dash-revenue').innerText = `$${revenue.toFixed(2)}`;
            
            let recentHtml = '<ul>';
            orders.sort((a,b) => b.id - a.id).slice(0, 5).forEach(o => {
                recentHtml += `<li>Order #${o.id} - $${o.total_amount.toFixed(2)} - ${o.order_status}</li>`;
            });
            recentHtml += '</ul>';
            document.getElementById('dash-recent-orders').innerHTML = recentHtml;
        }
    } catch (e) {}
}

// Listeners
document.getElementById('search-btn').addEventListener('click', () => {
    loadCatalog(document.getElementById('search-input').value);
});
document.getElementById('checkout-btn').addEventListener('click', () => {
    navigate('checkout');
});
document.getElementById('confirm-order-btn').addEventListener('click', checkout);

window.onload = init;
