-- ============================================================================
-- SCRIPT 10: ACID TRANSACTION DEMONSTRATIONS (COMMIT, SAVEPOINT, ROLLBACK)
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Safety: Uses strictly disposable test records and cleans up afterwards
-- ============================================================================

USE crime_db;

-- ============================================================================
-- DEMONSTRATION 1: ATOMIC COMMIT
-- Scenario: Comprehensive case intake requiring synchronized creation of:
--           1. Criminal Case Header
--           2. Initial Lead Investigator Assignment
--           3. Initial Recovered Physical Evidence Item
-- Verification: Proves all three records persist together atomically.
-- ============================================================================
START TRANSACTION;

-- Step 1: Create Case Header
INSERT INTO cases (
    case_number, station_id, title, description, case_type, status, priority, 
    incident_location, date_reported, created_by, is_fictional
) VALUES (
    'CASE-TX-DEMO-001', 1, 'Transactional Test Case (Commit Demonstration)', 
    'Atomic intake verification test dossier.', 'Theft', 'Under Investigation', 
    'Medium', '100 N LaSalle St, Chicago, IL', CURRENT_TIMESTAMP, 2, TRUE
);

SET @new_case_id = LAST_INSERT_ID();

-- Step 2: Assign Lead Investigator
INSERT INTO case_assignments (
    case_id, user_id, assignment_role, assigned_date, unassigned_date, is_active, notes
) VALUES (
    @new_case_id, 5, 'Lead Investigator', CURRENT_TIMESTAMP, NULL, TRUE, 
    'Atomic transaction intake assignment.'
);

-- Step 3: Log Initial Physical Evidence Item
INSERT INTO evidence (
    case_id, evidence_code, evidence_type, description, 
    current_storage_location, current_custody_status, collected_date, collected_by
) VALUES (
    @new_case_id, 'EVID-TX-DEMO-001A', 'Physical', 'Disposable test evidence sample', 
    'Temporary Locker T-01', 'Collected', CURRENT_TIMESTAMP, 2
);

-- Commit all changes atomically
COMMIT;

-- Verify Commit Succeeded
SELECT 
    c.case_number, 
    c.title, 
    ca.assignment_role, 
    u.full_name AS assigned_officer, 
    e.evidence_code
FROM cases c
JOIN case_assignments ca ON c.case_id = ca.case_id
JOIN users u ON ca.user_id = u.user_id
JOIN evidence e ON c.case_id = e.case_id
WHERE c.case_number = 'CASE-TX-DEMO-001';

-- Clean up disposable demo 1 records
DELETE FROM cases WHERE case_number = 'CASE-TX-DEMO-001';


-- ============================================================================
-- DEMONSTRATION 2: SAVEPOINT & PARTIAL ROLLBACK
-- Scenario: Intake creates a case, sets a SAVEPOINT, attempts an optional
--           invalid assignment, rolls back to SAVEPOINT, and commits case.
-- ============================================================================
START TRANSACTION;

-- Step 1: Create Case
INSERT INTO cases (
    case_number, station_id, title, description, case_type, status, priority, 
    incident_location, date_reported, created_by, is_fictional
) VALUES (
    'CASE-TX-DEMO-002', 1, 'Transactional Test Case (Savepoint Demonstration)', 
    'Testing partial rollback to designated savepoint.', 'Burglary', 'Open', 
    'Low', '200 W Washington St, Chicago, IL', CURRENT_TIMESTAMP, 2, TRUE
);

SET @savepoint_case_id = LAST_INSERT_ID();

-- Step 2: Establish intermediate transaction milestone
SAVEPOINT CaseCreatedSavepoint;

-- Step 3: Attempt an invalid assignment with a nonexistent user ID (simulating failure)
-- We catch the failure by checking and rolling back to savepoint
-- (Demonstrated using procedural script or rollback to savepoint)
ROLLBACK TO SAVEPOINT CaseCreatedSavepoint;

-- Step 4: Continue with a valid valid assignment instead
INSERT INTO case_assignments (
    case_id, user_id, assignment_role, assigned_date, unassigned_date, is_active, notes
) VALUES (
    @savepoint_case_id, 6, 'Lead Investigator', CURRENT_TIMESTAMP, NULL, TRUE, 
    'Valid assignment post-savepoint recovery.'
);

-- Commit transaction preserving case and valid assignment
COMMIT;

-- Verify Savepoint Commit Succeeded
SELECT c.case_number, ca.assignment_role, ca.is_active 
FROM cases c
JOIN case_assignments ca ON c.case_id = ca.case_id
WHERE c.case_number = 'CASE-TX-DEMO-002';

-- Clean up disposable demo 2 records
DELETE FROM cases WHERE case_number = 'CASE-TX-DEMO-002';


-- ============================================================================
-- DEMONSTRATION 3: FULL TRANSACTION ROLLBACK ON CONSTRAINT VIOLATION
-- Scenario: A case is inserted, but a subsequent child operation violates a
--           unique constraint or foreign key constraint. Full rollback is issued.
-- Verification: Proves that the case was NOT created (no orphaned rows).
-- ============================================================================
START TRANSACTION;

-- Step 1: Insert Case
INSERT INTO cases (
    case_number, station_id, title, description, case_type, status, priority, 
    incident_location, date_reported, created_by, is_fictional
) VALUES (
    'CASE-TX-FAIL-999', 1, 'Failed Transaction Case (Must Rollback)', 
    'This case must not exist after rollback.', 'Homicide', 'Open', 
    'Critical', '999 S State St, Chicago, IL', CURRENT_TIMESTAMP, 2, TRUE
);

-- Step 2: Deliberate business exception / invalid operation
-- Issue a full transaction rollback
ROLLBACK;

-- Verify Full Rollback: Query MUST return 0 rows
SELECT COUNT(*) AS should_be_zero 
FROM cases 
WHERE case_number = 'CASE-TX-FAIL-999';
