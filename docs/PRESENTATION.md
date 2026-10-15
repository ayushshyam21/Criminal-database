# Criminal Case Management & Crime Analytics System
## Project Evaluation — Slide-by-Slide Presentation Guide

---

### SLIDE 1: Title & Project Overview
- **Title:** Criminal Case Management & Crime Analytics Relational DBMS
- **Course:** Database Management Systems (Project Evaluation)
- **Architecture:** MySQL 9.7 / 8.0+ (InnoDB) + Python 3.14 (Flask / SQLAlchemy / PyMySQL) + Bootstrap 5 + Chart.js
- **Key Proposition:** A production-grade relational DBMS that balances operational law enforcement case dossiers with macro-level public crime trend analysis, enforcing BCNF normalization, least-privilege security, and tamper-proof audit trails.

---

### SLIDE 2: Problem Statement & Engineering Challenges
- **Challenges in Real-World Crime Databases:**
  - **Redundancy & Inconsistency:** Public crime types and officer titles repeated across incident records.
  - **Broken Chain-of-Custody:** Physical evidence transfers vulnerable to retroactive record modification or unauthorized tampering.
  - **Dangerous Database Privileges:** Web applications historically run with full `GRANT ALL` permissions, allowing SQL injection attacks to compromise or drop schemas.
  - **Mixing Public & Confidential Data:** Blurring unverified municipal crime statistics with sensitive active investigation files.

---

### SLIDE 3: System Architecture & Dual-Account Privilege Model
- **Security Boundary:**
  - **Migration & Admin Account (`crimedb_admin`):** Executes migrations, owns DEFINER triggers, performs batch ingestion.
  - **Runtime Application Account (`crimedb_app`):** Used exclusively by the Flask web application.
- **Least-Privilege Enforcement:**
  - Operational tables: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
  - Public crime data & canonical IUCR: **Read-Only (`SELECT`)**.
  - Audit logs (`audit_log`, `evidence_custody_log`): **ZERO direct write permissions**.
  - DDL commands (`CREATE`, `DROP`, `ALTER`): **Denied**.

---

### SLIDE 4: Relational Schema & BCNF Normalization
- **12 Base Tables in Boyce-Codd Normal Form (BCNF):**
  - Precincts: `police_stations`
  - Personnel & RBAC: `users`
  - Dossiers & Junctions: `cases`, `case_assignments`, `case_persons`, `persons`
  - Forensic Management: `evidence`, `investigation_notes`
  - Immutable Ledgers: `evidence_custody_log`, `audit_log`
  - Public Crime Domain: `iucr_codes`, `public_crime_incidents`
- **BCNF Proof:** Every non-trivial functional dependency $X \rightarrow Y$ in every table has a superkey as $X$. Zero transitive or partial dependencies.

---

### SLIDE 5: Public Data Ingestion & Data Preservation
- **Real-World Integration:** City of Chicago Socrata Open Data Portal (`ijzp-q8t2.json`).
- **Data Normalization Reconciled with Source Preservation:**
  - Raw source strings (`source_iucr_code`, `source_primary_type`) are preserved untouched for auditing.
  - Standardized reference codes are mapped to canonical `iucr_codes(iucr_code)`.
  - Batching, deduplication (`external_incident_id` unique index), and repeatable CLI ingestion (`python scripts/import_chicago_data.py --limit 50`).

---

### SLIDE 6: Declarative Constraints & Business Rules
- **Check Constraints (`CHECK`):**
  - `chk_cases_closure_consistency`: Case cannot be `'Closed'` without `date_closed`, and cannot have `date_closed` unless `'Closed'`.
  - `chk_persons_fictional_only`: `is_fictional = TRUE` prevents mixing real citizens with fictional investigation personas.
  - Status and priority enums enforced declaratively.
- **Foreign Key Actions:**
  - `cases(station_id)` $\rightarrow$ `ON DELETE RESTRICT` (prevents deleting active stations).
  - `case_assignments(case_id)` $\rightarrow$ `ON DELETE CASCADE` (cleans up assignments when a test case is purged).

---

