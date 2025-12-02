// Global state
let products = [];
let config = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadProducts();

    // Add event listeners
    document.getElementById('regionSelect').addEventListener('change', updateRetailersList);
    document.getElementById('searchBox').addEventListener('input', filterProducts);
    document.getElementById('sortSelect').addEventListener('change', filterProducts);
    document.getElementById('filterGender').addEventListener('change', filterProducts);
    document.getElementById('filterRetailer').addEventListener('change', filterProducts);
});

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        config = await response.json();
        updateRetailersList();
    } catch (error) {
        console.error('Error loading config:', error);
        showToast('Error loading configuration', 'error');
    }
}

// Update retailers list based on selected region
async function updateRetailersList() {
    const region = document.getElementById('regionSelect').value;
    const retailersContainer = document.getElementById('retailersList');

    try {
        const response = await fetch(`/api/retailers/${region}`);
        const retailers = await response.json();

        retailersContainer.innerHTML = retailers.map(retailer => `
            <label class="checkbox-label">
                <input type="checkbox" value="${retailer.key}" class="retailer-checkbox" checked>
                <span>${retailer.name}</span>
            </label>
        `).join('');
    } catch (error) {
        console.error('Error loading retailers:', error);
    }
}

// Select/Deselect all retailers
function selectAllRetailers() {
    document.querySelectorAll('.retailer-checkbox').forEach(cb => cb.checked = true);
}

function deselectAllRetailers() {
    document.querySelectorAll('.retailer-checkbox').forEach(cb => cb.checked = false);
}

// Start scraping
async function startScraping() {
    const region = document.getElementById('regionSelect').value;

    const selectedRetailers = Array.from(
        document.querySelectorAll('.retailer-checkbox:checked')
    ).map(cb => cb.value);

    const selectedGenders = Array.from(
        document.querySelectorAll('.gender-checkbox:checked')
    ).map(cb => cb.value);

    if (selectedRetailers.length === 0) {
        showToast('Please select at least one retailer', 'error');
        return;
    }

    if (selectedGenders.length === 0) {
        showToast('Please select at least one gender', 'error');
        return;
    }

    const data = {
        region: region,
        retailers: selectedRetailers,
        genders: selectedGenders
    };

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'block';
            document.getElementById('progressSection').style.display = 'block';

            showToast('Scraping started!', 'success');
            startStatusPolling();
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to start scraping', 'error');
        }
    } catch (error) {
        console.error('Error starting scrape:', error);
        showToast('Failed to start scraping', 'error');
    }
}

// Stop scraping
async function stopScraping() {
    try {
        const response = await fetch('/api/stop', { method: 'POST' });

        if (response.ok) {
            showToast('Stopping scraper...', 'info');
        }
    } catch (error) {
        console.error('Error stopping scrape:', error);
    }
}

// Poll status
let statusInterval;
function startStatusPolling() {
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();

            updateProgress(status);

            if (!status.is_scraping) {
                stopStatusPolling();
                document.getElementById('startBtn').style.display = 'block';
                document.getElementById('stopBtn').style.display = 'none';

                if (status.total_products > 0) {
                    showToast(`Scraping complete! Found ${status.total_products} products`, 'success');
                    loadProducts();
                }
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 2000);
}

function stopStatusPolling() {
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
}

// Update progress
function updateProgress(status) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const activityLog = document.getElementById('activityLog');

    progressBar.style.width = `${status.progress}%`;
    progressBar.textContent = `${status.progress}%`;

    if (status.current_retailer) {
        progressText.textContent = `Scraping ${status.current_retailer}...`;
    } else if (status.progress === 100) {
        progressText.textContent = 'Complete!';
    }

    // Update activity log
    if (status.log && status.log.length > 0) {
        activityLog.innerHTML = status.log.slice(-20).map(log =>
            `<div>${log}</div>`
        ).join('');
        activityLog.scrollTop = activityLog.scrollHeight;
    }
}

// Load products
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        products = await response.json();

        displayProducts(products);
        updateRetailerFilter();
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('Error loading products', 'error');
    }
}

