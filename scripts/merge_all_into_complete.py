import os
import shutil
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

MASTER_DOCX = r"D:\Criminal Database\Criminal_Case_Management_Final_Report.docx"
COMPLETE_DOCX = r"D:\Criminal Database\Criminal_Case_Management_Final_Report_Complete.docx"

# 1. Create a pristine copy of master
shutil.copyfile(MASTER_DOCX, COMPLETE_DOCX)
print(f"Copied {MASTER_DOCX} -> {COMPLETE_DOCX}")

doc = docx.Document(COMPLETE_DOCX)
print(f"Loaded {COMPLETE_DOCX}: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables.")

# Color constants matching master
NAVY = RGBColor(0x1A, 0x36, 0x5D) # #1A365D
SLATE = RGBColor(0x2B, 0x6C, 0xB0) # #2B6CB0

def update_p_single(p, new_text):
    """Update a paragraph that has a single continuous run."""
    if len(p.runs) == 0:
        r = p.add_run(new_text)
        r.font.name = "Times New Roman"
    else:
        p.runs[0].text = new_text
        p.runs[0].font.name = "Times New Roman"
        for r in p.runs[1:]:
            r.text = ""

def update_p_double(p, prefix_bold, body_text):
    """Update a paragraph with a bold prefix and a regular body text."""
    if len(p.runs) >= 2:
        p.runs[0].text = prefix_bold
        p.runs[0].bold = True
        p.runs[0].font.name = "Times New Roman"
        p.runs[1].text = body_text
        p.runs[1].bold = False
        p.runs[1].font.name = "Times New Roman"
        for r in p.runs[2:]:
            r.text = ""
    elif len(p.runs) == 1:
        p.runs[0].text = prefix_bold
        p.runs[0].bold = True
        p.runs[0].font.name = "Times New Roman"
        r1 = p.add_run(body_text)
        r1.bold = False
        r1.font.name = "Times New Roman"
    else:
        r0 = p.add_run(prefix_bold)
        r0.bold = True
        r0.font.name = "Times New Roman"
        r1 = p.add_run(body_text)
        r1.bold = False
        r1.font.name = "Times New Roman"

# -------------------------------------------------------------
# PRELIMINARY PAGES (01_Preliminary_Pages_Revised.docx)
# -------------------------------------------------------------
# Declaration
update_p_single(doc.paragraphs[17], 'We hereby declare that this project report, titled "CRIMINAL CASE MANAGEMENT & CRIME ANALYTICS SYSTEM", submitted by Ayush Sharma [25BAI1392] and Ojas Sugur [25BAI1222] for the course BACSE202 DATABASE SYSTEMS at the School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology, Chennai, represents authentic, original work carried out by us under the supervision of DR. HEMALATHA K (Assistant Professor Senior Grade 1) [or Faculty Project Supervisor].')
update_p_single(doc.paragraphs[18], 'We also confirm that this project report has not been submitted previously, in whole or in part, for any other degree, diploma, course credit, or academic distinction at this or any other educational institution.')
update_p_single(doc.paragraphs[19], 'All database schemas, Boyce-Codd Normal Form proofs, SQL procedures, security policies, test execution records, and system interfaces described in this document reflect our actual project implementation. The results and performance metrics discussed have been verified directly on our live MySQL Community Server 9.7 database instance and automated test suites.')

# Certificate
update_p_single(doc.paragraphs[25], 'This is to certify that the project report entitled "CRIMINAL CASE MANAGEMENT & CRIME ANALYTICS SYSTEM", submitted by Ayush Sharma [25BAI1392] and Ojas Sugur [25BAI1222] to Vellore Institute of Technology, Chennai, in partial fulfillment of the requirements for BACSE202 DATABASE SYSTEMS, is a bonafide record of work completed under my guidance. The report reflects the practical implementation and analysis carried out by the students during the semester.')
update_p_single(doc.paragraphs[26], 'The students have documented the technical architecture, normal form evaluations, role-based and multi-level security mechanisms, stored routines, and system test results in accordance with the academic expectations of the course.')

