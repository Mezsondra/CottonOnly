# 🧵 100% Cotton Clothing Scraper

A Python-based web scraper that finds **100% cotton** clothing products from multiple retailers across UK and USA.

## ✨ Features

- **Multi-retailer support**: H&M, ASOS, Uniqlo, Gap, Next, M&S, and more
- **Multi-region**: UK and USA with region-specific pricing
- **Gender filtering**: Men, Women, Kids
- **Material verification**: Only scrapes products confirmed to be 100% cotton
- **Async scraping**: Fast parallel processing with Playwright
- **Extensible**: Easy to add new retailers

## 📁 Project Structure

```
cotton-scraper/
├── main.py                 # Main entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py     # Abstract base class
│   ├── hm_scraper.py       # H&M scraper
│   ├── asos_scraper.py     # ASOS scraper
│   └── generic_scraper.py  # Generic/configurable scraper
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Utility functions
└── data/                   # Scraped data output (JSON)
```

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
cd cotton-scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Web Interface (Recommended) 🌐

The easiest way to use the scraper is through the web interface:

```bash
# Start the web application
python app.py

# Open your browser to:
# http://localhost:5000
```

**Features:**
- 🎨 Beautiful, responsive UI
- 📊 Real-time scraping progress
- 🔍 Search and filter products
- 📥 Download results as JSON
- 📈 View scraping history
- 🚀 Multi-retailer concurrent scraping

### Command Line Usage

```bash
# Run demo (quick test with H&M UK)
python main.py --demo

# Scrape all retailers in UK
python main.py --region UK

# Scrape USA retailers
python main.py --region USA

# Scrape specific retailer
python main.py --retailer hm

# Scrape specific genders
python main.py --gender men women

# Scrape multiple retailers concurrently (faster!)
python main.py --region UK --retailer hm asos uniqlo --concurrent

# Combine options
python main.py --region USA --retailer hm asos --gender men

# Show all configured retailers
python show_retailers.py
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` / `-r` | Region to scrape (UK, USA, ALL) | UK |
| `--retailer` / `-s` | Specific retailer(s) | All available |
| `--gender` / `-g` | Gender categories | All (men, women, kids) |
| `--output` / `-o` | Output filename | all_products.json |
| `--demo` | Quick demo mode | False |
| `--concurrent` | Scrape multiple retailers in parallel | False |

## 📊 Output Format

Products are saved as JSON with the following structure:

```json
{
  "scraped_at": "2024-01-15T10:30:00",
  "total_products": 150,
  "products": [
    {
      "id": "abc123def456",
      "name": "Pure Cotton T-Shirt",
      "brand": "H&M",
      "price": 12.99,
      "currency": "GBP",
      "url": "https://www2.hm.com/...",
      "image_url": "https://...",
      "gender": "men",
      "category": "t-shirts",
      "material": "100% Cotton",
      "color": "White",
      "sizes": ["S", "M", "L", "XL"],
      "source": "hm",
      "region": "UK",
      "scraped_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## 🌍 Supported Retailers

### UK Region (9 retailers)
| Retailer | Status | Notes |
|----------|--------|-------|
| H&M | ✅ Active | Full support with dedicated scraper |
| ASOS | ✅ Active | Dedicated scraper with material filter |
| Uniqlo | 🔧 Generic | Configurable generic scraper |
| Next | 🔧 Generic | Configurable generic scraper |
| Marks & Spencer | 🔧 Generic | Configurable generic scraper |
| Zara | 🔧 Generic | Configurable generic scraper |
| Primark | 🔧 Generic | Configurable generic scraper |
| John Lewis | 🔧 Generic | Configurable generic scraper |
| Debenhams | 🔧 Generic | Configurable generic scraper |

### USA Region (10 retailers)
| Retailer | Status | Notes |
|----------|--------|-------|
| H&M | ✅ Active | Full support with dedicated scraper |
| Uniqlo | 🔧 Generic | Configurable generic scraper |
| Gap | 🔧 Generic | Configurable generic scraper |
| Old Navy | 🔧 Generic | Configurable generic scraper |
| Target | 🔧 Generic | Configurable generic scraper |
| Zara | 🔧 Generic | Configurable generic scraper |
| Macy's | 🔧 Generic | Configurable generic scraper |
| Nordstrom | 🔧 Generic | Configurable generic scraper |
| J.Crew | 🔧 Generic | Configurable generic scraper |
| Banana Republic | 🔧 Generic | Configurable generic scraper |

## 🔧 Adding New Retailers

### Option 1: Use Generic Scraper (Easy)

Add configuration to `config.py`:

```python
RETAILERS["newstore"] = {
    "name": "New Store",
    "base_urls": {
        "UK": "https://www.newstore.co.uk",
        "USA": "https://www.newstore.com"
    },
    "search_paths": {
        "men": "/mens-clothing",
        "women": "/womens-clothing",
        "kids": "/kids-clothing"
    },
    "supports_material_filter": False
}
```

### Option 2: Create Custom Scraper (Advanced)

Create a new file `scrapers/newstore_scraper.py`:

```python
from scrapers.base_scraper import BaseScraper

