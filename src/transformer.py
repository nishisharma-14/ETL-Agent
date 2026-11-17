from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

def clean_record(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cleans and standardizes a single raw product record from the API.
    Returns None if required fields (like id) are invalid or missing.
    """
    raw_id = raw.get("id")
    if raw_id is None:
        return None

    try:
        product_id = int(raw_id)
        title = str(raw.get("title", "")).strip()
        category = str(raw.get("category", "uncategorized")).strip().lower()
        price = round(float(raw.get("price", 0.0)), 2)
        rating = round(float(raw.get("rating", 0.0)), 2)
        stock = int(raw.get("stock", 0))
        brand = str(raw.get("brand") or "Generic").strip()
        
        # Include UTC timestamp when this record was processed
        updated_at = datetime.now(timezone.utc).isoformat()

        return {
            "product_id": product_id,
            "title": title,
            "category": category,
            "price": price,
            "rating": rating,
            "stock": stock,
            "brand": brand,
            "updated_at": updated_at
        }
    except (ValueError, TypeError):
        return None

def transform_products(raw_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms a batch of raw API product dictionaries into clean, validated records.
    Filters out duplicates and corrupt items.
    """
    cleaned: List[Dict[str, Any]] = []
    seen_ids = set()

    for item in raw_products:
        record = clean_record(item)
        if record and record["product_id"] not in seen_ids:
            seen_ids.add(record["product_id"])
            cleaned.append(record)

    return cleaned

if __name__ == "__main__":
    sample_raw = [
        {"id": 1, "title": " Test Item ", "category": "Beauty", "price": 9.99, "rating": 4.5, "stock": 10, "brand": None},
        {"id": 1, "title": "Duplicate Item"}, # Duplicate test
        {"id": "bad", "title": "Corrupt Item"}, # Invalid ID test
    ]
    result = transform_products(sample_raw)
    print("Transformed sample records:", result)
