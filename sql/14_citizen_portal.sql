-- ============================================================================
-- SCRIPT 14: CITIZEN PORTAL SCHEMA, DEMO SEED DATA, AND LEAST-PRIVILEGE GRANTS
-- Project: Criminal Case Management & Crime Analytics System
-- Target Database: crime_db
-- ============================================================================

USE crime_db;

-- 1. CITIZENS TABLE (Separate from police staff users table)
CREATE TABLE IF NOT EXISTS citizens (
    citizen_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone_number VARCHAR(30) NULL,
    address VARCHAR(255) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_citizens_email (email),
    INDEX idx_citizens_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. CITIZEN REPORTS TABLE (Fictional citizen-submitted demo reports)
CREATE TABLE IF NOT EXISTS citizen_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(32) NOT NULL UNIQUE,
    citizen_id INT NOT NULL,
    category VARCHAR(60) NOT NULL,
    incident_date DATE NOT NULL,
    incident_location VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Submitted', 'Under Review', 'Information Requested', 'Resolved', 'Closed') NOT NULL DEFAULT 'Submitted',
    public_status_notes TEXT NULL,
    is_demo_submission BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_citizen_reports_citizen FOREIGN KEY (citizen_id) 
        REFERENCES citizens(citizen_id) ON DELETE CASCADE,
    INDEX idx_citizen_reports_citizen (citizen_id),
    INDEX idx_citizen_reports_tracking (tracking_number),
    INDEX idx_citizen_reports_status (status),
    INDEX idx_citizen_reports_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. SEED INITIAL DEMO CITIZEN ACCOUNT
-- Email: citizen.jane@example.com, Password: Citizen123!
INSERT INTO citizens (citizen_id, email, password_hash, full_name, phone_number, address, is_active)
VALUES (
    1, 
    'citizen.jane@example.com', 
    'scrypt:32768:8:1$puzlSi8JsBqHC1V2$4dfbd3bdf3233d350a046e696595bf8d6a2c3856b1d299fd60aa47f129b79e84487169f056577eb0690f959c728f08f8a94f862c828b69cb2b90de2ef9627729',
    'Jane Doe (Demo Citizen)',
    '312-555-0199',
    'Fictional 742 Evergreen Terrace, Chicago, IL',
    TRUE
)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- 4. SEED SAMPLE CITIZEN REPORTS
INSERT INTO citizen_reports (
    report_id, tracking_number, citizen_id, category, incident_date, 
    incident_location, title, description, status, public_status_notes, is_demo_submission
) VALUES (
    1,
    'CR-2026-00001',
    1,
    'Lost Property',
    '2026-03-10',
    'Millennium Park near Cloud Gate, Chicago, IL',
    'Lost Navy Blue Backpack with Student ID',
    'Left a navy blue Herschel backpack on a park bench near the pavilion around 3:30 PM. Contains textbooks and student identification.',
    'Under Review',
    'Report received and assigned to Community Liaison Desk. Local park security has been queried for recovered items.',
    TRUE
), (
    2,
    'CR-2026-00002',
    1,
    'Vandalism',
    '2026-03-15',
    '1200 N Lake Shore Dr Alleyway, Chicago, IL',
    'Graffiti Tagging on Residential Garage Gate',
    'Discovered spray paint tagging on the exterior residential garage door overnight. No personal confrontation.',
    'Submitted',
    'Initial report logged. Community patrol unit will document damage during next neighborhood sweep.',
    TRUE
)
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- 5. LEAST-PRIVILEGE APPLICATION RUNTIME GRANTS
-- Applied by MySQL Administrator / root (or via sql/12_runtime_privileges.sql)
-- GRANT SELECT, INSERT, UPDATE ON crime_db.citizens TO 'crimedb_app'@'localhost';
-- GRANT SELECT, INSERT, UPDATE ON crime_db.citizen_reports TO 'crimedb_app'@'localhost';
-- FLUSH PRIVILEGES;
