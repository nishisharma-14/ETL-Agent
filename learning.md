# 📚 Learning Tracker — Automated Data Pipeline / ETL

> **Your goal:** Build an industry-level, resume-ready ETL project while learning every concept step by step.
> **Skill level at start:** Beginner/Intermediate (3/5)
> **Teaching style:** Explain → Example → Task → You implement → Review → Checkpoint → Next phase

---

## 🗺️ Overall Progress

| Phase | Topic | Status |
|-------|-------|--------|
| Phase 1 | Project Foundation | ✅ Done |
| Phase 2 | API & Data Extraction | ✅ Done |
| Phase 3 | Pagination & Complete Extraction | ✅ Done |
| Phase 4 | Robust Extraction & Error Handling | 🔄 In Progress |
| Phase 5 | Data Profiling & Transformation | ⬜ Not Started |
| Phase 6 | Database & SQL Foundation | ⬜ Not Started |
| Phase 7 | Load Data into PostgreSQL | ⬜ Not Started |
| Phase 8 | Incremental Processing | ⬜ Not Started |
| Phase 9 | Pipeline Orchestration | ⬜ Not Started |
| Phase 10 | Logging & Configuration | ⬜ Not Started |
| Phase 11 | FastAPI | ⬜ Not Started |
| Phase 12 | Dockerization | ⬜ Not Started |
| Phase 13 | Testing & Production Polish | ⬜ Not Started |
| Phase 14 | GitHub, Documentation & Interview Prep | ⬜ Not Started |

**Progress: 3.5 / 14 phases complete (~25%)**

```
[████░░░░░░░░░░░░░░░░░░░░░░░░░░] 25%
```

---

## ✅ PHASE 1 — Project Foundation
**Status:** ✅ Complete

### What You Learned
- [x] What ETL means (Extract, Transform, Load)
- [x] Why automated pipelines are needed
- [x] Project problem statement & objectives
- [x] High-level architecture overview
- [x] Technologies and why we chose them
- [x] Folder structure setup
- [x] Virtual environment (venv)
- [x] requirements.txt
- [x] .gitignore
- [x] README basics

### What You Built
```
Automated-ETL/
├── src/
├── README.md
├── requirements.txt
├── .gitignore
└── venv/
```

### Checkpoint Question
> **"What problem does this project solve?"**

---

## ✅ PHASE 2 — API & Data Extraction
**Status:** ✅ Complete

### What You Learned
- [x] What is an API?
- [x] HTTP requests (GET)
- [x] API response & status codes
- [x] JSON format
- [x] Python dictionaries & lists
- [x] requests library

### What You Built
- src/extractor.py — calls DummyJSON API and extracts fields: id, title, price, etc.

### Checkpoint Question
> **"How does Python get data from the API?"**

---

## ✅ PHASE 3 — Pagination & Complete Extraction
**Status:** ✅ Complete

### What You Learned
- [x] What API pagination is
- [x] limit, skip, total parameters
- [x] Loops for fetching all pages
- [x] extend() to collect all records
- [x] Why pagination exists
- [x] Dynamic pagination using total = None pattern

### Key Concept Implemented
```python
total = None
while total is None or skip < total:
    # request API
    # read JSON
    # get total
    # collect products
    # increase skip
```

> ⚠️ The total = None pattern allows the first API request to happen BEFORE the total is known. Do NOT remove it without understanding it.

### What You Built
- Dynamic paginator in src/extractor.py — fetches all 194 products

### Checkpoint Question
> **"How does the pipeline collect all records if the API returns only 30 at a time?"**

---

## 🔄 PHASE 4 — Robust Extraction & Error Handling
**Status:** 🔄 In Progress

### What You Are Learning
- [x] timeout=10 — stops waiting if API is slow
- [x] response.raise_for_status() — raises error on bad HTTP status
- [x] try / except blocks
- [x] RequestException handling
- [ ] Connection errors (what happens when internet is down)
- [ ] HTTP errors (e.g., 404, 500)
- [ ] Why pipelines should fail safely

### Current Extraction Flow
```
API
 ↓
requests.get()
 ↓
timeout=10
 ↓
raise_for_status()
 ↓
response.json()
 ↓
pagination
 ↓
all_products
```

### Still To Do in Phase 4
- [ ] Fully understand connection errors vs HTTP errors
- [ ] Complete checkpoint questions

### Checkpoint Question
> **"What happens if the API is down?"**

---

## ⬜ PHASE 5 — Data Profiling & Transformation
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Data profiling
- [ ] Required vs optional fields
- [ ] Missing values
- [ ] Incorrect data types
- [ ] Duplicates
- [ ] Selecting useful columns
- [ ] Cleaning data
- [ ] Transformation

### What You Will Build
- A transformation function that cleans raw API data into structured records
- Fields to keep: id, title, category, price, rating, stock, brand, updated_at

### Checkpoint Question
> **"Why should we NOT put raw API data directly into the database?"**

---

## ⬜ PHASE 6 — Database & SQL Foundation
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] What a database is
- [ ] Tables, Rows, Columns
- [ ] Primary Key
- [ ] Data types in SQL
- [ ] INSERT, SELECT, UPDATE, DELETE
- [ ] Constraints
- [ ] PostgreSQL basics

### What You Will Build
- Design the products table schema

### Checkpoint Question
> **"What is the primary key and why do we need it?"**

---

## ⬜ PHASE 7 — Load Data into PostgreSQL
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Database connections from Python
- [ ] Connection strings
- [ ] SQL execution from Python
- [ ] Transactions (COMMIT, ROLLBACK)
- [ ] INSERT into PostgreSQL

