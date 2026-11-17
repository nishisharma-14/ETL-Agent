import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from src.database import ProductModel, SessionLocal
from src.pipeline import run_pipeline
from src.dynamic_extractor import extract_from_url
from src.dynamic_transformer import transform_dynamic_products
from src.loader import load_products_incrementally
from src.logger import logger

app = FastAPI(
    title="Automated ETL Data API & Console",
    description="REST API and Industrial Monitoring Console for the Automated ETL Pipeline",
    version="1.0.0"
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    source_url: Optional[str] = None
    total_extracted: int
    total_transformed: int
    inserted: int
    updated: int
    unchanged: int

class IngestUrlRequest(BaseModel):
    url: str
    auth_header: Optional[str] = ""

@app.get("/", include_in_schema=False)
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "ETL API active."}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Automated ETL API"}

@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category (case-insensitive)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    limit: int = Query(500, ge=1, le=1000, description="Page limit"),
    skip: int = Query(0, ge=0, description="Page offset"),
    db: Session = Depends(get_db)
):
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
    product = db.query(ProductModel).filter(ProductModel.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return product

@app.post("/pipeline/run", response_model=PipelineRunResponse, tags=["Pipeline"])
def trigger_pipeline():
    try:
        summary = run_pipeline()
        return summary
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(exc)}")

@app.post("/pipeline/ingest-url", response_model=PipelineRunResponse, tags=["Pipeline"])
def ingest_custom_url(payload: IngestUrlRequest):
    """
    Dynamically extracts data from any user-provided REST API URL,
    cleans & normalizes it, and incrementally loads it into the database.
    """
    url = payload.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Invalid URL. Must begin with http:// or https://")

    try:
        logger.info(f"Initiating on-demand dynamic ingestion from URL: {url}")
        raw_items = extract_from_url(url=url, auth_header=payload.auth_header or "")
        
        if not raw_items:
            raise HTTPException(status_code=400, detail="Endpoint returned 0 records or unsupported JSON schema.")

        cleaned = transform_dynamic_products(raw_items)
        inserted, updated, unchanged = load_products_incrementally(cleaned)

        return {
            "status": "success",
            "source_url": url,
            "total_extracted": len(raw_items),
            "total_transformed": len(cleaned),
            "inserted": inserted,
            "updated": updated,
            "unchanged": unchanged
        }
    except Exception as exc:
        logger.error(f"Dynamic ingestion failed for {url}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
