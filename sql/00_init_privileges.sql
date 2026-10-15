-- ============================================================================
-- SCRIPT 00: DATABASE CREATION & LEAST-PRIVILEGE USER PROVISIONING
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Database Engine: MySQL 8.0+ / 9.x
-- Role: EXECUTED BY LOCAL ROOT / SYSTEM ADMINISTRATOR ONLY (STEP A)
-- ============================================================================
-- EXECUTION WORKFLOW:
-- Step A: Local Administrator runs this script (00_init_privileges.sql) as root.
-- Step B: User creates local .env file with chosen passwords.
-- Step C: Connection check verifies 'crimedb_admin' connectivity.
-- Step D: Migration runner executes scripts 01 through 07 using 'crimedb_admin'.
-- Step E: Local Administrator runs sql/12_runtime_privileges.sql as root.
-- Step F: Verification checks that 'crimedb_app' has restricted runtime access.
-- Step G: Verification script audits all 12 tables, views, routines, triggers.
--
-- NOTE: 'crimedb_admin' intentionally DOES NOT have GRANT OPTION.
--       Table-level runtime privileges for 'crimedb_app' are applied in Step E.
-- ============================================================================

-- 1. DATABASE CONTAINER PROVISIONING
CREATE DATABASE IF NOT EXISTS crime_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE crime_db;

-- 2. PROVISION MIGRATION / ADMINISTRATIVE ACCOUNT
-- Role: Schema management, DDL migrations, trigger creation, and test teardown
CREATE USER IF NOT EXISTS 'crimedb_admin'@'localhost' 
    IDENTIFIED BY 'Shyam';

-- Grant full DDL and DML permissions on crime_db to administrative user
GRANT CREATE, ALTER, DROP, INDEX, REFERENCES, 
      CREATE VIEW, SHOW VIEW, 
      CREATE ROUTINE, ALTER ROUTINE, EXECUTE, 
      TRIGGER, SELECT, INSERT, UPDATE, DELETE 
    ON crime_db.* TO 'crimedb_admin'@'localhost';

-- 3. PROVISION RUNTIME APPLICATION ACCOUNT (RESTRICTED ACCESS)
-- Role: Web service runtime (Flask backend)
CREATE USER IF NOT EXISTS 'crimedb_app'@'localhost' 
    IDENTIFIED BY 'Shyam';

-- Revoke any preexisting global privileges on this database to guarantee least privilege
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'crimedb_app'@'localhost';

-- Ensure crimedb_app has connection rights to crime_db container
-- (Specific table, view, and routine grants are applied in 12_runtime_privileges.sql)
GRANT USAGE ON crime_db.* TO 'crimedb_app'@'localhost';

FLUSH PRIVILEGES;

-- Verification query: Confirms both accounts exist on localhost
SELECT user, host, plugin FROM mysql.user WHERE user IN ('crimedb_admin', 'crimedb_app');
