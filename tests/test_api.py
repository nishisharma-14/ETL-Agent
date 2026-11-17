from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Automated ETL API"}

def test_get_products():
    response = client.get("/products?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "product_id" in item
        assert "title" in item
        assert "price" in item

def test_get_product_not_found():
    response = client.get("/products/9999999")
    assert response.status_code == 404
