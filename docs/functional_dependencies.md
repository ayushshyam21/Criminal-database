# Functional Dependencies & Candidate Key Analysis
**Project:** Criminal Case Management & Crime Analytics System (Project Evaluation)  
**Database:** `crime_db`  
**Standard:** Relational Database Theory & Decomposition Analysis  

---

## 1. Mathematical Notation & Formal Definitions
* Let $R(A_1, A_2, \dots, A_n)$ denote a relation schema.
* An attribute set $X \subseteq R$ functionally determines $Y \subseteq R$ ($X \to Y$) if in every legal instance $r(R)$, any two tuples agreeing on $X$ must agree on $Y$.
* A **Candidate Key** $K$ is a superkey ($K \to R$) such that no proper subset $K' \subset K$ satisfies $K' \to R$ (minimality).
* A **Superkey** is any set of attributes containing a candidate key.

---

## 2. Table-by-Table Functional Dependency Specifications

### 1. `police_stations`
* **Attributes:** `(station_id, station_name, district_code, address, phone, created_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{station\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{station\_name}\}$ (Natural Unique Facility Name)
  3. $CK_3 = \{\text{district\_code}\}$ (Natural Unique Precinct Code)
* **Minimal Functional Dependencies:**
  * $\text{station\_id} \to \{\text{station\_name}, \text{district\_code}, \text{address}, \text{phone}, \text{created\_at}\}$
  * $\text{station\_name} \to \{\text{station\_id}, \text{district\_code}, \text{address}, \text{phone}, \text{created\_at}\}$
  * $\text{district\_code} \to \{\text{station\_id}, \text{station\_name}, \text{address}, \text{phone}, \text{created\_at}\}$

### 2. `users`
* **Attributes:** `(user_id, station_id, username, email, password_hash, role, full_name, badge_number, is_active, created_at, updated_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{user\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{username}\}$ (Unique Login Handle)
  3. $CK_3 = \{\text{email}\}$ (Unique Certified Address)
  4. $CK_4 = \{\text{badge\_number}\}$ (Unique Identifier for Sworn Officers)
* **Minimal Functional Dependencies:**
  * $\text{user\_id} \to \{\text{station\_id}, \text{username}, \text{email}, \text{password\_hash}, \text{role}, \text{full\_name}, \text{badge\_number}, \text{is\_active}, \text{created\_at}, \text{updated\_at}\}$
  * $\text{username} \to \text{user\_id}$
  * $\text{email} \to \text{user\_id}$
  * $\text{badge\_number} \to \text{user\_id}$

### 3. `cases`
* **Attributes:** `(case_id, case_number, station_id, title, description, case_type, status, priority, incident_location, date_reported, date_closed, created_by, is_fictional, created_at, updated_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{case\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{case\_number}\}$ (Unique Natural Departmental File Code)
* **Minimal Functional Dependencies:**
  * $\text{case\_id} \to \{\text{case\_number}, \text{station\_id}, \text{title}, \text{description}, \text{case\_type}, \text{status}, \text{priority}, \text{incident\_location}, \text{date\_reported}, \text{date\_closed}, \text{created\_by}, \text{is\_fictional}, \text{created\_at}, \text{updated\_at}\}$
  * $\text{case\_number} \to \text{case\_id}$

### 4. `persons`
* **Attributes:** `(person_id, first_name, last_name, date_of_birth, gender, phone_contact, address_line, is_fictional, created_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{person\_id}\}$ (Surrogate Primary Key)
* **Minimal Functional Dependencies:**
  * $\text{person\_id} \to \{\text{first\_name}, \text{last\_name}, \text{date\_of\_birth}, \text{gender}, \text{phone\_contact}, \text{address\_line}, \text{is\_fictional}, \text{created\_at}\}$

### 5. `case_assignments`
* **Attributes:** `(assignment_id, case_id, user_id, assignment_role, assigned_date, unassigned_date, is_active, notes, active_assignment_key, active_lead_key)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{assignment\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{active\_assignment\_key}\}$ (Conditional candidate key over active assignments)
  3. $CK_3 = \{\text{active\_lead\_key}\}$ (Conditional candidate key enforcing single active lead)
* **Minimal Functional Dependencies:**
  * $\text{assignment\_id} \to \{\text{case\_id}, \text{user\_id}, \text{assignment\_role}, \text{assigned\_date}, \text{unassigned\_date}, \text{is\_active}, \text{notes}, \text{active\_assignment\_key}, \text{active\_lead\_key}\}$
  * *Note on Historical Reassignment:* When $\text{is\_active} = \text{FALSE}$, $\{\text{case\_id}, \text{user\_id}\}$ is NOT a candidate key because an officer may have multiple past assignments over time. Each past assignment is uniquely identified by `assignment_id`.

### 6. `case_persons`
* **Attributes:** `(case_person_id, case_id, person_id, role_in_case, statement_summary, added_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{case\_person\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{case\_id}, \text{person\_id}, \text{role\_in\_case}\}$ (Compound Natural Key)
* **Minimal Functional Dependencies:**
  * $\text{case\_person\_id} \to \{\text{case\_id}, \text{person\_id}, \text{role\_in\_case}, \text{statement\_summary}, \text{added\_at}\}$
  * $\{\text{case\_id}, \text{person\_id}, \text{role\_in\_case}\} \to \{\text{case\_person\_id}, \text{statement\_summary}, \text{added\_at}\}$

### 7. `evidence`
* **Attributes:** `(evidence_id, case_id, evidence_code, evidence_type, description, current_storage_location, current_custody_status, collected_date, collected_by, created_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{evidence\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{evidence\_code}\}$ (Unique Evidence Barcode / Tag)
* **Minimal Functional Dependencies:**
  * $\text{evidence\_id} \to \{\text{case\_id}, \text{evidence\_code}, \text{evidence\_type}, \text{description}, \text{current\_storage\_location}, \text{current\_custody\_status}, \text{collected\_date}, \text{collected\_by}, \text{created\_at}\}$
  * $\text{evidence\_code} \to \text{evidence\_id}$

### 8. `evidence_custody_log`
* **Attributes:** `(custody_id, evidence_id, previous_status, new_status, from_location, to_location, handled_by, reason_for_transfer, logged_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{custody\_id}\}$ (Surrogate Primary Key)
* **Minimal Functional Dependencies:**
  * $\text{custody\_id} \to \{\text{evidence\_id}, \text{previous\_status}, \text{new\_status}, \text{from\_location}, \text{to\_location}, \text{handled\_by}, \text{reason\_for\_transfer}, \text{logged\_at}\}$

### 9. `investigation_notes`
* **Attributes:** `(note_id, case_id, author_id, note_title, note_body, is_confidential, logged_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{note\_id}\}$ (Surrogate Primary Key)
* **Minimal Functional Dependencies:**
  * $\text{note\_id} \to \{\text{case\_id}, \text{author\_id}, \text{note\_title}, \text{note\_body}, \text{is\_confidential}, \text{logged\_at}\}$

### 10. `audit_log`
* **Attributes:** `(log_id, table_name, record_id, operation_type, old_values, new_values, performed_by, timestamp)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{log\_id}\}$ (Surrogate Primary Key)
* **Minimal Functional Dependencies:**
  * $\text{log\_id} \to \{\text{table\_name}, \text{record\_id}, \text{operation\_type}, \text{old\_values}, \text{new\_values}, \text{performed\_by}, \text{timestamp}\}$

### 11. `iucr_codes`
* **Attributes:** `(iucr_code, primary_type, description, fbi_code, is_active)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{iucr\_code}\}$ (Canonical IUCR Standard Code)
* **Minimal Functional Dependencies:**
  * $\text{iucr\_code} \to \{\text{primary\_type}, \text{description}, \text{fbi\_code}, \text{is\_active}\}$

### 12. `public_crime_incidents`
* **Attributes:** `(incident_id, source_id, case_number, incident_date, block, source_iucr_code, source_primary_type, source_description, canonical_iucr_code, location_description, arrest_made, domestic, beat, district, ward, community_area, fbi_code, latitude, longitude, incident_year, updated_on, imported_at)`
* **Candidate Keys:**
  1. $CK_1 = \{\text{incident\_id}\}$ (Surrogate Primary Key)
  2. $CK_2 = \{\text{source\_id}\}$ (Immutable External Socrata SODA Identifier)
* **Minimal Functional Dependencies:**
  * $\text{source\_id} \to \{\text{incident\_id}, \text{case\_number}, \text{incident\_date}, \text{block}, \text{source\_iucr\_code}, \text{source\_primary\_type}, \text{source\_description}, \text{canonical\_iucr\_code}, \text{location\_description}, \text{arrest\_made}, \text{domestic}, \text{beat}, \text{district}, \text{ward}, \text{community\_area}, \text{fbi\_code}, \text{latitude}, \text{longitude}, \text{incident\_year}, \text{updated\_on}, \text{imported\_at}\}$
  * $\text{incident\_id} \to \text{source\_id}$
  * *Crucial Real-World Note:* $\text{source\_iucr\_code} \not\to \text{source\_primary\_type}$ strictly in raw historical feeds due to multi-decade municipal reclassifications. Storing raw reported attributes separately from the canonical lookup relation `iucr_codes` preserves raw open data without invalidating BCNF.
