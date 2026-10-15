# Normalization Analysis & Normal Form Proof (1NF $\to$ BCNF)
**Project:** Criminal Case Management & Crime Analytics System (Project Evaluation)  
**Database:** `crime_db`  
**Theoretical Baseline:** Relational Database Normalization Theory (Codd, Boyce)  

---

## 1. Normal Form Definitions & Criteria

1. **First Normal Form (1NF):**
   * A relation $R$ is in 1NF if and only if all underlying domains contain exclusively atomic (indivisible) scalar values, there are no repeating groups or multivalued arrays, and every tuple is uniquely identifiable via a designated Primary Key.

2. **Second Normal Form (2NF):**
   * A relation $R$ is in 2NF if and only if it is in 1NF and every non-prime attribute $A \in R$ is **fully functionally dependent** on every candidate key of $R$. That is, no non-prime attribute is functionally dependent on a proper subset of any composite candidate key (no partial functional dependency).

3. **Third Normal Form (3NF):**
   * A relation $R$ is in 3NF if and only if it is in 2NF and whenever a non-trivial functional dependency $X \to A$ holds in $R$, either:
     * $X$ is a superkey of $R$, OR
     * $A$ is a prime attribute (a member of some candidate key of $R$).
   * Alternatively stated: No non-prime attribute transitively depends on any candidate key ($X \to Y \to Z$ where $Y$ is not a superkey).

4. **Boyce-Codd Normal Form (BCNF):**
   * A relation $R$ is in BCNF if and only if for every non-trivial functional dependency $X \to Y$ holding in $R$, **$X$ is a superkey** of $R$. BCNF eliminates all anomalies arising from functional dependencies, including those where a prime attribute depends on a non-superkey.

---

## 2. Table-by-Table Normalization Proof

### 1. `police_stations`
* **Candidate Keys:** $CK_1 = \{\text{station\_id}\}$, $CK_2 = \{\text{station\_name}\}$, $CK_3 = \{\text{district\_code}\}$.
* **1NF:** Addresses, station names, district codes, and phone numbers are atomic strings. Satisfies 1NF.
* **2NF:** All candidate keys are single attributes ($\text{cardinality} = 1$). A proper subset of a single attribute is the empty set $\emptyset$, making partial dependency mathematically impossible. Satisfies 2NF.
* **3NF:** Dependencies exist solely from candidate keys to non-prime attributes:
  $\text{station\_id} \to \{\text{address}, \text{phone}, \text{created\_at}\}$. There is no dependency among non-prime attributes ($\text{address} \not\to \text{phone}$). Satisfies 3NF.
* **BCNF:** The non-trivial dependencies have left-hand determinants $\text{station\_id}$, $\text{station\_name}$, and $\text{district\_code}$. Each determinant is an explicit candidate key and therefore a superkey. **Satisfies BCNF.**

---

### 2. `users`
* **Candidate Keys:** $CK_1 = \{\text{user\_id}\}$, $CK_2 = \{\text{username}\}$, $CK_3 = \{\text{email}\}$, $CK_4 = \{\text{badge\_number}\}$.
* **1NF:** All attributes (usernames, hashed passwords, roles, names) are atomic scalars. Satisfies 1NF.
* **2NF:** All candidate keys consist of single attributes. Partial functional dependencies cannot exist. Satisfies 2NF.
* **3NF:** No non-prime attribute determines any other non-prime attribute ($\text{full\_name} \not\to \text{role}$). Alternate candidate keys (`username`, `email`, `badge_number`) are prime attributes. Satisfies 3NF.
* **BCNF:** For all non-trivial FDs $X \to Y$, the determinant $X \in \{\text{user\_id}, \text{username}, \text{email}, \text{badge\_number}\}$ is a candidate key / superkey. **Satisfies BCNF.**

---

### 3. `cases`
* **Candidate Keys:** $CK_1 = \{\text{case\_id}\}$, $CK_2 = \{\text{case\_number}\}$.
* **1NF:** Case numbers, titles, priorities, and timestamps are atomic. Satisfies 1NF.
* **2NF:** Candidate keys are single-column attributes. Partial dependency is impossible. Satisfies 2NF.
* **3NF:** Foreign keys `station_id` and `created_by` do not determine case-specific attributes like `title` or `incident_location`. No transitive dependency exists among non-prime attributes. Satisfies 3NF.
* **BCNF:** All determinants ($\text{case\_id}$, $\text{case\_number}$) are superkeys. **Satisfies BCNF.**

---

### 4. `persons`
* **Candidate Keys:** $CK_1 = \{\text{person\_id}\}$.
* **1NF:** First names, last names, DOBs, and phone numbers are atomic. Satisfies 1NF.
* **2NF:** Single-column candidate key. Satisfies 2NF.
* **3NF:** No non-prime attribute determines another non-prime attribute ($\text{last\_name} \not\to \text{phone\_contact}$). Satisfies 3NF.
* **BCNF:** Determinant $\text{person\_id}$ is a superkey. **Satisfies BCNF.**

---

### 5. `case_assignments`
* **Candidate Keys:** $CK_1 = \{\text{assignment\_id}\}$, $CK_2 = \{\text{active\_assignment\_key}\}$, $CK_3 = \{\text{active\_lead\_key}\}$.
* **1NF:** Assignment role, dates, notes are atomic. Satisfies 1NF.
* **2NF:** Surrogate PK `assignment_id` is a single column. For historical tracking, non-prime attributes (`assignment_role`, `assigned_date`, `unassigned_date`, `is_active`) depend on the full surrogate key `assignment_id`. No partial dependency exists. Satisfies 2NF.
* **3NF:** No non-prime attribute determines another non-prime attribute. Satisfies 3NF.
* **BCNF:** All non-trivial functional dependencies have determinants that are superkeys. **Satisfies BCNF.**

