-- ============================================================================
-- SCRIPT 11: DATABASE BACKUP & DISASTER RECOVERY PROCEDURES
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Target Tools: mysqldump, mysql CLI (MySQL 8.0+ / 9.x)
-- ============================================================================

-- ============================================================================
-- SECTION A: BACKUP PROCEDURES (Executed from Windows PowerShell / Terminal)
-- ============================================================================

/*
1. FULL LOGICAL BACKUP (Schema + Data + Stored Routines + Triggers)
   Uses --single-transaction to produce an ACID-consistent snapshot without table locks.

   PowerShell Command:
   & "C:\Program Files\MySQL\MySQL Server 9.7\bin\mysqldump.exe" `
       -u crimedb_admin -p `
       --host=127.0.0.1 `
       --port=3306 `
       --default-character-set=utf8mb4 `
       --single-transaction `
       --routines `
       --triggers `
       --databases crime_db > "d:\Criminal Database\sql\backup_crime_db_full.sql"

2. SCHEMA-ONLY BACKUP (DDL Definitions, Routines, Triggers - No Records)
   Useful for deploying empty database environments and CI/CD testing.

   PowerShell Command:
   & "C:\Program Files\MySQL\MySQL Server 9.7\bin\mysqldump.exe" `
       -u crimedb_admin -p `
       --host=127.0.0.1 `
       --port=3306 `
       --no-data `
       --routines `
       --triggers `
       --databases crime_db > "d:\Criminal Database\sql\backup_schema_only.sql"

3. APPLICATION DATA-ONLY BACKUP (Excluding Public Statistical Table)
   Dumps only fictional case dossiers, personnel, and evidence.

   PowerShell Command:
   & "C:\Program Files\MySQL\MySQL Server 9.7\bin\mysqldump.exe" `
       -u crimedb_admin -p `
       --host=127.0.0.1 `
       --port=3306 `
       --single-transaction `
       --ignore-table=crime_db.public_crime_incidents `
       crime_db > "d:\Criminal Database\sql\backup_app_data_only.sql"
*/

-- ============================================================================
-- SECTION B: RESTORATION & DISASTER RECOVERY DRILL
-- ============================================================================

/*
DISASTER RECOVERY RESTORATION STEP-BY-STEP:

Step 1: Verify Backup File Integrity
   Ensure the target backup file exists and has a non-zero size:
   Get-Item "d:\Criminal Database\sql\backup_crime_db_full.sql"

Step 2: Recreate Clean Database Container
   PowerShell Command:
   & "C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe" `
       -u crimedb_admin -p `
       --host=127.0.0.1 `
       -e "DROP DATABASE IF EXISTS crime_db_restored; CREATE DATABASE crime_db_restored CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

Step 3: Execute Restoration Pipeline
   PowerShell Command:
   Get-Content "d:\Criminal Database\sql\backup_crime_db_full.sql" | & "C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe" `
       -u crimedb_admin -p `
       --host=127.0.0.1 `
       --database=crime_db_restored

Step 4: Post-Restoration Verification Queries (Execute in MySQL CLI/Workbench):
*/

-- Run following verification queries against restored database:
USE crime_db;

-- 1. Verify Table Count (Must equal 12)
SELECT COUNT(*) AS restored_table_count 
FROM information_schema.tables 
WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE';

-- 2. Verify View Count (Must equal 3)
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = DATABASE();

-- 3. Verify Routine Count (Must equal 2: sp_assign_case, fn_case_duration)
SELECT routine_type, routine_name 
FROM information_schema.routines 
WHERE routine_schema = DATABASE();

-- 4. Verify Trigger Count (Must equal 3)
SELECT trigger_name, event_manipulation, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = DATABASE();

-- 5. Verify Record Counts
SELECT 'police_stations' AS tbl, COUNT(*) AS cnt FROM police_stations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'cases', COUNT(*) FROM cases
UNION ALL
SELECT 'persons', COUNT(*) FROM persons
UNION ALL
SELECT 'case_assignments', COUNT(*) FROM case_assignments
UNION ALL
SELECT 'case_persons', COUNT(*) FROM case_persons
UNION ALL
SELECT 'evidence', COUNT(*) FROM evidence
UNION ALL
SELECT 'evidence_custody_log', COUNT(*) FROM evidence_custody_log
UNION ALL
SELECT 'investigation_notes', COUNT(*) FROM investigation_notes
UNION ALL
SELECT 'audit_log', COUNT(*) FROM audit_log
UNION ALL
SELECT 'iucr_codes', COUNT(*) FROM iucr_codes
UNION ALL
SELECT 'public_crime_incidents', COUNT(*) FROM public_crime_incidents;
