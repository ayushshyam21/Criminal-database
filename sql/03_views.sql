-- ============================================================================
-- SCRIPT 03: DATABASE VIEWS DEFINITION
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Views: v_case_summary, v_officer_workload, v_public_incident_trends
-- ============================================================================

USE crime_db;

-- ============================================================================
-- VIEW 1: v_case_summary
-- Purpose: Consolidates complete case dossier headers, assigned jurisdiction,
--          active lead investigator, and aggregated counts of persons and evidence.
-- ============================================================================
CREATE OR REPLACE VIEW v_case_summary AS
SELECT 
    c.case_id,
    c.case_number,
    c.title,
    c.case_type,
    c.status,
    c.priority,
    c.incident_location,
    ps.station_name,
    ps.district_code,
    c.date_reported,
    c.date_closed,
    DATEDIFF(COALESCE(c.date_closed, CURRENT_TIMESTAMP), c.date_reported) AS days_elapsed,
    DATEDIFF(COALESCE(c.date_closed, CURRENT_TIMESTAMP), c.date_reported) AS elapsed_days,
    u_creator.full_name AS reported_by,
    u_lead.full_name AS lead_investigator,
    u_lead.badge_number AS lead_badge,
    COUNT(DISTINCT ca.user_id) AS assigned_officer_count,
    COUNT(DISTINCT ca.user_id) AS total_officers_assigned,
    COUNT(DISTINCT cp.person_id) AS total_persons_involved,
    COUNT(DISTINCT e.evidence_id) AS evidence_count,
    COUNT(DISTINCT e.evidence_id) AS total_evidence_items,
    COUNT(DISTINCT n.note_id) AS total_notes_logged
FROM cases c
JOIN police_stations ps ON c.station_id = ps.station_id
JOIN users u_creator ON c.created_by = u_creator.user_id
LEFT JOIN case_assignments ca_lead ON c.case_id = ca_lead.case_id 
    AND ca_lead.assignment_role = 'Lead Investigator' 
    AND ca_lead.is_active = TRUE
LEFT JOIN users u_lead ON ca_lead.user_id = u_lead.user_id
LEFT JOIN case_assignments ca ON c.case_id = ca.case_id
LEFT JOIN case_persons cp ON c.case_id = cp.case_id
LEFT JOIN evidence e ON c.case_id = e.case_id
LEFT JOIN investigation_notes n ON c.case_id = n.case_id
GROUP BY 
    c.case_id, 
    c.case_number, 
    c.title, 
    c.case_type, 
    c.status, 
    c.priority, 
    c.incident_location,
    ps.station_name, 
    ps.district_code, 
    c.date_reported, 
    c.date_closed,
    u_creator.full_name,
    u_lead.full_name,
    u_lead.badge_number;

-- ============================================================================
-- VIEW 2: v_officer_workload
-- Purpose: Evaluates police personnel resource allocation, tracking active case
--          assignments, closed case investigations, and evidence custody intake.
-- ============================================================================
CREATE OR REPLACE VIEW v_officer_workload AS
SELECT 
    u.user_id,
    u.badge_number,
    u.full_name,
    u.full_name AS officer_name,
    u.role,
    ps.station_name,
    ps.district_code,
    COUNT(DISTINCT ca.case_id) AS total_assigned_cases,
    COUNT(DISTINCT CASE WHEN ca.is_active = TRUE THEN ca.case_id END) AS active_cases,
    COUNT(DISTINCT CASE WHEN ca.is_active = TRUE THEN ca.case_id END) AS active_cases_assigned,
    COUNT(DISTINCT CASE WHEN ca.assignment_role = 'Lead Investigator' AND ca.is_active = TRUE THEN ca.case_id END) AS lead_investigator_cases,
    COUNT(DISTINCT CASE WHEN ca.assignment_role = 'Lead Investigator' AND ca.is_active = TRUE THEN ca.case_id END) AS active_leads,
    COUNT(DISTINCT CASE WHEN c.priority = 'Critical' AND ca.is_active = TRUE THEN ca.case_id END) AS critical_priority_cases,
    COUNT(DISTINCT CASE WHEN c.status = 'Closed' THEN ca.case_id END) AS lifetime_closed_cases,
    COUNT(DISTINCT e.evidence_id) AS evidence_items_collected
FROM users u
LEFT JOIN police_stations ps ON u.station_id = ps.station_id
LEFT JOIN case_assignments ca ON u.user_id = ca.user_id
LEFT JOIN cases c ON ca.case_id = c.case_id
LEFT JOIN evidence e ON u.user_id = e.collected_by
WHERE u.is_active = TRUE
GROUP BY u.user_id, u.badge_number, u.full_name, u.role, ps.station_name, ps.district_code;

-- ============================================================================
-- VIEW 3: v_public_incident_trends
-- Purpose: Aggregates real-world Chicago reported crime trends by year, month,
--          and primary category, computing exact arrest percentages.
-- ============================================================================
CREATE OR REPLACE VIEW v_public_incident_trends AS
SELECT 
    incident_year,
    MONTH(incident_date) AS incident_month,
    source_primary_type,
    COUNT(*) AS total_reported_incidents,
    SUM(CASE WHEN arrest_made = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    SUM(CASE WHEN domestic = TRUE THEN 1 ELSE 0 END) AS total_domestic,
    ROUND(
        (SUM(CASE WHEN arrest_made = TRUE THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)) * 100, 
        2
    ) AS arrest_rate_pct
FROM public_crime_incidents
GROUP BY incident_year, MONTH(incident_date), source_primary_type;