### SLIDE 7: Database Triggers & Dynamic Actor Tracking
- **The Definer Architecture:**
  - `crimedb_app` cannot insert into `audit_log` or `evidence_custody_log`.
  - Triggers are created with `DEFINER = 'crimedb_admin'@'localhost'`.
- **Dynamic Session Context:**
  - Flask executes `SET @app_user_id = %s, @app_username = %s;` on every authenticated request.
- **Trigger Implementations:**
  - `trg_evidence_initial_custody`: Generates initial custody record upon evidence intake.
  - `trg_evidence_custody_update`: Detects changes to location or status, recording handler and reason.
  - `trg_cases_status_audit`: Detects changes to case status/priority, writing JSON snapshots to `audit_log`.

---

### SLIDE 8: Stored Procedures & Stored Functions
- **Stored Procedure `sp_assign_case`:**
  - Handles personnel allocation with transactional safety.
  - Enforces the business rule: **Only one Lead Investigator can be active on any case**.
  - Automatically deactivates previous leads and advances case status from `'Open'` to `'Under Investigation'`.
  - Catches errors via `DECLARE EXIT HANDLER FOR SQLEXCEPTION` with rollback.
- **Stored Function `fn_case_duration`:**
  - Calculates case lifespan in days (`DATEDIFF(COALESCE(date_closed, NOW()), date_opened)`).

---

### SLIDE 9: Analytical Views & Complex SQL
- **Views:**
  - `v_case_summary`: Aggregates case metadata, precinct names, lead investigators, and evidence counts.
  - `v_officer_workload`: Analyzes active officer assignments across precincts.
  - `v_public_incident_trends`: Computes monthly crime totals, arrest rates, and domestic violence ratios.
- **Advanced Query Concepts:**
  - Multi-table `INNER JOIN` & `LEFT JOIN`.
  - Correlated nested subqueries (e.g., stations with active caseloads above department average).

---

### SLIDE 10: Indexing & Query Optimization (EXPLAIN)
- **12 Secondary Composite Indexes** targeting high-frequency filter paths.
- **EXPLAIN Analysis:**
  - Without Index: `SELECT * FROM public_crime_incidents WHERE district_number = 1` results in **`type: ALL` (Full Table Scan)**, examining all rows.
  - With Index (`idx_pci_district`): Results in **`type: ref` (Index Lookup)**, examining only rows for district 1, achieving a >95% query speedup.

---

### SLIDE 11: Live Web Application Demo Sequence
1. **Login:** Demonstrate RBAC with `admin_sys`, `investigator_chen`, and `officer_carter`.
2. **Dashboard:** KPI summary cards, status doughnut, priority bar chart, and crime distribution chart.
3. **Case Dossier:** View `CASE-2026-0005`, allocate personnel via `sp_assign_case`, observe duration banner from `fn_case_duration`.
4. **Evidence & Chain of Custody:** Transfer evidence location, show trigger-generated custody history.
5. **Crime Analytics:** View live Chicago crime trends and arrest rate charts.
6. **SQL Showcase (`/sql-demo`):** Execute live queries, views, routines, and comparative EXPLAIN plans.

---

### SLIDE 12: Automated Verification & Testing
- **15 Automated Unit & Integration Tests (100% Pass Rate):**
  - Authentication & Session Lifecycle (`tests/test_auth.py`)
  - Case Dossier CRUD & Validation (`tests/test_cases_crud.py`)
  - API Ingestion Repeatability (`tests/test_importer.py`)
  - Role-Based Access Control (`tests/test_permissions.py`)
  - Stored Procedures & Functions (`tests/test_stored_routines.py`)
  - Trigger Chain-of-Custody & Audit Logs (`tests/test_triggers.py`)
- **Execution Command:** `python -m pytest -v` (6.30s execution time).

---

### SLIDE 13: Summary & Q&A
- **Key Takeaways:**
  - 100% compliant BCNF relational schema.
  - Dual-account least-privilege security model with DEFINER triggers.
  - Seamless coupling of real Chicago open data with operational police workflows.
  - Verified performance optimization through composite secondary indexing.
- **Questions & Evaluator Discussion.**
