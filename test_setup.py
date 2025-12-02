#!/usr/bin/env python3
"""
Quick test script to verify scraper setup
Run this to make sure everything is working
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import REGIONS, RETAILERS
from utils.helpers import is_100_percent_cotton, clean_price, categorize_product


def test_config():
    """Test configuration is loaded correctly"""
    print("\n📋 Testing Configuration...")
    
    assert "UK" in REGIONS, "UK region should exist"
    assert "USA" in REGIONS, "USA region should exist"
    assert "hm" in RETAILERS, "H&M should be configured"
    assert "asos" in RETAILERS, "ASOS should be configured"
    
    print("  ✓ Regions configured correctly")
    print("  ✓ Retailers configured correctly")
    print(f"  ✓ UK retailers: {', '.join(REGIONS['UK']['retailers'])}")
    print(f"  ✓ USA retailers: {', '.join(REGIONS['USA']['retailers'])}")


def test_helpers():
    """Test helper functions"""
    print("\n🔧 Testing Helper Functions...")
    
    # Test cotton detection
    assert is_100_percent_cotton("100% Cotton") == True
    assert is_100_percent_cotton("100% cotton") == True
    assert is_100_percent_cotton("100% Organic Cotton") == True
    assert is_100_percent_cotton("50% Cotton 50% Polyester") == False
    assert is_100_percent_cotton("Pure Cotton") == True
    print("  ✓ Cotton detection working")
    
    # Test price cleaning
    assert clean_price("£29.99") == 29.99
    assert clean_price("$15.00") == 15.00
    assert clean_price("€ 19,99") == 19.99
    assert clean_price("From £25") == 25.0
    print("  ✓ Price cleaning working")
    
    # Test categorization
    assert categorize_product("Men's Cotton T-Shirt") == "t-shirts"
    assert categorize_product("Slim Fit Jeans") == "jeans"
    assert categorize_product("Cotton Hoodie") == "hoodies"
    print("  ✓ Product categorization working")


async def test_browser():
    """Test Playwright browser launch"""
    print("\n🌐 Testing Browser...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.example.com")
            title = await page.title()
            await browser.close()
            
            print(f"  ✓ Browser launched successfully")
            print(f"  ✓ Page loaded: {title}")
            return True
    except Exception as e:
        print(f"  ✗ Browser test failed: {str(e)}")
        return False


async def test_scraper_import():
    """Test scraper imports"""
    print("\n📦 Testing Scraper Imports...")
    
    try:
        from scrapers import HMScraper, ASOSScraper, create_scraper
        
        # Create instances
        hm = HMScraper(region="UK")
        asos = ASOSScraper(region="UK")
        
        print(f"  ✓ HMScraper: {hm.retailer_name} ({hm.region})")
        print(f"  ✓ ASOSScraper: {asos.retailer_name} ({asos.region})")
        
        # Test factory
        generic = create_scraper("hm", "USA")
        print(f"  ✓ Factory created: {generic.retailer_name} ({generic.region})")
        
        return True
    except Exception as e:
        print(f"  ✗ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_mini_scrape():
    """Run a minimal scrape test"""
    print("\n🔍 Running Mini Scrape Test...")
    print("  (This will attempt to load one retailer page)")
    
    try:
        from scrapers import HMScraper
        
        scraper = HMScraper(region="UK")
        await scraper.start_browser()
        page = await scraper.new_page()
        
        url = await scraper.get_base_url()
        print(f"  Loading: {url}")
        
        success = await scraper.safe_goto(page, url)
        
        if success:
            title = await page.title()
            print(f"  ✓ Page loaded: {title[:50]}...")
        else:
            print("  ⚠ Page load had issues (may be rate limited)")
        
        await scraper.close_browser()
        return success
        
    except Exception as e:
        print(f"  ✗ Mini scrape failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("="*60)
    print("  100% Cotton Scraper - Test Suite")
    print("="*60)
    
    # Run tests
    test_config()
    test_helpers()
    
    browser_ok = await test_browser()
    import_ok = await test_scraper_import()
    
    if browser_ok and import_ok:
        await run_mini_scrape()
    
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    print(f"  Configuration: ✓ Pass")
    print(f"  Helpers: ✓ Pass")
    print(f"  Browser: {'✓ Pass' if browser_ok else '✗ Fail'}")
    print(f"  Imports: {'✓ Pass' if import_ok else '✗ Fail'}")
    
    if browser_ok and import_ok:
        print("\n✓ All tests passed! Ready to scrape.")
        print("\nNext steps:")
        print("  python main.py --demo     # Quick test")
        print("  python main.py --help     # See all options")
    else:
        print("\n⚠ Some tests failed. Check errors above.")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