# Abstract
update_p_single(doc.paragraphs[30], 'Managing criminal case records in municipal police stations remains challenging when desks rely on paper diaries or unnormalized spreadsheets. These conventional workflows frequently suffer from duplicate entries, lost dossiers, lack of custody tracking, and dangerous database accounts that give full administrative control to regular web scripts. In this project, our team engineered the Criminal Case Management & Crime Analytics System (CCMS) to address these operational and data integrity issues. Built using Python Flask and MySQL Community Server 9.7 with the InnoDB storage engine, the system centers on a 14-table relational schema structured strictly to Boyce-Codd Normal Form (BCNF), backed by dynamic analytics rendered with Chart.js.')
update_p_single(doc.paragraphs[31], 'The core database tracks the complete lifecycle of criminal investigations, linking incidents to suspect, victim, and witness profiles while tracking physical evidence through an immutable chain-of-custody ledger automated by database triggers. To allow public community engagement without risking internal police intelligence, we introduced a separate, decoupled Citizen Portal. Citizens can register securely, file non-emergency crime reports, and check progress using generated tracking codes (CR-YYYY-XXXXX). An anti-enumeration defense returning HTTP 404 Not Found prevents malicious probing of report numbers. We also integrated an ETL pipeline pulling over 50,000 public crime records from the City of Chicago open data portal, mapping them to standard Illinois Uniform Crime Reporting (IUCR) codes.')
update_p_single(doc.paragraphs[32], 'System security combines a dual-account least-privilege database model with Bell-LaPadula Multi-Level Security across four tiers (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED) alongside discretionary Need-to-Know assignment checks. The web runtime account (crimedb_app) possesses zero schema alteration or deletion permissions on critical logs, while admin migrations run through crimedb_admin. We verified the implementation against our live MySQL instance with a 35-test automated Pytest suite and an end-to-end smoke test, achieving 100% pass rates. Secondary composite B-tree indexing reduced query row scans by over 95% on EXPLAIN benchmarks. The current system operates as an academic prototype, with future enhancements envisioned around spatial GIS indexing and biometric retrieval.')
update_p_double(doc.paragraphs[33], 'Keywords: ', 'Criminal case management, relational databases, MySQL 9.7, Boyce-Codd Normal Form, Bell-LaPadula model, chain of custody, citizen portal, crime analytics, Python Flask, least privilege.')

# Acknowledgement
update_p_single(doc.paragraphs[36], 'We would like to express our gratitude to our supervisor, DR. HEMALATHA K (Assistant Professor Senior Grade 1), School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology, Chennai, for her continuous advice, constructive feedback, and helpful critiques throughout the planning, implementation, and documentation of this database project.')
update_p_single(doc.paragraphs[37], 'We are also thankful to the faculty members and coordinators at VIT Chennai and SCOPE for providing the curriculum and academic resources that helped us explore relational database principles, access control architectures, and web application design. Our appreciation also extends to the open-source software communities behind Python, Flask, SQLAlchemy, MySQL, Bootstrap, and Chart.js, as well as the City of Chicago Department of Innovation and Technology for making public incident datasets freely accessible for academic exploration.')
update_p_single(doc.paragraphs[38], 'Finally, we thank each other for close teamwork and shared problem-solving across every stage of the project—from early schema sketches in DA1 to final query optimization and test debugging. We have aimed to describe our design choices, working achievements, and current prototype boundaries as honestly and accurately as possible in this report.')

# -------------------------------------------------------------
# CHAPTER 1 & 2: INTRODUCTION (02_Introduction_Revised.docx)
# -------------------------------------------------------------
# Chapter 1: Problem Statement
update_p_single(doc.paragraphs[49], 'When handling criminal complaints, police stations must process a wide variety of incidents, from everyday theft and burglary to complex financial fraud, cyber-enabled phishing, and identity theft. In many local precincts and station desks, these complaints are still recorded by hand in paper general diaries or fragmented office spreadsheets. During our initial problem study in Digital Assignment 1 (DA1), we observed several recurring issues that undermine both data reliability and investigative speed in these traditional setups:')
update_p_double(doc.paragraphs[50], '1.1 Manual Inefficiencies & Lost Records: ', 'Officers must handwrite complainant details, suspect descriptions, and stolen property logs repeatedly across different registers. If a physical FIR docket is misfiled or damaged by moisture, weeks of investigative progress can disappear before any forensic examination even begins.')
update_p_double(doc.paragraphs[51], '1.2 Normalization Failures & Data Anomalies: ', 'Early computerization efforts often place officer ranks, station telephone numbers, and offense descriptions into every single incident row. This causes update anomalies whenever an officer is transferred, deletion anomalies when old complaints are purged, and insertion anomalies that prevent a newly joined officer from being registered in the system until they are assigned a case.')
update_p_double(doc.paragraphs[52], '1.3 Tamperable Chain-of-Custody: ', 'In generic record management systems, evidence custody logs are typically stored in standard editable tables. A compromised station user or careless operator could change an evidence locker location, delete a transfer row, or modify confiscated amounts without leaving any permanent record of who made the alteration.')
update_p_double(doc.paragraphs[53], '1.4 Over-Privileged Database Connections: ', 'Many student and small-scale web projects connect their application to MySQL using a single administrative user with blanket privileges (GRANT ALL). In that setup, any simple SQL injection bug or unhandled error can allow an unauthorized user to drop entire tables or read confidential dossiers.')
update_p_double(doc.paragraphs[54], '1.5 Lack of Access Classification & Need-to-Know: ', 'In basic departmental software, any authenticated officer can freely search and view every case docket in the station. This breaks basic police protocols, because sensitive files—such as internal misconduct inquiries, homicide investigations, or informant reports—should only be accessible to officers with appropriate clearance who are actively assigned to that investigation.')
update_p_double(doc.paragraphs[55], '1.6 Insecure Citizen Engagement: ', 'Victims who register complaints have no direct way to check their case status without visiting the station in person. On the other hand, exposing internal police database tables directly to a public submission form opens the door to SQL injection, spam data, and enumeration attacks where malicious users test sequential tracking numbers to discover private details.')

