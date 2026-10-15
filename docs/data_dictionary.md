# Data Dictionary & Attribute Catalog
**Project:** Criminal Case Management & Crime Analytics System (Project Evaluation)  
**Database:** `crime_db`  
**Storage Engine:** InnoDB  
**Character Set:** `utf8mb4`  
**Collation:** `utf8mb4_unicode_ci`  

---

## Table 1: `police_stations`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `station_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `station_name` | VARCHAR(100) | No | **UK** (`uq_station_name`) | None | Official name of police district station. |
| `district_code` | VARCHAR(10) | No | **UK** (`uq_station_district`) | None | Numeric district code (e.g., '001', '019'). |
| `address` | VARCHAR(200) | No | None | None | Physical municipal street address. |
| `phone` | VARCHAR(25) | No | None | None | Official contact telephone number. |
| `created_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Record creation timestamp. |

---

## Table 2: `users`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `user_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key for system personnel. |
| `station_id` | INT | Yes | **FK** $\to$ `police_stations` | NULL | Assigned precinct station facility. |
| `username` | VARCHAR(50) | No | **UK** (`uq_user_username`) | None | Unique login handle. |
| `email` | VARCHAR(120) | No | **UK** (`uq_user_email`), CHECK | None | Official email address with format validation. |
| `password_hash` | VARCHAR(256) | No | None | None | Werkzeug salted scrypt password digest. |
| `role` | ENUM('Admin','Officer','Investigator') | No | None | `'Officer'` | Role-based authorization type. |
| `full_name` | VARCHAR(100) | No | None | None | Officer full legal and operational name. |
| `badge_number` | VARCHAR(30) | Yes | **UK** (`uq_user_badge`) | NULL | Official departmental badge identification. |
| `is_active` | BOOLEAN | No | None | `TRUE` | Soft status flag indicating active service. |
| `created_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Account provisioning timestamp. |
| `updated_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Automatic update timestamp on record edit. |

---

## Table 3: `cases`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `case_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key for case file. |
| `case_number` | VARCHAR(30) | No | **UK** (`uq_case_number`) | None | Formatted case file number (e.g. 'CASE-2026-0001'). |
| `station_id` | INT | No | **FK** $\to$ `police_stations` | None | Handling jurisdictional police station. |
| `title` | VARCHAR(200) | No | None | None | Descriptive operational case incident title. |
| `description` | TEXT | Yes | None | NULL | Detailed narrative overview of the offense. |
| `case_type` | ENUM(...) | No | None | None | Offense classification category. |
| `status` | ENUM(...) | No | CHECK | `'Open'` | Workflow state: Open, Under Investigation, Closed, etc. |
| `priority` | ENUM('Low','Medium','High','Critical') | No | None | `'Medium'` | Investigative resource priority tier. |
| `incident_location` | VARCHAR(200) | No | None | None | Address or street block where offense occurred. |
| `date_reported` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Official date and time complaint was logged. |
| `date_closed` | DATETIME | Yes | CHECK | NULL | Timestamp when case was officially resolved. |
| `created_by` | INT | No | **FK** $\to$ `users` | None | Personnel user who created the case record. |
| `is_fictional` | BOOLEAN | No | CHECK (`is_fictional = TRUE`) | `TRUE` | Academic demonstration flag enforcing isolation. |
| `created_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Initial database insertion timestamp. |
| `updated_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Automatic update timestamp on record edit. |

---

