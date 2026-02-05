"""
GROCERY INVENTORY MANAGEMENT SYSTEM
Single-file version - Everything in one file!
Just run: python grocery_app_complete.py
"""

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
DATABASE = 'grocery.db'

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grocery Inventory Management</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #111827;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        .header {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
            margin: 0 0 5px 0;
        }
        
        .header p { color: #6b7280; margin: 0; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover { transform: translateY(-5px); }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 5px;
        }
        
        .stat-label { color: #6b7280; font-size: 0.9rem; }
        .stat-card.primary { border-left: 4px solid #4f46e5; }
        .stat-card.success { border-left: 4px solid #10b981; }
        .stat-card.warning { border-left: 4px solid #f59e0b; }
        .stat-card.danger { border-left: 4px solid #ef4444; }
        
        .card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .card-header {
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
            color: white;
            padding: 20px 30px;
            font-size: 1.25rem;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .card-body { padding: 30px; }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .form-group { display: flex; flex-direction: column; }
        
        .form-label {
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        
        .form-control, .form-select {
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .form-control:focus, .form-select:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
        }
        
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-primary { background: #4f46e5; color: white; }
        .btn-primary:hover:not(:disabled) {
            background: #4338ca;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .btn-success { background: #10b981; color: white; }
        .btn-warning { background: #f59e0b; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn-sm { padding: 8px 16px; font-size: 0.875rem; }
        .btn-group { display: flex; gap: 10px; flex-wrap: wrap; }
        
        .table-container {
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }
        
        table { width: 100%; border-collapse: collapse; background: white; }
        thead { background: #f9fafb; }
        thead th {
            padding: 16px;
            text-align: left;
            font-weight: 600;
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            white-space: nowrap;
        }
        tbody td {
            padding: 16px;
            border-bottom: 1px solid #e5e7eb;
            color: #111827;
        }
        tbody tr { transition: background-color 0.2s ease; }
        tbody tr:hover { background: #f9fafb; }
        tbody tr:last-child td { border-bottom: none; }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-success { background: rgba(16, 185, 129, 0.1); color: #10b981; }
        .badge-warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
        .badge-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
        .badge-primary { background: rgba(79, 70, 229, 0.1); color: #4f46e5; }
        .badge-secondary { background: rgba(107, 114, 128, 0.1); color: #6b7280; }
        
        .alert {
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: start;
            gap: 12px;
        }
        .alert-success { background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; color: #10b981; }
        .alert-warning { background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; color: #f59e0b; }
        .alert-danger { background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; color: #ef4444; }
        
        .spinner {
            border: 3px solid #e5e7eb;
            border-top: 3px solid #4f46e5;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }
        .empty-state-icon { font-size: 4rem; margin-bottom: 20px; opacity: 0.5; }
        
        .d-none { display: none !important; }
        .text-center { text-align: center; }
        .mt-3 { margin-top: 1rem; }
        
        #alertsContainer {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        }
        
        .filters { display: flex; gap: 10px; align-items: center; }
        
        @media (max-width: 768px) {
            .header-content { flex-direction: column; align-items: flex-start; }
            .form-grid, .stats-grid { grid-template-columns: 1fr; }
            .btn-group { flex-direction: column; }
            .table-container { font-size: 0.85rem; }
            thead th, tbody td { padding: 10px; }
        }
    </style>
</head>
<body>
    <div id="alertsContainer"></div>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div>
                    <h1>🛒 Grocery Inventory Management</h1>
                    <p>Track, manage, and monitor your grocery inventory</p>
                </div>
                <button class="btn btn-warning" onclick="checkExpiry()">🔔 Check Alerts</button>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="stat-value" id="totalProducts">0</div>
                <div class="stat-label">📦 Total Products</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value" id="totalValue">₹0.00</div>
                <div class="stat-label">💰 Inventory Value</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value" id="expiringSoon">0</div>
                <div class="stat-label">⚠️ Expiring Soon</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-value" id="lowStock">0</div>
                <div class="stat-label">📉 Low Stock Items</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header" id="productFormHeader">➕ Add New Product</div>
            <div class="card-body">
                <form id="productForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Product Name *</label>
                            <input type="text" id="productName" class="form-control" placeholder="Enter product name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Category</label>
                            <select id="productCategory" class="form-select">
                                <option value="Uncategorized">Uncategorized</option>
                                <option value="Dairy">Dairy</option>
                                <option value="Produce">Produce</option>
                                <option value="Bakery">Bakery</option>
                                <option value="Meat">Meat</option>
                                <option value="Beverages">Beverages</option>
                                <option value="Snacks">Snacks</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Manufacturing Date *</label>
                            <input type="date" id="manufacturingDate" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Expiry Date *</label>
                            <input type="date" id="expiryDate" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Quantity *</label>
                            <input type="number" id="quantity" class="form-control" placeholder="0" min="0" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Price (₹)</label>
                            <input type="number" id="price" class="form-control" placeholder="0.00" step="0.01" min="0">
                        </div>
                    </div>
                    <div class="btn-group mt-3">
                        <button type="submit" class="btn btn-primary" id="submitButton">➕ Add Product</button>
                        <button type="button" class="btn btn-secondary d-none" id="cancelEditButton">❌ Cancel</button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div>📋 Product Inventory</div>
                <div class="filters">
                    <label style="color: white;">Filter:</label>
                    <select id="categoryFilter" class="form-select" style="width: auto; min-width: 180px;">
                        <option value="">All Categories</option>
                        <option value="Dairy">Dairy</option>
                        <option value="Produce">Produce</option>
                        <option value="Bakery">Bakery</option>
                        <option value="Meat">Meat</option>
                        <option value="Beverages">Beverages</option>
                        <option value="Snacks">Snacks</option>
                    </select>
                </div>
            </div>
            <div style="padding: 0;">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Mfg. Date</th>
                                <th>Expiry Date</th>
                                <th>Quantity</th>
                                <th>Price</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="productTable">
                            <tr>
                                <td colspan="7" class="text-center">
                                    <div class="spinner"></div>
                                    <p style="margin-top: 15px; color: #6b7280;">Loading products...</p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let isEditMode = false;
        let currentEditId = null;
        
        document.addEventListener('DOMContentLoaded', () => {
            setDefaultDates();
            attachEventListeners();
            loadProducts();
            loadStatistics();
        });
        
        function setDefaultDates() {
            const today = new Date();
            document.getElementById('manufacturingDate').valueAsDate = today;
            const expiryDate = new Date(today);
            expiryDate.setDate(today.getDate() + 30);
            document.getElementById('expiryDate').valueAsDate = expiryDate;
        }
        
        function attachEventListeners() {
            document.getElementById('productForm').addEventListener('submit', handleFormSubmit);
            document.getElementById('categoryFilter').addEventListener('change', loadProducts);
            document.getElementById('cancelEditButton').addEventListener('click', resetForm);
        }
        
        async function handleFormSubmit(e) {
            e.preventDefault();
            const formData = {
                name: document.getElementById('productName').value.trim(),
                category: document.getElementById('productCategory').value,
                manufacturing_date: document.getElementById('manufacturingDate').value,
                expiry_date: document.getElementById('expiryDate').value,
                quantity: parseInt(document.getElementById('quantity').value),
                price: parseFloat(document.getElementById('price').value) || 0
            };
            
            if (!validateFormData(formData)) return;
            
            try {
                let response;
                if (isEditMode && currentEditId) {
                    response = await fetch(`/edit_product/${currentEditId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                } else {
                    response = await fetch('/add_product', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                }
                
                const data = await response.json();
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                    resetForm();
                    loadProducts();
                    loadStatistics();
                } else {
                    showAlert(data.message, 'danger');
                }
            } catch (error) {
                showAlert('An error occurred. Please try again.', 'danger');
            }
        }
        
        function validateFormData(data) {
            if (!data.name) {
                showAlert('Product name is required', 'warning');
                return false;
            }
            const mfgDate = new Date(data.manufacturing_date);
            const expDate = new Date(data.expiry_date);
            if (expDate <= mfgDate) {
                showAlert('Expiry date must be after manufacturing date', 'warning');
                return false;
            }
            if (data.quantity < 0 || data.price < 0) {
                showAlert('Quantity and price cannot be negative', 'warning');
                return false;
            }
            return true;
        }
        
        async function loadProducts() {
            try {
                const category = document.getElementById('categoryFilter').value;
                const response = await fetch(`/get_products?category=${category}`);
                const products = await response.json();
                renderProductTable(products);
            } catch (error) {
                showAlert('Error loading products', 'danger');
            }
        }
        
        function renderProductTable(products) {
            const tableBody = document.getElementById('productTable');
            if (products.length === 0) {
                tableBody.innerHTML = `
                    <tr><td colspan="7" class="text-center">
                        <div class="empty-state">
                            <div class="empty-state-icon">📦</div>
                            <h3>No products found</h3>
                            <p>Add your first product to get started</p>
                        </div>
                    </td></tr>
                `;
                return;
            }
            
            tableBody.innerHTML = products.map(product => {
                const expiryStatus = getExpiryStatus(product.days_until_expiry);
                const stockStatus = getStockStatus(product.quantity);
                return `
                    <tr>
                        <td><strong>${escapeHtml(product.name)}</strong></td>
                        <td><span class="badge badge-${getCategoryColor(product.category)}">${escapeHtml(product.category)}</span></td>
                        <td>${formatDate(product.manufacturing_date)}</td>
                        <td>${formatDate(product.expiry_date)}<br><small class="badge ${expiryStatus.class}">${expiryStatus.text}</small></td>
                        <td>${product.quantity}${stockStatus ? `<br><small class="badge ${stockStatus.class}">${stockStatus.text}</small>` : ''}</td>
                        <td>₹${product.price.toFixed(2)}</td>
                        <td>
                            <div class="btn-group">
                                <button class="btn btn-primary btn-sm" onclick="editProduct(${product.id})">✏️ Edit</button>
                                <button class="btn btn-danger btn-sm" onclick="deleteProduct(${product.id})">🗑️ Delete</button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        }
        
        function getExpiryStatus(daysUntilExpiry) {
            if (daysUntilExpiry < 0) return { text: `Expired ${Math.abs(daysUntilExpiry)} days ago`, class: 'badge-danger' };
            else if (daysUntilExpiry === 0) return { text: 'Expires today', class: 'badge-danger' };
            else if (daysUntilExpiry <= 7) return { text: `${daysUntilExpiry} days left`, class: 'badge-warning' };
            else return { text: `${daysUntilExpiry} days left`, class: 'badge-success' };
        }
        
        function getStockStatus(quantity) {
            if (quantity === 0) return { text: 'Out of stock', class: 'badge-danger' };
            else if (quantity <= 10) return { text: 'Low stock', class: 'badge-warning' };
            return null;
        }
        
        function getCategoryColor(category) {
            const colors = { 'Dairy': 'primary', 'Produce': 'success', 'Bakery': 'warning', 'Meat': 'danger', 'Beverages': 'primary', 'Snacks': 'warning' };
            return colors[category] || 'secondary';
        }
        
        async function editProduct(productId) {
            try {
                const response = await fetch('/get_products');
                const products = await response.json();
                const product = products.find(p => p.id === productId);
                
                if (product) {
                    document.getElementById('productName').value = product.name;
                    document.getElementById('productCategory').value = product.category;
                    document.getElementById('manufacturingDate').value = product.manufacturing_date;
                    document.getElementById('expiryDate').value = product.expiry_date;
                    document.getElementById('quantity').value = product.quantity;
                    document.getElementById('price').value = product.price;
                    
                    isEditMode = true;
                    currentEditId = productId;
                    
                    document.getElementById('productFormHeader').textContent = '✏️ Edit Product';
                    document.getElementById('submitButton').innerHTML = '✅ Update';
                    document.getElementById('cancelEditButton').classList.remove('d-none');
                    document.getElementById('productForm').scrollIntoView({ behavior: 'smooth' });
                }
            } catch (error) {
                showAlert('Error loading product details', 'danger');
            }
        }
        
        async function deleteProduct(productId) {
            if (!confirm('Are you sure you want to delete this product?')) return;
            try {
                const response = await fetch(`/delete_product/${productId}`, { method: 'DELETE' });
                const data = await response.json();
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                    loadProducts();
                    loadStatistics();
                } else {
                    showAlert(data.message, 'danger');
                }
            } catch (error) {
                showAlert('Error deleting product', 'danger');
            }
        }
        
        function resetForm() {
            document.getElementById('productForm').reset();
            setDefaultDates();
            isEditMode = false;
            currentEditId = null;
            document.getElementById('productFormHeader').textContent = '➕ Add New Product';
            document.getElementById('submitButton').innerHTML = '➕ Add Product';
            document.getElementById('cancelEditButton').classList.add('d-none');
        }
        
        async function checkExpiry() {
            try {
                const response = await fetch('/check_expiry');
                const data = await response.json();
                let messages = [];
                if (data.expired && data.expired.length > 0) {
                    messages.push({ type: 'danger', title: 'Expired Products', items: data.expired.map(p => `${p.name} (expired ${p.days_ago} days ago)`) });
                }
                if (data.expiring_soon && data.expiring_soon.length > 0) {
                    messages.push({ type: 'warning', title: 'Expiring Soon', items: data.expiring_soon.map(p => `${p.name} (${p.days_left} days left)`) });
                }
                if (data.low_stock && data.low_stock.length > 0) {
                    messages.push({ type: 'warning', title: 'Low Stock', items: data.low_stock.map(p => `${p.name} (${p.quantity} remaining)`) });
                }
                
                if (messages.length > 0) {
                    showExpiryAlert(messages);
                    speakAlert(messages);
                } else {
                    showAlert('All products are in good condition!', 'success');
                }
            } catch (error) {
                showAlert('Error checking product status', 'danger');
            }
        }
        
        function showExpiryAlert(messages) {
            const alertHtml = messages.map(msg => `
                <div class="alert alert-${msg.type}">
                    <strong>${msg.title}:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        ${msg.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `).join('');
            
            const modal = `
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 20px;" onclick="this.remove()">
                    <div style="background: white; padding: 30px; border-radius: 16px; max-width: 600px; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);" onclick="event.stopPropagation()">
                        <h2 style="margin-bottom: 20px; color: #1f2937;">🔔 Inventory Alerts</h2>
                        ${alertHtml}
                        <button class="btn btn-primary" style="width: 100%;" onclick="this.closest('div[style*=\\"fixed\\"]').remove()">Close</button>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modal);
        }
        
        function speakAlert(messages) {
            if ('speechSynthesis' in window) {
                let text = 'Inventory Alert! ';
                messages.forEach(msg => { text += `${msg.title}: ${msg.items.join(', ')}. `; });
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                window.speechSynthesis.speak(utterance);
            }
        }
        
        async function loadStatistics() {
            try {
                const response = await fetch('/get_statistics');
                const stats = await response.json();
                document.getElementById('totalProducts').textContent = stats.total_products || 0;
                document.getElementById('totalValue').textContent = `₹${stats.total_value.toFixed(2)}`;
                document.getElementById('expiringSoon').textContent = stats.expiring_soon_count || 0;
                
                const response2 = await fetch('/get_products');
                const products = await response2.json();
                const lowStockCount = products.filter(p => p.quantity <= 10).length;
                document.getElementById('lowStock').textContent = lowStockCount;
            } catch (error) {
                console.error('Error loading statistics:', error);
            }
        }
        
        function showAlert(message, type = 'info') {
            const alertEl = document.createElement('div');
            alertEl.className = `alert alert-${type}`;
            alertEl.innerHTML = `<span>${escapeHtml(message)}</span>`;
            document.getElementById('alertsContainer').appendChild(alertEl);
            setTimeout(() => {
                alertEl.style.transition = 'opacity 0.3s ease';
                alertEl.style.opacity = '0';
                setTimeout(() => alertEl.remove(), 300);
            }, 5000);
        }
        
        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        window.editProduct = editProduct;
        window.deleteProduct = deleteProduct;
        window.checkExpiry = checkExpiry;
    </script>
</body>
</html>'''

def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                manufacturing_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        required_fields = ['name', 'manufacturing_date', 'expiry_date', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"status": "error", "message": f"{field.replace('_', ' ').title()} is required"}), 400

        mfg_date = datetime.strptime(data['manufacturing_date'], '%Y-%m-%d')
        exp_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
        if exp_date <= mfg_date:
            return jsonify({"status": "error", "message": "Expiry date must be after manufacturing date"}), 400

        name = data['name'].strip()
        category = data.get('category', 'Uncategorized')
        manufacturing_date = data['manufacturing_date']
        expiry_date = data['expiry_date']
        quantity = int(data['quantity'])
        price = float(data.get('price', 0))

        if quantity < 0 or price < 0:
            return jsonify({"status": "error", "message": "Quantity and price cannot be negative"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, category, manufacturing_date, expiry_date, quantity, price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, category, manufacturing_date, expiry_date, quantity, price))
            conn.commit()

        return jsonify({"status": "success", "message": "Product added successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/edit_product/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
    try:
        data = request.get_json()
        required_fields = ['name', 'manufacturing_date', 'expiry_date', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"status": "error", "message": f"{field.replace('_', ' ').title()} is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name=?, category=?, manufacturing_date=?, expiry_date=?, quantity=?, price=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (data['name'], data['category'], data['manufacturing_date'], data['expiry_date'], int(data['quantity']), float(data.get('price', 0)), product_id))
            conn.commit()

        return jsonify({"status": "success", "message": "Product updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_products', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category', '')
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM products WHERE category = ? ORDER BY expiry_date ASC", (category,))
            else:
                cursor.execute("SELECT * FROM products ORDER BY expiry_date ASC")
            products = cursor.fetchall()
            
            today = datetime.today()
            product_list = []
            for p in products:
                expiry_date = datetime.strptime(p["expiry_date"], '%Y-%m-%d')
                days_until_expiry = (expiry_date - today).days
                product_list.append({
                    "id": p["id"],
                    "name": p["name"],
                    "category": p["category"],
                    "manufacturing_date": p["manufacturing_date"],
                    "expiry_date": p["expiry_date"],
                    "quantity": p["quantity"],
                    "price": p["price"],
                    "days_until_expiry": days_until_expiry
                })
            return jsonify(product_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
        return jsonify({"status": "success", "message": "Product deleted successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/check_expiry', methods=['GET'])
def check_expiry():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, expiry_date, quantity FROM products")
            products = cursor.fetchall()

        today = datetime.today()
        expiring_soon = []
        expired = []
        low_stock = []

        for p in products:
            expiry_date = datetime.strptime(p["expiry_date"], '%Y-%m-%d')
            days_left = (expiry_date - today).days

            if days_left < 0:
                expired.append({"name": p["name"], "days_ago": abs(days_left)})
            elif days_left <= 7:
                expiring_soon.append({"name": p["name"], "days_left": days_left})

            if p["quantity"] <= 10:
                low_stock.append({"name": p["name"], "quantity": p["quantity"]})

        return jsonify({"expiring_soon": expiring_soon, "expired": expired, "low_stock": low_stock})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_statistics', methods=['GET'])
def get_statistics():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM products")
            total_products = cursor.fetchone()['total']
            cursor.execute("SELECT SUM(price * quantity) as total_value FROM products")
            total_value = cursor.fetchone()['total_value'] or 0
            cursor.execute("SELECT id, expiry_date FROM products")
            products = cursor.fetchall()
            today = datetime.today()
            expiring_count = sum(1 for p in products if (datetime.strptime(p['expiry_date'], '%Y-%m-%d') - today).days <= 7)
            
            return jsonify({"total_products": total_products, "total_value": round(total_value, 2), "expiring_soon_count": expiring_count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("   GROCERY INVENTORY MANAGEMENT SYSTEM")
    print("="*60)
    print("\nStarting server...")
    print("\nOpen your browser and go to:")
    print("   http://localhost:5000")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
