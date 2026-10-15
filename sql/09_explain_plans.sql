-- ============================================================================
-- SCRIPT 09: EXECUTION PLAN BENCHMARKING & EXPLAIN ANALYZE
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Target Table: public_crime_incidents
-- Canonical Index: idx_public_incidents_year_district_type
-- ============================================================================

USE crime_db;

-- ============================================================================
-- 1. BENCHMARK QUERY DEFINITION
-- Description: Aggregates incident counts and arrest tallies for a specific
--              year and police district grouped by primary crime category.
-- ============================================================================
-- SELECT 
--     source_primary_type, 
--     COUNT(*) AS total_incidents, 
--     SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
-- FROM public_crime_incidents
-- WHERE incident_year = 2024 AND district = '001'
-- GROUP BY source_primary_type;

-- ============================================================================
-- STEP A: EXECUTION PLAN WITHOUT COMPOSITE INDEX (BASELINE / UNINDEXED)
-- ============================================================================
-- 1. Ensure the composite index is absent for baseline measurement
ALTER TABLE public_crime_incidents 
    DROP INDEX IF EXISTS idx_public_incidents_year_district_type;

-- 2. Standard Tabular EXPLAIN Output
-- Expected Behavior: type = 'ALL' (Full Table Scan), rows examined = Total Table Cardinality
EXPLAIN 
SELECT 
    source_primary_type, 
    COUNT(*) AS total_incidents, 
    SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
FROM public_crime_incidents
WHERE incident_year = 2024 AND district = '001'
GROUP BY source_primary_type;

-- 3. Detailed JSON EXPLAIN with Cost Model Metrics
EXPLAIN FORMAT=JSON
SELECT 
    source_primary_type, 
    COUNT(*) AS total_incidents, 
    SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
FROM public_crime_incidents
WHERE incident_year = 2024 AND district = '001'
GROUP BY source_primary_type;

-- 4. EXPLAIN ANALYZE (Actual Execution Tree, Iterator Costs, and Timing)
-- (Available in MySQL 8.0.18+ / 9.x)
EXPLAIN ANALYZE
SELECT 
    source_primary_type, 
    COUNT(*) AS total_incidents, 
    SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
FROM public_crime_incidents
WHERE incident_year = 2024 AND district = '001'
GROUP BY source_primary_type;

-- ============================================================================
-- STEP B: CREATE CANONICAL COMPOSITE INDEX
-- ============================================================================
CREATE INDEX idx_public_incidents_year_district_type 
    ON public_crime_incidents (incident_year, district, source_primary_type, arrest_made);

-- ============================================================================
-- STEP C: EXECUTION PLAN WITH COMPOSITE INDEX (OPTIMIZED)
-- ============================================================================
-- 1. Standard Tabular EXPLAIN Output
-- Expected Behavior: type = 'ref' or 'range', key = 'idx_public_incidents_year_district_type'
-- Rows examined reduced strictly to the matching year/district slice.
EXPLAIN 
SELECT 
    source_primary_type, 
    COUNT(*) AS total_incidents, 
    SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
FROM public_crime_incidents
WHERE incident_year = 2024 AND district = '001'
GROUP BY source_primary_type;

-- 2. Detailed JSON EXPLAIN with Cost Model Metrics
EXPLAIN FORMAT=JSON
SELECT 
    source_primary_type, 
    COUNT(*) AS total_incidents, 
    SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
FROM public_crime_incidents
WHERE incident_year = 2024 AND district = '001'
GROUP BY source_primary_type;

-- 3. EXPLAIN ANALYZE with Index Applied
EXPLAIN ANALYZE
SELECT 
    source_primary_type, 
    COUNT(*) AS total_incidents, 
    SUM(CASE WHEN arrest_made = 1 THEN 1 ELSE 0 END) AS total_arrests
FROM public_crime_incidents
WHERE incident_year = 2024 AND district = '001'
GROUP BY source_primary_type;