## Table 4: `persons`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `person_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `first_name` | VARCHAR(50) | No | None | None | Given name of fictional individual. |
| `last_name` | VARCHAR(50) | No | None | None | Surname of fictional individual. |
| `date_of_birth` | DATE | Yes | None | NULL | Birth date for demographic analysis. |
| `gender` | ENUM('Male','Female','Non-Binary','Unknown') | No | None | `'Unknown'` | Self-reported or observed gender identity. |
| `phone_contact` | VARCHAR(25) | Yes | None | NULL | Contact telephone number. |
| `address_line` | VARCHAR(200) | Yes | None | NULL | Residential or contact address. |
| `is_fictional` | BOOLEAN | No | CHECK (`is_fictional = TRUE`) | `TRUE` | Academic demonstration safety constraint. |
| `created_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Persona intake timestamp. |

---

## Table 5: `case_assignments`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `assignment_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `case_id` | INT | No | **FK** $\to$ `cases` | None | Case dossier receiving assignment. |
| `user_id` | INT | No | **FK** $\to$ `users` | None | Personnel assigned to investigation. |
| `assignment_role` | ENUM(...) | No | None | `'Assisting Officer'` | Operational capacity (Lead Investigator, Assisting, Forensic). |
| `assigned_date` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Timestamp assignment commenced. |
| `unassigned_date` | DATETIME | Yes | CHECK | NULL | Timestamp assignment concluded (NULL if active). |
| `is_active` | BOOLEAN | No | CHECK | `TRUE` | Status flag indicating ongoing assignment. |
| `notes` | VARCHAR(255) | Yes | None | NULL | Specific briefing or operational scope notes. |
| `active_assignment_key` | VARCHAR(64) GENERATED | Yes | **UK** | VIRTUAL | Virtual key preventing duplicate active user assignments. |
| `active_lead_key` | VARCHAR(64) GENERATED | Yes | **UK** | VIRTUAL | Virtual key enforcing max 1 active lead investigator. |

---

## Table 6: `case_persons`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `case_person_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `case_id` | INT | No | **FK** $\to$ `cases` | None | Reference to criminal case dossier. |
| `person_id` | INT | No | **FK** $\to$ `persons` | None | Reference to linked fictional individual. |
| `role_in_case` | ENUM(...) | No | None | None | Legal role: Suspect, Victim, Witness, etc. |
| `statement_summary` | TEXT | Yes | None | NULL | Abstract of interview or deposition statement. |
| `added_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Timestamp link was officially registered. |

---

## Table 7: `evidence`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `evidence_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `case_id` | INT | No | **FK** $\to$ `cases` | None | Parent criminal case file. |
| `evidence_code` | VARCHAR(50) | No | **UK** (`uq_evidence_code`) | None | Unique tracking barcode / evidence tag code. |
| `evidence_type` | ENUM(...) | No | None | None | Physical, Digital, Forensic, Weapon, Document. |
| `description` | TEXT | No | None | None | Item physical appearance and identifying markings. |
| `current_storage_location`| VARCHAR(100) | No | None | None | Locker, vault, or laboratory location. |
| `current_custody_status` | ENUM(...) | No | None | `'Collected'` | Current legal status in chain of custody. |
| `collected_date` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Date item was discovered and secured. |
| `collected_by` | INT | Yes | **FK** $\to$ `users` | NULL | Officer who originally cataloged item. |
| `created_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Record creation timestamp. |

---

## Table 8: `evidence_custody_log`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `custody_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key for log entry. |
| `evidence_id` | INT | No | **FK** $\to$ `evidence` | None | Evidence item being transferred. |
| `previous_status` | ENUM(...) | Yes | None | NULL | Pre-transfer custody status. |
| `new_status` | ENUM(...) | No | None | None | Post-transfer custody status. |
| `from_location` | VARCHAR(100) | Yes | None | NULL | Originating facility or storage location. |
| `to_location` | VARCHAR(100) | No | None | None | Destination storage location or lab. |
| `handled_by` | INT | Yes | **FK** $\to$ `users` | NULL | Personnel handling custody (NULL if unverified). |
| `reason_for_transfer` | VARCHAR(255) | No | None | None | Legal justification for transfer. |
| `logged_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Exact moment transfer was registered. |

---

## Table 9: `investigation_notes`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `note_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `case_id` | INT | No | **FK** $\to$ `cases` | None | Associated criminal case file. |
| `author_id` | INT | No | **FK** $\to$ `users` | None | Investigator who authored the note. |
| `note_title` | VARCHAR(150) | No | None | None | Headline or summary of investigative progress. |
| `note_body` | TEXT | No | None | None | Detailed diary entry or interview memorandum. |
| `is_confidential` | BOOLEAN | No | None | `FALSE` | Flag restricting visibility to assigned investigators. |
| `logged_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Timestamp note was logged. |

---

## Table 10: `audit_log`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `log_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `table_name` | VARCHAR(50) | No | None | None | Modified database table. |
| `record_id` | INT | No | None | None | Primary key value of modified row. |
| `operation_type` | ENUM('INSERT','UPDATE','DELETE') | No | None | None | DML action that triggered audit entry. |
| `old_values` | JSON | Yes | None | NULL | Pre-modification state serialized as JSON. |
| `new_values` | JSON | Yes | None | NULL | Post-modification state serialized as JSON. |
| `performed_by` | VARCHAR(50) | Yes | None | NULL | Authenticated web session username (or NULL). |
| `timestamp` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Moment trigger fired. |

