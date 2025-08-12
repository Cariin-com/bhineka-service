from fetcher import fetch_html
from parser import parse_product_page
from item import ProductItem

def run_spider(url):
    soup = fetch_html(url)
    raw_data = parse_product_page(soup)

    item = ProductItem(
        name=raw_data["name"],
        price=raw_data["price"],
        sku=raw_data["sku"],
        images=raw_data["images"],
        specs=raw_data["specs"],
        availability=raw_data["availability"],
        estimate=raw_data.get("estimate", ""),
        store_info=raw_data.get("store_info", ""),
        warranty=raw_data.get("warranty", ""),
        src=url  # URL sumber scraping
    )

    return item
