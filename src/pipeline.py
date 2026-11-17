from typing import Dict, Any
from src.extractor import extract_all_products
from src.transformer import transform_products
from src.loader import load_products_incrementally
from src.logger import logger
from src.config import settings

def run_pipeline() -> Dict[str, Any]:
    """
    Orchestrates the entire Automated ETL pipeline:
    1. Extract raw records from the API with pagination and error handling
    2. Transform and validate the raw data into clean records
    3. Load data incrementally into the database with change detection
    """
    logger.info("==========================================")
    logger.info("Starting Automated ETL Pipeline Execution")
    logger.info("==========================================")

    # 1. Extraction Phase
    logger.info(f"Extracting products from API endpoint: {settings.API_URL}")
    raw_products = extract_all_products(limit=settings.API_PAGE_LIMIT)
    logger.info(f"Extracted {len(raw_products)} raw items successfully.")

    # 2. Transformation Phase
    logger.info("Transforming and cleaning raw data...")
    clean_records = transform_products(raw_products)
    logger.info(f"Successfully cleaned and validated {len(clean_records)} unique records.")

    # 3. Loading Phase (Incremental UPSERT)
    logger.info(f"Loading data incrementally into database ({settings.DATABASE_URL})...")
    inserted, updated, unchanged = load_products_incrementally(clean_records)

    summary = {
        "status": "success",
        "total_extracted": len(raw_products),
        "total_transformed": len(clean_records),
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
    }

    logger.info("==========================================")
    logger.info(f"Pipeline Finished: {summary}")
    logger.info("==========================================")
    return summary

if __name__ == "__main__":
    run_pipeline()
