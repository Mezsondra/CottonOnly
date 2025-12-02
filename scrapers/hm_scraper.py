"""
H&M Scraper - Works for UK and USA
Scrapes 100% cotton products from H&M website
"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from playwright.async_api import Page

import sys
sys.path.append('..')
from scrapers.base_scraper import BaseScraper
from utils.helpers import is_100_percent_cotton, clean_price, clean_text
from config import RETAILERS


class HMScraper(BaseScraper):
    """
    Scraper for H&M website
    """
    
    @property
    def retailer_name(self) -> str:
        return "H&M"
    
    @property
    def retailer_id(self) -> str:
        return "hm"
    
    async def get_base_url(self) -> str:
        """Get base URL for current region"""
        urls = RETAILERS["hm"]["base_urls"]
        return urls.get(self.region, urls["UK"])
    
    def get_category_url(self, gender: str) -> str:
        """Get the category URL for a gender"""
        base = asyncio.get_event_loop().run_until_complete(self.get_base_url())
        
        # H&M URL structure
        gender_paths = {
            "men": "/men/products/view-all.html",
            "women": "/women/products/view-all.html",
            "kids": "/kids/products/view-all.html"
        }
        
        return f"{base}{gender_paths.get(gender, gender_paths['men'])}"
    
    async def scrape_category(self, gender: str, page: Page) -> List[Dict[str, Any]]:
        """
        Scrape products from H&M category page
        """
        products = []
        base_url = await self.get_base_url()
        
        # Gender-specific paths for H&M
        gender_paths = {
            "men": "/men/products/view-all.html",
            "women": "/women/products/view-all.html", 
            "kids": "/kids/products/view-all.html"
        }
        
        category_url = f"{base_url}{gender_paths.get(gender)}"
        
        print(f"  Loading {category_url}")
        
        if not await self.safe_goto(page, category_url):
            return products
        
        # Wait for products to load
        try:
            await page.wait_for_selector('article[data-testid="productTile"]', timeout=10000)
        except:
            # Try alternative selector
            try:
                await page.wait_for_selector('.product-item', timeout=10000)
            except:
                print(f"  Could not find product listings")
                return products
        
        # Scroll to load more products (H&M uses infinite scroll)
        await self.scroll_page(page, scrolls=3)
        
        # Get product links
        product_links = await self.extract_product_links(page)
        print(f"  Found {len(product_links)} product links, checking for 100% cotton...")
        
        # Limit products to check (for demo purposes)
        product_links = product_links[:30]  # Check first 30 products
        
        for i, link in enumerate(product_links):
            print(f"  Checking product {i+1}/{len(product_links)}...", end='\r')
            
            product = await self.get_product_details(link, page, gender)
            if product:
                products.append(product)
            
            await self.random_delay()
        
        print(f"  Completed checking {len(product_links)} products")
        
        return products
    
    async def scroll_page(self, page: Page, scrolls: int = 3):
        """Scroll page to load more products"""
        for i in range(scrolls):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1.5)
    
    async def extract_product_links(self, page: Page) -> List[str]:
        """Extract product links from category page"""
        links = []
        
        # Try multiple selectors for H&M
        selectors = [
            'article[data-testid="productTile"] a',
            '.product-item a',
            'a.item-link',
            '[data-test="product-link"]'
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    href = await elem.get_attribute('href')
                    if href and '/productpage' in href.lower() or '.html' in href:
                        full_url = href if href.startswith('http') else f"https://www2.hm.com{href}"
                        if full_url not in links:
                            links.append(full_url)
            except:
                continue
        
        return links
    
    async def get_product_details(self, product_url: str, page: Page, gender: str = "men") -> Optional[Dict[str, Any]]:
        """
        Get detailed product information and check if 100% cotton
        """
        if not await self.safe_goto(page, product_url):
            return None
        
        try:
            # Wait for product details to load
            await page.wait_for_selector('h1', timeout=5000)
            
            # Get product name
            name_elem = await page.query_selector('h1')
            name = await name_elem.inner_text() if name_elem else ""
            
            # Get price
            price_elem = await page.query_selector('[data-testid="product-price"] span, .price-value, .product-price')
            price_text = await price_elem.inner_text() if price_elem else ""
            price = clean_price(price_text)
            
            # Get image
            img_elem = await page.query_selector('img[data-testid="product-image"], .product-image img, .pdp-image img')
            image_url = await img_elem.get_attribute('src') if img_elem else ""
            
            # Get material composition - this is the key check
            material = await self.get_material_composition(page)
            
            if not material or not is_100_percent_cotton(material):
                return None  # Skip non-cotton products
            
            # Get color if available
            color_elem = await page.query_selector('[data-testid="selected-color"], .color-name')
            color = await color_elem.inner_text() if color_elem else None
            
            # Get available sizes
            sizes = await self.get_available_sizes(page)
            
            if name and price:
                return self.create_product_entry(
                    name=name,
                    price=price,
                    url=product_url,
                    image_url=image_url,
                    gender=gender,
                    material=material,
                    color=color,
                    sizes=sizes
                )
            
        except Exception as e:
            self.errors.append(f"Error getting details for {product_url}: {str(e)}")
        
        return None
    
    async def get_material_composition(self, page: Page) -> str:
        """Extract material composition from product page"""
        # H&M has composition in product details/description section
        selectors = [
            '[data-testid="product-description-text"]',
            '.product-description',
            '.product-detail-info',
            '#product-description',
            '.composition',
            'div:has-text("Composition")',
            'div:has-text("Material")'
        ]
        
        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    # Look for composition/material info
                    if 'cotton' in text.lower():
                        return text
            except:
                continue
        
        # Try clicking on details/composition tab
        try:
            details_btn = await page.query_selector('button:has-text("Details"), button:has-text("Composition")')
            if details_btn:
                await details_btn.click()
                await asyncio.sleep(0.5)
                
                # Try to get composition after clicking
                content = await page.content()
                match = re.search(r'(composition|material)[:\s]*(.*?cotton.*?)(?:\.|<|$)', content.lower())
                if match:
                    return match.group(2)
        except:
            pass
        
        return ""
    
    async def get_available_sizes(self, page: Page) -> List[str]:
        """Extract available sizes from product page"""
        sizes = []
        
        try:
            # H&M size selectors
            size_elems = await page.query_selector_all('[data-testid="size-selector"] button, .size-selector button, .sizes-list button')
            
            for elem in size_elems:
                size_text = await elem.inner_text()
                disabled = await elem.get_attribute('disabled')
                if size_text and not disabled:
                    sizes.append(clean_text(size_text))
        except:
            pass
        
        return sizes


# For testing
if __name__ == "__main__":
    async def test():
        scraper = HMScraper(region="UK")
        products = await scraper.scrape_all(genders=["men"])
        print(f"\nFound {len(products)} products")
        for p in products[:5]:
            print(f"  - {p['name']}: {p['price']} {p['currency']}")
    
    asyncio.run(test())
