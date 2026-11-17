from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from src.database import ProductModel, SessionLocal, init_db
from src.logger import logger

def load_products_incrementally(clean_records: List[Dict[str, Any]]) -> Tuple[int, int, int]:
    """
    Loads transformed records into the database with incremental change detection (UPSERT logic).
    Returns (inserted_count, updated_count, unchanged_count).
    
    Logic:
    - Primary key (product_id) not in DB => INSERT
    - Primary key in DB but values (price, stock, title, etc.) changed => UPDATE
    - Primary key in DB and all tracked values match => UNCHANGED (skip)
    """
    init_db()
    session: Session = SessionLocal()

    inserted = 0
    updated = 0
    unchanged = 0

    try:
        # Fetch existing records into a dictionary keyed by product_id
        existing_products = {p.product_id: p for p in session.query(ProductModel).all()}

        for record in clean_records:
            pid = record["product_id"]
            existing = existing_products.get(pid)

            if existing is None:
                # 1. NEW RECORD -> INSERT
                new_item = ProductModel(
                    product_id=record["product_id"],
                    title=record["title"],
                    category=record["category"],
                    price=record["price"],
                    rating=record["rating"],
                    stock=record["stock"],
                    brand=record["brand"],
                    updated_at=record["updated_at"]
                )
                session.add(new_item)
                inserted += 1
            else:
                # 2. CHECK FOR CHANGES
                has_changed = (
                    existing.price != record["price"]
                    or existing.stock != record["stock"]
                    or existing.rating != record["rating"]
                    or existing.title != record["title"]
                    or existing.category != record["category"]
                    or existing.brand != record["brand"]
                )

                if has_changed:
                    # UPDATE EXISTING RECORD
                    existing.title = record["title"]
                    existing.category = record["category"]
                    existing.price = record["price"]
                    existing.rating = record["rating"]
                    existing.stock = record["stock"]
                    existing.brand = record["brand"]
                    existing.updated_at = record["updated_at"]
                    updated += 1
                else:
                    unchanged += 1

        session.commit()
        logger.info(
            f"Database Sync Completed -> Inserted: {inserted}, Updated: {updated}, Unchanged: {unchanged}"
        )
        return inserted, updated, unchanged

    except Exception as exc:
        session.rollback()
        logger.error(f"Database transaction failed: {exc}")
        raise exc
    finally:
        session.close()