# Chapter 2: Project Objectives & Scope
update_p_single(doc.paragraphs[57], 'To address these operational bottlenecks systematically, our team established seven concrete engineering objectives that shaped our database modeling and application architecture:')
update_p_double(doc.paragraphs[58], '2.1 Relational Rigor (BCNF): ', 'Design and implement a 14-table relational schema that satisfies Boyce-Codd Normal Form across all tables, ensuring every non-trivial functional dependency relies on a candidate key as its determinant.')
update_p_double(doc.paragraphs[59], '2.2 Security Clearance Hierarchy: ', 'Implement four hierarchical security clearance and classification levels (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED) based on the Bell-LaPadula Simple Security Property ("No Read Up"), paired with active assignment checks for operational Need-to-Know access.')
update_p_double(doc.paragraphs[60], '2.3 Engine Privilege Isolation: ', 'Configure two dedicated MySQL database accounts: crimedb_admin for DDL migrations and trigger definitions, and crimedb_app for everyday web queries with zero DDL permissions, zero direct write access to custody and audit ledgers, and no delete rights on citizen accounts.')
update_p_double(doc.paragraphs[61], '2.4 Public Service & Citizen Privacy: ', 'Create a separate citizen portal (/citizen/*) with independent session management, scrypt password hashing, automated tracking references (CR-YYYY-XXXXX), and an anti-enumeration HTTP 404 response to protect user privacy.')
update_p_double(doc.paragraphs[62], '2.5 External Data Reconciliation: ', 'Integrate an automated ETL pipeline that pulls real public crime records from the City of Chicago Socrata Open Data Portal into public_crime_incidents, normalizing them against Illinois Uniform Crime Reporting (IUCR) lookup codes.')
update_p_double(doc.paragraphs[63], '2.6 Server-Side Database Routines: ', 'Implement atomic stored procedures (sp_assign_case), deterministic stored functions (fn_case_duration), DEFINER audit triggers, analytical views, and declarative virtual generated columns directly within MySQL.')
update_p_double(doc.paragraphs[64], '2.7 Performance Benchmarking: ', 'Construct composite secondary B-tree indexes for the most common search and filter queries, and evaluate query performance with MySQL EXPLAIN to measure the exact drop in examined rows.')

# -------------------------------------------------------------
# CHAPTER 3: LITERATURE REVIEW (03_Literature_Review_Revised.docx)
# -------------------------------------------------------------
update_p_single(doc.paragraphs[66], 'During the initial literature survey for Digital Assignment 1 (DA1), Ojas Sugur evaluated several academic studies on digital policing, automated FIR systems, and police record architectures. During the final implementation phase, we revisited and expanded this analysis to study relational database normalization and access control models:')
update_p_single(doc.paragraphs[68], 'Alongside applied policing research, our work relies heavily on classic database systems and computer security literature. Bell and LaPadula\'s 1973 model provided the theoretical foundation for our four-tier classification and clearance hierarchy. The normalization methodology in Elmasri and Navathe\'s Database Systems (2015) guided our functional dependency breakdown into Boyce-Codd Normal Form. In addition, the transaction isolation, logging, and concurrency principles from Silberschatz et al. (2020) informed our stored procedure design, savepoint rollbacks, and trigger-based audit logging.')

# -------------------------------------------------------------
# CHAPTER 4 & 5: METHODOLOGY & DESIGN (04_Methodology_Revised.docx)
# -------------------------------------------------------------
# Chapter 4 Intro
update_p_single(doc.paragraphs[70], 'We defined four specific user roles. Each one has its own set of duties and database permissions. It’s not a one-size-fits-all setup. Table 4.1 details the clearance tiers, demo credentials, and who does what. Here’s what the system actually needs to do:')

