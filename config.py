"""
Configuration for 100% Cotton Clothing Scraper
Supports multiple countries and retailers
"""

# Supported regions
REGIONS = {
    "UK": {
        "currency": "GBP",
        "currency_symbol": "£",
        "retailers": ["hm", "asos", "uniqlo", "next", "marksandspencer", "zara", "primark", "johnlewis", "debenhams"]
    },
    "USA": {
        "currency": "USD",
        "currency_symbol": "$",
        "retailers": ["hm", "uniqlo", "gap", "oldnavy", "target", "zara", "macys", "nordstrom", "jcrew", "bananarepublic"]
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
    },
    "oldnavy": {
        "name": "Old Navy",
        "base_urls": {
            "USA": "https://oldnavy.gap.com"
        },
        "search_paths": {
            "men": "/browse/category.do?cid=1011502",
            "women": "/browse/category.do?cid=1011506",
            "kids": "/browse/category.do?cid=1011510"
        },
        "supports_material_filter": False
    },
    "target": {
        "name": "Target",
        "base_urls": {
            "USA": "https://www.target.com"
        },
        "search_paths": {
            "men": "/c/men-s-clothing/-/N-5xtcd",
            "women": "/c/women-s-clothing/-/N-5xtco",
            "kids": "/c/kids-clothing/-/N-5xtcv"
        },
        "supports_material_filter": False
    },
    "zara": {
        "name": "Zara",
        "base_urls": {
            "UK": "https://www.zara.com/uk",
            "USA": "https://www.zara.com/us"
        },
        "search_paths": {
            "men": "/en/man-new-in-l603.html",
            "women": "/en/woman-new-in-l1180.html",
            "kids": "/en/kids-new-in-l585.html"
        },
        "supports_material_filter": False
    },
    "primark": {
        "name": "Primark",
        "base_urls": {
            "UK": "https://www.primark.com/en-gb"
        },
        "search_paths": {
            "men": "/products/mens/clothing",
            "women": "/products/womens/clothing",
            "kids": "/products/kids"
        },
        "supports_material_filter": False
    },
    "johnlewis": {
        "name": "John Lewis",
        "base_urls": {
            "UK": "https://www.johnlewis.com"
        },
        "search_paths": {
            "men": "/browse/men/mens-clothing/_/N-7jzh",
            "women": "/browse/women/womens-clothing/_/N-7jzf",
            "kids": "/browse/baby-child/kids-clothing/_/N-7jzg"
        },
        "supports_material_filter": False
    },
    "debenhams": {
        "name": "Debenhams",
        "base_urls": {
            "UK": "https://www.debenhams.com"
        },
        "search_paths": {
            "men": "/men/mens-clothing",
            "women": "/women/womens-clothing",
            "kids": "/kids"
        },
        "supports_material_filter": False
    },
    "macys": {
        "name": "Macy's",
        "base_urls": {
            "USA": "https://www.macys.com"
        },
        "search_paths": {
            "men": "/shop/mens-clothing?id=1",
            "women": "/shop/womens-clothing?id=255",
            "kids": "/shop/kids-clothes?id=5991"
        },
        "supports_material_filter": False
    },
    "nordstrom": {
        "name": "Nordstrom",
        "base_urls": {
            "USA": "https://www.nordstrom.com"
        },
        "search_paths": {
            "men": "/browse/men/clothing",
            "women": "/browse/women/clothing",
            "kids": "/browse/kids/clothing"
        },
        "supports_material_filter": False
    },
    "jcrew": {
        "name": "J.Crew",
        "base_urls": {
            "USA": "https://www.jcrew.com"
        },
        "search_paths": {
            "men": "/c/mens_category/clothing",
            "women": "/c/womens_category/clothing",
            "kids": "/c/girls_category"
        },
        "supports_material_filter": False
    },
    "bananarepublic": {
        "name": "Banana Republic",
        "base_urls": {
            "USA": "https://bananarepublic.gap.com"
        },
        "search_paths": {
            "men": "/browse/category.do?cid=32643",
            "women": "/browse/category.do?cid=70174",
            "kids": "/browse/category.do?cid=1056958"
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
