import pytest
from src.transformer import clean_record, transform_products

def test_clean_record_valid():
    raw = {
        "id": 10,
        "title": "  Mechanical Keyboard  ",
        "category": "Electronics",
        "price": 99.99,
        "rating": 4.8,
        "stock": 25,
        "brand": "Keychron"
    }
    cleaned = clean_record(raw)
    assert cleaned is not None
    assert cleaned["product_id"] == 10
    assert cleaned["title"] == "Mechanical Keyboard"
    assert cleaned["category"] == "electronics"
    assert cleaned["price"] == 99.99
    assert cleaned["stock"] == 25
    assert cleaned["brand"] == "Keychron"

def test_clean_record_missing_id():
    raw = {"title": "No ID Item", "price": 10.0}
    assert clean_record(raw) is None

def test_clean_record_corrupt_id():
    raw = {"id": "invalid_id_type", "title": "Item"}
    assert clean_record(raw) is None

def test_transform_products_removes_duplicates():
    raw_list = [
        {"id": 1, "title": "Item 1", "price": 10.0},
        {"id": 1, "title": "Item 1 Duplicate", "price": 10.0},
        {"id": 2, "title": "Item 2", "price": 20.0},
    ]
    cleaned = transform_products(raw_list)
    assert len(cleaned) == 2
    assert [c["product_id"] for c in cleaned] == [1, 2]
