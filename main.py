from spider import run_spider
from pipeline import save_to_json
import requests
from bs4 import BeautifulSoup

SEARCH_URL = "https://www.bhinneka.com/jual?cari=laptop"


def get_product_links(search_url):
    html = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    product_links = []
    for a in soup.find_all("a", class_="oe_product_image_link"):
        href = a.get("href")
        if href and href.startswith("/"):
            product_links.append("https://www.bhinneka.com" + href)
        elif href:
            product_links.append(href)
    return product_links


def scrape_search_results(search_url, max_products=10):
    links = get_product_links(search_url)
    print(f"Found {len(links)} product links. Scraping up to {max_products}...")
    products = []
    for url in links[:max_products]:
        print(f"Scraping: {url}")
        try:
            product = run_spider(url)
            products.append(product.__dict__)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    return products

if __name__ == "__main__":
    products = scrape_search_results(SEARCH_URL, max_products=10)
    save_to_json(products, filename="products.json")
    print("Scraped and saved successfully.")
