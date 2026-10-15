-- ============================================================================
-- SCRIPT 01: RELATIONAL DATABASE SCHEMA DEFINITION (DDL)
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Normalized Table Count: 12
-- Normal Form: Boyce-Codd Normal Form (BCNF)
-- ============================================================================

USE crime_db;

-- Drop child tables first in reverse dependency order (safe script execution)
DROP TABLE IF EXISTS evidence_custody_log;
DROP TABLE IF EXISTS evidence;
DROP TABLE IF EXISTS investigation_notes;
DROP TABLE IF EXISTS case_persons;
DROP TABLE IF EXISTS case_assignments;
DROP TABLE IF EXISTS cases;
DROP TABLE IF EXISTS persons;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS public_crime_incidents;
DROP TABLE IF EXISTS iucr_codes;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS police_stations;

-- ============================================================================
-- 1. POLICE STATIONS (Precincts / Jurisdictional Facilities)
-- ============================================================================
CREATE TABLE police_stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    district_code VARCHAR(10) NOT NULL,
    address VARCHAR(200) NOT NULL,
    phone VARCHAR(25) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_station_name UNIQUE (station_name),
    CONSTRAINT uq_station_district UNIQUE (district_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. SYSTEM USERS (Authentication & Role-Based Access Control)
-- Supertype: Users | Disjoint Total Subtypes: Admin, Officer, Investigator
-- ============================================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role ENUM('Admin', 'Officer', 'Investigator') NOT NULL DEFAULT 'Officer',
    full_name VARCHAR(100) NOT NULL,
    badge_number VARCHAR(30) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_username UNIQUE (username),
    CONSTRAINT uq_user_email UNIQUE (email),
    CONSTRAINT uq_user_badge UNIQUE (badge_number),
    CONSTRAINT fk_users_station FOREIGN KEY (station_id) 
        REFERENCES police_stations(station_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_user_email CHECK (email LIKE '%_@__%.__%')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. FICTIONAL PERSONS (Demonstration Individuals: Suspects, Victims, Witnesses)
-- Strictly isolated from real-world persons
-- ============================================================================
CREATE TABLE persons (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NULL,
    gender ENUM('Male', 'Female', 'Non-Binary', 'Unknown') NOT NULL DEFAULT 'Unknown',
    phone_contact VARCHAR(25) NULL,
    address_line VARCHAR(200) NULL,
    is_fictional BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_persons_fictional CHECK (is_fictional = TRUE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. CRIMINAL CASES (Fictional Case Management Dossiers)
-- ============================================================================
CREATE TABLE cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    case_number VARCHAR(30) NOT NULL,
    station_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    case_type ENUM('Homicide', 'Robbery', 'Assault', 'Burglary', 'Theft', 
                   'Narcotics', 'Fraud', 'Cybercrime', 'Other') NOT NULL,
    status ENUM('Open', 'Under Investigation', 'Pending Review', 'Closed', 'Cold Case') 
           NOT NULL DEFAULT 'Open',
    priority ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    incident_location VARCHAR(200) NOT NULL,
    date_reported DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_closed DATETIME NULL,
    created_by INT NOT NULL,
    is_fictional BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_case_number UNIQUE (case_number),
    CONSTRAINT fk_cases_station FOREIGN KEY (station_id) 
        REFERENCES police_stations(station_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cases_creator FOREIGN KEY (created_by) 
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_cases_fictional CHECK (is_fictional = TRUE),
    CONSTRAINT chk_cases_closure_consistency CHECK (
        (status = 'Closed' AND date_closed IS NOT NULL AND date_closed >= date_reported)
        OR
        (status <> 'Closed' AND date_closed IS NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. CASE ASSIGNMENTS (Personnel Allocation & Historical Tracking)
-- Enforces: Max 1 active Lead Investigator, No duplicate active assignments
-- ============================================================================
CREATE TABLE case_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    user_id INT NOT NULL,
    assignment_role ENUM('Lead Investigator', 'Assisting Officer', 'Forensic Specialist') 
                    NOT NULL DEFAULT 'Assisting Officer',
    assigned_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    unassigned_date DATETIME NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notes VARCHAR(255) NULL,

    -- Generated column: non-null only when active. Prevents duplicate ACTIVE assignments.
    -- (Defined as VIRTUAL to permit InnoDB cascading foreign keys on case_id and user_id)
    active_assignment_key VARCHAR(64) GENERATED ALWAYS AS (
        IF(is_active = TRUE, CONCAT(case_id, '_', user_id), NULL)
    ) VIRTUAL,

    -- Generated column: non-null only when active lead. Prevents multiple ACTIVE leads per case.
    -- (Defined as VIRTUAL to permit InnoDB cascading foreign keys on case_id)
    active_lead_key VARCHAR(64) GENERATED ALWAYS AS (
        IF(is_active = TRUE AND assignment_role = 'Lead Investigator', CONCAT('LEAD_', case_id), NULL)
    ) VIRTUAL,

    CONSTRAINT fk_assign_case FOREIGN KEY (case_id) 
        REFERENCES cases(case_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_assign_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_active_user_assignment UNIQUE (active_assignment_key),
    CONSTRAINT uq_single_active_lead UNIQUE (active_lead_key),
    CONSTRAINT chk_assignment_lifecycle CHECK (
        (is_active = TRUE AND unassigned_date IS NULL) OR
        (is_active = FALSE AND unassigned_date IS NOT NULL AND unassigned_date >= assigned_date)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 6. CASE PERSONS (M:N Associative Link with Role Classification)
-- ============================================================================
CREATE TABLE case_persons (
    case_person_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    person_id INT NOT NULL,
    role_in_case ENUM('Suspect', 'Victim', 'Witness', 'Person of Interest', 'Reporting Party') NOT NULL,
    statement_summary TEXT NULL,
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cp_case FOREIGN KEY (case_id) 
        REFERENCES cases(case_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cp_person FOREIGN KEY (person_id) 
        REFERENCES persons(person_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_case_person_role UNIQUE (case_id, person_id, role_in_case)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. EVIDENCE (Recovered Physical, Digital & Forensic Items)
-- ============================================================================
CREATE TABLE evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    evidence_code VARCHAR(50) NOT NULL,
    evidence_type ENUM('Physical', 'Digital', 'Forensic', 'Documentary', 'Weapons', 'Other') NOT NULL,
    description TEXT NOT NULL,
    current_storage_location VARCHAR(100) NOT NULL,
    current_custody_status ENUM('Collected', 'In Analysis', 'Vault Storage', 
                                 'Court Presentation', 'Disposed') 
                            NOT NULL DEFAULT 'Collected',
    collected_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    collected_by INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_evidence_code UNIQUE (evidence_code),
    CONSTRAINT fk_evidence_case FOREIGN KEY (case_id) 
        REFERENCES cases(case_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_evidence_collector FOREIGN KEY (collected_by) 
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 8. EVIDENCE CUSTODY LOG (Chain-of-Custody Append-Only Historical Ledger)
-- ============================================================================
CREATE TABLE evidence_custody_log (
    custody_id INT AUTO_INCREMENT PRIMARY KEY,
    evidence_id INT NOT NULL,
    previous_status ENUM('Collected', 'In Analysis', 'Vault Storage', 
                         'Court Presentation', 'Disposed') NULL,
    new_status ENUM('Collected', 'In Analysis', 'Vault Storage', 
                    'Court Presentation', 'Disposed') NOT NULL,
    from_location VARCHAR(100) NULL,
    to_location VARCHAR(100) NOT NULL,
    handled_by INT NULL,
    reason_for_transfer VARCHAR(255) NOT NULL,
    logged_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_custody_evidence FOREIGN KEY (evidence_id) 
        REFERENCES evidence(evidence_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_custody_handler FOREIGN KEY (handled_by) 
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 9. INVESTIGATION NOTES (Chronological Case Diary)
-- ============================================================================
CREATE TABLE investigation_notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    author_id INT NOT NULL,
    note_title VARCHAR(150) NOT NULL,
    note_body TEXT NOT NULL,
    is_confidential BOOLEAN NOT NULL DEFAULT FALSE,
    logged_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notes_case FOREIGN KEY (case_id) 
        REFERENCES cases(case_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notes_author FOREIGN KEY (author_id) 
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 10. AUDIT LOG (System-Level Operational Event Ledger)
-- ============================================================================
CREATE TABLE audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    operation_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    performed_by VARCHAR(50) NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 11. IUCR CODES (Illinois Uniform Crime Reporting Reference Standards)
-- ============================================================================
CREATE TABLE iucr_codes (
    iucr_code VARCHAR(10) PRIMARY KEY,
    primary_type VARCHAR(50) NOT NULL,
    description VARCHAR(120) NOT NULL,
    fbi_code VARCHAR(10) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 12. PUBLIC CRIME INCIDENTS (Imported Public Open Data - City of Chicago)
-- Strictly isolated from application fictional persons and cases
-- ============================================================================
CREATE TABLE public_crime_incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    source_id BIGINT NOT NULL,
    case_number VARCHAR(25) NULL,
    incident_date DATETIME NOT NULL,
    block VARCHAR(120) NULL,
    
    -- Raw Ingested Source Attributes (Guarantees no data loss)
    source_iucr_code VARCHAR(10) NULL,
    source_primary_type VARCHAR(50) NOT NULL,
    source_description VARCHAR(120) NULL,
    
    -- Normalized Reference Foreign Key (Nullable for unmapped historical codes)
    canonical_iucr_code VARCHAR(10) NULL,
    
    location_description VARCHAR(100) NULL,
    arrest_made BOOLEAN NULL,        -- Three-valued logic: TRUE, FALSE, or NULL
    domestic BOOLEAN NULL,           -- Three-valued logic: TRUE, FALSE, or NULL
    beat VARCHAR(10) NULL,
    district VARCHAR(10) NULL,
    ward INT NULL,
    community_area VARCHAR(15) NULL,
    fbi_code VARCHAR(10) NULL,
    latitude DECIMAL(11, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    incident_year INT NOT NULL,
    updated_on DATETIME NULL,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_incident_source UNIQUE (source_id),
    CONSTRAINT fk_incident_canonical_iucr FOREIGN KEY (canonical_iucr_code) 
        REFERENCES iucr_codes(iucr_code) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_incidents_year CHECK (incident_year >= 2001)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
