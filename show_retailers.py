#!/usr/bin/env python3
"""
Show all configured retailers and their availability by region
"""

from config import RETAILERS, REGIONS


def show_retailers():
    """Display all configured retailers"""
    print("\n" + "="*70)
    print("  CONFIGURED RETAILERS")
    print("="*70)

    # Group by region
    for region, region_config in REGIONS.items():
        print(f"\n{region} Region ({region_config['currency_symbol']} {region_config['currency']})")
        print("-" * 70)

        available_retailers = region_config.get('retailers', [])

        for retailer_key in available_retailers:
            if retailer_key in RETAILERS:
                retailer = RETAILERS[retailer_key]
                name = retailer.get('name', retailer_key)
                urls = retailer.get('base_urls', {})
                has_region = region in urls

                status = "✓" if has_region else "✗"
                url = urls.get(region, "N/A")

                print(f"  {status} {name:20s} - {url}")

    print("\n" + "="*70)
    print(f"Total retailers: {len(RETAILERS)}")
    print(f"UK retailers: {len([r for r in REGIONS['UK']['retailers'] if r in RETAILERS])}")
    print(f"USA retailers: {len([r for r in REGIONS['USA']['retailers'] if r in RETAILERS])}")
    print("="*70 + "\n")


def show_retailer_details(retailer_key: str):
    """Show details for a specific retailer"""
    if retailer_key not in RETAILERS:
        print(f"Retailer '{retailer_key}' not found")
        return

    retailer = RETAILERS[retailer_key]

    print(f"\n{retailer['name']}")
    print("-" * 40)
    print(f"Key: {retailer_key}")
    print(f"\nURLs:")
    for region, url in retailer.get('base_urls', {}).items():
        print(f"  {region}: {url}")

    print(f"\nSearch Paths:")
    for gender, path in retailer.get('search_paths', {}).items():
        print(f"  {gender}: {path}")

    print(f"\nMaterial Filter Support: {retailer.get('supports_material_filter', False)}")
    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Show details for specific retailer
        show_retailer_details(sys.argv[1])
    else:
        # Show all retailers
        show_retailers()