### What You Will Build
- Full ETL flow: API → Extract → Transform → Load → PostgreSQL

### Checkpoint
> Verify: records extracted from API actually exist in PostgreSQL.

---

## ⬜ PHASE 8 — Incremental Processing ⭐ (Most Important Phase)
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Full load vs incremental load
- [ ] New records
- [ ] Updated records
- [ ] Existing/unchanged records
- [ ] Change detection
- [ ] UPSERT
- [ ] Why reprocessing everything is inefficient

### Key Concept
```
Database:         API today:
ID 1 → $100       ID 1 → $100   → unchanged (skip)
ID 2 → $200       ID 2 → $250   → updated (update)
                  ID 3 → new    → insert
```

### Checkpoint Question
> **"How does our pipeline avoid processing unchanged records?"**

---

## ⬜ PHASE 9 — Pipeline Orchestration
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Separation of concerns
- [ ] Functions & modules
- [ ] Pipeline flow design
- [ ] Reusable code principles

### What You Will Build
```
src/
├── extractor.py
├── transformer.py
├── loader.py
└── pipeline.py
```

### Checkpoint Question
> **"Explain the complete ETL flow from API to database."**

---

## ⬜ PHASE 10 — Logging & Configuration
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Python logging module
- [ ] Log levels: INFO, WARNING, ERROR
- [ ] Debugging with logs
- [ ] Environment variables
- [ ] .env files
- [ ] Never hardcode passwords or API keys

### What You Will Build
- .env configuration file
- Logs like: Pipeline started, 194 records fetched, Pipeline finished

### Checkpoint Question
> **"How would we know what happened if the pipeline runs at 3 AM?"**

---

## ⬜ PHASE 11 — FastAPI
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] REST API concepts
- [ ] Endpoints
- [ ] GET requests
- [ ] Query parameters
- [ ] HTTP response formats
- [ ] FastAPI basics

### What You Will Build
```
GET /products
GET /products/{id}
GET /health
```

### Checkpoint Question
> **"Why did we add FastAPI to an ETL project?"**

---

## ⬜ PHASE 12 — Dockerization
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] What Docker is
- [ ] Container vs Image
- [ ] Dockerfile
- [ ] docker-compose
- [ ] Environment variables in Docker
- [ ] Container networking

### What You Will Build
- Containerized: FastAPI + PostgreSQL + ETL app
- docker compose up starts the entire project

### Checkpoint Question
> **"Why is Docker useful for this project?"**

---

## ⬜ PHASE 13 — Testing & Production Polish
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Unit tests
- [ ] Integration tests
- [ ] Edge cases
- [ ] Failure testing

### What You Will Test
- [ ] API extraction
- [ ] Transformation logic
- [ ] Empty / Duplicate / Invalid data
- [ ] Database insertion
- [ ] Incremental updates
- [ ] API endpoints

### Checkpoint Question
> **"How did you test your ETL pipeline?"**

---

## ⬜ PHASE 14 — GitHub, Documentation & Interview Preparation
**Status:** ⬜ Not Started

### What You Will Learn
- [ ] Git workflow (branches, commits)
- [ ] Writing a professional README
- [ ] Architecture diagrams
- [ ] API documentation
- [ ] Interview Q&A preparation
- [ ] Resume bullet points

### README Sections to Complete
- [ ] Project overview
- [ ] Problem statement & objectives
- [ ] Architecture
- [ ] Technologies
- [ ] Project structure
- [ ] Setup & run instructions
- [ ] API endpoints
- [ ] ETL flow explanation
- [ ] Incremental processing explanation
- [ ] Docker instructions
- [ ] Testing notes
- [ ] Future improvements

### Interview Questions to Prepare
- Why did you choose PostgreSQL?
- Why use incremental processing?
- How does pagination work?
- What happens if the API fails?
- Why use Docker?
- How does UPSERT work?
- What is the primary key?
- How does FastAPI interact with PostgreSQL?
- How would you scale this pipeline?

---

## 🏁 Final Quality Checklist

| Item | Done? |
|------|-------|
| API extraction works | ✅ |
| Pagination works | ✅ |
| Error handling works | 🔄 |
| Data transformation works | ⬜ |
| PostgreSQL integration works | ⬜ |
| Incremental processing works | ⬜ |
| UPSERT works | ⬜ |
| FastAPI works | ⬜ |
| Logging works | ⬜ |
| Configuration is secure (.env) | ⬜ |
| Docker works | ⬜ |
| Tests exist | ⬜ |
| Git repository is organized | ⬜ |
| README is complete | ⬜ |
| Architecture diagram exists | ⬜ |
| Project can be explained in an interview | ⬜ |

---

## 🔖 Optional Technologies — Do NOT Add Yet

After the core project is 100% complete ONLY:

- Apache Airflow
- Kafka
- Redis
- Cloud deployment (AWS / GCP / Azure)
- Frontend
- Kubernetes
- Apache Spark

> Priority: **CORE PROJECT FIRST.** Every technology must have a reason.

---

## 📝 How Every Phase Works

```
EXPLAIN → SHOW SMALL EXAMPLE → GIVE TASK → YOU IMPLEMENT → REVIEW → CHECKPOINT → NEXT PHASE
```

- Say **"why"** anytime → you get an explanation, not just more code
- Say **"I don't understand"** → concept re-explained with a small example
- Say **"next"** → continue from exactly where we stopped
- You provide code → it gets reviewed before moving forward

---

*Last updated: Phase 4 in progress | 3.5 / 14 phases complete (~25%)*
