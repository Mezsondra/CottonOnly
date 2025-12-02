"""
Utility functions for the cotton clothing scraper
"""

import re
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import COTTON_PATTERNS, GENDER_CATEGORIES, OUTPUT_DIR


def is_100_percent_cotton(material_text: str) -> bool:
    """
    Check if the material composition indicates 100% cotton
    
    Args:
        material_text: The material/composition text from product page
        
    Returns:
        True if the product is 100% cotton, False otherwise
    """
    if not material_text:
        return False
    
    material_lower = material_text.lower().strip()
    
    for pattern in COTTON_PATTERNS:
        if re.search(pattern, material_lower, re.IGNORECASE):
            return True
    
    return False


def normalize_gender(gender_text: str) -> Optional[str]:
    """
    Normalize gender text to standard categories: men, women, kids
    
    Args:
        gender_text: Raw gender text from website
        
    Returns:
        Normalized gender string or None
    """
    if not gender_text:
        return None
        
    gender_lower = gender_text.lower().strip()
    
    for standard_gender, variants in GENDER_CATEGORIES.items():
        if any(variant in gender_lower for variant in variants):
            return standard_gender
    
    return None


def clean_price(price_text: str) -> Optional[float]:
    """
    Extract numeric price from price text
    
    Args:
        price_text: Raw price text (e.g., "£29.99", "$15.00", "€ 19,99")
        
    Returns:
        Float price value or None
    """
    if not price_text:
        return None
    
    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[£$€\s]', '', price_text)
    
    # Handle European format (comma as decimal separator)
    # If there's a comma followed by exactly 2 digits at the end, treat as decimal
    if re.search(r',\d{2}$', cleaned):
        cleaned = cleaned.replace(',', '.')
    else:
        # Otherwise remove commas (thousand separators)
        cleaned = cleaned.replace(',', '')
    
    # Extract first number (handles "From £29.99" etc.)
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    
    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = ' '.join(text.split())
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


def generate_product_id(source: str, product_url: str) -> str:
    """
    Generate a unique product ID based on source and URL
    
    Args:
        source: Retailer name
        product_url: Product page URL
        
    Returns:
        Unique product ID string
    """
    import hashlib
    
    unique_string = f"{source}:{product_url}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]


def save_products_json(products: List[Dict[str, Any]], filename: str) -> str:
    """
    Save products to JSON file
    
    Args:
        products: List of product dictionaries
        filename: Output filename
        
    Returns:
        Path to saved file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    output_data = {
        "scraped_at": datetime.now().isoformat(),
        "total_products": len(products),
        "products": products
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def load_products_json(filename: str) -> List[Dict[str, Any]]:
    """
    Load products from JSON file
    
    Args:
        filename: JSON filename to load
        
    Returns:
        List of product dictionaries
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('products', [])


def merge_products(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """
    Merge new products with existing, avoiding duplicates
    
    Args:
        existing: Existing product list
        new: New products to add
        
    Returns:
        Merged product list
    """
    existing_ids = {p.get('id') for p in existing}
    
    merged = existing.copy()
    for product in new:
        if product.get('id') not in existing_ids:
            merged.append(product)
            existing_ids.add(product.get('id'))
    
    return merged


def format_product_summary(products: List[Dict]) -> str:
    """
    Generate a summary of scraped products
    
    Args:
        products: List of product dictionaries
        
    Returns:
        Formatted summary string
    """
    if not products:
        return "No products found."
    
    summary_lines = [
        f"\n{'='*50}",
        f"SCRAPING SUMMARY",
        f"{'='*50}",
        f"Total Products: {len(products)}",
        ""
    ]
    
    # Group by gender
    by_gender = {}
    for p in products:
        gender = p.get('gender', 'unknown')
        by_gender[gender] = by_gender.get(gender, 0) + 1
    
    summary_lines.append("By Gender:")
    for gender, count in sorted(by_gender.items()):
        summary_lines.append(f"  - {gender.capitalize()}: {count}")
    
    # Group by source
    by_source = {}
    for p in products:
        source = p.get('source', 'unknown')
        by_source[source] = by_source.get(source, 0) + 1
    
    summary_lines.append("\nBy Retailer:")
    for source, count in sorted(by_source.items()):
        summary_lines.append(f"  - {source}: {count}")
    
    # Price range
    prices = [p.get('price') for p in products if p.get('price')]
    if prices:
        summary_lines.append(f"\nPrice Range: {min(prices):.2f} - {max(prices):.2f}")
    
    summary_lines.append(f"{'='*50}\n")
    
    return '\n'.join(summary_lines)


def categorize_product(product_name: str, product_url: str = "") -> Optional[str]:
    """
    Attempt to categorize a product based on its name
    
    Args:
        product_name: Product name/title
        product_url: Product URL (optional)
        
    Returns:
        Category string or None
    """
    text = f"{product_name} {product_url}".lower()
    
    category_keywords = {
        "t-shirts": ["t-shirt", "tee", "tshirt"],
        "shirts": ["shirt", "blouse", "button-up"],
        "jeans": ["jeans", "denim"],
        "trousers": ["trousers", "pants", "chinos", "slacks"],
        "dresses": ["dress"],
        "skirts": ["skirt"],
        "shorts": ["shorts"],
        "sweaters": ["sweater", "jumper", "pullover", "knit"],
        "hoodies": ["hoodie", "sweatshirt"],
        "jackets": ["jacket", "coat", "blazer"],
        "underwear": ["underwear", "briefs", "boxers", "panties", "bra"],
        "socks": ["socks", "sock"],
        "activewear": ["joggers", "leggings", "sports", "gym", "athletic"]
    }
    
    for category, keywords in category_keywords.items():
        if any(kw in text for kw in keywords):
            return category
    
    return "other"
