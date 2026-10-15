-- ============================================================================
-- SCRIPT 06: PERFORMANCE OPTIMIZATION INDEXES
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- ============================================================================

USE crime_db;

-- 1. CANONICAL BENCHMARK COMPOSITE INDEX (PUBLIC CRIME INCIDENTS)
-- Optimizes multi-dimensional grouping and filtering across year, district, crime type, and arrest flag
CREATE INDEX idx_public_incidents_year_district_type 
    ON public_crime_incidents (incident_year, district, source_primary_type, arrest_made);

-- 2. TEMPORAL INDEX (PUBLIC CRIME INCIDENTS)
-- Accelerates date-range window searches and monthly timeline charts
CREATE INDEX idx_public_incidents_date 
    ON public_crime_incidents (incident_date);

-- 3. NORMALIZED LOOKUP FOREIGN KEY INDEX (PUBLIC CRIME INCIDENTS)
CREATE INDEX idx_public_incidents_canonical_iucr 
    ON public_crime_incidents (canonical_iucr_code);

-- 4. CASE MANAGEMENT STATUS & PRIORITY COMPOSITE INDEX
-- Accelerates department backlog triage queries filtering active urgent cases
CREATE INDEX idx_cases_status_priority 
    ON cases (status, priority);

-- 5. JURISDICTIONAL STATION INDEX
-- Accelerates precinct-level case dossier searches
CREATE INDEX idx_cases_station 
    ON cases (station_id);

-- 6. CASE DOSSIER EVIDENCE LOOKUP INDEX
-- Accelerates retrieving all evidence items for a specific case categorized by type
CREATE INDEX idx_evidence_case_type 
    ON evidence (case_id, evidence_type);

-- 7. ACTIVE PERSONNEL WORKLOAD INDEX
-- Optimizes officer active assignment lookups and dashboard metrics
CREATE INDEX idx_assignments_user_active 
    ON case_assignments (user_id, is_active);

-- 8. INVESTIGATION DIARY CHRONOLOGICAL RETRIEVAL INDEX
CREATE INDEX idx_notes_case_chronology 
    ON investigation_notes (case_id, logged_at);

-- 9. AUDIT LOG RECORD RETRIEVAL INDEX
CREATE INDEX idx_audit_table_record 
    ON audit_log (table_name, record_id);