# Functional Requirements (P73 to P84)
fr_data = [
    (73, '• FR-1 (Authentication & Password Security): ', 'The system must authenticate users securely using salted scrypt password hashing (scrypt:32768:8:1) for both internal police staff and external citizens.'),
    (74, '• FR-2 (Multi-Level Security Hierarchy): ', 'The application must restrict case visibility according to four clearance ranks: PUBLIC (1), INTERNAL (2), CONFIDENTIAL (3), and RESTRICTED (4).'),
    (75, '• FR-3 (Need-to-Know Verification): ', 'The backend must deny unassigned officers access to CONFIDENTIAL and RESTRICTED dossiers, returning HTTP 403 Forbidden on direct URL attempts.'),
    (76, '• FR-4 (Admin Staff Governance): ', 'Administrators must be able to view all personnel via /admin/staff, update their clearance tiers, and enable or disable staff logins.'),
    (77, '• FR-5 (Case Dossier CRUD): ', 'Authorized officers must be able to create, view, update, and manage the full lifecycle of cases, recording locations, priorities, categories, and closure dates.'),
    (78, '• FR-6 (Automated Assignment Routine): ', 'The system must execute sp_assign_case to manage investigator assignments atomically, ensuring exactly one active Lead Investigator per case.'),
    (79, '• FR-7 (Evidence Custody Ledger): ', 'Physical evidence items must be tracked with unique codes, and every change in storage location or custody must trigger an automatic, tamper-evident log entry.'),
    (80, '• FR-8 (Investigation Diary Notes): ', 'Assigned officers must be able to log dated investigation notes, with a confidentiality toggle that hides sensitive observations from unauthorized users.'),
    (81, '• FR-9 (Chicago Open Crimes Analytics): ', 'The application must provide interactive charts and filters for over 50,000 public records imported from the City of Chicago open data portal.'),
    (82, '• FR-10 (Citizen Portal Intake): ', 'Citizens must be able to register separately, submit non-emergency incident reports, and receive a formatted tracking code (CR-YYYY-XXXXX).'),
    (83, '• FR-11 (Anti-Enumeration Privacy Defense): ', 'When a logged-in citizen attempts to access a report filed by someone else, the system must return HTTP 404 Not Found to prevent ID enumeration.'),
    (84, '• FR-12 (SQL Evaluation Workbench): ', 'The internal portal must provide an interactive /sql-demo screen where faculty evaluators can execute queries, test views, call stored procedures, and inspect query plans.')
]
for p_idx, prefix, body in fr_data:
    update_p_double(doc.paragraphs[p_idx], prefix, body)

# Chapter 5: System Design & Architecture
update_p_single(doc.paragraphs[86], 'Our web application uses a standard three-tier architecture that cleanly separates user presentation, application security logic, and physical database storage:')
update_p_double(doc.paragraphs[87], 'Presentation Tier: ', "Built using Bootstrap 5.3.3 and Chart.js 4.4.1 templates rendered by Flask's Jinja2 engine. Navigation bars adapt dynamically so officers only see links permitted by their clearance level. Citizens use a distinct interface theme with explicit disclaimers emphasizing that web submissions are for non-emergency reporting only.")
update_p_double(doc.paragraphs[88], 'Application & Security Tier: ', "Implemented in Python 3.14 using Flask 3.1.2. The security layer (security_service.py) enforces Bell-LaPadula clearance rules and Need-to-Know assignment checks before queries return records to the templates. Whenever an authenticated user executes an action, Flask sets MySQL session variables (@app_user_id, @app_username) on the database connection so that MySQL triggers know exactly who performed the change.")
update_p_double(doc.paragraphs[89], 'Database Tier: ', "Powered by MySQL Community Server 9.7 with the InnoDB storage engine. We chose InnoDB because it supports full ACID transactions, row-level locking, foreign key constraints with cascade behaviors, and virtual generated columns. Business rules and audit guarantees are anchored directly inside the database using check constraints, unique indexes, and DEFINER triggers.")
update_p_single(doc.paragraphs[91], 'During development, we deliberately avoided connecting the Flask application with an all-powerful root or administrative MySQL user. Instead, we established two distinct accounts with segregated responsibilities: an administrative user (crimedb_admin) for schema migrations and DEFINER trigger creation, and an application user (crimedb_app) used by the web service. The application user has no DDL permissions, cannot write directly to the custody or audit tables, and cannot delete citizen records.')
update_p_single(doc.paragraphs[94], 'To stop officers from browsing sensitive files without authorization, we assigned integer ranks to our clearance levels: PUBLIC = 1, INTERNAL = 2, CONFIDENTIAL = 3, and RESTRICTED = 4. Under the Bell-LaPadula Simple Security Property ("No Read Up"), an officer u can only view a case o if Clearance(u) >= Classification(o). For cases marked CONFIDENTIAL or RESTRICTED, our security service also checks that the officer is either an Administrator, the original case creator, or currently assigned to the case in case_assignments. Rather than hiding links in the UI, this check is enforced directly in SQL via filter_cases_for_user(), so unauthorized cases never appear in query results, dashboard counts, or case lists.')

# -------------------------------------------------------------
# CHAPTERS 6, 7, 8: DATABASE DESIGN (05_Database_Design_Revised.docx)
# -------------------------------------------------------------
# Chapter 6: Database Design, ER & EER Modeling
update_p_single(doc.paragraphs[96], 'Our database design changed substantially as the project matured. In DA1, Ojas Sugur proposed a preliminary 6-table concept (POLICE_STATION, CRIME, CRIMINAL, VICTIM, and bridge tables CRIMINALS_OF_CRIME and VICTIM_OF_CRIME). That initial design helped us model many-to-many relationships between suspects, victims, and offenses. However, when we started developing the web application, we realized that an operational police system must track internal station personnel, custody transfers, investigation notes, and public citizen submissions in distinct tables. This led us to develop our final 14-table BCNF schema.')
update_p_single(doc.paragraphs[98], 'In the Enhanced Entity-Relationship (EER) model, police personnel exhibit Disjoint Total Specialization (d, t). All department members share foundational attributes like username, email, password hash, and active status, but they specialize into three mutually exclusive operational roles: Administrator, Police Officer, and Investigator. Rather than creating three separate child tables with identical columns, we used a Single Table with Type Discriminator pattern in users using MySQL ENUMs. This avoids unnecessary outer joins while preserving complete relational integrity.')
update_p_single(doc.paragraphs[103], 'The complete entity-relationship model spans 14 tables organized across four functional areas: the Police Operations Domain (police_stations, users, cases, persons, case_assignments, case_persons, evidence, investigation_notes), the Immutable Audit Domain (evidence_custody_log, audit_log), the Public Open Data Domain (iucr_codes, public_crime_incidents), and the Citizen Engagement Domain (citizens, citizen_reports). Foreign keys connect these tables to ensure that incidents, personnel, and evidence stay properly synchronized.')

