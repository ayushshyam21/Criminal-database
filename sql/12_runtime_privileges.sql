-- ============================================================================
-- SCRIPT 12: RUNTIME APPLICATION LEAST-PRIVILEGE GRANTS
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Target User: 'crimedb_app'@'localhost'
-- Execution: EXECUTED BY LOCAL ROOT / SYSTEM ADMINISTRATOR (STEP E)
--            Run this script ONLY AFTER migration scripts 01 through 07 have completed.
-- ============================================================================

USE crime_db;

-- 1. REVOKE PREEXISTING PERMISSIONS (Ensures clean additive least-privilege state)
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'crimedb_app'@'localhost';

-- 2. OPERATIONAL APPLICATION TABLES: FULL DML (SELECT, INSERT, UPDATE, DELETE)
-- Required for routine case management, personnel assignment, evidence intake, and notes
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.police_stations TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.users TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.cases TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.persons TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.case_assignments TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.case_persons TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.evidence TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_db.investigation_notes TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON crime_db.citizens TO 'crimedb_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON crime_db.citizen_reports TO 'crimedb_app'@'localhost';

-- 3. PUBLIC DATA & REFERENCE LOOKUPS: READ-ONLY (SELECT ONLY)
-- Strict read-only access prevents accidental modification of public incident statistics
GRANT SELECT ON crime_db.public_crime_incidents TO 'crimedb_app'@'localhost';
GRANT SELECT ON crime_db.iucr_codes TO 'crimedb_app'@'localhost';

-- 4. IMMUTABLE AUDIT & CUSTODY LEDGERS: READ-ONLY (SELECT ONLY)
-- 'crimedb_app' CANNOT directly INSERT, UPDATE, or DELETE on audit ledgers.
-- Audit and chain-of-custody inserts are performed strictly via DEFINER-secured triggers.
GRANT SELECT ON crime_db.audit_log TO 'crimedb_app'@'localhost';
GRANT SELECT ON crime_db.evidence_custody_log TO 'crimedb_app'@'localhost';

-- 5. PROCEDURAL & ANALYTICAL ROUTINE EXECUTION
GRANT EXECUTE ON PROCEDURE crime_db.sp_assign_case TO 'crimedb_app'@'localhost';
GRANT EXECUTE ON FUNCTION crime_db.fn_case_duration TO 'crimedb_app'@'localhost';

-- 6. DATABASE VIEWS: READ-ONLY (SELECT ONLY)
GRANT SELECT ON crime_db.v_case_summary TO 'crimedb_app'@'localhost';
GRANT SELECT ON crime_db.v_officer_workload TO 'crimedb_app'@'localhost';
GRANT SELECT ON crime_db.v_public_incident_trends TO 'crimedb_app'@'localhost';

FLUSH PRIVILEGES;

-- Verification: Display all effective grants for the runtime user
SHOW GRANTS FOR 'crimedb_app'@'localhost';
