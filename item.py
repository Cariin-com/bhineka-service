# name, price, sku, images, specs, availability
from typing import List, Dict, Any
class ProductItem:
    def __init__(self, name: str, price: str, sku: str, images: List[str], specs: Dict[str, Any], availability: str, estimate: str = "", store_info: str = "", warranty: str = "", src: str = ""):
        self.name: str = name
        self.price: str = price
        self.sku: str = sku
        self.images: List[str] = images
        self.specs: Dict[str, Any] = specs
        self.availability: str = availability
        self.estimate: str = estimate
        self.store_info: str = store_info
        self.warranty: str = warranty
        self.src: str = src