# Test Cases & Verification Matrix
## Criminal Case Management & Crime Analytics System (Project Evaluation)

This document provides the complete specification, execution methodology, expected outcomes, and verified results for all automated and security test cases.

---

## 1. Automated Test Suite Matrix (`pytest`)

**Test Command:** `python -m pytest -v`  
**Environment:** Python 3.14.0, pytest 9.1.1, MySQL Community Server 9.7.1  
**Total Tests:** 15 | **Passed:** 15 | **Failed:** 0 | **Pass Rate:** 100%

| Test ID | Module | Test Function | Description & Test Objective | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `test_auth.py` | `test_unauthenticated_redirect` | Unauthenticated user attempts to access `/dashboard`. | HTTP 302 Redirect to `/login?next=%2Fdashboard`. | Redirected to `/login`; status 302. | **PASS** |
| **TC-02** | `test_auth.py` | `test_valid_admin_login` | Authenticate with username `admin_sys` and valid password `DemoPass123!`. | HTTP 200 OK; redirects to `/dashboard`; contains `"Chief Eleanor Vance"`. | Authenticated; dashboard loaded. | **PASS** |
| **TC-03** | `test_auth.py` | `test_invalid_password` | Authenticate with username `admin_sys` and invalid password `WrongPassword!`. | HTTP 200 OK; remains on `/login`; flashes error `"Invalid username or password"`. | Flash error displayed; session denied. | **PASS** |
| **TC-04** | `test_auth.py` | `test_logout` | Authenticated administrator accesses `/logout`. | HTTP 302 Redirect to `/login`; session cookie cleared; message `"signed out successfully"`. | Logged out cleanly; session cleared. | **PASS** |
| **TC-05** | `test_cases_crud.py` | `test_list_cases_filter` | Query `/cases` filtering by `status=Under Investigation`. | HTTP 200 OK; returned HTML contains filtered cases and table layout. | Filtered cases returned; status 200. | **PASS** |
| **TC-06** | `test_cases_crud.py` | `test_create_case_validation` | POST `/cases/create` with missing case title. | HTTP 200 OK; re-renders form; flashes warning `"Case title cannot be empty"`. | Re-rendered with validation flash. | **PASS** |
| **TC-07** | `test_cases_crud.py` | `test_create_and_read_case` | POST `/cases/create` with valid dossier data, then GET newly created dossier. | Dossier persisted; unique case number generated; details match input. | Case persisted and retrieved cleanly. | **PASS** |
| **TC-08** | `test_importer.py` | `test_importer_repeatability` | Ingest sample batch of 2 Chicago crime records twice consecutively. | First run inserts records; second run detects duplicate IDs and skips them (zero duplicates created). | Duplicate count matches; database integrity preserved. | **PASS** |
| **TC-09** | `test_permissions.py` | `test_admin_access_allowed` | Administrator requests `/dashboard`. | Full access granted; operational overview cards displayed. | HTTP 200; operational cards visible. | **PASS** |
| **TC-10** | `test_permissions.py` | `test_officer_cannot_delete_case` | Standard Patrol Officer (`officer_carter`) attempts POST to `/cases/<id>/delete`. | Access denied; redirected to dashboard; flashes warning `"Administrative credentials required"`. | Deletion blocked; flash warning shown. | **PASS** |
| **TC-11** | `test_permissions.py` | `test_investigator_confidential_notes` | Senior Investigator (`investigator_chen`) requests `/cases/<id>`. | Full dossier rendered including confidential investigative diary section and assignment controls. | Confidential controls visible. | **PASS** |
| **TC-12** | `test_stored_routines.py` | `test_stored_function_duration` | Execute `SELECT fn_case_duration(:cid) AS days` for valid and non-existent case IDs. | Valid case returns non-null non-negative integer; non-existent ID returns `NULL`. | Valid integer returned; invalid returns NULL. | **PASS** |
| **TC-13** | `test_stored_routines.py` | `test_stored_procedure_assignment` | Execute POST to `/cases/<id>/assign` triggering `CALL sp_assign_case(...)`. | Stored procedure returns code `'SUCCESS'`; personnel assigned; case status advanced if open. | Personnel allocated; status advanced. | **PASS** |
| **TC-14** | `test_triggers.py` | `test_case_status_audit_trigger` | Modify case priority/status via POST `/cases/<id>/edit`. | MySQL trigger `trg_cases_status_audit` automatically writes JSON old/new values to `audit_log` with actor `admin_sys`. | Audit row written with correct actor and JSON delta. | **PASS** |
| **TC-15** | `test_triggers.py` | `test_evidence_custody_transfer_trigger` | Transfer evidence location via POST `/evidence/<id>/transfer`. | MySQL trigger `trg_evidence_custody_update` automatically inserts append-only row to `evidence_custody_log`. | Custody log count incremented; destination recorded. | **PASS** |

---

## 2. Runtime Security & Privilege Negative Tests

The following security constraints were verified directly against the live MySQL server to guarantee that the application runtime account `crimedb_app` cannot exceed its intended authority:

| Security Test ID | Target Object | Operation Attempted | Expected Database Error | Actual Error Code | Security Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SEC-01** | `audit_log` | Direct `INSERT` by `crimedb_app` | Error 1142: INSERT command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (Immutable)** |
| **SEC-02** | `audit_log` | Direct `UPDATE` by `crimedb_app` | Error 1142: UPDATE command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (Immutable)** |
| **SEC-03** | `audit_log` | Direct `DELETE` by `crimedb_app` | Error 1142: DELETE command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (Immutable)** |
| **SEC-04** | `evidence_custody_log` | Direct `INSERT` by `crimedb_app` | Error 1142: INSERT command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (Immutable)** |
| **SEC-05** | `evidence_custody_log` | Direct `DELETE` by `crimedb_app` | Error 1142: DELETE command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (Immutable)** |
| **SEC-06** | `public_crime_incidents`| Direct `UPDATE` by `crimedb_app` | Error 1142: UPDATE command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (Read-Only)** |
| **SEC-07** | `cases` | `DROP TABLE cases` by `crimedb_app` | Error 1142: DROP command denied to user `'crimedb_app'` | `1142 (42000)` | **SECURE (No DDL)** |

---

## 3. Business Rule Validation Tests

| Rule ID | Table | Constraint Name | Enforcement Test | Observed Result |
| :--- | :--- | :--- | :--- | :--- |
| **BR-01** | `cases` | `chk_cases_closure_consistency` | Attempt to set `status = 'Closed'` while leaving `date_closed = NULL`. | MySQL rejects with check constraint violation `chk_cases_closure_consistency`. Enforced in both SQL and Flask. |
| **BR-02** | `persons` | `chk_persons_fictional_only` | Attempt to insert a person with `is_fictional = FALSE`. | MySQL rejects with check constraint violation `chk_persons_fictional_only`. |
| **BR-03** | `case_assignments` | `sp_assign_case` Single Lead | Assign a second Lead Investigator to an active case. | Stored procedure automatically deactivates previous active lead investigator, maintaining exactly one lead. |
| **BR-04** | `case_assignments` | `sp_assign_case` Closed Case | Assign an officer to a case with `status = 'Closed'`. | Procedure returns error code `'ERR_CASE_CLOSED'` and rejects assignment. |
