# Architectural Note 03: Version Control & Git Strategy
**Project:** Macro-Sensitized Credit Default Simulation Engine

## 1. Repository Philosophy
This repository strictly separates code logic from operational state. We track the "instructions" but ignore the heavy "outputs" to ensure the repository remains lightweight, reproducible, and secure.

## 2. Tracked Assets (Uploaded to GitHub)
* `src/`: All data engineering and econometric pipeline scripts.
* `docs/`: Public-facing methodology, ERD schemas, and project documentation.
* `data/raw/`: Lightweight, foundational CSV inputs required for pipeline execution.

## 3. Ignored Assets (Protected via `.gitignore`)
* `*.db`: Compiled SQLite databases (Generated locally via `src/pipeline/01_sqlite_ingestion.py`).
* `*.~lock.*`: Ghost files and temporary system lock artifacts.
* `PROJECT_STATE.md`: Internal session management and operational cheat sheets.
* `__pycache__/` & `venv/`: Local Python environment artifacts.