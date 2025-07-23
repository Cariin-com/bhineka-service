from spider import run_spider
from pipeline import save_to_json
import requests
from bs4 import BeautifulSoup
from paginate import get_total_pages_from_soup
import concurrent.futures

SEARCH_URL = "https://www.bhinneka.com/jual?cari=laptop"

def get_product_links_from_soup(soup):
    product_links = []
    for a in soup.find_all("a", class_="oe_product_image_link"):
        href = a.get("href")
        if href and href.startswith("/"):
            product_links.append("https://www.bhinneka.com" + href)
        elif href:
            product_links.append(href)
    return product_links

def scrape_all_pages(search_url, max_products_per_page=None):
    html = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    total_pages = get_total_pages_from_soup(soup)
    print(f"Total pages found: {total_pages}")

    all_links = get_product_links_from_soup(soup)
    if max_products_per_page:
        all_links = all_links[:max_products_per_page]

    for page in range(2, total_pages + 1):
        page_url = f"https://www.bhinneka.com/jual?page={page}&cari=laptop"
        print(f"Scraping page {page}: {page_url}")
        html = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        links = get_product_links_from_soup(soup)
        if max_products_per_page:
            links = links[:max_products_per_page]
        all_links.extend(links)
    print(f"Total product links collected: {len(all_links)}")
    return all_links

def scrape_search_results(search_url, max_products=10, all_pages=False, max_workers=8):
    if all_pages:
        links = scrape_all_pages(search_url)
    else:
        html = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        links = get_product_links_from_soup(soup)
    print(f"Found {len(links)} product links. Scraping up to {max_products if not all_pages else len(links)}...")

    products = []

    def scrape_url(url):
        print(f"Scraping: {url}")
        try:
            product = run_spider(url)
            return product.__dict__
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(scrape_url, links[:max_products] if not all_pages else links)
        for result in results:
            if result:
                products.append(result)
    return products

if __name__ == "__main__":
    # Set all_pages=True to scrape all pages
    products = scrape_search_results(SEARCH_URL, all_pages=True)
    save_to_json(products, filename="products.json")
    print("Scraped and saved successfully.")