---

## Table 11: `iucr_codes`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `iucr_code` | VARCHAR(10) | No | **PK** | None | Illinois Uniform Crime Reporting 4-character code. |
| `primary_type` | VARCHAR(50) | No | None | None | Canonical primary crime category. |
| `description` | VARCHAR(120) | No | None | None | Canonical subcategory specification. |
| `fbi_code` | VARCHAR(10) | Yes | None | NULL | National Incident-Based Reporting System code. |
| `is_active` | BOOLEAN | No | None | `TRUE` | Indicates whether code is actively in use. |

---

## Table 12: `public_crime_incidents`
| Column Name | MySQL Data Type | Nullable | Key / Constraint | Default | Business Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `incident_id` | INT AUTO_INCREMENT | No | **PK** | None | Surrogate primary key. |
| `source_id` | BIGINT | No | **UK** (`uq_incident_source`) | None | Immutable Socrata SODA API identifier. |
| `case_number` | VARCHAR(25) | Yes | None | NULL | Chicago Police Department Records Division number. |
| `incident_date` | DATETIME | No | None | None | Estimated date and time offense occurred. |
| `block` | VARCHAR(120) | Yes | None | NULL | Partially redacted block address. |
| `source_iucr_code` | VARCHAR(10) | Yes | None | NULL | Exact raw IUCR string from public API payload. |
| `source_primary_type` | VARCHAR(50) | No | None | None | Exact raw primary type from public API payload. |
| `source_description` | VARCHAR(120) | Yes | None | NULL | Exact raw subcategory from public API payload. |
| `canonical_iucr_code`| VARCHAR(10) | Yes | **FK** $\to$ `iucr_codes` | NULL | Normalized lookup reference (NULL if unmapped). |
| `location_description`| VARCHAR(100) | Yes | None | NULL | Property description (Street, Residence, Store). |
| `arrest_made` | BOOLEAN | Yes | None | NULL | Three-valued flag (TRUE/FALSE/NULL) for arrest. |
| `domestic` | BOOLEAN | Yes | None | NULL | Three-valued flag (TRUE/FALSE/NULL) for domestic. |
| `beat` | VARCHAR(10) | Yes | None | NULL | Police beat geographic sector car zone. |
| `district` | VARCHAR(10) | Yes | None | NULL | Police district numeric code. |
| `ward` | INT | Yes | None | NULL | City council ward. |
| `community_area` | VARCHAR(15) | Yes | None | NULL | Chicago community area number. |
| `fbi_code` | VARCHAR(10) | Yes | None | NULL | FBI NIBRS code. |
| `latitude` | DECIMAL(11, 8) | Yes | None | NULL | Geographic coordinate latitude. |
| `longitude` | DECIMAL(11, 8) | Yes | None | NULL | Geographic coordinate longitude. |
| `incident_year` | INT | No | CHECK (`incident_year >= 2001`) | None | Reporting calendar year. |
| `updated_on` | DATETIME | Yes | None | NULL | Public portal last update timestamp. |
| `imported_at` | DATETIME | No | None | `CURRENT_TIMESTAMP` | Local ingestion timestamp. |