class NewStoreScraper(BaseScraper):
    @property
    def retailer_name(self) -> str:
        return "New Store"
    
    @property
    def retailer_id(self) -> str:
        return "newstore"
    
    async def get_base_url(self) -> str:
        # Implementation
        pass
    
    async def scrape_category(self, gender, page):
        # Implementation
        pass
    
    async def get_product_details(self, url, page):
        # Implementation
        pass
```

## 🔍 Material Detection

The scraper looks for these patterns to identify 100% cotton:

- `100% cotton`
- `100% organic cotton`
- `100% BCI cotton`
- `pure cotton`
- `all cotton`

Pattern matching is case-insensitive and handles various formatting.

## ⚡ Performance Features

### Concurrent Scraping
The scraper now supports parallel execution for multiple retailers:

```bash
# Scrape multiple retailers at the same time (faster)
python main.py --region UK --retailer hm asos uniqlo zara --concurrent
```

**Benefits:**
- Significantly faster when scraping multiple retailers
- Each retailer runs in parallel with its own browser instance
- Ideal for scraping all retailers in a region

**Note:** Concurrent mode uses more system resources (CPU, memory, network).

## ⚠️ Important Notes

### Rate Limiting
- Default delay between requests: 2-3.5 seconds
- Respects website rate limits
- Use `--demo` mode for testing
- Concurrent mode scrapes retailers in parallel but still respects per-retailer delays

### Legal Considerations
- Only scrape public product information
- Respect robots.txt directives
- Don't overload servers
- Use data responsibly

### Website Changes
Websites frequently update their structure. If scraping fails:

1. Check if the website is accessible
2. Inspect the page structure for changes
3. Update selectors in the scraper
4. Consider using the generic scraper as fallback

## 🗄️ Database Integration (Future)

The output JSON can be imported into a database:

```python
# Example: PostgreSQL with SQLAlchemy
from sqlalchemy import create_engine
import json

with open('data/all_products.json') as f:
    data = json.load(f)

# Insert into database
for product in data['products']:
    # Insert logic here
    pass
```

## 🔍 Utility Scripts

### Show Retailers
View all configured retailers and their availability:

```bash
# Show all retailers
python show_retailers.py

# Show details for a specific retailer
python show_retailers.py hm
```

This will display:
- All configured retailers grouped by region
- Base URLs for each region
- Current availability status
- Total retailer count

## 📈 Roadmap

- [x] Add more retailers (Zara, Primark, John Lewis, etc.)
- [x] Concurrent/parallel scraping support
- [x] Enhanced generic scraper for broader compatibility
- [ ] Scheduled scraping with cron
- [ ] Price change tracking
- [ ] Database integration (PostgreSQL)
- [ ] API endpoint for the scraped data
- [ ] Docker containerization

## 🤝 Contributing

To add support for a new retailer:

1. Test the website structure manually
2. Create a scraper (generic or custom)
3. Add configuration to `config.py`
4. Test thoroughly with `--demo` mode
5. Submit changes

## 📜 License

MIT License - Use freely for personal and commercial projects.

---

Made with 🧵 for cotton lovers everywhere!
