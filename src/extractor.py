import requests
from typing import List, Dict, Any

API_URL = "https://dummyjson.com/products"

def extract_all_products(limit: int = 30) -> List[Dict[str, Any]]:
    """
    Extract all product records dynamically handling pagination.
    Uses 'total = None' pattern to determine record count on the first request.
    Fails safely on network or HTTP errors.
    """
    all_products: List[Dict[str, Any]] = []
    skip = 0
    total = None

    while total is None or skip < total:
        params = {"skip": skip, "limit": limit}
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Data extraction failed at offset skip={skip}: {exc}") from exc

        total = data.get("total", 0)
        products = data.get("products", [])
        all_products.extend(products)
        skip += limit

    return all_products

if __name__ == "__main__":
    records = extract_all_products()
    print(f"Extracted {len(records)} products from API.")
