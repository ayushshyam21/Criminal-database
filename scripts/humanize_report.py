import os
import shutil
import docx

SRC_DOCX = "Criminal_Case_Management_Final_Report.docx"
DST_DOCX = "Criminal_Case_Management_Final_Report_Humanized.docx"

# 1. Create a pristine copy
shutil.copyfile(SRC_DOCX, DST_DOCX)
print(f"Copied {SRC_DOCX} -> {DST_DOCX}")

doc = docx.Document(DST_DOCX)

# Define our humanized text mappings
# (paragraph_index, run_index_or_none, new_text)
# If run_index is None, update p.runs[0].text or full p.text

replacements = {
    # DECLARATION
    17: (0, 'We hereby declare that this project report, titled "CRIMINAL CASE MANAGEMENT & CRIME ANALYTICS SYSTEM", submitted by Ayush Sharma [25BAI1392] and Ojas Sugur [25BAI1222] for the course BACSE202 DATABASE SYSTEMS at the School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology, Chennai, represents authentic, original work carried out by us under the supervision of DR. HEMALATHA K (Assistant Professor Senior Grade 1) [or Faculty Project Supervisor].'),
    18: (0, 'We also confirm that this project report has not been submitted previously, in whole or in part, for any other degree, diploma, course credit, or academic distinction at this or any other educational institution.'),
    19: (0, 'All database schemas, Boyce-Codd Normal Form proofs, SQL procedures, security policies, test execution records, and system interfaces described in this document reflect our actual project implementation. The results and performance metrics discussed have been verified directly on our live MySQL Community Server 9.7 database instance and automated test suites.'),

    # CERTIFICATE
    25: (0, 'This is to certify that the project report entitled "CRIMINAL CASE MANAGEMENT & CRIME ANALYTICS SYSTEM", submitted by Ayush Sharma [25BAI1392] and Ojas Sugur [25BAI1222] to Vellore Institute of Technology, Chennai, in partial fulfillment of the requirements for BACSE202 DATABASE SYSTEMS, is a bonafide record of work completed under my guidance. The report reflects the practical implementation and analysis carried out by the students during the semester.'),
    26: (0, 'The students have documented the technical architecture, normal form evaluations, role-based and multi-level security mechanisms, stored routines, and system test results in accordance with the academic expectations of the course.'),

    # ABSTRACT
    30: (0, 'Managing criminal case records in municipal police stations remains challenging when desks rely on paper diaries or unnormalized spreadsheets. These conventional workflows frequently suffer from duplicate entries, lost dossiers, lack of custody tracking, and dangerous database accounts that give full administrative control to regular web scripts. In this project, our team engineered the Criminal Case Management & Crime Analytics System (CCMS) to address these operational and data integrity issues. Built using Python Flask and MySQL Community Server 9.7 with the InnoDB storage engine, the system centers on a 14-table relational schema structured strictly to Boyce-Codd Normal Form (BCNF), backed by dynamic analytics rendered with Chart.js.'),
    31: (0, 'The core database tracks the complete lifecycle of criminal investigations, linking incidents to suspect, victim, and witness profiles while tracking physical evidence through an immutable chain-of-custody ledger automated by database triggers. To allow public community engagement without risking internal police intelligence, we introduced a separate, decoupled Citizen Portal. Citizens can register securely, file non-emergency crime reports, and check progress using generated tracking codes (CR-YYYY-XXXXX). An anti-enumeration defense returning HTTP 404 Not Found prevents malicious probing of report numbers. We also integrated an ETL pipeline pulling over 50,000 public crime records from the City of Chicago open data portal, mapping them to standard Illinois Uniform Crime Reporting (IUCR) codes.'),
    32: (0, 'System security combines a dual-account least-privilege database model with Bell-LaPadula Multi-Level Security across four tiers (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED) alongside discretionary Need-to-Know assignment checks. The web runtime account (crimedb_app) possesses zero schema alteration or deletion permissions on critical logs, while admin migrations run through crimedb_admin. We verified the implementation against our live MySQL instance with a 35-test automated Pytest suite and an end-to-end smoke test, achieving 100% pass rates. Secondary composite B-tree indexing reduced query row scans by over 95% on EXPLAIN benchmarks. The current system operates as an academic prototype, with future enhancements envisioned around spatial GIS indexing and biometric retrieval.'),
    33: (1, 'Criminal case management, relational databases, MySQL 9.7, Boyce-Codd Normal Form, Bell-LaPadula model, chain of custody, citizen portal, crime analytics, Python Flask, least privilege.'),

    # ACKNOWLEDGEMENT
    36: (0, 'We would like to express our gratitude to our supervisor, DR. HEMALATHA K (Assistant Professor Senior Grade 1), School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology, Chennai, for her continuous advice, constructive feedback, and helpful critiques throughout the planning, implementation, and documentation of this database project.'),
    37: (0, 'We are also thankful to the faculty members and coordinators at VIT Chennai and SCOPE for providing the curriculum and academic resources that helped us explore relational database principles, access control architectures, and web application design. Our appreciation also extends to the open-source software communities behind Python, Flask, SQLAlchemy, MySQL, Bootstrap, and Chart.js, as well as the City of Chicago Department of Innovation and Technology for making public incident datasets freely accessible for academic exploration.'),
    38: (0, 'Finally, we thank each other for close teamwork and shared problem-solving across every stage of the project—from early schema sketches in DA1 to final query optimization and test debugging. We have aimed to describe our design choices, working achievements, and current prototype boundaries as honestly and accurately as possible in this report.'),

    # CHAPTER 1: PROBLEM STATEMENT
    49: (0, 'When handling criminal complaints, police stations must process a wide variety of incidents, from everyday theft and burglary to complex financial fraud, cyber-enabled phishing, and identity theft. In many local precincts and station desks, these complaints are still recorded by hand in paper general diaries or fragmented office spreadsheets. During our initial problem study in Digital Assignment 1 (DA1), we observed several recurring issues that undermine both data reliability and investigative speed in these traditional setups:'),
    50: (1, 'Officers must handwrite complainant details, suspect descriptions, and stolen property logs repeatedly across different registers. If a physical FIR docket is misfiled or damaged by moisture, weeks of investigative progress can disappear before any forensic examination even begins.'),
    51: (1, 'Early computerization efforts often place officer ranks, station telephone numbers, and offense descriptions into every single incident row. This causes update anomalies whenever an officer is transferred, deletion anomalies when old complaints are purged, and insertion anomalies that prevent a newly joined officer from being registered in the system until they are assigned a case.'),
    52: (1, 'In generic record management systems, evidence custody logs are typically stored in standard editable tables. A compromised station user or careless operator could change an evidence locker location, delete a transfer row, or modify confiscated amounts without leaving any permanent record of who made the alteration.'),
    53: (1, 'Many student and small-scale web projects connect their application to MySQL using a single administrative user with blanket privileges (GRANT ALL). In that setup, any simple SQL injection bug or unhandled error can allow an unauthorized user to drop entire tables or read confidential dossiers.'),
    54: (1, 'In basic departmental software, any authenticated officer can freely search and view every case docket in the station. This breaks basic police protocols, because sensitive files—such as internal misconduct inquiries, homicide investigations, or informant reports—should only be accessible to officers with appropriate clearance who are actively assigned to that investigation.'),
    55: (1, 'Victims who register complaints have no direct way to check their case status without visiting the station in person. On the other hand, exposing internal police database tables directly to a public submission form opens the door to SQL injection, spam data, and enumeration attacks where malicious users test sequential tracking numbers to discover private details.'),

    # CHAPTER 2: OBJECTIVES & SCOPE
    57: (0, 'To address these operational bottlenecks systematically, our team established seven concrete engineering objectives that shaped our database modeling and application architecture:'),
    58: (1, 'Design and implement a 14-table relational schema that satisfies Boyce-Codd Normal Form across all tables, ensuring every non-trivial functional dependency relies on a candidate key as its determinant.'),
    59: (1, 'Implement four hierarchical security clearance and classification levels (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED) based on the Bell-LaPadula Simple Security Property ("No Read Up"), paired with active assignment checks for operational Need-to-Know access.'),
    60: (1, 'Configure two dedicated MySQL database accounts: crimedb_admin for DDL migrations and trigger definitions, and crimedb_app for everyday web queries with zero DDL permissions, zero direct write access to custody and audit ledgers, and no delete rights on citizen accounts.'),
    61: (1, 'Create a separate citizen portal (/citizen/*) with independent session management, scrypt password hashing, automated tracking references (CR-YYYY-XXXXX), and an anti-enumeration HTTP 404 response to protect user privacy.'),
    62: (1, 'Integrate an automated ETL pipeline that pulls real public crime records from the City of Chicago Socrata Open Data Portal into public_crime_incidents, normalizing them against Illinois Uniform Crime Reporting (IUCR) lookup codes.'),
    63: (1, 'Implement atomic stored procedures (sp_assign_case), deterministic stored functions (fn_case_duration), DEFINER audit triggers, analytical views, and declarative virtual generated columns directly within MySQL.'),
    64: (1, 'Construct composite secondary B-tree indexes for the most common search and filter queries, and evaluate query performance with MySQL EXPLAIN to measure the exact drop in examined rows.'),

    # CHAPTER 3: LITERATURE SURVEY
    66: (0, 'During the initial literature survey for Digital Assignment 1 (DA1), Ojas Sugur evaluated several academic studies on digital policing, automated FIR systems, and police record architectures. During the final implementation phase, we revisited and expanded this analysis to study relational database normalization and access control models:'),
    68: (0, 'Alongside applied policing research, our work relies heavily on classic database systems and computer security literature. Bell and LaPadula\'s 1973 model provided the theoretical foundation for our four-tier classification and clearance hierarchy. The normalization methodology in Elmasri and Navathe\'s Database Systems (2015) guided our functional dependency breakdown into Boyce-Codd Normal Form. In addition, the transaction isolation, logging, and concurrency principles from Silberschatz et al. (2020) informed our stored procedure design, savepoint rollbacks, and trigger-based audit logging.'),

    # CHAPTER 4: REQUIREMENTS & ROLES
    70: (0, 'The system recognizes four operational user roles, each tied to distinct administrative duties and database access levels:'),
    73: (0, '• FR-1 (Authentication & Password Security): The system must authenticate users securely using salted scrypt password hashing (scrypt:32768:8:1) for both internal police staff and external citizens.'),
    74: (0, '• FR-2 (Multi-Level Security Hierarchy): The application must restrict case visibility according to four clearance ranks: PUBLIC (1), INTERNAL (2), CONFIDENTIAL (3), and RESTRICTED (4).'),
    75: (0, '• FR-3 (Need-to-Know Verification): The backend must deny unassigned officers access to CONFIDENTIAL and RESTRICTED dossiers, returning HTTP 403 Forbidden on direct URL attempts.'),
    76: (0, '• FR-4 (Admin Staff Governance): Administrators must be able to view all personnel via /admin/staff, update their clearance tiers, and enable or disable staff logins.'),
    77: (0, '• FR-5 (Case Dossier CRUD): Authorized officers must be able to create, view, update, and manage the full lifecycle of cases, recording locations, priorities, categories, and closure dates.'),
    78: (0, '• FR-6 (Automated Assignment Routine): The system must execute sp_assign_case to manage investigator assignments atomically, ensuring exactly one active Lead Investigator per case.'),
    79: (0, '• FR-7 (Evidence Custody Ledger): Physical evidence items must be tracked with unique codes, and every change in storage location or custody must trigger an automatic, tamper-evident log entry.'),
    80: (0, '• FR-8 (Investigation Diary Notes): Assigned officers must be able to log dated investigation notes, with a confidentiality toggle that hides sensitive observations from unauthorized users.'),
    81: (0, '• FR-9 (Chicago Open Crimes Analytics): The application must provide interactive charts and filters for over 50,000 public records imported from the City of Chicago open data portal.'),
    82: (0, '• FR-10 (Citizen Portal Intake): Citizens must be able to register separately, submit non-emergency incident reports, and receive a formatted tracking code (CR-YYYY-XXXXX).'),
    83: (0, '• FR-11 (Anti-Enumeration Privacy Defense): When a logged-in citizen attempts to access a report filed by someone else, the system must return HTTP 404 Not Found to prevent ID enumeration.'),
    84: (0, '• FR-12 (SQL Evaluation Workbench): The internal portal must provide an interactive /sql-demo screen where faculty evaluators can execute queries, test views, call stored procedures, and inspect query plans.'),

    # CHAPTER 5: DESIGN & ARCHITECTURE
    86: (0, 'Our web application uses a standard three-tier architecture that cleanly separates user presentation, application security logic, and physical database storage:'),
    87: (1, 'Built using Bootstrap 5.3.3 and Chart.js 4.4.1 templates rendered by Flask\'s Jinja2 engine. Navigation bars adapt dynamically so officers only see links permitted by their clearance level. Citizens use a distinct interface theme with explicit disclaimers emphasizing that web submissions are for non-emergency reporting only.'),
    88: (1, 'Implemented in Python 3.14 using Flask 3.1.2. The security layer (security_service.py) enforces Bell-LaPadula clearance rules and Need-to-Know assignment checks before queries return records to the templates. Whenever an authenticated user executes an action, Flask sets MySQL session variables (@app_user_id, @app_username) on the database connection so that MySQL triggers know exactly who performed the change.'),
    89: (1, 'Powered by MySQL Community Server 9.7 with the InnoDB storage engine. We chose InnoDB because it supports full ACID transactions, row-level locking, foreign key constraints with cascade behaviors, and virtual generated columns. Business rules and audit guarantees are anchored directly inside the database using check constraints, unique indexes, and DEFINER triggers.'),
    91: (0, 'During development, we deliberately avoided connecting the Flask application with an all-powerful root or administrative MySQL user. Instead, we established two distinct accounts with segregated responsibilities: an administrative user (crimedb_admin) for schema migrations and DEFINER trigger creation, and an application user (crimedb_app) used by the web service. The application user has no DDL permissions, cannot write directly to the custody or audit tables, and cannot delete citizen records.'),
    94: (0, 'To stop officers from browsing sensitive files without authorization, we assigned integer ranks to our clearance levels: PUBLIC = 1, INTERNAL = 2, CONFIDENTIAL = 3, and RESTRICTED = 4. Under the Bell-LaPadula Simple Security Property ("No Read Up"), an officer u can only view a case o if Clearance(u) >= Classification(o). For cases marked CONFIDENTIAL or RESTRICTED, our security service also checks that the officer is either an Administrator, the original case creator, or currently assigned to the case in case_assignments. Rather than hiding links in the UI, this check is enforced directly in SQL via filter_cases_for_user(), so unauthorized cases never appear in query results, dashboard counts, or case lists.'),

    # CHAPTER 6: DATABASE DESIGN & EER
    96: (0, 'Our database design changed substantially as the project matured. In DA1, Ojas Sugur proposed a preliminary 6-table concept (POLICE_STATION, CRIME, CRIMINAL, VICTIM, and bridge tables CRIMINALS_OF_CRIME and VICTIM_OF_CRIME). That initial design helped us model many-to-many relationships between suspects, victims, and offenses. However, when we started developing the web application, we realized that an operational police system must track internal station personnel, custody transfers, investigation notes, and public citizen submissions in distinct tables. This led us to develop our final 14-table BCNF schema.'),
    98: (0, 'In the Enhanced Entity-Relationship (EER) model, police personnel exhibit Disjoint Total Specialization (d, t). All department members share foundational attributes like username, email, password hash, and active status, but they specialize into three mutually exclusive operational roles: Administrator, Police Officer, and Investigator. Rather than creating three separate child tables with identical columns, we used a Single Table with Type Discriminator pattern in users using MySQL ENUMs. This avoids unnecessary outer joins while preserving complete relational integrity.'),
    103: (0, 'The complete entity-relationship model spans 14 tables organized across four functional areas: the Police Operations Domain (police_stations, users, cases, persons, case_assignments, case_persons, evidence, investigation_notes), the Immutable Audit Domain (evidence_custody_log, audit_log), the Public Open Data Domain (iucr_codes, public_crime_incidents), and the Citizen Engagement Domain (citizens, citizen_reports). Foreign keys connect these tables to ensure that incidents, personnel, and evidence stay properly synchronized.'),

    # CHAPTER 7 & 8: SCHEMA & NORMALIZATION
    108: (0, 'The formal relational schema for our 14 tables is detailed below. Primary keys are marked with [PK], alternate candidate keys with [CK], and foreign keys reference their respective parent tables:'),
    126: (0, 'A relational schema R is in Boyce-Codd Normal Form (BCNF) if and only if, for every non-trivial functional dependency X -> Y, the determinant X is a superkey of R. When developing our schema across DA1 and DA2, we systematically eliminated normalization anomalies: moving from unnormalized data to 1NF by ensuring atomic attributes; reaching 2NF by removing partial key dependencies; reaching 3NF by removing transitive dependencies; and finally verifying that every table satisfies BCNF.'),
    127: (1, 'The candidate keys for this table are {user_id}, {username}, {email}, and {badge_number}. Because every functional dependency in this relation has one of these candidate keys as its determinant, the relation satisfies BCNF.'),
    128: (1, 'The candidate keys are {case_id} and {case_number}. Every case attribute—such as title, category, priority, and classification level—is uniquely determined by these keys. Since both determinants are superkeys, the table satisfies BCNF.'),
    129: (1, 'In many police database designs, ensuring that an officer is assigned only once to an active case requires extra application-level validation checks. In our project, we solved this directly inside MySQL using virtual generated columns. The column active_assignment_key is defined as CASE WHEN is_active=TRUE THEN CONCAT(case_id, \'-\', user_id) ELSE NULL END. By defining a UNIQUE index on active_assignment_key, MySQL allows multiple historical rows (where is_active is false and the key is null) but strictly prohibits duplicate active assignments. The functional dependency {active_assignment_key} -> {assignment_id, assignment_role, notes} holds for all active rows, keeping the table in BCNF without relying on error-prone application code.'),

    # CHAPTER 9: SQL IMPLEMENTATION
    131: (0, 'Our SQL implementation developed over two main stages: the initial relational queries, views, and joins created in Digital Assignment 2 (DA2) by Ayush Sharma (25BAI1392), followed by the expanded multi-table queries and analytical views written for the final 14-table system.'),
    133: (0, 'During DA2, Ayush Sharma authored and tested foundational SQL queries against the initial 6-table schema (POLICE_STATION, CRIME, CRIMINAL, VICTIM, CRIMINALS_OF_CRIME, VICTIM_OF_CRIME) to verify joins, subqueries, and aggregate grouping:'),
    143: (0, 'When scaling the system to the 14-table schema, we expanded these query patterns to incorporate multi-level clearance filtering, chain-of-custody tracking, and analytical views:'),

    # CHAPTER 10: ADVANCED DATABASE FEATURES
    148: (0, 'A central goal of our database project was placing critical business rules, access constraints, and audit logging directly inside the MySQL engine using stored procedures, deterministic functions, triggers, and virtual generated columns, rather than depending solely on web application code.'),
    159: (0, 'For the full application, we developed sp_assign_case to handle investigator assignments inside an explicit ACID transaction. When assigning a new Lead Investigator, the procedure automatically deactivates any existing lead officer, creates the new assignment record, and advances the case status to "Under Investigation". If any step fails, the entire transaction rolls back to ensure data consistency.'),
    162: (0, 'We wrote fn_case_duration as a deterministic stored function to calculate the duration of a case in days. For open cases, it computes the time elapsed from the incident date to the current date; for closed cases, it calculates the exact span between reporting and final closure.'),
    165: (0, 'Because MySQL triggers run within the database engine and cannot read Flask\'s session cookies directly, our application passes user identity down to MySQL using session variables (@app_user_id and @app_username) on each authenticated request. When an evidence item\'s location or custody status is modified, the trigger trg_evidence_custody_update automatically captures these session values and logs an immutable record in evidence_custody_log.'),
    168: (0, 'To enforce business constraints without running into concurrency race conditions, we used virtual generated columns with unique indexes. This prevents duplicate active assignments while still allowing complete historical records of past assignments to remain in the same table.'),
    171: (0, 'Testing transaction savepoint rollbacks during multi-step database operations:'),

    # CHAPTER 11: CLOUD DEPLOYMENT
    174: (0, 'Although our academic project runs and is tested locally using Python 3.14 and MySQL Community Server 9.7.1, we designed the architecture so it can be deployed to cloud environments such as AWS or Google Cloud. The Flask application is stateless, with container dependencies defined in a multi-stage Dockerfile:'),
    176: (0, 'In a cloud setup, incoming web traffic would enter through an Application Load Balancer with SSL termination. Flask container instances would run in private application subnets and scale horizontally behind the load balancer. The MySQL database would run on a managed database service (such as AWS RDS or GCP Cloud SQL) placed inside dedicated database subnets with no public internet access. Rather than hardcoding database passwords, secrets would be injected into container environment variables at runtime using a secrets manager.'),

    # CHAPTER 12: TESTING & QA
    178: (0, 'To ensure that our database constraints, access control rules, and application endpoints work properly, we built an automated test suite containing 35 Pytest integration tests, along with an end-to-end smoke test script (smoke_test.py). All 35 tests pass with a 100% success rate on our live MySQL 9.7 instance:'),
    180: (0, 'We also verified our least-privilege security model using a connection verification script (scripts/test_db_connection.py). The test confirms that when the web application user crimedb_app attempts to execute DROP TABLE, insert directly into audit_log, or update public_crime_incidents, MySQL rejects the query with Error 1142 ("command denied"), verifying that database permissions are strictly enforced.'),

    # CHAPTER 13: PERFORMANCE & INDEXING
    182: (0, 'After importing over 50,000 public crime incidents from the City of Chicago portal, queries filtering by district or date range suffered from noticeable latency because MySQL had to perform full table scans. To resolve this, we created 12 composite B-tree secondary indexes tailored to our most frequent search queries:'),
    185: (0, 'We evaluated our indexing decisions by analyzing query execution plans with MySQL EXPLAIN before and after adding the indexes. Filtering public_crime_incidents by district ("001") and date range without an index forced MySQL into a full table scan (type: ALL) that checked all ~50,000 rows. With our composite index idx_pci_district enabled, the access type changed to range/ref and the examined rows dropped to fewer than 500. This resulted in an over 95% reduction in scanned rows, reducing query execution time from roughly 160ms down to under 5ms.'),

    # CHAPTER 14: RESULTS & DISCUSSION
    187: (0, 'Designing, implementing, and testing our system provided several practical insights into database development and application security:'),
    188: (1, 'We found that enforcing integrity constraints directly in the database is much more dependable than relying only on web form validation. For example, our check constraint chk_cases_closure_consistency prevented cases from being marked "Closed" without a closing date, while virtual generated keys reliably blocked duplicate active assignments even during concurrent requests.'),
    189: (1, 'Working with a least-privilege database account revealed practical challenges during test automation. In our citizen test suite, our cleanup code initially attempted to delete test accounts using crimedb_app, which immediately failed with MySQL Error 1142 because DELETE permissions were intentionally revoked. We solved this by generating unique UUID emails for test records instead of trying to delete them, which also served as proof that our database permissions were working properly.'),
    190: (1, 'During initial prototyping, when a logged-in citizen requested another citizen\'s report, our endpoint returned HTTP 403 Forbidden. Although this blocked unauthorized access, it inadvertently confirmed that the requested report ID existed. We changed the response to HTTP 404 Not Found, eliminating the information leak and protecting citizens from automated tracking ID probing.'),
    191: (1, 'During smoke testing, requesting invalid URLs caused template rendering crashes because Flask\'s request.endpoint was None on 404 pages. We fixed this by adding null checks ({% if request.endpoint and \'cases\' in request.endpoint %}) across base.html, allowing custom error pages to display cleanly without triggering an unhandled 500 server error.'),

    # CHAPTER 15: CONCLUSION
    193: (0, 'The Criminal Case Management & Crime Analytics System (CCMS) successfully applies relational database theory to practical police record management. What began as an early concept in DA1 by Ojas Sugur and foundational SQL schema work in DA2 by Ayush Sharma has evolved into an integrated, 14-table BCNF database system. By implementing Bell-LaPadula access control, Need-to-Know authorization, trigger-automated custody tracking, dual-account privilege separation, and a decoupled Citizen Portal, our project addresses the security, traceability, and consistency challenges common in traditional station workflows. With 35 automated integration tests and a 24-point smoke test passing cleanly against live MySQL 9.7, the system demonstrates the practical value of anchoring business rules and security policies directly within the database engine.'),

    # CHAPTER 16: FUTURE SCOPE
    195: (0, 'Although the current system fulfills all course project requirements, several extensions could further enhance its real-world capabilities:'),
    196: (0, '• Geographic Information System (GIS) Spatial Indexing: Adding MySQL spatial data types (such as POINT with SPATIAL INDEX on R-trees) to enable spatial distance queries, radius-based incident searches, and automated patrol beat boundary mapping.'),
    197: (0, '• Biometric Vector Search: Exploring vector database extensions in MySQL to store high-dimensional embeddings of suspect facial mugshots and fingerprint descriptors for similarity matching.'),
    198: (0, '• Predictive Crime Analytics: Developing statistical and machine learning models on top of historical incident trends to identify high-risk patrol zones and seasonal incident spikes.'),
    199: (0, '• Blockchain Custody Anchoring: Anchoring cryptographic hashes of evidence_custody_log entries into a public or consortium ledger to provide mathematically verifiable proof of evidence custody in court.')
}

# Apply replacements
modified_count = 0
for p_idx, (r_idx, new_text) in replacements.items():
    p = doc.paragraphs[p_idx]
    if r_idx is not None and r_idx < len(p.runs):
        p.runs[r_idx].text = new_text
    else:
        p.runs[0].text = new_text
    modified_count += 1

print(f"Applied {modified_count} paragraph updates.")

# Save modified docx
doc.save(DST_DOCX)
print(f"Saved humanized report to {DST_DOCX}")
