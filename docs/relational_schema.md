# Relational Schema Specification
**Project:** Criminal Case Management & Crime Analytics System (Project Evaluation)  
**Database:** `crime_db`  
**Engine:** MySQL 8.0+ / 9.x (InnoDB)  
**Total Relations:** 12 Normalized Tables  

---

## 1. Relational Schema Formal Notation
*Primary Keys are underlined ($\underline{\text{column}}$); Candidate Keys are labeled with superscripts ($^\text{CK}$); Foreign Keys reference parent relations with directional arrows ($\to$).*

1. **POLICE_STATIONS** (
   $\underline{\text{station\_id}}$, 
   $\text{station\_name}^\text{CK}$, 
   $\text{district\_code}^\text{CK}$, 
   $\text{address}$, 
   $\text{phone}$, 
   $\text{created\_at}$
)

2. **USERS** (
   $\underline{\text{user\_id}}$, 
   $\text{station\_id} \to \text{POLICE\_STATIONS(station\_id)}$, 
   $\text{username}^\text{CK}$, 
   $\text{email}^\text{CK}$, 
   $\text{password\_hash}$, 
   $\text{role}$, 
   $\text{full\_name}$, 
   $\text{badge\_number}^\text{CK}$, 
   $\text{is\_active}$, 
   $\text{created\_at}$, 
   $\text{updated\_at}$
)

3. **PERSONS** (
   $\underline{\text{person\_id}}$, 
   $\text{first\_name}$, 
   $\text{last\_name}$, 
   $\text{date\_of\_birth}$, 
   $\text{gender}$, 
   $\text{phone\_contact}$, 
   $\text{address\_line}$, 
   $\text{is\_fictional}$, 
   $\text{created\_at}$
)

4. **CASES** (
   $\underline{\text{case\_id}}$, 
   $\text{case\_number}^\text{CK}$, 
   $\text{station\_id} \to \text{POLICE\_STATIONS(station\_id)}$, 
   $\text{title}$, 
   $\text{description}$, 
   $\text{case\_type}$, 
   $\text{status}$, 
   $\text{priority}$, 
   $\text{incident\_location}$, 
   $\text{date\_reported}$, 
   $\text{date\_closed}$, 
   $\text{created\_by} \to \text{USERS(user\_id)}$, 
   $\text{is\_fictional}$, 
   $\text{created\_at}$, 
   $\text{updated\_at}$
)

5. **CASE_ASSIGNMENTS** (
   $\underline{\text{assignment\_id}}$, 
   $\text{case\_id} \to \text{CASES(case\_id)}$, 
   $\text{user\_id} \to \text{USERS(user\_id)}$, 
   $\text{assignment\_role}$, 
   $\text{assigned\_date}$, 
   $\text{unassigned\_date}$, 
   $\text{is\_active}$, 
   $\text{notes}$, 
   $\text{active\_assignment\_key}^\text{CK}$, 
   $\text{active\_lead\_key}^\text{CK}$
)

6. **CASE_PERSONS** (
   $\underline{\text{case\_person\_id}}$, 
   $\text{case\_id} \to \text{CASES(case\_id)}$, 
   $\text{person\_id} \to \text{PERSONS(person\_id)}$, 
   $\text{role\_in\_case}$, 
   $\text{statement\_summary}$, 
   $\text{added\_at}$
)  
*Alternate Candidate Key:* ($\text{case\_id}$, $\text{person\_id}$, $\text{role\_in\_case}$)

7. **EVIDENCE** (
   $\underline{\text{evidence\_id}}$, 
   $\text{case\_id} \to \text{CASES(case\_id)}$, 
   $\text{evidence\_code}^\text{CK}$, 
   $\text{evidence\_type}$, 
   $\text{description}$, 
   $\text{current\_storage\_location}$, 
   $\text{current\_custody\_status}$, 
   $\text{collected\_date}$, 
   $\text{collected\_by} \to \text{USERS(user\_id)}$, 
   $\text{created\_at}$
)

