# Test Cases & Verification Matrix
## Criminal Case Management & Crime Analytics System (Project Evaluation)

This document provides the complete specification, execution methodology, expected outcomes, and verified results for all automated and security test cases.

---

## 1. Automated Test Suite Matrix (`pytest`)

**Test Command:** `python -m pytest -v`  
**Environment:** Python 3.14.0, pytest 9.1.1, MySQL Community Server 9.7.1  
**Total Tests:** 35 | **Passed:** 35 | **Failed:** 0 | **Pass Rate:** 100%

| Test ID | Module | Test Function | Description & Test Objective | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `test_auth.py` | `test_unauthenticated_redirect` | Unauthenticated user attempts to access `/dashboard`. | HTTP 302 Redirect to `/login?next=%2Fdashboard`. | Redirected to `/login`; status 302. | **PASS** |
| **TC-02** | `test_auth.py` | `test_valid_admin_login` | Authenticate with username `admin_sys` and valid password `DemoPass123!`. | HTTP 200 OK; redirects to `/dashboard`; contains `"Chief Eleanor Vance"`. | Authenticated; dashboard loaded. | **PASS** |
| **TC-03** | `test_auth.py` | `test_invalid_password` | Authenticate with username `admin_sys` and invalid password `WrongPassword!`. | HTTP 200 OK; remains on `/login`; flashes error `"Invalid username or password"`. | Flash error displayed; session denied. | **PASS** |
| **TC-04** | `test_auth.py` | `test_logout` | Authenticated administrator accesses `/logout`. | HTTP 302 Redirect to `/login`; session cookie cleared; message `"signed out successfully"`. | Logged out cleanly; session cleared. | **PASS** |
| **TC-05** | `test_cases_crud.py` | `test_list_cases_filter` | Query `/cases` filtering by `status=Under Investigation`. | HTTP 200 OK; returned HTML contains filtered cases and table layout. | Filtered cases returned; status 200. | **PASS** |
| **TC-06** | `test_cases_crud.py` | `test_create_case_validation` | POST `/cases/create` with missing case title. | HTTP 200 OK; re-renders form; flashes warning `"Case title must be at least 5 characters"`. | Re-rendered with validation flash. | **PASS** |
| **TC-07** | `test_cases_crud.py` | `test_create_and_read_case` | POST `/cases/create` with valid dossier data, then GET newly created dossier. | Dossier persisted; unique case number generated; details match input. | Case persisted and retrieved cleanly. | **PASS** |
| **TC-08** | `test_citizen_portal.py` | `test_unauthenticated_citizen_redirect` | Unauthenticated citizen attempts to visit `/citizen/dashboard`. | HTTP 302 Redirect to `/citizen/login`. | Redirected to citizen login. | **PASS** |
| **TC-09** | `test_citizen_portal.py` | `test_citizen_registration_and_login` | New citizen registration and subsequent login with salted hash verification. | Password hashed with scrypt (not plaintext); account created; logs in successfully. | Password hashed; dashboard rendered. | **PASS** |
| **TC-10** | `test_citizen_portal.py` | `test_citizen_login_invalid_password` | Citizen attempts login with incorrect password. | Rejected; error flash `"Invalid email or password"`. | Denied; remains on login. | **PASS** |
| **TC-11** | `test_citizen_portal.py` | `test_citizen_report_submission_and_tracking` | Citizen submits non-emergency incident report via `/citizen/reports/new`. | Generates unique tracking code `CR-2026-XXXXX`; status is `'Submitted'`; demo flag is True. | Tracking code generated; report logged. | **PASS** |
| **TC-12** | `test_citizen_portal.py` | `test_cross_citizen_privacy_isolation` | Citizen B attempts to access report submitted by Citizen A via `/citizen/reports/<id>`. | HTTP 404 Not Found (prevents resource enumeration and leaks). | HTTP 404 returned; data isolated. | **PASS** |
| **TC-13** | `test_citizen_portal.py` | `test_citizen_session_cannot_access_staff_routes` | Signed-in citizen attempts to access staff routes (`/dashboard`, `/cases`, `/evidence`). | HTTP 302 Redirect to staff login `/login` (treated as unauthenticated staff). | Staff routes blocked from citizen session. | **PASS** |
| **TC-14** | `test_classification_security.py` | `test_clearance_rank_hierarchy` | Validates Bell-LaPadula clearance rank order (`PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED`). | Simple Security Property: no read up; permitted read down. | All clearance combinations match MLS rules. | **PASS** |
| **TC-15** | `test_classification_security.py` | `test_admin_restricted_case_access` | Chief Vance (Admin, RESTRICTED clearance) views RESTRICTED classified case. | HTTP 200 OK; dossier rendered with RESTRICTED badge. | Full access granted. | **PASS** |
| **TC-16** | `test_classification_security.py` | `test_investigator_cannot_access_restricted_case` | Investigator Chen (CONFIDENTIAL clearance) attempts to access RESTRICTED case. | HTTP 403 Forbidden; Access Denied page rendered. | HTTP 403 returned; access blocked. | **PASS** |
| **TC-17** | `test_classification_security.py` | `test_officer_cannot_access_confidential_case` | Officer Carter (INTERNAL clearance) attempts to access CONFIDENTIAL case. | HTTP 403 Forbidden; Access Denied page rendered. | HTTP 403 returned; access blocked. | **PASS** |
| **TC-18** | `test_classification_security.py` | `test_assigned_investigator_accesses_confidential_case` | Investigator Chen (CONFIDENTIAL, assigned to case 7) views case 7. | HTTP 200 OK; dossier details rendered. | Access permitted based on clearance + assignment. | **PASS** |
| **TC-19** | `test_classification_security.py` | `test_unassigned_investigator_denied_need_to_know` | Investigator Hayes (CONFIDENTIAL clearance, but NOT assigned to case 7) attempts access. | Access denied; reason explicitly cites need-to-know requirement. | Need-to-know enforced. | **PASS** |
| **TC-20** | `test_classification_security.py` | `test_deactivated_user_blocked_from_all_cases` | Inactive/suspended user attempts to access case dossier. | Denied; reasons state account is inactive or unauthenticated. | Inactive account blocked. | **PASS** |
| **TC-21** | `test_classification_security.py` | `test_dashboard_query_isolation` | Verifies that dashboard metrics and charts exclude classified records beyond user's clearance. | Officer cannot see RESTRICTED or unassigned CONFIDENTIAL cases in KPIs. | Database-level query filtering verified. | **PASS** |
| **TC-22** | `test_classification_security.py` | `test_officer_forbidden_from_admin_staff` | Patrol officer attempts to access `/admin/staff`. | Redirected with `"Access Restricted"` flash message. | Non-admin blocked from clearance panel. | **PASS** |
| **TC-23** | `test_classification_security.py` | `test_admin_staff_clearance_management` | Admin views staff register and promotes/demotes clearance via `/admin/staff/<id>/clearance`. | Clearance level updated; verified in database and audit. | Personnel clearance updated successfully. | **PASS** |
| **TC-24** | `test_importer.py` | `test_importer_repeatability` | Ingest sample batch of 2 Chicago crime records twice consecutively. | First run inserts records; second run detects duplicate IDs and skips them (zero duplicates created). | Duplicate count matches; database integrity preserved. | **PASS** |
| **TC-25** | `test_permissions.py` | `test_admin_access_allowed` | Administrator requests `/dashboard`. | Full access granted; operational overview cards displayed. | HTTP 200; operational cards visible. | **PASS** |
| **TC-26** | `test_permissions.py` | `test_officer_cannot_delete_case` | Standard Patrol Officer (`officer_carter`) attempts POST to `/cases/<id>/delete`. | Access denied; redirected to dashboard; flashes warning `"Administrative credentials required"`. | Deletion blocked; flash warning shown. | **PASS** |
| **TC-27** | `test_permissions.py` | `test_investigator_confidential_notes` | Senior Investigator (`investigator_chen`) requests `/cases/<id>`. | Full dossier rendered including confidential investigative diary section and assignment controls. | Confidential controls visible. | **PASS** |
| **TC-28** | `test_stored_routines.py` | `test_stored_function_duration` | Execute `SELECT fn_case_duration(:cid) AS days` for valid and non-existent case IDs. | Valid case returns non-null non-negative integer; non-existent ID returns `NULL`. | Valid integer returned; invalid returns NULL. | **PASS** |
| **TC-29** | `test_stored_routines.py` | `test_stored_procedure_assignment` | Execute POST to `/cases/<id>/assign` triggering `CALL sp_assign_case(...)`. | Stored procedure returns code `'SUCCESS'`; personnel assigned; case status advanced if open. | Personnel allocated; status advanced. | **PASS** |
| **TC-30** | `test_triggers.py` | `test_case_status_audit_trigger` | Modify case priority/status via POST `/cases/<id>/edit`. | MySQL trigger `trg_cases_status_audit` automatically writes JSON old/new values to `audit_log` with actor `admin_sys`. | Audit row written with correct actor and JSON delta. | **PASS** |
| **TC-31** | `test_triggers.py` | `test_evidence_custody_transfer_trigger` | Transfer evidence location via POST `/evidence/<id>/transfer`. | MySQL trigger `trg_evidence_custody_update` automatically inserts append-only row to `evidence_custody_log`. | Custody log count incremented; destination recorded. | **PASS** |
| **TC-32** | `test_views.py` | `test_case_summary_query` | Query view `v_case_summary` directly and check column schema. | Columns `days_elapsed`, `assigned_officer_count`, `evidence_count`, `classification_level` present. | View query returns expected columns. | **PASS** |
| **TC-33** | `test_views.py` | `test_case_summary_orm_model` | Query `VCaseSummary` via SQLAlchemy ORM. | Returns mapped model instances matching underlying view records. | ORM mapping verified. | **PASS** |
| **TC-34** | `test_views.py` | `test_officer_workload_orm_model` | Query `VOfficerWorkload` via SQLAlchemy ORM. | Returns workload counts per officer. | Workload metrics verified. | **PASS** |
| **TC-35** | `test_views.py` | `test_sql_demo_views_tab_http` | Request `/sql-demo` with views tab. | HTTP 200 OK; views table rendered. | Tab loads successfully. | **PASS** |

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
