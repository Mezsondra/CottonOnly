"""
Base scraper class for all retailer scrapers
"""

import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page
from fake_useragent import UserAgent

import sys
sys.path.append('..')
from config import REQUEST_SETTINGS, REGIONS
from utils.helpers import (
    is_100_percent_cotton,
    generate_product_id,
    clean_text,
    clean_price,
    categorize_product
)


class BaseScraper(ABC):
    """
    Abstract base class for all retailer scrapers
    """
    
    def __init__(self, region: str = "UK"):
        """
        Initialize the scraper
        
        Args:
            region: Country/region code (UK, USA, etc.)
        """
        self.region = region
        self.region_config = REGIONS.get(region, REGIONS["UK"])
        self.currency = self.region_config["currency"]
        self.currency_symbol = self.region_config["currency_symbol"]
        
        self.browser: Optional[Browser] = None
        self.ua = UserAgent()
        
        self.products: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        
        # Request settings
        self.timeout = REQUEST_SETTINGS["timeout"] * 1000  # Convert to ms
        self.delay = REQUEST_SETTINGS["delay_between_requests"]
        self.max_retries = REQUEST_SETTINGS["max_retries"]
    
    @property
    @abstractmethod
    def retailer_name(self) -> str:
        """Return the retailer name"""
        pass
    
    @property
    @abstractmethod
    def retailer_id(self) -> str:
        """Return the retailer ID (lowercase, no spaces)"""
        pass
    
    @abstractmethod
    async def get_base_url(self) -> str:
        """Return the base URL for the current region"""
        pass
    
    @abstractmethod
    async def scrape_category(self, gender: str, page: Page) -> List[Dict[str, Any]]:
        """
        Scrape products from a specific gender category
        
        Args:
            gender: Gender category (men, women, kids)
            page: Playwright page instance
            
        Returns:
            List of product dictionaries
        """
        pass
    
    @abstractmethod
    async def get_product_details(self, product_url: str, page: Page) -> Optional[Dict[str, Any]]:
        """
        Get detailed product information including material composition
        
        Args:
            product_url: URL of the product page
            page: Playwright page instance
            
        Returns:
            Product dictionary or None if not 100% cotton
        """
        pass
    
    async def start_browser(self) -> Browser:
        """Start the Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self.browser
    
    async def close_browser(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
    
    async def new_page(self) -> Page:
        """Create a new browser page with random user agent"""
        if not self.browser:
            await self.start_browser()
        
        context = await self.browser.new_context(
            user_agent=self.ua.random,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        page.set_default_timeout(self.timeout)
        
        return page
    
    async def random_delay(self):
        """Add a random delay between requests"""
        delay = self.delay + random.uniform(0.5, 1.5)
        await asyncio.sleep(delay)
    
    async def safe_goto(self, page: Page, url: str, retries: int = 0) -> bool:
        """
        Safely navigate to a URL with retry logic
        
        Args:
            page: Playwright page instance
            url: URL to navigate to
            retries: Current retry count
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await page.goto(url, wait_until='domcontentloaded')
            await self.random_delay()
            return True
        except Exception as e:
            if retries < self.max_retries:
                print(f"  Retry {retries + 1}/{self.max_retries} for {url}")
                await asyncio.sleep(2 ** retries)  # Exponential backoff
                return await self.safe_goto(page, url, retries + 1)
            else:
                self.errors.append(f"Failed to load {url}: {str(e)}")
                return False
    
    def create_product_entry(
        self,
        name: str,
        price: float,
        url: str,
        image_url: str,
        gender: str,
        material: str = "100% Cotton",
        brand: Optional[str] = None,
        category: Optional[str] = None,
        color: Optional[str] = None,
        sizes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized product entry
        
        Args:
            name: Product name
            price: Product price
            url: Product URL
            image_url: Product image URL
            gender: Gender category
            material: Material composition
            brand: Brand name (optional)
            category: Product category (optional)
            color: Product color (optional)
            sizes: Available sizes (optional)
            
        Returns:
            Standardized product dictionary
        """
        product_id = generate_product_id(self.retailer_id, url)
        
        return {
            "id": product_id,
            "name": clean_text(name),
            "brand": brand or self.retailer_name,
            "price": price,
            "currency": self.currency,
            "url": url,
            "image_url": image_url,
            "gender": gender,
            "category": category or categorize_product(name, url),
            "material": material,
            "color": color,
            "sizes": sizes or [],
            "source": self.retailer_id,
            "region": self.region,
            "scraped_at": datetime.now().isoformat()
        }
    
    async def scrape_all(self, genders: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape all products for specified genders
        
        Args:
            genders: List of genders to scrape (default: all)
            
        Returns:
            List of all scraped products
        """
        if genders is None:
            genders = ["men", "women", "kids"]
        
        print(f"\n{'='*50}")
        print(f"Starting {self.retailer_name} scraper ({self.region})")
        print(f"{'='*50}")
        
        try:
            await self.start_browser()
            page = await self.new_page()
            
            for gender in genders:
                print(f"\nScraping {gender}'s products...")
                try:
                    products = await self.scrape_category(gender, page)
                    self.products.extend(products)
                    print(f"  Found {len(products)} 100% cotton products for {gender}")
                except Exception as e:
                    error_msg = f"Error scraping {gender}: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"  {error_msg}")
            
            await page.close()
            
        finally:
            await self.close_browser()
        
        print(f"\nTotal products found: {len(self.products)}")
        if self.errors:
            print(f"Errors encountered: {len(self.errors)}")
        
        return self.products
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get scraping results including products and errors
        
        Returns:
            Dictionary with products and metadata
        """
        return {
            "retailer": self.retailer_name,
            "retailer_id": self.retailer_id,
            "region": self.region,
            "total_products": len(self.products),
            "products": self.products,
            "errors": self.errors,
            "scraped_at": datetime.now().isoformat()
        }