// Display products
function displayProducts(productsToShow) {
    const grid = document.getElementById('productsGrid');
    const countElement = document.getElementById('productCount');

    countElement.textContent = productsToShow.length;

    if (productsToShow.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>No products to display</p></div>';
        return;
    }

    grid.innerHTML = productsToShow.map(product => `
        <div class="product-card" onclick="window.open('${product.url}', '_blank')">
            <img src="${product.image_url || 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'280\' height=\'250\'%3E%3Crect fill=\'%23ecf0f1\' width=\'280\' height=\'250\'/%3E%3Ctext fill=\'%237f8c8d\' x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\' font-family=\'sans-serif\' font-size=\'18\'%3ENo Image%3C/text%3E%3C/svg%3E'}"
                 class="product-image"
                 alt="${product.name}"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'280\' height=\'250\'%3E%3Crect fill=\'%23ecf0f1\' width=\'280\' height=\'250\'/%3E%3Ctext fill=\'%237f8c8d\' x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\' font-family=\'sans-serif\' font-size=\'18\'%3ENo Image%3C/text%3E%3C/svg%3E'">
            <div class="product-info">
                <h3 class="product-name">${escapeHtml(product.name)}</h3>
                <div class="product-price">${product.currency_symbol || getCurrencySymbol(product.currency)}${product.price.toFixed(2)}</div>
                <div class="product-meta">
                    <span class="product-badge badge-${product.gender}">${product.gender}</span>
                    <span>${product.category || 'clothing'}</span>
                </div>
                <div class="product-material">✓ ${product.material}</div>
                <div class="product-footer">
                    <span class="product-retailer">${product.brand || product.source}</span>
                    <a href="${product.url}" class="product-link" target="_blank" onclick="event.stopPropagation()">View →</a>
                </div>
            </div>
        </div>
    `).join('');
}

// Filter and sort products
function filterProducts() {
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    const sortBy = document.getElementById('sortSelect').value;
    const genderFilter = document.getElementById('filterGender').value;
    const retailerFilter = document.getElementById('filterRetailer').value;

    let filtered = products.filter(product => {
        const matchesSearch = !searchTerm ||
            product.name.toLowerCase().includes(searchTerm) ||
            (product.brand || '').toLowerCase().includes(searchTerm);

        const matchesGender = !genderFilter || product.gender === genderFilter;
        const matchesRetailer = !retailerFilter || product.source === retailerFilter;

        return matchesSearch && matchesGender && matchesRetailer;
    });

    // Sort
    filtered.sort((a, b) => {
        switch (sortBy) {
            case 'name':
                return a.name.localeCompare(b.name);
            case 'price-low':
                return a.price - b.price;
            case 'price-high':
                return b.price - a.price;
            case 'retailer':
                return (a.brand || a.source).localeCompare(b.brand || b.source);
            default:
                return 0;
        }
    });

    displayProducts(filtered);
}

// Update retailer filter dropdown
function updateRetailerFilter() {
    const filterSelect = document.getElementById('filterRetailer');
    const retailers = [...new Set(products.map(p => p.source))].sort();

    filterSelect.innerHTML = '<option value="">All Retailers</option>' +
        retailers.map(r => `<option value="${r}">${r}</option>`).join('');
}

// Show files modal
async function showFiles() {
    try {
        const response = await fetch('/api/products/files');
        const files = await response.json();

        const filesContainer = document.getElementById('filesList');

        if (files.length === 0) {
            filesContainer.innerHTML = '<p class="empty-state">No saved files</p>';
        } else {
            filesContainer.innerHTML = files.map(file => `
                <div class="file-item">
                    <div class="file-info">
                        <h4>${file.name}</h4>
                        <p>${formatFileSize(file.size)} • ${formatDate(file.modified)}</p>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-sm btn-primary" onclick="loadFile('${file.name}')">Load</button>
                        <button class="btn btn-sm btn-secondary" onclick="downloadFile('${file.name}')">Download</button>
                    </div>
                </div>
            `).join('');
        }

        document.getElementById('filesModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading files:', error);
        showToast('Error loading files', 'error');
    }
}

function closeFilesModal() {
    document.getElementById('filesModal').style.display = 'none';
}

// Load specific file
async function loadFile(filename) {
    try {
        const response = await fetch(`/api/products/file/${filename}`);
        products = await response.json();

        displayProducts(products);
        updateRetailerFilter();
        closeFilesModal();

        showToast(`Loaded ${products.length} products from ${filename}`, 'success');
    } catch (error) {
        console.error('Error loading file:', error);
        showToast('Error loading file', 'error');
    }
}

// Download file
function downloadFile(filename) {
    window.open(`/api/download/${filename}`, '_blank');
}

// Utility functions
function getCurrencySymbol(currency) {
    const symbols = { 'GBP': '£', 'USD': '$', 'EUR': '€' };
    return symbols[currency] || '$';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    // Simple toast notification - could be enhanced
    console.log(`[${type.toUpperCase()}] ${message}`);

    // You could add a toast UI element here
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('filesModal');
    if (event.target === modal) {
        closeFilesModal();
    }
}
