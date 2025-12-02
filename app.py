#!/usr/bin/env python3
"""
Flask Web Application for 100% Cotton Clothing Scraper
Provides a web interface for scraping and viewing products
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
from threading import Thread
import queue

from config import REGIONS, RETAILERS
from scrapers import create_scraper
from utils.helpers import save_products_json, format_product_summary

app = Flask(__name__)
CORS(app)

# Global state for scraping status
scraping_status = {
    "is_scraping": False,
    "current_retailer": None,
    "progress": 0,
    "total_products": 0,
    "errors": [],
    "log": []
}

# Queue for progress updates
progress_queue = queue.Queue()


def log_message(message):
    """Add a log message to the status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    scraping_status["log"].append(log_entry)
    progress_queue.put({"type": "log", "message": log_entry})
    print(log_entry)


async def scrape_async(region, retailers, genders):
    """Run scraping asynchronously"""
    scraping_status["is_scraping"] = True
    scraping_status["log"] = []
    scraping_status["errors"] = []
    all_products = []

    log_message(f"Starting scrape for {region} region")
    log_message(f"Retailers: {', '.join(retailers)}")
    log_message(f"Genders: {', '.join(genders)}")

    total_retailers = len(retailers)

    for idx, retailer in enumerate(retailers):
        if not scraping_status["is_scraping"]:
            log_message("Scraping stopped by user")
            break

        scraping_status["current_retailer"] = retailer
        scraping_status["progress"] = int((idx / total_retailers) * 100)

        log_message(f"Scraping {retailer}...")

        try:
            scraper = create_scraper(retailer, region)
            products = await scraper.scrape_all(genders=genders)
            all_products.extend(products)

            log_message(f"Found {len(products)} products from {retailer}")

            # Save intermediate results
            if products:
                filename = f"{retailer}_{region.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                save_products_json(products, filename)

        except Exception as e:
            error_msg = f"Error scraping {retailer}: {str(e)}"
            scraping_status["errors"].append(error_msg)
            log_message(error_msg)

    # Save combined results
    if all_products:
        filename = f"all_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = save_products_json(all_products, filename)
        log_message(f"Saved {len(all_products)} total products to {filename}")

    scraping_status["is_scraping"] = False
    scraping_status["progress"] = 100
    scraping_status["total_products"] = len(all_products)
    scraping_status["current_retailer"] = None

    log_message("Scraping complete!")

    return all_products


def run_scraping(region, retailers, genders):
    """Run scraping in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(scrape_async(region, retailers, genders))
    loop.close()
    return result


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/config')
def get_config():
    """Get configuration (regions and retailers)"""
    return jsonify({
        "regions": REGIONS,
        "retailers": {k: v["name"] for k, v in RETAILERS.items()}
    })


@app.route('/api/retailers/<region>')
def get_retailers_for_region(region):
    """Get available retailers for a region"""
    if region not in REGIONS:
        return jsonify({"error": "Invalid region"}), 400

    available_retailers = []
    for retailer_key in REGIONS[region]["retailers"]:
        if retailer_key in RETAILERS:
            retailer = RETAILERS[retailer_key]
            if region in retailer.get("base_urls", {}):
                available_retailers.append({
                    "key": retailer_key,
                    "name": retailer["name"]
                })

    return jsonify(available_retailers)


@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """Start a new scraping job"""
    if scraping_status["is_scraping"]:
        return jsonify({"error": "Scraping already in progress"}), 400

    data = request.json
    region = data.get('region', 'UK')
    retailers = data.get('retailers', [])
    genders = data.get('genders', ['men', 'women', 'kids'])

    if not retailers:
        retailers = REGIONS[region]["retailers"]

    # Start scraping in a background thread
    thread = Thread(target=run_scraping, args=(region, retailers, genders))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started"})


@app.route('/api/stop', methods=['POST'])
def stop_scrape():
    """Stop the current scraping job"""
    scraping_status["is_scraping"] = False
    log_message("Stop requested by user")
    return jsonify({"status": "stopping"})


@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)


@app.route('/api/products')
def get_products():
    """Get all scraped products"""
    data_dir = "data"
    all_products = []

    if not os.path.exists(data_dir):
        return jsonify([])

    # Get all JSON files
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]

    # Load the most recent file
    if json_files:
        json_files.sort(reverse=True)
        latest_file = os.path.join(data_dir, json_files[0])

        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
                all_products = data.get('products', [])
        except:
            pass

    return jsonify(all_products)


@app.route('/api/products/files')
def get_product_files():
    """Get list of all product JSON files"""
    data_dir = "data"
    files = []

    if not os.path.exists(data_dir):
        return jsonify([])

    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    json_files.sort(reverse=True)

    for filename in json_files:
        filepath = os.path.join(data_dir, filename)
        stat = os.stat(filepath)

        files.append({
            "name": filename,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })

    return jsonify(files)


@app.route('/api/products/file/<filename>')
def get_product_file(filename):
    """Get products from a specific file"""
    filepath = os.path.join("data", filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return jsonify(data.get('products', []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download a product file"""
    filepath = os.path.join("data", filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    return send_file(filepath, as_attachment=True)


@app.route('/api/stream')
def stream():
    """Server-Sent Events endpoint for real-time updates"""
    def generate():
        while True:
            try:
                # Get update from queue (timeout after 30 seconds)
                update = progress_queue.get(timeout=30)
                yield f"data: {json.dumps(update)}\n\n"
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    print("\n" + "="*60)
    print("  100% COTTON CLOTHING SCRAPER - Web Interface")
    print("="*60)
    print("\n  Server starting at: http://localhost:5000")
    print("\n  Press Ctrl+C to stop\n")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
