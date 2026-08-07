# Architectural Note 02: Database Schema & Data Lineage
**Project:** Macro-Sensitized Credit Default Simulation Engine
**Focus:** Entity Relationship mapping and Data Generating Process (DGP) verification.

## 1. Entity Relationship Diagram (Logical Schema)
The SQLite warehouse (`risk_warehouse.db`) is structured using a standard Fact/Dimension architecture, allowing for dynamic `LEFT JOIN` operations during feature assembly.

**Dimension Table A: `internal_loan_vintages` (The "Who")**
* `cohort_id` (Primary Key - Unique Identifier)
* `origination_date`
* `fico_tier` (Prime / Subprime)
* `interest_rate_type` (Fixed / Variable)

**Dimension Table B: `macro_trends` (The "Environment")**
* `observation_date` (Primary Key - Unique Identifier)
* `fdtr_index` (Fed Funds Rate)
* `cpi_yoy` (Inflation)
* `usurtot_index` (Unemployment)
* `ahe_yoy` (Wage Growth)

**Fact Table: `portfolio_monthly_performance` (The "Action")**
* `reporting_date` (Foreign Key -> `macro_trends.observation_date`)
* `cohort_id` (Foreign Key -> `internal_loan_vintages.cohort_id`)
* `npl_ratio` (The target variable / default rate)

## 2. Volume Verification & DGP Math
To satisfy the Difference-in-Differences (DiD) requirements, the synthetic portfolio was engineered with specific volume and lifecycle constraints:

* **144 Unique Cohorts:** Originations occurred over a 36-month window (Jan 2020 to Dec 2022). Each month generated 4 distinct borrower profiles (Prime/Fixed, Prime/Variable, Subprime/Fixed, Subprime/Variable). (36 months × 4 profiles = 144 cohorts).
* **3,984 Performance Records:** Each cohort reports a monthly Non-Performing Loan (NPL) ratio from its origination date through the end of the simulation lifecycle (Dec 2023), mirroring the natural seasoning of a live banking portfolio.