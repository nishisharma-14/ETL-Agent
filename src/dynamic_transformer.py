import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

def clean_record_generic(raw: Dict[str, Any], fallback_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    Intelligently extracts and maps fields from any unknown API payload
    into our clean database schema:
    - ID (mapped from id, uuid, code, symbol, or generated hash)
    - Title (mapped from title, name, product_name, designation, headline)
    - Category (mapped from category, type, department, genre)
    - Price (mapped from price, current_price, rate, cost, amount)
    - Rating (mapped from rating, score, stars, rank)
    - Stock (mapped from stock, quantity, volume, count)
    - Brand (mapped from brand, company, symbol, source, provider)
    """
    if not isinstance(raw, dict):
        return None

    # 1. Resolve ID
    raw_id = raw.get("id") or raw.get("uuid") or raw.get("code") or raw.get("symbol") or raw.get("key")
    if raw_id is not None:
        try:
            product_id = int(raw_id)
        except (ValueError, TypeError):
            # If string ID (e.g., 'bitcoin' or 'uuid-123'), compute deterministic positive int hash
            product_id = int(hashlib.md5(str(raw_id).encode("utf-8")).hexdigest()[:7], 16)
    else:
        product_id = fallback_id

    # 2. Resolve Title / Name
    title = (
        raw.get("title") or
        raw.get("name") or
        raw.get("product_name") or
        raw.get("headline") or
        raw.get("label") or
        f"Item #{product_id}"
    )
    title = str(title).strip()[:250]

    # 3. Resolve Category
    category = (
        raw.get("category") or
        raw.get("type") or
        raw.get("department") or
        raw.get("genre") or
        "general"
    )
    if isinstance(category, dict):
        category = category.get("name") or "general"
    category = str(category).strip().lower()[:95]

    # 4. Resolve Price
    price = 0.0
    for key in ["price", "current_price", "rate", "cost", "amount", "value"]:
        val = raw.get(key)
        if val is not None:
            try:
                price = round(float(val), 2)
                break
            except (ValueError, TypeError):
                continue

    # 5. Resolve Rating
    rating = 0.0
    for key in ["rating", "score", "stars", "rank"]:
        val = raw.get(key)
        if val is not None:
            try:
                if isinstance(val, dict): # E.g. {"rate": 4.5, "count": 120}
                    val = val.get("rate") or val.get("score")
                rating = round(float(val), 2)
                break
            except (ValueError, TypeError):
                continue

    # 6. Resolve Stock / Quantity
    stock = 0
    for key in ["stock", "quantity", "inventory", "total_volume", "count"]:
        val = raw.get(key)
        if val is not None:
            try:
                stock = int(float(val))
                break
            except (ValueError, TypeError):
                continue

    # 7. Resolve Brand / Provider
    brand = (
        raw.get("brand") or
        raw.get("company") or
        raw.get("symbol") or
        raw.get("source") or
        raw.get("provider") or
        "Generic"
    )
    if isinstance(brand, dict):
        brand = brand.get("name") or "Generic"
    brand = str(brand).strip()[:95]

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

def transform_dynamic_products(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transforms dynamically fetched items into clean unique records."""
    cleaned: List[Dict[str, Any]] = []
    seen_ids = set()

    for idx, item in enumerate(raw_items, start=1):
        record = clean_record_generic(item, fallback_id=idx)
        if record and record["product_id"] not in seen_ids:
            seen_ids.add(record["product_id"])
            cleaned.append(record)

    return cleaned
