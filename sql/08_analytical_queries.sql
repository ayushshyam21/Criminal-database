-- ============================================================================
-- SCRIPT 08: ANALYTICAL SQL DEMONSTRATIONS & QUERY CATALOG
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Demonstrations: Multi-table JOINs, Nested/Correlated Subqueries, Aggregations,
--                HAVING filters, Window Functions, and Common Table Expressions (CTEs)
-- ============================================================================

USE crime_db;

-- ============================================================================
-- 1. MULTI-TABLE JOIN (INNER + LEFT JOINs)
-- Purpose: Retrieves complete case dossier with station, creator, active lead,
--          and total counts of involved persons and physical evidence items.
-- ============================================================================
SELECT 
    c.case_number,
    c.title,
    c.case_type,
    c.status,
    c.priority,
    ps.station_name,
    ps.district_code,
    u_lead.full_name AS lead_investigator,
    u_lead.badge_number AS lead_badge,
    COUNT(DISTINCT cp.person_id) AS total_persons_linked,
    COUNT(DISTINCT e.evidence_id) AS total_evidence_pieces
FROM cases c
INNER JOIN police_stations ps ON c.station_id = ps.station_id
INNER JOIN users u_creator ON c.created_by = u_creator.user_id
LEFT JOIN case_assignments ca ON c.case_id = ca.case_id 
    AND ca.assignment_role = 'Lead Investigator' 
    AND ca.is_active = TRUE
LEFT JOIN users u_lead ON ca.user_id = u_lead.user_id
LEFT JOIN case_persons cp ON c.case_id = cp.case_id
LEFT JOIN evidence e ON c.case_id = e.case_id
GROUP BY c.case_id, ps.station_name, ps.district_code, u_lead.full_name, u_lead.badge_number
ORDER BY c.date_reported DESC;

-- ============================================================================
-- 2. CORRELATED SUBQUERY
-- Purpose: Identifies high-complexity cases that possess more cataloged evidence
--          items than the departmental average across all cases.
-- ============================================================================
SELECT 
    c.case_number,
    c.title,
    c.case_type,
    c.status,
    (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.case_id) AS case_evidence_count
FROM cases c
WHERE (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.case_id) > (
    SELECT AVG(evidence_per_case)
    FROM (
        SELECT COUNT(e2.evidence_id) AS evidence_per_case
        FROM cases c2
        LEFT JOIN evidence e2 ON c2.case_id = e2.case_id
        GROUP BY c2.case_id
    ) AS departmental_averages
)
ORDER BY case_evidence_count DESC;

-- ============================================================================
-- 3. AGGREGATION WITH GROUP BY AND HAVING
-- Purpose: Finds police districts handling above-average case loads with multiple
--          high-priority active investigations.
-- ============================================================================
SELECT 
    ps.district_code,
    ps.station_name,
    COUNT(c.case_id) AS total_cases_handled,
    SUM(CASE WHEN c.priority IN ('High', 'Critical') THEN 1 ELSE 0 END) AS high_priority_cases,
    SUM(CASE WHEN c.status = 'Closed' THEN 1 ELSE 0 END) AS closed_cases
FROM police_stations ps
JOIN cases c ON ps.station_id = c.station_id
GROUP BY ps.station_id, ps.district_code, ps.station_name
HAVING total_cases_handled >= 3
ORDER BY high_priority_cases DESC;

-- ============================================================================
-- 4. WINDOW FUNCTIONS (DENSE_RANK & PARTITION BY)
-- Purpose: Ranks criminal cases within each crime classification by elapsed days
--          investigated, identifying protracted investigations per category.
-- ============================================================================
SELECT 
    case_number,
    case_type,
    status,
    priority,
    DATEDIFF(COALESCE(date_closed, CURRENT_TIMESTAMP), date_reported) AS days_active,
    DENSE_RANK() OVER (
        PARTITION BY case_type 
        ORDER BY DATEDIFF(COALESCE(date_closed, CURRENT_TIMESTAMP), date_reported) DESC
    ) AS category_duration_rank
FROM cases
WHERE status <> 'Closed'
ORDER BY case_type, category_duration_rank ASC;

-- ============================================================================
-- 5. COMMON TABLE EXPRESSIONS (CTEs)
-- Purpose: Computes a multi-tier pipeline measuring clearance rates and custody
--          workload per operational unit.
-- ============================================================================
WITH StationCaseMetrics AS (
    SELECT 
        station_id,
        COUNT(*) AS total_cases,
        SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS resolved_cases,
        SUM(CASE WHEN status = 'Under Investigation' THEN 1 ELSE 0 END) AS active_investigations
    FROM cases
    GROUP BY station_id
),
StationEvidenceMetrics AS (
    SELECT 
        c.station_id,
        COUNT(e.evidence_id) AS total_evidence_pieces
    FROM cases c
    JOIN evidence e ON c.case_id = e.case_id
    GROUP BY c.station_id
)
SELECT 
    ps.station_name,
    ps.district_code,
    COALESCE(scm.total_cases, 0) AS total_cases,
    COALESCE(scm.resolved_cases, 0) AS resolved_cases,
    ROUND((COALESCE(scm.resolved_cases, 0) / NULLIF(scm.total_cases, 0)) * 100, 2) AS clearance_rate_pct,
    COALESCE(sem.total_evidence_pieces, 0) AS total_evidence_secured
FROM police_stations ps
LEFT JOIN StationCaseMetrics scm ON ps.station_id = scm.station_id
LEFT JOIN StationEvidenceMetrics sem ON ps.station_id = sem.station_id
ORDER BY total_cases DESC;

-- ============================================================================
-- 6. PUBLIC DATA ANALYTICAL SUMMARY (City of Chicago Statistics)
-- Purpose: Computes monthly arrest conversion rates across primary crime types
--          from imported public reported incidents.
-- ============================================================================
SELECT 
    source_primary_type,
    incident_year,
    COUNT(*) AS total_reported_incidents,
    SUM(CASE WHEN arrest_made = TRUE THEN 1 ELSE 0 END) AS total_arrests_logged,
    ROUND((SUM(CASE WHEN arrest_made = TRUE THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)) * 100, 2) AS arrest_rate_pct
FROM public_crime_incidents
GROUP BY source_primary_type, incident_year
HAVING total_reported_incidents > 0
ORDER BY total_reported_incidents DESC;
