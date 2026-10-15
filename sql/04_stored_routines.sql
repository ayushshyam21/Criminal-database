-- ============================================================================
-- SCRIPT 04: STORED PROCEDURES & STORED FUNCTIONS
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Routines: sp_assign_case, fn_case_duration
-- ============================================================================

USE crime_db;

DROP PROCEDURE IF EXISTS sp_assign_case;
DROP FUNCTION IF EXISTS fn_case_duration;

DELIMITER $$

-- ============================================================================
-- STORED PROCEDURE: sp_assign_case
-- Purpose: Atomically assigns personnel to a case, enforces lead investigator
--          exclusivity without destroying past assignment history, and advances
--          case workflow state.
-- ============================================================================
CREATE DEFINER = 'crimedb_admin'@'localhost' PROCEDURE sp_assign_case(
    IN p_case_id INT,
    IN p_user_id INT,
    IN p_role VARCHAR(50),
    IN p_notes VARCHAR(255),
    OUT p_status_code VARCHAR(20),
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_case_status VARCHAR(30);
    DECLARE v_user_role VARCHAR(30);
    DECLARE v_user_active BOOLEAN;

    -- Standard rollback handler for unexpected runtime SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 'ERR_SQL';
        SET p_status_message = 'Internal database error during personnel assignment.';
    END;

    START TRANSACTION;

    -- 1. Validate Case Exists and is Actionable
    SELECT status INTO v_case_status FROM cases WHERE case_id = p_case_id;
    IF v_case_status IS NULL THEN
        SET p_status_code = 'ERR_NO_CASE';
        SET p_status_message = 'Target criminal case dossier does not exist.';
        ROLLBACK;
        LEAVE proc_body;
    ELSEIF v_case_status = 'Closed' THEN
        SET p_status_code = 'ERR_CASE_CLOSED';
        SET p_status_message = 'Cannot assign personnel to an officially closed case.';
        ROLLBACK;
        LEAVE proc_body;
    END IF;

    -- 2. Validate Target User Status and Operational Role
    SELECT role, is_active INTO v_user_role, v_user_active FROM users WHERE user_id = p_user_id;
    IF v_user_role IS NULL OR v_user_active = FALSE THEN
        SET p_status_code = 'ERR_INVALID_USER';
        SET p_status_message = 'Target personnel is inactive or does not exist.';
        ROLLBACK;
        LEAVE proc_body;
    ELSEIF v_user_role NOT IN ('Officer', 'Investigator', 'Admin') THEN
        SET p_status_code = 'ERR_ROLE';
        SET p_status_message = 'User lacks certified operational credentials.';
        ROLLBACK;
        LEAVE proc_body;
    END IF;

    -- 3. Lead Investigator Transition (Single Active Lead Enforcement)
    -- If a new Lead is designated, close any existing active lead assignment cleanly
    -- without overwriting or destroying their historical record.
    IF p_role = 'Lead Investigator' THEN
        UPDATE case_assignments
           SET is_active = FALSE,
               unassigned_date = CURRENT_TIMESTAMP,
               notes = CONCAT(COALESCE(notes, ''), ' [Lead role transitioned via sp_assign_case]')
         WHERE case_id = p_case_id
           AND assignment_role = 'Lead Investigator'
           AND is_active = TRUE;
    END IF;

    -- 4. Check for Existing Active Assignment of this User on this Case
    IF EXISTS (SELECT 1 FROM case_assignments WHERE case_id = p_case_id AND user_id = p_user_id AND is_active = TRUE) THEN
        -- If already active, adjust role or notes without violating active unique key
        UPDATE case_assignments
           SET assignment_role = p_role,
               notes = p_notes
         WHERE case_id = p_case_id 
           AND user_id = p_user_id 
           AND is_active = TRUE;
    ELSE
        -- 5. Insert New Clean Active Assignment Record
        -- (Safely handles re-assignment after an earlier assignment ended)
        INSERT INTO case_assignments (
            case_id, 
            user_id, 
            assignment_role, 
            assigned_date, 
            unassigned_date, 
            is_active, 
            notes
        ) VALUES (
            p_case_id, 
            p_user_id, 
            p_role, 
            CURRENT_TIMESTAMP, 
            NULL, 
            TRUE, 
            p_notes
        );
    END IF;

    -- 6. Advance Case State from 'Open' to 'Under Investigation'
    IF v_case_status = 'Open' THEN
        UPDATE cases SET status = 'Under Investigation' WHERE case_id = p_case_id;
    END IF;

    COMMIT;
    SET p_status_code = 'SUCCESS';
    SET p_status_message = 'Personnel successfully allocated to case dossier.';
END$$

-- ============================================================================
-- STORED FUNCTION: fn_case_duration
-- Declaration: NOT DETERMINISTIC (because open cases evaluate against CURRENT_TIMESTAMP)
-- Purpose: Calculates elapsed calendar days for a criminal case file.
-- Return Values:
--   - Closed Case: Exact elapsed days between reported and closed timestamps.
--   - Open / Ongoing Case: Exact elapsed days between reported timestamp and now.
--   - Nonexistent Case ID: NULL.
-- ============================================================================
CREATE DEFINER = 'crimedb_admin'@'localhost' FUNCTION fn_case_duration(p_case_id INT)
RETURNS INT
NOT DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_reported DATETIME;
    DECLARE v_closed DATETIME;
    DECLARE v_exists INT DEFAULT 0;

    -- Query case reporting and closure timestamps
    SELECT 1, date_reported, date_closed 
      INTO v_exists, v_reported, v_closed
      FROM cases 
     WHERE case_id = p_case_id;

    -- Scenario 1: Nonexistent case ID -> Return NULL
    IF v_exists = 0 OR v_reported IS NULL THEN
        RETURN NULL;
    END IF;

    -- Scenario 2: Officially Closed Case -> Return duration up to closing moment
    IF v_closed IS NOT NULL THEN
        RETURN GREATEST(0, DATEDIFF(v_closed, v_reported));
    END IF;

    -- Scenario 3: Open / In-Progress Case -> Return duration up to current moment
    RETURN GREATEST(0, DATEDIFF(CURRENT_TIMESTAMP, v_reported));
END$$

DELIMITER ;
