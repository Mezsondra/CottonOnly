"""
Generic Retailer Scraper - Configurable for multiple sites
Works with common e-commerce site structures
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from playwright.async_api import Page

import sys
sys.path.append('..')
from scrapers.base_scraper import BaseScraper
from utils.helpers import is_100_percent_cotton, clean_price, clean_text
from config import RETAILERS


class GenericRetailerScraper(BaseScraper):
    """
    Generic scraper that can be configured for different retailers
    """
    
    def __init__(self, retailer_key: str, region: str = "UK"):
        """
        Initialize with retailer configuration
        
        Args:
            retailer_key: Key from RETAILERS config
            region: Country/region code
        """
        super().__init__(region)
        
        self.retailer_key = retailer_key
        self.config = RETAILERS.get(retailer_key, {})
        
        if not self.config:
            raise ValueError(f"Unknown retailer: {retailer_key}")
    
    @property
    def retailer_name(self) -> str:
        return self.config.get("name", self.retailer_key)
    
    @property
    def retailer_id(self) -> str:
        return self.retailer_key
    
    async def get_base_url(self) -> str:
        """Get base URL for current region"""
        urls = self.config.get("base_urls", {})
        return urls.get(self.region, list(urls.values())[0] if urls else "")
    
    async def scrape_category(self, gender: str, page: Page) -> List[Dict[str, Any]]:
        """
        Scrape products using a generic approach
        """
        products = []
        base_url = await self.get_base_url()
        
        if not base_url:
            print(f"  No URL configured for {self.region}")
            return products
        
        search_paths = self.config.get("search_paths", {})
        path = search_paths.get(gender, "")
        
        if not path:
            # Try search approach
            category_url = f"{base_url}/search?q=100%25+cotton+{gender}"
        else:
            category_url = f"{base_url}{path}"
        
        print(f"  Loading {category_url[:80]}...")
        
        if not await self.safe_goto(page, category_url):
            return products
        
        # Wait for content to load
        await asyncio.sleep(3)
        
        # Try to find products using common selectors
        product_links = await self.find_product_links(page)
        
        print(f"  Found {len(product_links)} product links")
        
        # Check each product
        for i, link in enumerate(product_links[:15]):  # Limit for demo
            print(f"  Checking product {i+1}/{min(len(product_links), 15)}...", end='\r')
            
            product = await self.get_product_details(link, page, gender)
            if product:
                products.append(product)
            
            await self.random_delay()
        
        print(f"  Completed checking products")
        
        return products
    
    async def find_product_links(self, page: Page) -> List[str]:
        """Find product links using common patterns"""
        links = []
        base_url = await self.get_base_url()
        
        # Common product link selectors
        selectors = [
            'a[href*="/product"]',
            'a[href*="/p/"]',
            'a[href*="/pd/"]',
            'a[href*="/shop/"]',
            '.product-card a',
            '.product-item a',
            '.product-tile a',
            'article a[href]',
            '[data-testid*="product"] a'
        ]
        
        seen = set()
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    href = await elem.get_attribute('href')
                    if href:
                        # Make absolute URL
                        if not href.startswith('http'):
                            href = f"{base_url}{href}" if href.startswith('/') else f"{base_url}/{href}"
                        
                        if href not in seen:
                            seen.add(href)
                            links.append(href)
            except:
                continue
        
        return links
    
    async def get_product_details(self, product_url: str, page: Page, gender: str = "men") -> Optional[Dict[str, Any]]:
        """
        Get product details and verify 100% cotton
        """
        if not await self.safe_goto(page, product_url):
            return None
        
        try:
            await asyncio.sleep(2)  # Wait for page to fully load
            
            # Get product name
            name = await self.extract_text(page, [
                'h1',
                '[data-testid="product-title"]',
                '.product-name',
                '.product-title',
                '#product-title'
            ])
            
            # Get price
            price_text = await self.extract_text(page, [
                '[data-testid="price"]',
                '.price',
                '.product-price',
                '[class*="price"]',
                'span[data-price]'
            ])
            price = clean_price(price_text)
            
            # Get image
            image_url = await self.extract_attribute(page, 'src', [
                '.product-image img',
                '#product-image img',
                '[data-testid="product-image"] img',
                '.gallery img',
                'img[alt*="product"]'
            ])
            
            # Get material - THE KEY CHECK
            material = await self.extract_material(page)
            
            if not material or not is_100_percent_cotton(material):
                return None
            
            # Get color if available
            color = await self.extract_text(page, [
                '.selected-color',
                '.color-name',
                '[data-testid="color"]'
            ])
            
            # Get sizes
            sizes = await self.extract_sizes(page)
            
            if name and price:
                return self.create_product_entry(
                    name=name,
                    price=price,
                    url=product_url,
                    image_url=image_url or "",
                    gender=gender,
                    material=material,
                    color=color if color else None,
                    sizes=sizes
                )
                
        except Exception as e:
            self.errors.append(f"Error: {str(e)}")
        
        return None
    
    async def extract_text(self, page: Page, selectors: List[str]) -> str:
        """Try multiple selectors to extract text"""
        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text:
                        return clean_text(text)
            except:
                continue
        return ""
    
    async def extract_attribute(self, page: Page, attr: str, selectors: List[str]) -> str:
        """Try multiple selectors to extract an attribute"""
        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    value = await elem.get_attribute(attr)
                    if value:
                        return value
            except:
                continue
        return ""
    
    async def extract_material(self, page: Page) -> str:
        """Extract material composition from product page"""
        # Common material/composition selectors
        selectors = [
            '[data-testid="composition"]',
            '.composition',
            '.material',
            '#composition',
            '#material',
            '.product-details',
            '.product-description',
            '[class*="composition"]',
            '[class*="material"]'
        ]
        
        for selector in selectors:
            text = await self.extract_text(page, [selector])
            if 'cotton' in text.lower():
                return text
        
        # Try to find in page content
        try:
            content = await page.content()
            patterns = [
                r'composition[:\s]*(100%?\s*cotton)',
                r'material[:\s]*(100%?\s*cotton)',
                r'(100%\s*cotton)',
                r'(pure\s*cotton)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content.lower())
                if match:
                    return match.group(1)
        except:
            pass
        
        return ""
    
    async def extract_sizes(self, page: Page) -> List[str]:
        """Extract available sizes"""
        sizes = []
        
        selectors = [
            '.size-selector button:not([disabled])',
            '.size-option:not(.disabled)',
            '[data-testid="size"] option',
            'select[name*="size"] option'
        ]
        
        for selector in selectors:
            try:
                elems = await page.query_selector_all(selector)
                for elem in elems:
                    text = await elem.inner_text()
                    if text and 'select' not in text.lower():
                        sizes.append(clean_text(text))
            except:
                continue
            
            if sizes:
                break
        
        return sizes


# Factory function to create retailer scrapers
def create_scraper(retailer: str, region: str = "UK") -> BaseScraper:
    """
    Factory function to create the appropriate scraper
    
    Args:
        retailer: Retailer key (hm, asos, uniqlo, etc.)
        region: Region code (UK, USA)
        
    Returns:
        Appropriate scraper instance
    """
    # Import specific scrapers
    from scrapers.hm_scraper import HMScraper
    from scrapers.asos_scraper import ASOSScraper
    
    scrapers = {
        "hm": HMScraper,
        "asos": ASOSScraper,
    }
    
    scraper_class = scrapers.get(retailer)
    
    if scraper_class:
        return scraper_class(region=region)
    else:
        # Use generic scraper for other retailers
        return GenericRetailerScraper(retailer, region=region)