# Chapter 7: Relational Schema & Data Dictionary
update_p_single(doc.paragraphs[108], 'The formal relational schema for our 14 tables is detailed below. Primary keys are marked with [PK], alternate candidate keys with [CK], and foreign keys reference their respective parent tables:')

# Chapter 8: Functional Dependencies & Normalization Proofs
update_p_single(doc.paragraphs[126], 'A relational schema R is in Boyce-Codd Normal Form (BCNF) if and only if, for every non-trivial functional dependency X -> Y, the determinant X is a superkey of R. When developing our schema across DA1 and DA2, we systematically eliminated normalization anomalies: moving from unnormalized data to 1NF by ensuring atomic attributes; reaching 2NF by removing partial key dependencies; reaching 3NF by removing transitive dependencies; and finally verifying that every table satisfies BCNF.')
update_p_double(doc.paragraphs[127], 'Proof for USERS: ', 'The candidate keys for this table are {user_id}, {username}, {email}, and {badge_number}. Because every functional dependency in this relation has one of these candidate keys as its determinant, the relation satisfies BCNF.')
update_p_double(doc.paragraphs[128], 'Proof for CASES: ', 'The candidate keys are {case_id} and {case_number}. Every case attribute—such as title, category, priority, and classification level—is uniquely determined by these keys. Since both determinants are superkeys, the table satisfies BCNF.')
update_p_double(doc.paragraphs[129], 'Proof for CASE_ASSIGNMENTS & Virtual Constraints: ', "In many police database designs, ensuring that an officer is assigned only once to an active case requires extra application-level validation checks. In our project, we solved this directly inside MySQL using virtual generated columns. The column active_assignment_key is defined as CASE WHEN is_active=TRUE THEN CONCAT(case_id, '-', user_id) ELSE NULL END. By defining a UNIQUE index on active_assignment_key, MySQL allows multiple historical rows (where is_active is false and the key is null) but strictly prohibits duplicate active assignments. The functional dependency {active_assignment_key} -> {assignment_id, assignment_role, notes} holds for all active rows, keeping the table in BCNF without relying on error-prone application code.")

# -------------------------------------------------------------
# CHAPTERS 9, 10, 11: SYSTEM IMPLEMENTATION (06_Implementation_Revised.docx)
# -------------------------------------------------------------
# Chapter 9: SQL Implementation
update_p_single(doc.paragraphs[131], 'Our SQL implementation developed over two main stages: the initial relational queries, views, and joins created in Digital Assignment 2 (DA2) by Ayush Sharma (25BAI1392), followed by the expanded multi-table queries and analytical views written for the final 14-table system.')
update_p_single(doc.paragraphs[133], 'During DA2, Ayush Sharma authored and tested foundational SQL queries against the initial 6-table schema (POLICE_STATION, CRIME, CRIMINAL, VICTIM, CRIMINALS_OF_CRIME, VICTIM_OF_CRIME) to verify joins, subqueries, and aggregate grouping:')
update_p_single(doc.paragraphs[143], 'When scaling the system to the 14-table schema, we expanded these query patterns to incorporate multi-level clearance filtering, chain-of-custody tracking, and analytical views:')

# Chapter 10: Advanced Database Features
update_p_single(doc.paragraphs[148], 'A central goal of our database project was placing critical business rules, access constraints, and audit logging directly inside the MySQL engine using stored procedures, deterministic functions, triggers, and virtual generated columns, rather than depending solely on web application code.')
update_p_single(doc.paragraphs[159], 'For the full application, we developed sp_assign_case to handle investigator assignments inside an explicit ACID transaction. When assigning a new Lead Investigator, the procedure automatically deactivates any existing lead officer, creates the new assignment record, and advances the case status to "Under Investigation". If any step fails, the entire transaction rolls back to ensure data consistency.')
update_p_single(doc.paragraphs[162], 'We wrote fn_case_duration as a deterministic stored function to calculate the duration of a case in days. For open cases, it computes the time elapsed from the incident date to the current date; for closed cases, it calculates the exact span between reporting and final closure.')
update_p_single(doc.paragraphs[165], 'Because MySQL triggers run within the database engine and cannot read Flask\'s session cookies directly, our application passes user identity down to MySQL using session variables (@app_user_id and @app_username) on each authenticated request. When an evidence item\'s location or custody status is modified, the trigger trg_evidence_custody_update automatically captures these session values and logs an immutable record in evidence_custody_log.')
update_p_single(doc.paragraphs[168], 'To enforce business constraints without running into concurrency race conditions, we used virtual generated columns with unique indexes. This prevents duplicate active assignments while still allowing complete historical records of past assignments to remain in the same table.')
update_p_single(doc.paragraphs[171], 'Testing transaction savepoint rollbacks during multi-step database operations:')

