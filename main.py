#!/usr/bin/env python3
"""
100% Cotton Clothing Scraper
Main entry point for scraping multiple retailers across regions

Usage:
    python main.py                    # Scrape all retailers, all genders, UK region
    python main.py --region USA       # Scrape USA retailers
    python main.py --retailer hm      # Scrape only H&M
    python main.py --gender men women # Scrape only men's and women's products
"""

import asyncio
import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from config import REGIONS, RETAILERS
from scrapers import create_scraper
from utils.helpers import (
    save_products_json,
    merge_products,
    format_product_summary
)


async def scrape_retailer(
    retailer: str,
    region: str,
    genders: List[str]
) -> List[Dict[str, Any]]:
    """
    Scrape a single retailer
    
    Args:
        retailer: Retailer key
        region: Region code
        genders: List of genders to scrape
        
    Returns:
        List of scraped products
    """
    try:
        scraper = create_scraper(retailer, region)
        products = await scraper.scrape_all(genders=genders)
        return products
    except Exception as e:
        print(f"Error scraping {retailer}: {str(e)}")
        return []


async def scrape_region(
    region: str,
    retailers: List[str] = None,
    genders: List[str] = None,
    concurrent: bool = False
) -> List[Dict[str, Any]]:
    """
    Scrape all retailers for a region

    Args:
        region: Region code (UK, USA)
        retailers: List of retailers to scrape (None = all)
        genders: List of genders to scrape (None = all)
        concurrent: Whether to scrape retailers concurrently (default: False)

    Returns:
        List of all scraped products
    """
    region_config = REGIONS.get(region)
    if not region_config:
        print(f"Unknown region: {region}")
        return []

    if retailers is None:
        retailers = region_config["retailers"]

    if genders is None:
        genders = ["men", "women", "kids"]

    # Filter retailers to only those available in the region
    available_retailers = []
    for r in retailers:
        if r in RETAILERS:
            retailer_urls = RETAILERS[r].get("base_urls", {})
            if region in retailer_urls:
                available_retailers.append(r)
            else:
                print(f"Skipping {r} - not available in {region}")

    all_products = []

    print(f"\n{'#'*60}")
    print(f"# Scraping {region} Region")
    print(f"# Retailers: {', '.join(available_retailers)}")
    print(f"# Genders: {', '.join(genders)}")
    print(f"# Mode: {'Concurrent' if concurrent else 'Sequential'}")
    print(f"{'#'*60}")

    if concurrent and len(available_retailers) > 1:
        # Scrape all retailers concurrently
        print(f"\nScraping {len(available_retailers)} retailers in parallel...")

        tasks = [
            scrape_retailer(retailer, region, genders)
            for retailer in available_retailers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for retailer, result in zip(available_retailers, results):
            if isinstance(result, Exception):
                print(f"\nError scraping {retailer}: {str(result)}")
                continue

            products = result
            all_products.extend(products)

            # Save intermediate results
            if products:
                filename = f"{retailer}_{region.lower()}_{datetime.now().strftime('%Y%m%d')}.json"
                save_products_json(products, filename)
                print(f"\nSaved {len(products)} products from {retailer} to data/{filename}")
    else:
        # Sequential scraping (original behavior)
        for retailer in available_retailers:
            products = await scrape_retailer(retailer, region, genders)
            all_products.extend(products)

            # Save intermediate results
            if products:
                filename = f"{retailer}_{region.lower()}_{datetime.now().strftime('%Y%m%d')}.json"
                save_products_json(products, filename)
                print(f"Saved {len(products)} products to data/{filename}")

    return all_products


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Scrape 100% cotton clothing from multiple retailers'
    )
    
    parser.add_argument(
        '--region', '-r',
        choices=['UK', 'USA', 'ALL'],
        default='UK',
        help='Region to scrape (default: UK)'
    )
    
    parser.add_argument(
        '--retailer', '-s',
        nargs='+',
        choices=list(RETAILERS.keys()),
        help='Specific retailer(s) to scrape'
    )
    
    parser.add_argument(
        '--gender', '-g',
        nargs='+',
        choices=['men', 'women', 'kids'],
        help='Gender categories to scrape'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='all_products.json',
        help='Output filename for combined results'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode (fewer products)'
    )

    parser.add_argument(
        '--concurrent',
        action='store_true',
        help='Scrape multiple retailers concurrently (faster but more resource intensive)'
    )

    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  100% COTTON CLOTHING SCRAPER")
    print("  Finding pure cotton products for you!")
    print("="*60)
    
    all_products = []
    
    regions_to_scrape = ['UK', 'USA'] if args.region == 'ALL' else [args.region]
    
    for region in regions_to_scrape:
        products = await scrape_region(
            region=region,
            retailers=args.retailer,
            genders=args.gender,
            concurrent=args.concurrent
        )
        all_products.extend(products)
    
    # Save combined results
    if all_products:
        filepath = save_products_json(all_products, args.output)
        print(f"\n✓ Saved all {len(all_products)} products to {filepath}")
    
    # Print summary
    print(format_product_summary(all_products))
    
    return all_products


def run_demo():
    """Run a quick demo scrape"""
    print("\n" + "="*60)
    print("  DEMO MODE - Quick test scrape")
    print("="*60)
    
    async def demo():
        # Quick demo with just H&M UK, men's products
        products = await scrape_retailer("hm", "UK", ["men"])
        
        if products:
            print("\n✓ Demo completed!")
            print(f"  Found {len(products)} 100% cotton products")
            print("\nSample products:")
            for p in products[:5]:
                print(f"  • {p['name']}")
                print(f"    Price: {p['currency_symbol'] if 'currency_symbol' in p else '£'}{p['price']}")
                print(f"    URL: {p['url'][:60]}...")
                print()
        else:
            print("\n⚠ No products found in demo")
            print("  This might be due to website changes or rate limiting")
        
        return products
    
    return asyncio.run(demo())


if __name__ == "__main__":
    import sys
    
    if '--demo' in sys.argv:
        run_demo()
    else:
        asyncio.run(main())