---

### 6. `case_persons`
* **Candidate Keys:** $CK_1 = \{\text{case\_person\_id}\}$, $CK_2 = \{\text{case\_id}, \text{person\_id}, \text{role\_in\_case}\}$.
* **1NF:** Text summary and role classifications are atomic. Satisfies 1NF.
* **2NF:** For the composite candidate key $\{\text{case\_id}, \text{person\_id}, \text{role\_in\_case}\}$, the non-prime attribute `statement_summary` requires the full combination of the case, the specific person, and their specific role in that case (a suspect's statement differs from their witness statement if they hold multiple roles across incidents). No partial dependency exists. Satisfies 2NF.
* **3NF:** No non-prime attribute determines any other attribute. Satisfies 3NF.
* **BCNF:** Both determinants ($\text{case\_person\_id}$ and $\{\text{case\_id}, \text{person\_id}, \text{role\_in\_case}\}$) are superkeys. **Satisfies BCNF.**

---

### 7. `evidence`
* **Candidate Keys:** $CK_1 = \{\text{evidence\_id}\}$, $CK_2 = \{\text{evidence\_code}\}$.
* **1NF:** Evidence codes, types, locations, and status flags are atomic. Satisfies 1NF.
* **2NF:** Single-column candidate keys prevent partial functional dependencies. Satisfies 2NF.
* **3NF:** `current_storage_location` does not determine `current_custody_status` (different items in the same vault locker can have distinct custody statuses). No transitive dependencies exist. Satisfies 3NF.
* **BCNF:** Determinants $\text{evidence\_id}$ and $\text{evidence\_code}$ are superkeys. **Satisfies BCNF.**

---

### 8. `evidence_custody_log`
* **Candidate Keys:** $CK_1 = \{\text{custody\_id}\}$.
* **1NF:** Locations, statuses, reasons, and timestamps are atomic. Satisfies 1NF.
* **2NF:** Single-column candidate key. Satisfies 2NF.
* **3NF:** `handled_by` does not determine `reason_for_transfer` or `to_location`. Non-prime attributes are mutually independent. Satisfies 3NF.
* **BCNF:** Determinant $\text{custody\_id}$ is a superkey. **Satisfies BCNF.**

---

### 9. `investigation_notes`
* **Candidate Keys:** $CK_1 = \{\text{note\_id}\}$.
* **1NF:** Note titles, bodies, and confidentiality flags are atomic. Satisfies 1NF.
* **2NF:** Single-column candidate key. Satisfies 2NF.
* **3NF:** `author_id` does not determine note content. No transitive dependencies. Satisfies 3NF.
* **BCNF:** Determinant $\text{note\_id}$ is a superkey. **Satisfies BCNF.**

---

### 10. `audit_log`
* **Candidate Keys:** $CK_1 = \{\text{log\_id}\}$.
* **1NF:** System table names, operation types, timestamps, and serialized JSON payloads are atomic scalar/document values. Satisfies 1NF.
* **2NF:** Single-column candidate key. Satisfies 2NF.
* **3NF:** No transitive dependencies. Satisfies 3NF.
* **BCNF:** Determinant $\text{log\_id}$ is a superkey. **Satisfies BCNF.**

---

### 11. `iucr_codes`
* **Candidate Keys:** $CK_1 = \{\text{iucr\_code}\}$.
* **1NF:** IUCR codes, primary types, descriptions, and FBI codes are atomic. Satisfies 1NF.
* **2NF:** Single-column candidate key. Satisfies 2NF.
* **3NF:** In this reference table, `primary_type` and `description` depend solely on `iucr_code`. Satisfies 3NF.
* **BCNF:** Determinant $\text{iucr\_code}$ is a superkey. **Satisfies BCNF.**

---

### 12. `public_crime_incidents` & The Normalization Resolution
* **Candidate Keys:** $CK_1 = \{\text{incident\_id}\}$, $CK_2 = \{\text{source\_id}\}$.
* **Historical Source Problem:** In raw City of Chicago public data, incidents contain both IUCR code and primary category. Over 25 years of data, municipal agencies occasionally revised categories, meaning raw `source_iucr_code` does not strictly form a valid determinant across all historical years.
* **Normalization Resolution:**
  1. We store raw incident report fields (`source_iucr_code`, `source_primary_type`, `source_description`) as direct attributes of the reported incident. All raw attributes are fully and solely dependent on the unique incident report identifier:
     $$\text{source\_id} \to \{\text{case\_number}, \text{incident\_date}, \text{block}, \text{source\_iucr\_code}, \text{source\_primary\_type}, \text{source\_description}, \dots\}$$
  2. We decompose canonical crime classification standards into the independent reference table `iucr_codes`, linked via nullable foreign key `canonical_iucr_code`.
* **1NF:** Coordinates, timestamps, and blocks are atomic. Satisfies 1NF.
* **2NF:** Candidate keys ($\text{incident\_id}$, $\text{source\_id}$) are single columns; no partial dependencies exist. Satisfies 2NF.
* **3NF:** Within `public_crime_incidents`, all raw attributes describe the specific reported incident and depend directly on $\text{source\_id}$. There are no transitive dependencies between non-prime attributes in this relation. Satisfies 3NF.
* **BCNF:** Determinants $\text{incident\_id}$ and $\text{source\_id}$ are superkeys. **Satisfies BCNF.**
