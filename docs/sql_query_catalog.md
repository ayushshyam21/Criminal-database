# Advanced SQL Query Catalog & Routine Reference Guide
**Project:** Criminal Case Management & Crime Analytics System (Project Evaluation)  
**Database:** `crime_db`  
**Engine:** MySQL 8.0+ / 9.x  

---

## 1. Programmable Routines Catalog

### 1.1 Stored Procedure: `sp_assign_case`
* **File:** `sql/04_stored_routines.sql`
* **Signature:**
  ```sql
  sp_assign_case(
      IN p_case_id INT,
      IN p_user_id INT,
      IN p_role VARCHAR(50),
      IN p_notes VARCHAR(255),
      OUT p_status_code VARCHAR(20),
      OUT p_status_message VARCHAR(255)
  )
  ```
* **Operational Rules:**
  1. Opens an explicit transaction (`START TRANSACTION`).
  2. Verifies case existence and ensures case status is not 'Closed'.
  3. Verifies user exists, is active, and possesses an operational role (`Officer`, `Investigator`, or `Admin`).
  4. If assigning role 'Lead Investigator', automatically sets any existing active lead assignment on this case to `is_active = FALSE` and `unassigned_date = CURRENT_TIMESTAMP`, cleanly preserving past assignment history without modifying earlier dates or roles.
  5. Inserts a new active record or updates role/notes if the user was already actively assigned.
  6. Automatically advances case status from 'Open' to 'Under Investigation'.
  7. Commits transaction and sets `p_status_code = 'SUCCESS'`. Rollback issued on failure.
* **Demonstration Call:**
  ```sql
  CALL sp_assign_case(1, 6, 'Lead Investigator', 'Reassigned lead to Detective Hayes', @code, @msg);
  SELECT @code AS status_code, @msg AS status_message;
  ```

---

### 1.2 Stored Function: `fn_case_duration`
* **File:** `sql/04_stored_routines.sql`
* **Declaration:** `NOT DETERMINISTIC READS SQL DATA`
* **Signature:** `fn_case_duration(p_case_id INT) RETURNS INT`
* **Logic:**
  * If `case_id` does not exist: returns `NULL`.
  * If case is 'Closed' (`date_closed IS NOT NULL`): returns `GREATEST(0, DATEDIFF(date_closed, date_reported))`.
  * If case is 'Open' or ongoing: returns `GREATEST(0, DATEDIFF(CURRENT_TIMESTAMP, date_reported))`.
* **Demonstration Call:**
  ```sql
  SELECT case_number, status, date_reported, date_closed, fn_case_duration(case_id) AS duration_days 
  FROM cases 
  WHERE case_id IN (1, 3, 99999);
  ```

---

## 2. Database Views Catalog

| View Name | File | Primary Tables Joined | Business Purpose |
| :--- | :--- | :--- | :--- |
| **`v_case_summary`** | `sql/03_views.sql` | `cases`, `police_stations`, `users`, `case_assignments`, `case_persons`, `evidence` | Comprehensive case dossier header, active lead investigator, counts of persons and physical evidence pieces. |
| **`v_officer_workload`** | `sql/03_views.sql` | `users`, `police_stations`, `case_assignments`, `cases`, `evidence` | Real-time police staffing dashboard tracking active assignments, active leads, resolved cases, and evidence collected. |
| **`v_public_incident_trends`**| `sql/03_views.sql` | `public_crime_incidents` | Multi-dimensional public safety statistical summary grouping by year, month, and category with arrest percentage. |

---

## 3. Database Triggers Catalog

| Trigger Name | Event | Target Table | Purpose & Security Scope |
| :--- | :--- | :--- | :--- |
| **`trg_evidence_initial_custody`** | `AFTER INSERT` | `evidence` | Initiates the first chain-of-custody entry in `evidence_custody_log` immediately upon cataloging an evidence item. Uses `NEW.collected_by` (or NULL). |
| **`trg_evidence_custody_update`** | `AFTER UPDATE` | `evidence` | Appends a historical custody entry in `evidence_custody_log` whenever storage location or legal custody status changes. Reads session variable `@app_user_id` (or NULL). |
| **`trg_cases_status_audit`** | `AFTER UPDATE` | `cases` | Audits case lifecycle progression whenever `status` or `priority` changes, serializing old and new states into `audit_log` as JSON. Reads session variable `@app_username` (or NULL). |

---

## 4. Analytical SQL Catalog

### Query 1: Dossier Aggregation with Multi-Table Joins
```sql
SELECT 
    c.case_number, c.title, c.case_type, c.status, ps.station_name,
    u_lead.full_name AS lead_investigator,
    COUNT(DISTINCT cp.person_id) AS total_persons,
    COUNT(DISTINCT e.evidence_id) AS total_evidence
FROM cases c
JOIN police_stations ps ON c.station_id = ps.station_id
LEFT JOIN case_assignments ca ON c.case_id = ca.case_id AND ca.assignment_role = 'Lead Investigator' AND ca.is_active = TRUE
LEFT JOIN users u_lead ON ca.user_id = u_lead.user_id
LEFT JOIN case_persons cp ON c.case_id = cp.case_id
LEFT JOIN evidence e ON c.case_id = e.case_id
GROUP BY c.case_id, ps.station_name, u_lead.full_name;
```

### Query 2: Correlated Subquery for High-Evidence Cases
```sql
SELECT c.case_number, c.title, (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.case_id) AS evidence_count
FROM cases c
WHERE (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.case_id) > (
    SELECT AVG(cnt) FROM (SELECT COUNT(evidence_id) AS cnt FROM cases LEFT JOIN evidence ON cases.case_id = evidence.case_id GROUP BY cases.case_id) AS avg_tbl
);
```

### Query 3: Window Function (DENSE_RANK)
```sql
SELECT case_number, case_type, status,
       DATEDIFF(COALESCE(date_closed, CURRENT_TIMESTAMP), date_reported) AS days_active,
       DENSE_RANK() OVER (PARTITION BY case_type ORDER BY DATEDIFF(COALESCE(date_closed, CURRENT_TIMESTAMP), date_reported) DESC) AS rank_in_type
FROM cases
WHERE status <> 'Closed';
```

### Query 4: Common Table Expression (CTE)
```sql
WITH StationMetrics AS (
    SELECT station_id, COUNT(*) AS total_cases,
           SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS resolved_cases
    FROM cases GROUP BY station_id
)
SELECT ps.station_name, sm.total_cases, sm.resolved_cases,
       ROUND((sm.resolved_cases / sm.total_cases) * 100, 2) AS clearance_pct
FROM police_stations ps
JOIN StationMetrics sm ON ps.station_id = sm.station_id;
```
