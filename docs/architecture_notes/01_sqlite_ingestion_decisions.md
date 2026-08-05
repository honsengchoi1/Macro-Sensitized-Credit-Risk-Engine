# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 10:33:50 2026

@author: hon19
"""

# Architectural Decision Record (ADR): Macroeconomic Data Ingestion Pipeline

**Component:** `src/pipeline/01_sqlite_ingestion.py`
**Objective:** Ingest, parse, align, and commit raw macroeconomic time-series data (FDTR, USURTOT, CPI, AHE) from Bloomberg CSV exports into a persistent SQLite data warehouse.

## 1. The Architectural Shift: `pandas.to_sql` vs. SQLAlchemy ORM
**Initial Approach:** The original draft utilized `df.to_sql()` for rapid ingestion.
**The Pivot:** Refactored to a strict **SQLAlchemy ORM** (Object-Relational Mapping) architecture.
**The "Why" (Interview Defense):**
* `pandas.to_sql` is a "black box" that blindly pushes data. It lacks strict schema enforcement, making it highly susceptible to silent data corruption if the source CSV changes its format.
* SQLAlchemy ORM allows us to define a strict, explicit contract (the `MacroTrend` class). By mapping columns explicitly to `Date` and `Float` types, the pipeline aggressively rejects bad data at the door, preserving warehouse integrity.

## 2. Defensive Engineering: The Atomic Commit
**The Risk:** If a pipeline crashes halfway through a database insertion (e.g., due to a network blip or a bad row), the database is left in a corrupted, half-updated state.
**The Solution:** Implemented an **Atomic Transaction** using `session.begin()`.
**The "Why" (Interview Defense):**
* Atomicity guarantees an "all-or-nothing" execution. If the ingestion fails on row 47 of 48, the transaction automatically rolls back, leaving the database completely untouched. 
* To prevent Primary Key collisions on subsequent runs, the pipeline safely clears the target table within the same atomic block before utilizing `bulk_insert_mappings` for high-performance writing.

## 3. Data Integrity: Multi-Vector Date Alignment
**The Risk:** Bloomberg CSV exports often append arbitrary suffixes to duplicate headers (e.g., `Date`, `Date.1`, `Date.2`) and contain intraday timestamp noise, leading to misaligned feature vectors.
**The Solution:** 1. **Normalization:** Engineered a custom parsing function that forces all timestamps to the first of the month (`YYYY-MM-01`).
2. **The Fail-Safe:** Implemented a symmetric difference check using Python `set()` comparisons across all four temporal vectors.
**The "Why" (Interview Defense):**
* A Natural Experiment model relies entirely on strict chronological alignment. If the Fed Funds Rate is misaligned with CPI by even one month, the DiD (Difference-in-Differences) coefficients are invalid. The fail-safe ensures the pipeline instantly aborts if the `Date` sets do not perfectly mirror each other.