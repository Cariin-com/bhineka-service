from typing import Union, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

from spider import run_spider
from main import scrape_search_results

app = FastAPI(title="Bhineka Scraper API", description="API untuk scraping produk dari Bhineka.com")

class ScrapingRequest(BaseModel):
    search_query: str  # Required parameter, no default value
    max_products: int = 10
    all_pages: bool = False
    max_workers: int = 8

class ProductResponse(BaseModel):
    name: str
    price: str
    sku: str
    images: List[str]
    specs: dict
    availability: str
    estimate: str = ""
    store_info: str = ""
    warranty: str = ""
    src: str = ""

@app.get("/")
def read_root():
    return {
        "message": "Bhineka Scraper API",
        "endpoints": {
            "/scrape": "POST - Scrape products from Bhineka",
            "/products": "GET - Get saved products",
            "/scrape-single": "GET - Scrape single product by URL",
            "/search": "GET - Quick search with query parameter"
        }
    }

@app.post("/scrape", response_model=List[ProductResponse])
async def scrape_products(request: ScrapingRequest):
    """
    Scrape products from Bhineka.com based on search query
    """
    try:
        search_url = f"https://www.bhinneka.com/jual?cari={request.search_query}"
        
        products = scrape_search_results(
            search_url=search_url,
            max_products=request.max_products,
            all_pages=request.all_pages,
            max_workers=request.max_workers
        )
        
        # Save to JSON file
        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/products", response_model=List[ProductResponse])
async def get_products():
    """
    Get saved products from JSON file
    """
    try:
        if not os.path.exists("products.json"):
            return []
        
        with open("products.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load products: {str(e)}")

@app.get("/scrape-single")
async def scrape_single_product(url: str):
    """
    Scrape a single product by URL
    """
    try:
        if not url.startswith("https://www.bhinneka.com"):
            raise HTTPException(status_code=400, detail="URL must be from Bhineka.com")
        
        product = run_spider(url)
        return product.__dict__
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape product: {str(e)}")

@app.get("/search")
async def search_products(query: str, limit: int = 10):
    """
    Quick search endpoint with query parameter
    """
    try:
        search_url = f"https://www.bhinneka.com/jual?cari={query}"
        products = scrape_search_results(
            search_url=search_url,
            max_products=limit,
            all_pages=False,
            max_workers=4
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")