8. **EVIDENCE_CUSTODY_LOG** (
   $\underline{\text{custody\_id}}$, 
   $\text{evidence\_id} \to \text{EVIDENCE(evidence\_id)}$, 
   $\text{previous\_status}$, 
   $\text{new\_status}$, 
   $\text{from\_location}$, 
   $\text{to\_location}$, 
   $\text{handled\_by} \to \text{USERS(user\_id)}$, 
   $\text{reason\_for\_transfer}$, 
   $\text{logged\_at}$
)

9. **INVESTIGATION_NOTES** (
   $\underline{\text{note\_id}}$, 
   $\text{case\_id} \to \text{CASES(case\_id)}$, 
   $\text{author\_id} \to \text{USERS(user\_id)}$, 
   $\text{note\_title}$, 
   $\text{note\_body}$, 
   $\text{is\_confidential}$, 
   $\text{logged\_at}$
)

10. **AUDIT_LOG** (
    $\underline{\text{log\_id}}$, 
    $\text{table\_name}$, 
    $\text{record\_id}$, 
    $\text{operation\_type}$, 
    $\text{old\_values}$, 
    $\text{new\_values}$, 
    $\text{performed\_by}$, 
    $\text{timestamp}$
)

11. **IUCR_CODES** (
    $\underline{\text{iucr\_code}}$, 
    $\text{primary\_type}$, 
    $\text{description}$, 
    $\text{fbi\_code}$, 
    $\text{is\_active}$
)

12. **PUBLIC_CRIME_INCIDENTS** (
    $\underline{\text{incident\_id}}$, 
    $\text{source\_id}^\text{CK}$, 
    $\text{case\_number}$, 
    $\text{incident\_date}$, 
    $\text{block}$, 
    $\text{source\_iucr\_code}$, 
    $\text{source\_primary\_type}$, 
    $\text{source\_description}$, 
    $\text{canonical\_iucr\_code} \to \text{IUCR\_CODES(iucr\_code)}$, 
    $\text{location\_description}$, 
    $\text{arrest\_made}$, 
    $\text{domestic}$, 
    $\text{beat}$, 
    $\text{district}$, 
    $\text{ward}$, 
    $\text{community\_area}$, 
    $\text{fbi\_code}$, 
    $\text{latitude}$, 
    $\text{longitude}$, 
    $\text{incident\_year}$, 
    $\text{updated\_on}$, 
    $\text{imported\_at}$
)

---

## 2. Referential Integrity & Action Matrix

| Foreign Key | Source Column | Target Column | ON DELETE | ON UPDATE |
| :--- | :--- | :--- | :---: | :---: |
| `fk_users_station` | `users.station_id` | `police_stations.station_id` | `SET NULL` | `CASCADE` |
| `fk_cases_station` | `cases.station_id` | `police_stations.station_id` | `RESTRICT` | `CASCADE` |
| `fk_cases_creator` | `cases.created_by` | `users.user_id` | `RESTRICT` | `CASCADE` |
| `fk_assign_case` | `case_assignments.case_id` | `cases.case_id` | `CASCADE` | `CASCADE` |
| `fk_assign_user` | `case_assignments.user_id` | `users.user_id` | `RESTRICT` | `CASCADE` |
| `fk_cp_case` | `case_persons.case_id` | `cases.case_id` | `CASCADE` | `CASCADE` |
| `fk_cp_person` | `case_persons.person_id` | `persons.person_id` | `RESTRICT` | `CASCADE` |
| `fk_evidence_case` | `evidence.case_id` | `cases.case_id` | `CASCADE` | `CASCADE` |
| `fk_evidence_collector` | `evidence.collected_by` | `users.user_id` | `SET NULL` | `CASCADE` |
| `fk_custody_evidence` | `evidence_custody_log.evidence_id` | `evidence.evidence_id` | `CASCADE` | `CASCADE` |
| `fk_custody_handler` | `evidence_custody_log.handled_by` | `users.user_id` | `SET NULL` | `CASCADE` |
| `fk_notes_case` | `investigation_notes.case_id` | `cases.case_id` | `CASCADE` | `CASCADE` |
| `fk_notes_author` | `investigation_notes.author_id` | `users.user_id` | `RESTRICT` | `CASCADE` |
| `fk_incident_canonical_iucr` | `public_crime_incidents.canonical_iucr_code` | `iucr_codes.iucr_code` | `SET NULL` | `CASCADE` |
