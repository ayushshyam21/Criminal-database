-- ============================================================================
-- SCRIPT 05: DATABASE TRIGGERS DEFINITION
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Triggers: trg_evidence_initial_custody, trg_evidence_custody_update, trg_cases_status_audit
-- Security Model: DEFINER = 'crimedb_admin'@'localhost'
--   Ensures triggers write to immutable audit & custody ledgers under administrative
--   authority, even when invoked by the restricted 'crimedb_app' runtime account.
-- ============================================================================

USE crime_db;

DROP TRIGGER IF EXISTS trg_evidence_initial_custody;
DROP TRIGGER IF EXISTS trg_evidence_custody_update;
DROP TRIGGER IF EXISTS trg_cases_status_audit;

DELIMITER $$

-- ============================================================================
-- TRIGGER 1: trg_evidence_initial_custody
-- Event: AFTER INSERT ON evidence
-- Purpose: Guarantees that every newly cataloged evidence item automatically
--          initiates an immutable chain-of-custody history row.
-- Definer: crimedb_admin (Executes with admin insert rights on evidence_custody_log)
-- Actor: Uses NEW.collected_by (NULL if unverified; never hard-coded).
-- ============================================================================
CREATE DEFINER = 'crimedb_admin'@'localhost' TRIGGER trg_evidence_initial_custody
AFTER INSERT ON evidence
FOR EACH ROW
BEGIN
    INSERT INTO evidence_custody_log (
        evidence_id,
        previous_status,
        new_status,
        from_location,
        to_location,
        handled_by,
        reason_for_transfer,
        logged_at
    ) VALUES (
        NEW.evidence_id,
        NULL,
        NEW.current_custody_status,
        'Scene / Origin of Discovery',
        NEW.current_storage_location,
        NEW.collected_by, -- Authenticated collector or NULL; never hard-coded
        'Initial evidence intake and cataloging',
        CURRENT_TIMESTAMP
    );
END$$

-- ============================================================================
-- TRIGGER 2: trg_evidence_custody_update
-- Event: AFTER UPDATE ON evidence
-- Purpose: Records an audit trail of physical location or custody status changes.
-- Definer: crimedb_admin
-- Actor: Reads MySQL session variable @app_user_id (NULL if unauthenticated).
-- ============================================================================
CREATE DEFINER = 'crimedb_admin'@'localhost' TRIGGER trg_evidence_custody_update
AFTER UPDATE ON evidence
FOR EACH ROW
BEGIN
    IF (OLD.current_custody_status <> NEW.current_custody_status 
        OR OLD.current_storage_location <> NEW.current_storage_location) THEN
        
        INSERT INTO evidence_custody_log (
            evidence_id,
            previous_status,
            new_status,
            from_location,
            to_location,
            handled_by,
            reason_for_transfer,
            logged_at
        ) VALUES (
            NEW.evidence_id,
            OLD.current_custody_status,
            NEW.current_custody_status,
            OLD.current_storage_location,
            NEW.current_storage_location,
            @app_user_id, -- Verified session variable or NULL; never fabricated
            COALESCE(@app_transfer_reason, 'Operational status/location modification'),
            CURRENT_TIMESTAMP
        );
    END IF;
END$$

-- ============================================================================
-- TRIGGER 3: trg_cases_status_audit
-- Event: AFTER UPDATE ON cases
-- Purpose: Automatically audits criminal case dossier status or priority shifts.
-- Definer: crimedb_admin
-- Actor: Reads session variable @app_username (NULL if unauthenticated; never CURRENT_USER()).
-- ============================================================================
CREATE DEFINER = 'crimedb_admin'@'localhost' TRIGGER trg_cases_status_audit
AFTER UPDATE ON cases
FOR EACH ROW
BEGIN
    IF (OLD.status <> NEW.status OR OLD.priority <> NEW.priority) THEN
        INSERT INTO audit_log (
            table_name,
            record_id,
            operation_type,
            old_values,
            new_values,
            performed_by,
            timestamp
        ) VALUES (
            'cases',
            NEW.case_id,
            'UPDATE',
            JSON_OBJECT('status', OLD.status, 'priority', OLD.priority),
            JSON_OBJECT('status', NEW.status, 'priority', NEW.priority),
            @app_username, -- Verified session username or NULL; never CURRENT_USER()
            CURRENT_TIMESTAMP
        );
    END IF;
END$$

DELIMITER ;