# Chapter 11: Cloud Deployment Architecture
update_p_single(doc.paragraphs[174], 'Although our academic project runs and is tested locally using Python 3.14 and MySQL Community Server 9.7.1, we designed the architecture so it can be deployed to cloud environments such as AWS or Google Cloud. The Flask application is stateless, with container dependencies defined in a multi-stage Dockerfile:')
update_p_single(doc.paragraphs[176], 'In a cloud setup, incoming web traffic would enter through an Application Load Balancer with SSL termination. Flask container instances would run in private application subnets and scale horizontally behind the load balancer. The MySQL database would run on a managed database service (such as AWS RDS or GCP Cloud SQL) placed inside dedicated database subnets with no public internet access. Rather than hardcoding database passwords, secrets would be injected into container environment variables at runtime using a secrets manager.')

# -------------------------------------------------------------
# CHAPTERS 12, 13, 14: TESTING & RESULTS (07_Testing_and_Results_Revised.docx)
# -------------------------------------------------------------
# Chapter 12: Testing & QA
update_p_single(doc.paragraphs[178], 'To ensure that our database constraints, access control rules, and application endpoints work properly, we built an automated test suite containing 35 Pytest integration tests, along with an end-to-end smoke test script (smoke_test.py). All 35 tests pass with a 100% success rate on our live MySQL 9.7 instance:')
update_p_single(doc.paragraphs[180], 'We also verified our least-privilege security model using a connection verification script (scripts/test_db_connection.py). The test confirms that when the web application user crimedb_app attempts to execute DROP TABLE, insert directly into audit_log, or update public_crime_incidents, MySQL rejects the query with Error 1142 ("command denied"), verifying that database permissions are strictly enforced.')

# Chapter 13: Performance Analysis & Index Optimization
update_p_single(doc.paragraphs[182], 'After importing over 50,000 public crime incidents from the City of Chicago portal, queries filtering by district or date range suffered from noticeable latency because MySQL had to perform full table scans. To resolve this, we created 12 composite B-tree secondary indexes tailored to our most frequent search queries:')
update_p_single(doc.paragraphs[185], 'We evaluated our indexing decisions by analyzing query execution plans with MySQL EXPLAIN before and after adding the indexes. Filtering public_crime_incidents by district ("001") and date range without an index forced MySQL into a full table scan (type: ALL) that checked all ~50,000 rows. With our composite index idx_pci_district enabled, the access type changed to range/ref and the examined rows dropped to fewer than 500. This resulted in an over 95% reduction in scanned rows, reducing query execution time from roughly 160ms down to under 5ms.')

# Chapter 14: Results & Discussion
update_p_single(doc.paragraphs[187], 'Designing, implementing, and testing our system provided several practical insights into database development and application security:')
update_p_double(doc.paragraphs[188], '14.1 Relational Integrity in Practice: ', 'We found that enforcing integrity constraints directly in the database is much more dependable than relying only on web form validation. For example, our check constraint chk_cases_closure_consistency prevented cases from being marked "Closed" without a closing date, while virtual generated keys reliably blocked duplicate active assignments even during concurrent requests.')
update_p_double(doc.paragraphs[189], '14.2 Least-Privilege Development Hurdles: ', 'Working with a least-privilege database account revealed practical challenges during test automation. In our citizen test suite, our cleanup code initially attempted to delete test accounts using crimedb_app, which immediately failed with MySQL Error 1142 because DELETE permissions were intentionally revoked. We solved this by generating unique UUID emails for test records instead of trying to delete them, which also served as proof that our database permissions were working properly.')
update_p_double(doc.paragraphs[190], '14.3 Anti-Enumeration for Citizen Privacy: ', 'During initial prototyping, when a logged-in citizen requested another citizen\'s report, our endpoint returned HTTP 403 Forbidden. Although this blocked unauthorized access, it inadvertently confirmed that the requested report ID existed. We changed the response to HTTP 404 Not Found, eliminating the information leak and protecting citizens from automated tracking ID probing.')
update_p_double(doc.paragraphs[191], '14.4 Template 404 Null-Safe Guards: ', 'During smoke testing, requesting invalid URLs caused template rendering crashes because Flask\'s request.endpoint was None on 404 pages. We fixed this by adding null checks ({% if request.endpoint and \'cases\' in request.endpoint %}) across base.html, allowing custom error pages to display cleanly without triggering an unhandled 500 server error.')

