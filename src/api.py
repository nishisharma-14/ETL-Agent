import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from src.database import ProductModel, SessionLocal
from src.pipeline import run_pipeline

app = FastAPI(
    title="Automated ETL Data API & Console",
    description="REST API and Industrial Monitoring Console for the Automated ETL Pipeline",
    version="1.0.0"
)

# Static files path
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Dependency to provide database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas for response validation
class ProductResponse(BaseModel):
    product_id: int
    title: str
    category: str
    price: float
    rating: float
    stock: int
    brand: Optional[str]
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

class PipelineRunResponse(BaseModel):
    status: str
    total_extracted: int
    total_transformed: int
    inserted: int
    updated: int
    unchanged: int

@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serves the industrial dashboard user interface."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "ETL API active. Dashboard frontend files not found."}

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify API and service availability."""
    return {"status": "ok", "service": "Automated ETL API"}

@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category (case-insensitive)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    limit: int = Query(200, ge=1, le=500, description="Page limit"),
    skip: int = Query(0, ge=0, description="Page offset"),
    db: Session = Depends(get_db)
):
    """Fetch paginated, filtered products from the database."""
    query = db.query(ProductModel)

    if category:
        query = query.filter(ProductModel.category == category.lower())
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)

    return query.offset(skip).limit(limit).all()

@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a single product by its primary ID."""
    product = db.query(ProductModel).filter(ProductModel.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return product

@app.post("/pipeline/run", response_model=PipelineRunResponse, tags=["Pipeline"])
def trigger_pipeline():
    """Triggers the full ETL pipeline on-demand and returns execution statistics."""
    try:
        summary = run_pipeline()
        return summary
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(exc)}")
