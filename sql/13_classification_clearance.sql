-- ============================================================================
-- SCRIPT 13: CASE CLASSIFICATION AND STAFF CLEARANCE LEVELS
-- Project: Criminal Case Management & Crime Analytics System
-- Target Database: crime_db
-- ============================================================================

USE crime_db;

-- 1. Add classification_level to cases table (defaulting existing cases to INTERNAL)
ALTER TABLE cases 
ADD COLUMN classification_level ENUM('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED') 
NOT NULL DEFAULT 'INTERNAL' AFTER priority;

-- 2. Add clearance_level to users table (defaulting existing staff to INTERNAL)
ALTER TABLE users 
ADD COLUMN clearance_level ENUM('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED') 
NOT NULL DEFAULT 'INTERNAL' AFTER role;

-- 3. Set initial staff clearance levels based on rank and responsibilities
-- Chief Vance: RESTRICTED (highest clearance)
UPDATE users SET clearance_level = 'RESTRICTED' WHERE username = 'admin_sys';

-- Senior Detectives: CONFIDENTIAL
UPDATE users SET clearance_level = 'CONFIDENTIAL' WHERE username IN ('investigator_chen', 'investigator_hayes');

-- Detective Kowalski and Patrol Officers: INTERNAL
UPDATE users SET clearance_level = 'INTERNAL' WHERE username IN ('investigator_kowalski', 'officer_carter', 'officer_ramirez', 'officer_jordan');

-- 4. Classify a subset of sample cases to demonstrate multi-level security
-- Mark Homicide and Cyber Extortion cases as CONFIDENTIAL or RESTRICTED
UPDATE cases SET classification_level = 'RESTRICTED' WHERE case_type IN ('Homicide') LIMIT 2;
UPDATE cases SET classification_level = 'CONFIDENTIAL' WHERE case_type IN ('Cybercrime', 'Fraud') LIMIT 4;
UPDATE cases SET classification_level = 'PUBLIC' WHERE case_type IN ('Theft') LIMIT 5;

-- 5. Update v_case_summary view to include classification_level
CREATE OR REPLACE VIEW v_case_summary AS
SELECT 
    c.case_id,
    c.case_number,
    c.title,
    c.case_type,
    c.status,
    c.priority,
    c.classification_level,
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
    c.classification_level,
    c.incident_location,
    ps.station_name, 
    ps.district_code, 
    c.date_reported, 
    c.date_closed,
    u_creator.full_name,
    u_lead.full_name,
    u_lead.badge_number;
