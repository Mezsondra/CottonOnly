"""
Configuration for 100% Cotton Clothing Scraper
Supports multiple countries and retailers
"""

# Supported regions
REGIONS = {
    "UK": {
        "currency": "GBP",
        "currency_symbol": "£",
        "retailers": ["hm", "asos", "uniqlo", "next", "marksandspencer"]
    },
    "USA": {
        "currency": "USD", 
        "currency_symbol": "$",
        "retailers": ["hm", "uniqlo", "gap", "oldnavy", "target"]
    }
}

# Gender and age group categories
GENDER_CATEGORIES = {
    "men": ["men", "male", "mens", "him"],
    "women": ["women", "female", "womens", "ladies", "her"],
    "kids": ["kids", "children", "boys", "girls", "baby", "toddler", "infant"]
}

# Product categories
PRODUCT_CATEGORIES = [
    "t-shirts",
    "shirts",
    "jeans",
    "trousers",
    "dresses",
    "skirts",
    "shorts",
    "sweaters",
    "hoodies",
    "jackets",
    "underwear",
    "socks",
    "activewear"
]

# Retailer configurations
RETAILERS = {
    "hm": {
        "name": "H&M",
        "base_urls": {
            "UK": "https://www2.hm.com/en_gb",
            "USA": "https://www2.hm.com/en_us"
        },
        "search_paths": {
            "men": "/men/products/view-all.html",
            "women": "/women/products/view-all.html",
            "kids": "/kids/products/view-all.html"
        },
        "material_selector": ".product-details-list",
        "supports_material_filter": False
    },
    "asos": {
        "name": "ASOS",
        "base_urls": {
            "UK": "https://www.asos.com",
            "USA": "https://www.asos.com/us"
        },
        "search_paths": {
            "men": "/men/ctas/generic/generic-all-clothing-702/cat/?cid=3602",
            "women": "/women/ctas/generic/generic-all-clothing/cat/?cid=4209",
            "kids": "/kids/cat/?cid=27391"
        },
        "material_filter": "composition=100%25+Cotton",
        "supports_material_filter": True
    },
    "uniqlo": {
        "name": "Uniqlo",
        "base_urls": {
            "UK": "https://www.uniqlo.com/uk/en",
            "USA": "https://www.uniqlo.com/us/en"
        },
        "search_paths": {
            "men": "/men",
            "women": "/women",
            "kids": "/kids"
        },
        "supports_material_filter": False
    },
    "gap": {
        "name": "Gap",
        "base_urls": {
            "USA": "https://www.gap.com"
        },
        "search_paths": {
            "men": "/browse/category.do?cid=5225",
            "women": "/browse/category.do?cid=5736",
            "kids": "/browse/category.do?cid=6189"
        },
        "supports_material_filter": False
    },
    "next": {
        "name": "Next",
        "base_urls": {
            "UK": "https://www.next.co.uk"
        },
        "search_paths": {
            "men": "/shop/gender-men",
            "women": "/shop/gender-women", 
            "kids": "/shop/department-kids"
        },
        "supports_material_filter": False
    },
    "marksandspencer": {
        "name": "Marks & Spencer",
        "base_urls": {
            "UK": "https://www.marksandspencer.com"
        },
        "search_paths": {
            "men": "/l/men",
            "women": "/l/women",
            "kids": "/l/kids"
        },
        "supports_material_filter": False
    }
}

# Material patterns to identify 100% cotton
COTTON_PATTERNS = [
    r"100%\s*cotton",
    r"100\s*%\s*cotton",
    r"cotton\s*100%",
    r"pure\s*cotton",
    r"all\s*cotton",
    r"100%\s*organic\s*cotton",
    r"100%\s*bci\s*cotton"  # Better Cotton Initiative
]

# Request settings
REQUEST_SETTINGS = {
    "timeout": 30,
    "max_retries": 3,
    "delay_between_requests": 2,  # seconds
    "max_concurrent_requests": 5
}

# Output settings
OUTPUT_DIR = "data"
