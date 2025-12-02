"""
ASOS Scraper - Works for UK and USA
Scrapes 100% cotton products from ASOS website
ASOS has a material filter which makes it easier to find cotton products
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


class ASOSScraper(BaseScraper):
    """
    Scraper for ASOS website
    ASOS is particularly good because they have material composition filters
    """
    
    @property
    def retailer_name(self) -> str:
        return "ASOS"
    
    @property
    def retailer_id(self) -> str:
        return "asos"
    
    async def get_base_url(self) -> str:
        """Get base URL for current region"""
        urls = RETAILERS["asos"]["base_urls"]
        return urls.get(self.region, urls["UK"])
    
    async def scrape_category(self, gender: str, page: Page) -> List[Dict[str, Any]]:
        """
        Scrape products from ASOS category page
        ASOS supports filtering by 100% cotton composition
        """
        products = []
        base_url = await self.get_base_url()
        
        # ASOS category IDs and cotton filter
        # Note: ASOS uses category IDs, we'll search with cotton filter
        gender_searches = {
            "men": f"{base_url}/men/t-shirts-vests/cat/?cid=7616&refine=attribute_10992:100%25+Cotton",
            "women": f"{base_url}/women/tops/cat/?cid=4169&refine=attribute_10992:100%25+Cotton",
            "kids": f"{base_url}/search/?q=100%25+cotton+kids"
        }
        
        # Also try generic search
        search_url = f"{base_url}/search/?q=100%25+cotton+{gender}"
        
        urls_to_try = [gender_searches.get(gender, search_url)]
        
        for category_url in urls_to_try:
            print(f"  Loading {category_url[:80]}...")
            
            if not await self.safe_goto(page, category_url):
                continue
            
            # Wait for products to load
            try:
                await page.wait_for_selector('[data-auto-id="productTile"], article[data-auto-id]', timeout=15000)
            except:
                try:
                    await page.wait_for_selector('.product-card, .productTile', timeout=10000)
                except:
                    print(f"  Could not find product listings")
                    continue
            
            # Scroll to load more
            await self.scroll_page(page, scrolls=3)
            
            # Get product data from page
            page_products = await self.extract_products_from_page(page, gender)
            
            print(f"  Found {len(page_products)} products on listing page")
            
            # Verify each product's material composition
            for i, product_data in enumerate(page_products[:20]):  # Limit for demo
                print(f"  Verifying product {i+1}/{min(len(page_products), 20)}...", end='\r')
                
                verified_product = await self.verify_product_material(
                    product_data, page, gender
                )
                
                if verified_product:
                    products.append(verified_product)
                
                await self.random_delay()
            
            print(f"  Completed verification")
        
        return products
    
    async def scroll_page(self, page: Page, scrolls: int = 3):
        """Scroll page to load more products"""
        for i in range(scrolls):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
    
    async def extract_products_from_page(self, page: Page, gender: str) -> List[Dict]:
        """Extract basic product info from listing page"""
        products = []
        
        # Try to extract from ASOS's JSON data if available
        try:
            # ASOS often embeds product data in script tags
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                content = await script.inner_text()
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product':
                                products.append({
                                    'name': item.get('name', ''),
                                    'url': item.get('url', ''),
                                    'image_url': item.get('image', ''),
                                    'price': clean_price(str(item.get('offers', {}).get('price', '')))
                                })
                except:
                    continue
        except:
            pass
        
        # If no JSON data, extract from DOM
        if not products:
            product_cards = await page.query_selector_all('[data-auto-id="productTile"], article, .product-card')
            
            for card in product_cards:
                try:
                    # Get link
                    link_elem = await card.query_selector('a[href*="/prd/"], a[href*="/product/"]')
                    if not link_elem:
                        link_elem = await card.query_selector('a')
                    
                    url = await link_elem.get_attribute('href') if link_elem else ""
                    if url and not url.startswith('http'):
                        url = f"https://www.asos.com{url}"
                    
                    # Get name
                    name_elem = await card.query_selector('h3, h2, [data-auto-id="productTitle"], .product-name')
                    name = await name_elem.inner_text() if name_elem else ""
                    
                    # Get price
                    price_elem = await card.query_selector('[data-auto-id="productPrice"], .price, span[data-price]')
                    price_text = await price_elem.inner_text() if price_elem else ""
                    
                    # Get image
                    img_elem = await card.query_selector('img')
                    image_url = await img_elem.get_attribute('src') if img_elem else ""
                    
                    if url and name:
                        products.append({
                            'name': clean_text(name),
                            'url': url,
                            'image_url': image_url,
                            'price': clean_price(price_text)
                        })
                        
                except Exception as e:
                    continue
        
        return products
    
    async def verify_product_material(self, product_data: Dict, page: Page, gender: str) -> Optional[Dict[str, Any]]:
        """
        Verify product is 100% cotton by checking product page
        """
        product_url = product_data.get('url', '')
        
        if not product_url:
            return None
        
        if not await self.safe_goto(page, product_url):
            return None
        
        try:
            await page.wait_for_selector('#product-details, .product-details', timeout=8000)
            
            # Get material composition
            material = await self.get_material_composition(page)
            
            if not material or not is_100_percent_cotton(material):
                return None
            
            # Get updated product details from product page
            name = product_data.get('name', '')
            if not name:
                name_elem = await page.query_selector('h1')
                name = await name_elem.inner_text() if name_elem else ""
            
            price = product_data.get('price')
            if not price:
                price_elem = await page.query_selector('[data-id="current-price"], .current-price')
                price_text = await price_elem.inner_text() if price_elem else ""
                price = clean_price(price_text)
            
            image_url = product_data.get('image_url', '')
            if not image_url:
                img_elem = await page.query_selector('.gallery-image img, #product-images img')
                image_url = await img_elem.get_attribute('src') if img_elem else ""
            
            # Get color
            color_elem = await page.query_selector('[data-id="colour-value"], .selected-colour')
            color = await color_elem.inner_text() if color_elem else None
            
            # Get sizes
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
            self.errors.append(f"Error verifying {product_url}: {str(e)}")
        
        return None
    
    async def get_product_details(self, product_url: str, page: Page, gender: str = "men") -> Optional[Dict[str, Any]]:
        """
        Get detailed product information
        """
        return await self.verify_product_material({'url': product_url}, page, gender)
    
    async def get_material_composition(self, page: Page) -> str:
        """Extract material composition from product page"""
        # ASOS puts composition in product details section
        selectors = [
            '[data-test-id="product-details-composition"]',
            '.product-details-composition',
            '#productDescription',
            '.product-description',
            'div:has-text("Composition")',
            'div:has-text("Material")',
            '[class*="composition"]',
            '[class*="material"]'
        ]
        
        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if 'cotton' in text.lower():
                        return text
            except:
                continue
        
        # Try expanding product details
        try:
            details_btn = await page.query_selector('button[aria-label*="detail"], button:has-text("Product Details")')
            if details_btn:
                await details_btn.click()
                await asyncio.sleep(0.5)
        except:
            pass
        
        # Get full page content and search for composition
        try:
            content = await page.content()
            # Look for composition patterns
            patterns = [
                r'composition[:\s]*(.*?cotton.*?)(?:<|$)',
                r'material[:\s]*(.*?cotton.*?)(?:<|$)',
                r'100%\s*cotton',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content.lower())
                if match:
                    return match.group(0) if '100%' in pattern else match.group(1)
        except:
            pass
        
        return ""
    
    async def get_available_sizes(self, page: Page) -> List[str]:
        """Extract available sizes from product page"""
        sizes = []
        
        try:
            # ASOS size selector
            size_elems = await page.query_selector_all('[data-id="size-selector"] option, .size-option:not([disabled])')
            
            for elem in size_elems:
                size_text = await elem.inner_text()
                if size_text and 'select' not in size_text.lower():
                    sizes.append(clean_text(size_text))
        except:
            pass
        
        return sizes


# For testing
if __name__ == "__main__":
    async def test():
        scraper = ASOSScraper(region="UK")
        products = await scraper.scrape_all(genders=["men"])
        print(f"\nFound {len(products)} products")
        for p in products[:5]:
            print(f"  - {p['name']}: {p['price']} {p['currency']}")
    
    asyncio.run(test())
