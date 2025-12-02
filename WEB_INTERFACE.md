# 🌐 Web Interface Guide

The 100% Cotton Clothing Scraper comes with a modern, user-friendly web interface that makes scraping and browsing products a breeze!

## 🚀 Getting Started

### Start the Web Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

Open your web browser and navigate to that address.

## 📱 Features

### 1. **Scraping Control Panel**

Located on the left side of the screen, this panel lets you configure and start scraping jobs:

- **Region Selection**: Choose between UK (£) or USA ($) markets
- **Retailer Selection**: Select which retailers to scrape
  - Use "Select All" or "Deselect All" for quick selection
  - Retailers are automatically filtered based on selected region
- **Gender Categories**: Choose Men, Women, Kids, or any combination
- **Start/Stop Controls**: Begin or halt scraping operations

### 2. **Real-Time Progress Tracking**

Watch scraping progress in real-time:

- **Progress Bar**: Visual indication of completion percentage
- **Current Status**: See which retailer is currently being scraped
- **Activity Log**: Detailed log of scraping operations
  - Timestamps for each action
  - Success/error messages
  - Product counts per retailer

### 3. **Product Display**

Browse scraped products in a beautiful grid layout:

- **Product Cards** with:
  - Product image
  - Name and description
  - Price with currency
  - Gender badge
  - Material confirmation badge
  - Retailer name
  - Direct link to product page

### 4. **Search and Filter**

Find exactly what you're looking for:

- **Search Box**: Search by product name or brand
- **Sort Options**:
  - Name (A-Z)
  - Price: Low to High
  - Price: High to Low
  - Retailer
- **Filter by Gender**: Men, Women, Kids, or All
- **Filter by Retailer**: Show products from specific stores

### 5. **File Management**

Access your scraping history:

- **Files Button**: View all saved JSON files
- **Load**: Load products from previous scraping sessions
- **Download**: Download JSON files for backup or analysis
- **File Info**: See file size and timestamp

## 🎨 User Interface

### Layout

The interface uses a **responsive design** that works on:
- Desktop computers
- Tablets
- Mobile phones

### Color Scheme

- **Modern gradient background** for visual appeal
- **Clean white cards** for easy reading
- **Color-coded badges**:
  - Blue for Men's products
  - Pink for Women's products
  - Orange for Kids' products
  - Green for 100% cotton confirmation

### Interactions

- **Hover Effects**: Cards lift up when you hover over them
- **Click to View**: Click any product card to open the retailer's page
- **Toast Notifications**: Get feedback for all actions
- **Smooth Animations**: Progress bars and transitions

## 🔧 API Endpoints

The web interface is powered by a RESTful API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the main web page |
| `/api/config` | GET | Get regions and retailers configuration |
| `/api/retailers/<region>` | GET | Get available retailers for a region |
| `/api/scrape` | POST | Start a scraping job |
| `/api/stop` | POST | Stop current scraping job |
| `/api/status` | GET | Get current scraping status |
| `/api/products` | GET | Get all scraped products (latest file) |
| `/api/products/files` | GET | List all saved JSON files |
| `/api/products/file/<filename>` | GET | Get products from specific file |
| `/api/download/<filename>` | GET | Download a JSON file |

## 💡 Tips & Tricks

### Best Practices

1. **Start with a few retailers** to test the system
2. **Use concurrent mode** for faster results when scraping multiple retailers
3. **Check the activity log** to see what's happening in real-time
4. **Save your results** by clicking the Files button
5. **Filter by retailer** to compare offerings across stores

### Performance

- The web server runs on port 5000 by default
- Scraping runs in background threads to keep the UI responsive
- Status updates poll every 2 seconds during active scraping
- Products are automatically saved to the `/data` directory

### Storage

- Each scraping session creates a timestamped JSON file
- Files include metadata: scrape time, product count, etc.
- Files can be loaded later for browsing
- Old files can be safely deleted if not needed

## 🎯 Example Workflow

1. **Open the web interface** at `http://localhost:5000`
2. **Select UK region** from the dropdown
3. **Check H&M, ASOS, and Uniqlo** from the retailers list
4. **Select Men and Women** categories
5. **Click "Start Scraping"** button
6. **Watch the progress** in the activity log
7. **Browse results** as they appear in real-time
8. **Use search** to find specific items (e.g., "t-shirt")
9. **Sort by price** to find best deals
10. **Click products** to visit retailer websites
11. **Save your session** via the Files menu

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if port 5000 is already in use
lsof -i :5000

# Or use a different port
# Edit app.py and change: app.run(port=5001)
```

### Scraping gets stuck

- Click "Stop Scraping" button
- Refresh the page
- Check the activity log for error messages
- Try scraping fewer retailers at once

### Products not showing

- Click the "Refresh" button
- Check the "Files" menu to load from a specific file
- Ensure scraping has completed (progress bar at 100%)

### Images not loading

- Some retailers block external image requests
- This is normal behavior
- Product information is still valid

## 📊 Data Format

Products are saved in JSON format:

```json
{
  "scraped_at": "2024-12-02T19:30:00",
  "total_products": 150,
  "products": [
    {
      "id": "abc123def456",
      "name": "Pure Cotton T-Shirt",
      "brand": "H&M",
      "price": 12.99,
      "currency": "GBP",
      "url": "https://...",
      "image_url": "https://...",
      "gender": "men",
      "category": "t-shirts",
      "material": "100% Cotton",
      "color": "White",
      "sizes": ["S", "M", "L", "XL"],
      "source": "hm",
      "region": "UK",
      "scraped_at": "2024-12-02T19:30:00"
    }
  ]
}
```

## 🔒 Security Notes

- The web server is designed for **local use only**
- Don't expose it directly to the internet without proper security
- No authentication is required (since it's local)
- No sensitive data is stored

## 🚀 Next Steps

After using the web interface:

1. **Analyze your data** using the JSON files
2. **Import to a database** for more advanced queries
3. **Track price changes** over time
4. **Build a mobile app** using the API
5. **Schedule regular scraping** with cron jobs

---

Enjoy finding your perfect 100% cotton clothing! 🧵
