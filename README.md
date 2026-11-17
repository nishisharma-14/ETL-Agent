# Automated Data Pipeline & ETL System

An industry-standard, production-ready Automated Data Pipeline (ETL) built with Python, PostgreSQL, and FastAPI. The system reliably extracts product records from a public REST API with pagination and robust error handling, cleans and validates the schema, incrementally updates persistent storage using change detection (UPSERT), and exposes clean endpoints to consumers.

---

## 🏗️ Architecture

```
        Public REST API (DummyJSON)
                     │
                     ▼ (HTTP GET, pagination & timeout safety)
             Data Extractor (`src/extractor.py`)
                     │
                     ▼ (Raw JSON dictionary stream)
            Data Transformer (`src/transformer.py`)
                     │  • Type validation & normalization
                     │  • Deduplication & field pruning
                     ▼
         Incremental Change Detector (`src/loader.py`)
                     │  • Checks Primary Key (product_id)
                     │  • Compares values: Insert / Update / Skip
                     ▼
             PostgreSQL Database (`src/database.py`)
                     ▲
                     │ (SQLAlchemy ORM)
             FastAPI Service (`src/api.py`)
                     │
                     ▼ (Interactive Swagger UI & JSON Endpoints)
             API Consumers / Client Apps
```

---

## 🚀 Key Features

- **Dynamic Pagination Extraction:** Automatically discovers total record counts (`total = None` pattern) and extracts entire datasets without hardcoding offsets.
- **Fail-Safe Robustness:** Implements request timeouts, HTTP error inspection (`raise_for_status`), and safe exception recovery.
- **Data Profiling & Transformation:** Cleans dirty records, eliminates duplicates, formats data types, and discards unneeded attributes.
- **Incremental Processing (Change Detection / UPSERT):** Avoids redundant database overwrites by comparing existing records and applying `INSERT`, `UPDATE`, or `UNCHANGED` actions conditionally.
- **Multi-Database Support:** Defaults to local SQLite for instant zero-dependency execution out-of-the-box, or switches to PostgreSQL via a simple connection string.
- **FastAPI Endpoints:** Includes paginated filtering (`category`, `price`), individual lookups, and manual pipeline triggers.
- **Dockerized Multi-Container Setup:** Ready to run with `docker compose` across PostgreSQL and API containers.
- **Automated Test Suite:** Comprehensive test coverage with `pytest` for transformation logic and API endpoints.

---

## 📁 Project Structure

```
Automated-ETL/
├── src/
│   ├── __init__.py
│   ├── config.py         # Pydantic environment configuration
│   ├── database.py       # SQLAlchemy engine, session & ProductModel
│   ├── extractor.py      # Resilient API extraction & pagination logic
│   ├── loader.py         # Incremental database loader (UPSERT logic)
│   ├── logger.py         # Centralized pipeline logger
│   ├── pipeline.py       # End-to-end ETL orchestrator
│   ├── transformer.py    # Cleaning, validation & deduplication
│   └── api.py            # FastAPI REST endpoints
├── tests/
│   ├── test_api.py       # FastAPI endpoint tests
│   └── test_transformer.py # Data transformation unit tests
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules
├── docker-compose.yml    # Multi-container orchestration (DB + API)
├── Dockerfile            # Container definition
├── requirements.txt      # Project dependencies
└── README.md
```

---

## 🛠️ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+
- (Optional) Docker & Docker Compose for containerized deployment

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/Automated-ETL.git
cd Automated-ETL

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the ETL Pipeline
```bash
python -m src.pipeline
```
*Output on initial run:*
```
2026-11-17 21:02:23 [INFO] [ETL_Pipeline]: Starting Automated ETL Pipeline Execution
2026-11-17 21:02:28 [INFO] [ETL_Pipeline]: Extracted 194 raw items successfully.
2026-11-17 21:02:28 [INFO] [ETL_Pipeline]: Successfully cleaned and validated 194 unique records.
2026-11-17 21:02:28 [INFO] [ETL_Pipeline]: Database Sync Completed -> Inserted: 194, Updated: 0, Unchanged: 0
```
Running it a second time detects zero changes:
```
2026-11-17 21:06:40 [INFO] [ETL_Pipeline]: Database Sync Completed -> Inserted: 0, Updated: 0, Unchanged: 194
```

### 4. Start the FastAPI Server
```bash
uvicorn src.api:app --reload --port 8000
```
- Open Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Open Health Endpoint: [http://localhost:8000/health](http://localhost:8000/health)
- Query Products: [http://localhost:8000/products?category=beauty&limit=10](http://localhost:8000/products?category=beauty&limit=10)

---

## 🐳 Running with Docker Compose

Run the complete production stack (PostgreSQL + FastAPI + Pipeline):
```bash
docker compose up --build
```

---

## 🧪 Running Tests
```bash
python -m pytest -v
```
All unit tests validate data transformation, schema consistency, duplicate prevention, and FastAPI endpoints.

---

## 💡 Interview Concepts & Explanations

1. **Why Incremental Processing?**
   Processing only new or changed records prevents database lock contention, reduces write I/O, and scales efficiently when dealing with large volumes of records.
2. **Why the `total = None` pagination pattern?**
   It allows the pipeline to make an initial API call to inspect the payload header/metadata for `total` before creating the loop bounds, avoiding hardcoded offsets.
3. **Why layer FastAPI over the database?**
   Direct database access poses severe security and connection pooling risks. FastAPI adds abstraction, rate limiting, validation, and authentication layers.