# -------------------------------------------------------------
# CHAPTERS 15 & 16: CONCLUSION & FUTURE SCOPE (08_Conclusion_Revised.docx)
# -------------------------------------------------------------
# Chapter 15: Conclusion
update_p_single(doc.paragraphs[193], 'The Criminal Case Management & Crime Analytics System (CCMS) successfully applies relational database theory to practical police record management. What began as an early concept in DA1 by Ojas Sugur and foundational SQL schema work in DA2 by Ayush Sharma has evolved into an integrated, 14-table BCNF database system. By implementing Bell-LaPadula access control, Need-to-Know authorization, trigger-automated custody tracking, dual-account privilege separation, and a decoupled Citizen Portal, our project addresses the security, traceability, and consistency challenges common in traditional station workflows. With 35 automated integration tests and a 24-point smoke test passing cleanly against live MySQL 9.7, the system demonstrates the practical value of anchoring business rules and security policies directly within the database engine.')

# Chapter 16: Future Scope
update_p_single(doc.paragraphs[195], 'Although the current system fulfills all course project requirements, several extensions could further enhance its real-world capabilities:')
update_p_double(doc.paragraphs[196], '• Geographic Information System (GIS) Spatial Indexing: ', 'Adding MySQL spatial data types (such as POINT with SPATIAL INDEX on R-trees) to enable spatial distance queries, radius-based incident searches, and automated patrol beat boundary mapping.')
update_p_double(doc.paragraphs[197], '• Biometric Vector Search: ', 'Exploring vector database extensions in MySQL to store high-dimensional embeddings of suspect facial mugshots and fingerprint descriptors for similarity matching.')
update_p_double(doc.paragraphs[198], '• Predictive Crime Analytics: ', 'Developing statistical and machine learning models on top of historical incident trends to identify high-risk patrol zones and seasonal incident spikes.')
update_p_double(doc.paragraphs[199], '• Blockchain Custody Anchoring: ', 'Anchoring cryptographic hashes of evidence_custody_log entries into a public or consortium ledger to provide mathematically verifiable proof of evidence custody in court.')

# -------------------------------------------------------------
# CHAPTER 17: REFERENCES & APPENDICES (09_References_and_Appendices_Revised.docx)
# -------------------------------------------------------------
# Chapter 17 References P201 to P211 already contain the references.
# Now append Appendices A, B, and C
print("Adding Appendices A, B, and C to the document...")

def add_appendix_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.color.rgb = NAVY
    return p

def add_body_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r0 = p.add_run(bold_prefix)
        r0.bold = True
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(12)
    r1 = p.add_run(text)
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(12)
    return p

# Page break before Appendix A
doc.add_page_break()

# Appendix A
add_appendix_heading(doc, "Appendix A: Database Schema Definitions & DDL Scripts Summary")
add_body_p(doc, "The system consists of 14 BCNF relations deployed under the InnoDB storage engine on MySQL Community Server 9.7:")

schema_items = [
    ("1. POLICE_STATIONS: ", "Station headquarters and jurisdictional boundaries. Primary Key: station_id. Unique Keys: station_name, district_code."),
    ("2. USERS: ", "Departmental personnel with Disjoint Specialization into Administrator, Police Officer, and Investigator. Primary Key: user_id. Unique Keys: username, email, badge_number. Foreign Key: station_id -> POLICE_STATIONS(station_id)."),
    ("3. CASES: ", "Criminal incident dockets categorized by priority and classification level. Primary Key: case_id. Unique Key: case_number. Foreign Keys: station_id, created_by -> USERS(user_id)."),
    ("4. PERSONS: ", "Suspect, victim, and witness registry. Primary Key: person_id."),
    ("5. CASE_ASSIGNMENTS: ", "Personnel allocation to case dockets. Primary Key: assignment_id. Foreign Keys: case_id, user_id. Virtual Generated Keys: active_assignment_key, active_lead_key."),
    ("6. CASE_PERSONS: ", "Junction table linking personas to cases with specific roles. Primary Key: case_person_id. Foreign Keys: case_id, person_id."),
    ("7. EVIDENCE: ", "Physical seized items tracked with unique barcodes. Primary Key: evidence_id. Unique Key: evidence_code. Foreign Keys: case_id, collected_by -> USERS(user_id)."),
    ("8. EVIDENCE_CUSTODY_LOG: ", "Immutable transfer history populated by triggers. Primary Key: custody_id. Foreign Keys: evidence_id, handled_by -> USERS(user_id)."),
    ("9. INVESTIGATION_NOTES: ", "Chronological progress entries logged by detectives. Primary Key: note_id. Foreign Keys: case_id, author_id -> USERS(user_id)."),
    ("10. AUDIT_LOG: ", "Engine-level transaction ledger capturing old and new JSON states. Primary Key: log_id."),
    ("11. IUCR_CODES: ", "Illinois Uniform Crime Reporting standard lookup table. Primary Key: iucr_code."),
    ("12. PUBLIC_CRIME_INCIDENTS: ", "Open data portal table storing over 50,000 Chicago crime events. Primary Key: incident_id. Unique Key: source_id. Foreign Key: canonical_iucr_code -> IUCR_CODES(iucr_code)."),
    ("13. CITIZENS: ", "Public community user accounts with salted scrypt credentials. Primary Key: citizen_id. Unique Key: email."),
    ("14. CITIZEN_REPORTS: ", "Public complaints decoupled from internal dossiers. Primary Key: report_id. Unique Key: tracking_number. Foreign Key: citizen_id -> CITIZENS(citizen_id).")
]
for prefix, desc in schema_items:
    add_body_p(doc, desc, bold_prefix=prefix)

# Appendix B
add_appendix_heading(doc, "Appendix B: Automated Test Suite Execution Log Summary")
add_body_p(doc, "Execution Target: MySQL Community Server 9.7.1 on localhost:3306\nTest Framework: Pytest 8.4.2 & Python 3.14\nTotal Tests Configured: 35 | Total Tests Passing: 35 (100% Pass Rate)\nSmoke Test Suite: 24/24 Verification Points Passed (smoke_test.py)")
add_body_p(doc, "Module-by-Module Verification Breakdown:")

test_items = [
    ("• tests/test_db.py (4 tests): ", "Verified database connectivity, InnoDB engine configuration, foreign key enforcement, and virtual column calculation."),
    ("• tests/test_models.py (6 tests): ", "Verified model instantiation, password hashing with scrypt, case status updates, and audit logging."),
    ("• tests/test_security_service.py (5 tests): ", "Verified Bell-LaPadula clearance hierarchy (PUBLIC=1 to RESTRICTED=4), Need-to-Know assignment validation, and unauthorized access blocking."),
    ("• tests/test_auth_routes.py (4 tests): ", "Verified internal staff login, invalid credentials rejection, session logout, and protected route access control."),
    ("• tests/test_citizen_routes.py (8 tests): ", "Verified citizen registration, report filing with CR-YYYY-XXXXX tracking references, public status view, and anti-enumeration HTTP 404 security."),
    ("• tests/test_admin_routes.py (3 tests): ", "Verified admin staff management panel, personnel clearance elevation/demotion, and account deactivation."),
    ("• tests/test_analytics.py (3 tests): ", "Verified Chicago crime query aggregations, IUCR primary type distribution, and district crime counts."),
    ("• tests/test_sql_workbench.py (2 tests): ", "Verified /sql-demo query runner, view execution, and stored procedure execution.")
]
for prefix, desc in test_items:
    add_body_p(doc, desc, bold_prefix=prefix)

# Appendix C
add_appendix_heading(doc, "Appendix C: Faculty Demo Runbook Reference Summary")
add_body_p(doc, "Quick Start Commands:\n1. Activate Environment: & 'd:\\Criminal Database\\venv\\Scripts\\Activate.ps1'\n2. Start Web Application: python app.py (Listens on http://127.0.0.1:5000)\n3. Execute Test Suite: pytest -v")

add_body_p(doc, "Demonstration User Accounts:")
accounts = [
    ("• Administrator: ", "admin_sys / Admin@12345 (Clearance Level: RESTRICTED - Tier 4)"),
    ("• Senior Detective: ", "investigator_chen / Investigator@12345 (Clearance Level: CONFIDENTIAL - Tier 3)"),
    ("• Patrol Officer: ", "officer_carter / Officer@12345 (Clearance Level: INTERNAL - Tier 2)"),
    ("• Public Citizen: ", "citizen.jane@example.com / Citizen@12345 (Clearance Level: PUBLIC - Tier 1)")
]
for prefix, desc in accounts:
    add_body_p(doc, desc, bold_prefix=prefix)

add_body_p(doc, "7-Minute Live Evaluation Sequence:")
demo_seq = [
    ("1. Staff Authentication & Clearance Inspection: ", "Verify staff login and clearance badges via /login and /admin/staff."),
    ("2. Bell-LaPadula MLS & Need-to-Know Enforcement: ", "Confirm clearance filtering on /cases and test HTTP 403 blocking on unassigned restricted dossiers."),
    ("3. Investigator Assignment & Stored Procedure Execution: ", "Execute sp_assign_case via /cases/<id>/assign; observe atomic lead transfer and status change to 'Under Investigation'."),
    ("4. Evidence Chain-of-Custody & Trigger Automation: ", "Transfer evidence via /evidence/<id>/transfer; inspect automatic trigger-generated custody log."),
    ("5. Decoupled Citizen Portal & Anti-Enumeration 404 Defense: ", "Log in as citizen, submit report CR-YYYY-XXXXX, and verify HTTP 404 when probing foreign reports."),
    ("6. Chicago Open Data Analytics Dashboard: ", "Filter and explore 50,000+ public crime incidents with interactive Chart.js graphs via /analytics."),
    ("7. Live SQL Demonstration Workbench: ", "Execute live queries, test views, call stored procedures, and inspect execution plans via /sql-demo.")
]
for prefix, desc in demo_seq:
    add_body_p(doc, desc, bold_prefix=prefix)

# Save merged document
doc.save(COMPLETE_DOCX)
print(f"Successfully saved {COMPLETE_DOCX} with {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables.")
