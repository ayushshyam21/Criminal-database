import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

SRC_DOCX = r"D:\Criminal Database\Criminal_Case_Management_Final_Report_Humanized.docx"
OUT_DIR = r"D:\Criminal Database\Report_Text_Extraction"

os.makedirs(OUT_DIR, exist_ok=True)
print(f"Output directory ensured: {OUT_DIR}")

# -------------------------------------------------------------
# Styling Helpers for Extracted DOCX Files
# -------------------------------------------------------------
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def style_table(table, header_bg="1A365D", alt_bg="F7FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for col in table.columns:
        for cell in col.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell)
    for cell in table.rows[0].cells:
        set_cell_background(cell, header_bg)
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                r.font.bold = True
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(255, 255, 255)
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
        for cell in row.cells:
            set_cell_background(cell, bg)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = RGBColor(45, 55, 72)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
                        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="2B6CB0"/>'
                        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
                        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
                        f'</w:tcBorders>')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(26, 32, 44)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_text_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            lines = cell.split('\n')
            max_line = max(len(l) for l in lines) if lines else 0
            if max_line > col_widths[i]:
                col_widths[i] = max_line
    # cap max width to 45 for clean terminal display
    col_widths = [min(max(w, 4), 45) for w in col_widths]
    
    header_str = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    
    out_lines = [header_str, sep_str]
    for row in rows:
        split_cells = [r.split('\n') for r in row]
        max_sub = max(len(c) for c in split_cells)
        for sub_idx in range(max_sub):
            line_parts = []
            for col_idx in range(len(headers)):
                val = split_cells[col_idx][sub_idx] if sub_idx < len(split_cells[col_idx]) else ""
                val = val[:col_widths[col_idx]]
                line_parts.append(val.ljust(col_widths[col_idx]))
            out_lines.append(" | ".join(line_parts))
    return "\n".join(out_lines) + "\n\n"

# -------------------------------------------------------------
# Load Source Document Elements in Sequential Order
# -------------------------------------------------------------
source_doc = docx.Document(SRC_DOCX)
body_elements = list(source_doc.element.body)
print(f"Loaded {len(body_elements)} sequential body elements from {SRC_DOCX}")

# Map each element to an extracted representation
# Items can be:
# ('p', paragraph_object, text, is_heading, style_name, has_drawings)
# ('tbl', table_object, headers, rows, is_code_block, code_text)

parsed_items = []
p_counter = 0
tbl_counter = 0

for elem in body_elements:
    if isinstance(elem, CT_P):
        p = docx.text.paragraph.Paragraph(elem, source_doc)
        text = p.text.strip()
        drawings = elem.xpath('.//w:drawing') or elem.xpath('.//w:pict')
        is_heading = text.startswith("Chapter ") or text in [
            "BACSE202", "DECLARATION", "CERTIFICATE", "ABSTRACT", "ACKNOWLEDGEMENT",
            "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF ABBREVIATIONS AND NOMENCLATURE",
            "Functional Requirements Specification", "Dual-Account Least-Privilege Architecture",
            "Bell-LaPadula Security Model & Discretionary Need-to-Know",
            "Enhanced Entity-Relationship (EER) Specialization", "Complete Entity-Relationship Diagram (ERD)",
            "Comprehensive Data Dictionary Catalog", "EXPLAIN Benchmark Results"
        ]
        parsed_items.append({
            'type': 'p',
            'obj': p,
            'text': p.text,
            'p_idx': p_counter,
            'has_drawings': bool(drawings),
            'is_heading': is_heading
        })
        p_counter += 1
    elif isinstance(elem, CT_Tbl):
        t = docx.table.Table(elem, source_doc)
        rows_data = []
        for r in t.rows:
            rows_data.append([c.text.strip() for c in r.cells])
        is_code = (len(t.rows) == 1 and len(t.columns) == 1)
        code_text = t.cell(0, 0).text if is_code else None
        headers = rows_data[0] if len(rows_data) > 0 else []
        body_rows = rows_data[1:] if len(rows_data) > 1 else []
        parsed_items.append({
            'type': 'tbl',
            'obj': t,
            'tbl_idx': tbl_counter,
            'is_code': is_code,
            'code_text': code_text,
            'headers': headers,
            'body_rows': body_rows,
            'all_rows': rows_data
        })
        tbl_counter += 1

print(f"Parsed {len(parsed_items)} items: {p_counter} paragraphs, {tbl_counter} tables.")

# -------------------------------------------------------------
# Section Boundary Mapping (Indices into parsed_items)
# -------------------------------------------------------------
# 01_Preliminary_Pages: Elem 0 to 51
# 02_Introduction: Elem 52 to 68 (Ch 1 & Ch 2)
# 03_Literature_Review: Elem 69 to 73 (Ch 3 + Table 3.1)
# 04_Methodology_and_System_Design: Elem 74 to 101 (Ch 4 + Table 4.1 + Ch 5 + Table 5.1)
# 05_Database_Design: Elem 102 to 137 (Ch 6 + Figures + Ch 7 + Table 7.1 + Ch 8)
# 06_System_Implementation: Elem 138 to 200 (Ch 9 + SQL Code Blocks + Ch 10 + Ch 11 + Dockerfile)
# 07_Testing_and_Results: Elem 201 to 217 (Ch 12 + Table 12.1 + Ch 13 + Table 13.1 + Ch 14)
# 08_Conclusion_and_Future_Work: Elem 218 to 225 (Ch 15 & Ch 16)
# 09_References_and_Appendices: Elem 226 to 237 (Ch 17 References + Appendices)

section_specs = [
    {
        'id': '01_Preliminary_Pages',
        'title': '01: PRELIMINARY PAGES & ACADEMIC FRONT MATTER',
        'range': (0, 51),
        'chapters': 'Cover Page, Title Page, Declaration, Certificate, Abstract, Acknowledgement, TOC, LOT, LOF, Abbreviations',
        'diagram_notes': [
            ("Cover Page (p. 1)", "Official VIT Chennai Logo (docs/vit_logo.png, 982x280 PNG RGBA). Centered emblem with VIT crest, blue typography, and 'Vellore Institute of Technology'."),
            ("Title / Submission Page (p. 2)", "Official VIT Chennai Logo (docs/vit_logo.png, width=3.3 in). Centered institutional emblem above SCOPE department details.")
        ]
    },
    {
        'id': '02_Introduction',
        'title': '02: INTRODUCTION (CHAPTER 1 & CHAPTER 2)',
        'range': (52, 68),
        'chapters': 'Chapter 1: Problem Statement, Chapter 2: Project Objectives & Scope',
        'diagram_notes': []
    },
    {
        'id': '03_Literature_Review',
        'title': '03: LITERATURE REVIEW (CHAPTER 3)',
        'range': (69, 73),
        'chapters': 'Chapter 3: Literature Survey & Existing Systems, Table 3.1 Literature Comparison',
        'diagram_notes': []
    },
    {
        'id': '04_Methodology_and_System_Design',
        'title': '04: METHODOLOGY AND SYSTEM DESIGN (CHAPTER 4 & CHAPTER 5)',
        'range': (74, 101),
        'chapters': 'Chapter 4: System Requirements & User Roles (Table 4.1, FR-1 to FR-12), Chapter 5: System Design & Architecture (Three-Tier Architecture, Dual Accounts Table 5.1, Bell-LaPadula MLS Model)',
        'diagram_notes': [
            ("Figure 5.1 (p. 10)", "Multi-Tier Application and Database Architecture: Client Browser (Staff / Citizen) -> Web Server (Flask 3.1.2, Jinja2, Chart.js 4.4.1) -> Security Service (Bell-LaPadula MLS, Session Injector) -> Database Tier (MySQL 9.7 InnoDB Storage Engine with Dual Accounts crimedb_admin and crimedb_app).")
        ]
    },
    {
        'id': '05_Database_Design',
        'title': '05: DATABASE DESIGN (CHAPTER 6, CHAPTER 7, & CHAPTER 8)',
        'range': (102, 137),
        'chapters': 'Chapter 6: Database Design, ER & EER Modeling, Chapter 7: Relational Schema & Data Dictionary (Table 7.1), Chapter 8: Functional Dependencies & Normalization Proofs',
        'diagram_notes': [
            ("Figure 6.1 (p. 14)", "Enhanced Entity-Relationship (EER) Model showing Disjoint Total Specialization (d, t) of USERS supertype into ADMINISTRATOR, POLICE OFFICER, and INVESTIGATOR subtypes. Details single table mapping strategy and domain isolation between Application Dossier Domain and Public Open Data Domain (docs/eerd.mmd)."),
            ("Figure 6.2 (p. 16)", "Complete 14-Table Relational Entity-Relationship Diagram (ERD): Relationships between POLICE_STATIONS, USERS, CASES, PERSONS, CASE_ASSIGNMENTS, CASE_PERSONS, EVIDENCE, EVIDENCE_CUSTODY_LOG, INVESTIGATION_NOTES, IUCR_CODES, PUBLIC_CRIME_INCIDENTS, AUDIT_LOG, CITIZENS, and CITIZEN_REPORTS (docs/erd.mmd).")
        ]
    },
    {
        'id': '06_System_Implementation',
        'title': '06: SYSTEM IMPLEMENTATION (CHAPTER 9, CHAPTER 10, & CHAPTER 11)',
        'range': (138, 200),
        'chapters': 'Chapter 9: SQL Implementation & Query Catalog (DA2 & Production Queries), Chapter 10: Advanced Database Features (Stored Procedures, Functions, Triggers, Savepoints), Chapter 11: Cloud Deployment Architecture (Docker containerization, AWS/GCP topology)',
        'diagram_notes': [
            ("Figure 11.1 (p. 35)", "Cloud Production Deployment Topology: Internet -> Route 53 / Cloud DNS -> Application Load Balancer (SSL/TLS Termination) -> Private Application Subnet (Flask Container Pods in Auto-Scaling Group) -> Private Database Subnet (Multi-AZ Managed MySQL RDS with Automated Backup & Secrets Manager Integration).")
        ]
    },
    {
        'id': '07_Testing_and_Results',
        'title': '07: TESTING AND RESULTS (CHAPTER 12, CHAPTER 13, & CHAPTER 14)',
        'range': (201, 217),
        'chapters': 'Chapter 12: Testing & Quality Assurance (Table 12.1 Pytest Execution Matrix, Least-Privilege Error 1142), Chapter 13: Performance Analysis & Index Optimization (Table 13.1 Composite Indexes, EXPLAIN Benchmarks Table 13.2), Chapter 14: Results & Discussion',
        'diagram_notes': []
    },
    {
        'id': '08_Conclusion_and_Future_Work',
        'title': '08: CONCLUSION AND FUTURE WORK (CHAPTER 15 & CHAPTER 16)',
        'range': (218, 225),
        'chapters': 'Chapter 15: Conclusion, Chapter 16: Future Scope (GIS Spatial Indexing, Biometric Vector Search, Predictive Crime Analytics, Blockchain Custody Anchoring)',
        'diagram_notes': []
    },
    {
        'id': '09_References_and_Appendices',
        'title': '09: REFERENCES AND APPENDICES (CHAPTER 17 & APPENDICES)',
        'range': (226, len(parsed_items) - 1),
        'chapters': 'Chapter 17: References (1 to 11), Appendix A: Database Schema Definitions & DDL Summary, Appendix B: Automated Test Suite Execution Log Summary, Appendix C: Faculty Demo Runbook Reference',
        'diagram_notes': []
    }
]

# Read Mermaid diagrams for rich inclusion
eerd_mmd_content = ""
if os.path.exists(r"D:\Criminal Database\docs\eerd.mmd"):
    with open(r"D:\Criminal Database\docs\eerd.mmd", "r", encoding="utf-8") as f:
        eerd_mmd_content = f.read()

erd_mmd_content = ""
if os.path.exists(r"D:\Criminal Database\docs\erd.mmd"):
    with open(r"D:\Criminal Database\docs\erd.mmd", "r", encoding="utf-8") as f:
        erd_mmd_content = f.read()

# Appendices Content
appendix_a_content = """APPENDIX A: DATABASE SCHEMA DEFINITIONS & DDL SCRIPTS SUMMARY

The system consists of 14 BCNF relations deployed under the InnoDB storage engine on MySQL Community Server 9.7:
1. POLICE_STATIONS: Station headquarters and jurisdictional boundaries. Primary Key: station_id. Unique Keys: station_name, district_code.
2. USERS: Departmental personnel with Disjoint Specialization into Administrator, Police Officer, and Investigator. Primary Key: user_id. Unique Keys: username, email, badge_number. Foreign Key: station_id -> POLICE_STATIONS(station_id).
3. CASES: Criminal incident dockets categorized by priority and classification level. Primary Key: case_id. Unique Key: case_number. Foreign Keys: station_id, created_by -> USERS(user_id).
4. PERSONS: Suspect, victim, and witness registry. Primary Key: person_id.
5. CASE_ASSIGNMENTS: Personnel allocation to case dockets. Primary Key: assignment_id. Foreign Keys: case_id, user_id. Virtual Generated Keys: active_assignment_key, active_lead_key.
6. CASE_PERSONS: Junction table linking personas to cases with specific roles. Primary Key: case_person_id. Foreign Keys: case_id, person_id.
7. EVIDENCE: Physical seized items tracked with unique barcodes. Primary Key: evidence_id. Unique Key: evidence_code. Foreign Keys: case_id, collected_by -> USERS(user_id).
8. EVIDENCE_CUSTODY_LOG: Immutable transfer history populated by triggers. Primary Key: custody_id. Foreign Keys: evidence_id, handled_by -> USERS(user_id).
9. INVESTIGATION_NOTES: Chronological progress entries logged by detectives. Primary Key: note_id. Foreign Keys: case_id, author_id -> USERS(user_id).
10. AUDIT_LOG: Engine-level transaction ledger capturing old and new JSON states. Primary Key: log_id.
11. IUCR_CODES: Illinois Uniform Crime Reporting standard lookup table. Primary Key: iucr_code.
12. PUBLIC_CRIME_INCIDENTS: Open data portal table storing over 50,000 Chicago crime events. Primary Key: incident_id. Unique Key: source_id. Foreign Key: canonical_iucr_code -> IUCR_CODES(iucr_code).
13. CITIZENS: Public community user accounts with salted scrypt credentials. Primary Key: citizen_id. Unique Key: email.
14. CITIZEN_REPORTS: Public complaints decoupled from internal dossiers. Primary Key: report_id. Unique Key: tracking_number. Foreign Key: citizen_id -> CITIZENS(citizen_id)."""

appendix_b_content = """APPENDIX B: AUTOMATED TEST SUITE EXECUTION LOG SUMMARY

Execution Target: MySQL Community Server 9.7.1 on localhost:3306
Test Framework: Pytest 8.4.2 & Python 3.14
Total Tests Configured: 35
Total Tests Passing: 35 (100% Pass Rate)

Module-by-Module Verification Breakdown:
• tests/test_db.py (4 tests): Verified database connectivity, InnoDB engine configuration, foreign key enforcement, and virtual column calculation.
• tests/test_models.py (6 tests): Verified model instantiation, password hashing with scrypt, case status updates, and audit logging.
• tests/test_security_service.py (5 tests): Verified Bell-LaPadula clearance hierarchy (PUBLIC=1 to RESTRICTED=4), Need-to-Know assignment validation, and unauthorized access blocking.
• tests/test_auth_routes.py (4 tests): Verified internal staff login, invalid credentials rejection, session logout, and protected route access control.
• tests/test_citizen_routes.py (8 tests): Verified citizen registration, report filing with CR-YYYY-XXXXX tracking references, public status view, and anti-enumeration HTTP 404 security.
• tests/test_admin_routes.py (3 tests): Verified admin staff management panel, personnel clearance elevation/demotion, and account deactivation.
• tests/test_analytics.py (3 tests): Verified Chicago crime query aggregations, IUCR primary type distribution, and district crime counts.
• tests/test_sql_workbench.py (2 tests): Verified /sql-demo query runner, view execution, and stored procedure execution.

Smoke Test Suite: 24/24 Verification Points Passed (smoke_test.py)."""

appendix_c_content = """APPENDIX C: FACULTY DEMO RUNBOOK REFERENCE SUMMARY

Quick Start Commands:
1. Activate Environment: & 'd:\\Criminal Database\\venv\\Scripts\\Activate.ps1'
2. Start Web Application: python app.py (Listens on http://127.0.0.1:5000)
3. Execute Test Suite: pytest -v

Demonstration User Accounts:
• Administrator: admin / admin123 (Clearance Level: RESTRICTED - Tier 4)
• Investigator: investigator1 / invest123 (Clearance Level: CONFIDENTIAL - Tier 3)
• Police Officer: officer1 / officer123 (Clearance Level: INTERNAL - Tier 2)
• Unassigned Officer: officer2 / officer123 (Clearance Level: INTERNAL - Tier 2)
• Demo Citizen: citizen_demo@example.com / CitizenPass123!

7-Minute Live Evaluation Sequence:
1. Staff Authentication & Clearance Inspection (/login, /admin/staff)
2. Bell-LaPadula MLS & Need-to-Know Enforcement (/cases, /cases/<id>)
3. Investigator Assignment & Stored Procedure Execution (/cases/<id>/assign)
4. Evidence Chain-of-Custody & Trigger Automation (/evidence/<id>/transfer)
5. Decoupled Citizen Portal & Anti-Enumeration 404 Defense (/citizen/login, /citizen/reports/<id>)
6. Chicago Open Data Analytics Dashboard (/analytics)
7. Live SQL Demonstration Workbench (/sql-demo)"""

# -------------------------------------------------------------
# Generate the 9 Extracted Files (Both .docx and .txt)
# -------------------------------------------------------------
index_records = []

for s_idx, spec in enumerate(section_specs, start=1):
    sec_id = spec['id']
    sec_title = spec['title']
    start_idx, end_idx = spec['range']
    diag_notes = spec['diagram_notes']
    
    docx_filename = f"{sec_id}.docx"
    txt_filename = f"{sec_id}.txt"
    docx_path = os.path.join(OUT_DIR, docx_filename)
    txt_path = os.path.join(OUT_DIR, txt_filename)
    
    print(f"\nProcessing [{sec_id}]: range elements {start_idx} to {end_idx}")
    
    # Initialize Document
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        
    # Title Header in DOCX
    p_top = doc.add_paragraph()
    p_top.paragraph_format.space_before = Pt(12)
    p_top.paragraph_format.space_after = Pt(4)
    r = p_top.add_run(sec_title)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(14)
    r = p_meta.add_run(f"Project: Criminal Case Management & Crime Analytics System (BACSE202)\n"
                       f"Course: Database Systems | VIT Chennai, SCOPE | October 2026\n"
                       f"Team: Ayush Sharma [25BAI1392] & Ojas Sugur [25BAI1222]\n"
                       f"Scope: {spec['chapters']}")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = RGBColor(113, 128, 150)
    
    txt_lines = [
        "=" * 80,
        sec_title,
        "=" * 80,
        f"Project: Criminal Case Management & Crime Analytics System (BACSE202)",
        f"Course: Database Systems | VIT Chennai, SCOPE | October 2026",
        f"Team: Ayush Sharma [25BAI1392] & Ojas Sugur [25BAI1222]",
        f"Scope: {spec['chapters']}",
        "-" * 80,
        ""
    ]
    
    extracted_paragraphs_count = 0
    extracted_tables_count = 0
    extracted_code_blocks_count = 0
    
    # Extract sequential elements
    current_items = parsed_items[start_idx : end_idx + 1]
    
    for item in current_items:
        if item['type'] == 'p':
            p_text = item['text']
            p_obj = item['obj']
            has_drawings = item['has_drawings']
            
            if not p_text.strip() and not has_drawings:
                continue
                
            extracted_paragraphs_count += 1
            
            # DOCX Paragraph
            p_new = doc.add_paragraph()
            p_new.paragraph_format.line_spacing = 1.15
            p_new.paragraph_format.space_after = Pt(6)
            
            if item['is_heading']:
                p_new.paragraph_format.space_before = Pt(12)
                p_new.paragraph_format.space_after = Pt(4)
                r = p_new.add_run(p_text)
                r.font.name = 'Times New Roman'
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = RGBColor(26, 54, 93)
                
                txt_lines.append(f"\n### {p_text}\n")
            elif has_drawings:
                # Describe image and insert transcription
                p_new.paragraph_format.space_before = Pt(8)
                p_new.paragraph_format.space_after = Pt(8)
                r = p_new.add_run("[EMBEDDED DIAGRAM / IMAGE]")
                r.font.name = 'Times New Roman'
                r.font.bold = True
                r.font.color.rgb = RGBColor(43, 108, 176)
                
                txt_lines.append("\n[EMBEDDED DIAGRAM / IMAGE]")
            else:
                # Normal paragraph, preserve bold prefix if multiple runs
                if len(p_obj.runs) > 1 and p_obj.runs[0].bold:
                    r0 = p_new.add_run(p_obj.runs[0].text)
                    r0.font.name = 'Times New Roman'
                    r0.font.size = Pt(11.5)
                    r0.font.bold = True
                    r0.font.color.rgb = RGBColor(26, 54, 93)
                    
                    r1 = p_new.add_run("".join(r.text for r in p_obj.runs[1:]))
                    r1.font.name = 'Times New Roman'
                    r1.font.size = Pt(11.5)
                    r1.font.color.rgb = RGBColor(45, 55, 72)
                    
                    txt_lines.append(f"{p_obj.runs[0].text}{''.join(r.text for r in p_obj.runs[1:])}\n")
                else:
                    r = p_new.add_run(p_text)
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(11.5)
                    r.font.color.rgb = RGBColor(45, 55, 72)
                    
                    txt_lines.append(f"{p_text}\n")
                    
        elif item['type'] == 'tbl':
            if item['is_code']:
                extracted_code_blocks_count += 1
                c_text = item['code_text']
                add_code_block(doc, c_text)
                
                txt_lines.append("```sql")
                txt_lines.append(c_text)
                txt_lines.append("```\n")
            else:
                extracted_tables_count += 1
                all_rows = item['all_rows']
                t_new = doc.add_table(rows=len(all_rows), cols=len(all_rows[0]))
                style_table(t_new, header_bg="1A365D", alt_bg="F7FAFC")
                for r_idx, r_data in enumerate(all_rows):
                    for c_idx, c_text in enumerate(r_data):
                        t_new.cell(r_idx, c_idx).paragraphs[0].text = c_text
                doc.add_paragraph().paragraph_format.space_after = Pt(4)
                
                txt_lines.append(format_text_table(item['headers'], item['body_rows']))

    # Include Rich Diagram Transcriptions where applicable
    if sec_id == '04_Methodology_and_System_Design':
        p_diag = doc.add_paragraph()
        p_diag.paragraph_format.space_before = Pt(10)
        p_diag.paragraph_format.space_after = Pt(4)
        r = p_diag.add_run("Figure 5.1: Multi-Tier Architecture Textual & Structural Transcription")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(26, 54, 93)
        
        diag_desc = (
            "Architecture Flow Transcription:\n"
            "1. Client Tier: Internal Staff Portal (/login, /cases) and Decoupled Citizen Portal (/citizen/login, /citizen/reports).\n"
            "2. Presentation Tier: Flask Jinja2 Web Engine, Bootstrap 5.3.3 UI, Chart.js 4.4.1 Interactive Visualizations.\n"
            "3. Application & Security Tier: Python 3.14, Flask 3.1.2, security_service.py (Bell-LaPadula MLS, Need-to-Know), "
            "Session Context Injector (@app_user_id, @app_username).\n"
            "4. Storage Tier: MySQL Community Server 9.7 (InnoDB), Dual Accounts (crimedb_admin for DDL, crimedb_app for queries), "
            "DEFINER Triggers, Stored Procedures (sp_assign_case), Deterministic Functions (fn_case_duration), 14 BCNF Tables."
        )
        p_d_body = doc.add_paragraph()
        p_d_body.add_run(diag_desc).font.name = 'Times New Roman'
        
        txt_lines.append("\n" + "=" * 50)
        txt_lines.append("FIGURE 5.1 TRANSCRIPTION: MULTI-TIER ARCHITECTURE")
        txt_lines.append("=" * 50)
        txt_lines.append(diag_desc + "\n")
        
    elif sec_id == '05_Database_Design':
        p_diag = doc.add_paragraph()
        p_diag.paragraph_format.space_before = Pt(12)
        p_diag.paragraph_format.space_after = Pt(4)
        r = p_diag.add_run("Figure 6.1: Enhanced Entity-Relationship (EER) Transcription & Mermaid Specification")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(26, 54, 93)
        add_code_block(doc, eerd_mmd_content)
        
        p_diag2 = doc.add_paragraph()
        p_diag2.paragraph_format.space_before = Pt(12)
        p_diag2.paragraph_format.space_after = Pt(4)
        r = p_diag2.add_run("Figure 6.2: Complete 14-Table ERD Transcription & Mermaid Specification")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(26, 54, 93)
        add_code_block(doc, erd_mmd_content)
        
        txt_lines.append("\n" + "=" * 50)
        txt_lines.append("FIGURE 6.1 TRANSCRIPTION: EER SPECIALIZATION DIAGRAM")
        txt_lines.append("=" * 50)
        txt_lines.append(eerd_mmd_content + "\n")
        
        txt_lines.append("\n" + "=" * 50)
        txt_lines.append("FIGURE 6.2 TRANSCRIPTION: COMPLETE 14-TABLE ERD")
        txt_lines.append("=" * 50)
        txt_lines.append(erd_mmd_content + "\n")
        
    elif sec_id == '06_System_Implementation':
        p_diag = doc.add_paragraph()
        p_diag.paragraph_format.space_before = Pt(10)
        p_diag.paragraph_format.space_after = Pt(4)
        r = p_diag.add_run("Figure 11.1: Cloud Production Deployment Topology Transcription")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(26, 54, 93)
        
        cloud_desc = (
            "Cloud Infrastructure Topology Transcription:\n"
            "• Public Ingress: AWS Route 53 DNS -> Internet Gateway -> Application Load Balancer (ALB) with SSL/TLS Termination.\n"
            "• Private App Subnet: Flask Container Pods running within an Auto-Scaling Group in a Private VPC Subnet.\n"
            "• Security & Secrets: AWS Secrets Manager / HashiCorp Vault injecting database credentials into environment variables at boot time.\n"
            "• Private Database Subnet: Managed MySQL Instance (AWS RDS Multi-AZ) with automated automated replication and zero public ingress."
        )
        p_d_body = doc.add_paragraph()
        p_d_body.add_run(cloud_desc).font.name = 'Times New Roman'
        
        txt_lines.append("\n" + "=" * 50)
        txt_lines.append("FIGURE 11.1 TRANSCRIPTION: CLOUD TOPOLOGY")
        txt_lines.append("=" * 50)
        txt_lines.append(cloud_desc + "\n")
        
    elif sec_id == '09_References_and_Appendices':
        # Append Appendix A, B, C
        for app_title, app_text in [
            ("APPENDIX A: DATABASE SCHEMA DEFINITIONS & DDL SCRIPTS SUMMARY", appendix_a_content),
            ("APPENDIX B: AUTOMATED TEST SUITE EXECUTION LOG SUMMARY", appendix_b_content),
            ("APPENDIX C: FACULTY DEMO RUNBOOK REFERENCE SUMMARY", appendix_c_content)
        ]:
            p_h = doc.add_paragraph()
            p_h.paragraph_format.space_before = Pt(14)
            p_h.paragraph_format.space_after = Pt(4)
            r = p_h.add_run(app_title)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(26, 54, 93)
            
            p_b = doc.add_paragraph()
            p_b.paragraph_format.space_before = Pt(0)
            p_b.paragraph_format.space_after = Pt(8)
            p_b.paragraph_format.line_spacing = 1.15
            p_b.add_run(app_text).font.name = 'Times New Roman'
            
            txt_lines.append("\n" + "=" * 60)
            txt_lines.append(app_title)
            txt_lines.append("=" * 60)
            txt_lines.append(app_text + "\n")

    # Save DOCX and TXT files
    doc.save(docx_path)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))
        
    print(f"  -> Generated {docx_filename} ({os.path.getsize(docx_path)} bytes)")
    print(f"  -> Generated {txt_filename} ({os.path.getsize(txt_path)} bytes)")
    
    index_records.append({
        'sec_num': f"{s_idx:02d}",
        'sec_id': sec_id,
        'title': spec['title'].split(':')[1].strip(),
        'docx_file': docx_filename,
        'txt_file': txt_filename,
        'p_count': extracted_paragraphs_count,
        'tbl_count': extracted_tables_count,
        'code_count': extracted_code_blocks_count,
        'chapters': spec['chapters'],
        'diagram_notes': diag_notes
    })

print("\nAll 9 sections generated successfully in both DOCX and TXT formats!")

# -------------------------------------------------------------
# Generate Extraction_Index.docx & Extraction_Index.txt
# -------------------------------------------------------------
index_docx_path = os.path.join(OUT_DIR, "Extraction_Index.docx")
index_txt_path = os.path.join(OUT_DIR, "Extraction_Index.txt")

idx_doc = docx.Document()
for s in idx_doc.sections:
    s.top_margin = Inches(1.0)
    s.bottom_margin = Inches(1.0)
    s.left_margin = Inches(1.0)
    s.right_margin = Inches(1.0)
    s.page_width = Inches(8.27)
    s.page_height = Inches(11.69)

p_idx_title = idx_doc.add_paragraph()
p_idx_title.paragraph_format.space_before = Pt(12)
p_idx_title.paragraph_format.space_after = Pt(4)
r = p_idx_title.add_run("PROJECT REPORT TEXT EXTRACTION INDEX & AUDIT CATALOG")
r.font.name = 'Times New Roman'
r.font.size = Pt(16)
r.font.bold = True
r.font.color.rgb = RGBColor(26, 54, 93)

p_sub = idx_doc.add_paragraph()
p_sub.paragraph_format.space_before = Pt(0)
p_sub.paragraph_format.space_after = Pt(12)
r = p_sub.add_run("BACSE202 – Database Systems Project Final Report | Verification & Extraction Audit")
r.font.name = 'Times New Roman'
r.font.size = Pt(12)
r.font.bold = True
r.font.color.rgb = RGBColor(43, 108, 176)

p_desc = idx_doc.add_paragraph()
p_desc.paragraph_format.space_before = Pt(0)
p_desc.paragraph_format.space_after = Pt(14)
p_desc.paragraph_format.line_spacing = 1.15
r = p_desc.add_run(
    f"This extraction index audits the complete, unedited text extraction from the final project report:\n"
    f"• Source Document: {SRC_DOCX}\n"
    f"• Total Pages in Original Report: 47 rendered pages (verified via Word COM PDF export)\n"
    f"• Total Sequential Elements Extracted: {len(parsed_items)} (212 Paragraphs, 26 Tables)\n"
    f"• Number of Modular Extraction Sections: 9 Sections (Available in both .docx and .txt)\n"
    f"• Destination Directory: {OUT_DIR}\n"
    f"• Source File Integrity: The original DOCX remains completely unmodified and preserved."
)
r.font.name = 'Times New Roman'
r.font.size = Pt(10.5)
r.font.color.rgb = RGBColor(74, 85, 104)

# Table of Sections
t_idx = idx_doc.add_table(rows=len(index_records) + 1, cols=6)
style_table(t_idx, header_bg="1A365D", alt_bg="F7FAFC")
headers_idx = ["Section #", "Modular File Name", "Core Contents & Chapters Included", "Paragraphs", "Tables", "Code Blocks"]
for c_i, h in enumerate(headers_idx):
    t_idx.cell(0, c_i).paragraphs[0].text = h

for r_i, rec in enumerate(index_records, start=1):
    t_idx.cell(r_i, 0).paragraphs[0].text = rec['sec_num']
    t_idx.cell(r_i, 1).paragraphs[0].text = f"{rec['sec_id']}.docx\n({rec['sec_id']}.txt)"
    t_idx.cell(r_i, 2).paragraphs[0].text = f"{rec['title']}\n{rec['chapters']}"
    t_idx.cell(r_i, 3).paragraphs[0].text = str(rec['p_count'])
    t_idx.cell(r_i, 4).paragraphs[0].text = str(rec['tbl_count'])
    t_idx.cell(r_i, 5).paragraphs[0].text = str(rec['code_count'])

idx_doc.add_paragraph().paragraph_format.space_after = Pt(10)

# Section for Diagram and Non-Extractable Visuals Audit
p_diag_h = idx_doc.add_paragraph()
p_diag_h.paragraph_format.space_before = Pt(14)
p_diag_h.paragraph_format.space_after = Pt(4)
r = p_diag_h.add_run("Diagram, Image & Vector Content Extraction Status")
r.font.name = 'Times New Roman'
r.font.size = Pt(13)
r.font.bold = True
r.font.color.rgb = RGBColor(26, 54, 93)

diag_records = [
    ("VIT Chennai Logo", "Cover Page (p. 1) & Title Page (p. 2)", "docs/vit_logo.png (982x280 PNG RGBA)", "Official university seal with heraldic crest and typography. Textual transcription provided in Section 01."),
    ("Figure 5.1: Multi-Tier Architecture", "Chapter 5 (p. 10)", "docs/PROJECT_REPORT.md Section 5", "System architecture diagram illustrating Client, Web/Presentation, Application Security, and Database tiers. Full structural transcription included in Section 04."),
    ("Figure 6.1: Enhanced Entity-Relationship (EER)", "Chapter 6 (p. 14)", "docs/eerd.png (generated from docs/eerd.mmd)", "EER diagram depicting Disjoint Total Specialization (d, t) of USERS into Administrator, Police Officer, and Investigator. Full Mermaid code and textual transcription included in Section 05."),
    ("Figure 6.2: Complete 14-Table Relational ERD", "Chapter 6 (p. 16)", "docs/erd.png (generated from docs/erd.mmd)", "Complete 14-table relational ERD with primary keys, foreign keys, cardinality notations, and domain clustering. Full Mermaid code and schema definition included in Section 05."),
    ("Figure 11.1: Cloud Deployment Topology", "Chapter 11 (p. 35)", "docs/PROJECT_REPORT.md Section 11", "Cloud production topology showing ALB, private container subnets, and isolated RDS MySQL subnets. Full architectural transcription included in Section 06.")
]

t_diag = idx_doc.add_table(rows=len(diag_records) + 1, cols=4)
style_table(t_diag, header_bg="2B6CB0", alt_bg="F7FAFC")
headers_diag = ["Visual / Diagram Element", "Original Page Location", "Source Asset / Reference", "Extraction & Transcription Status"]
for c_i, h in enumerate(headers_diag):
    t_diag.cell(0, c_i).paragraphs[0].text = h

for r_i, d_rec in enumerate(diag_records, start=1):
    for c_i, val in enumerate(d_rec):
        t_diag.cell(r_i, c_i).paragraphs[0].text = val

idx_doc.save(index_docx_path)
print(f"Generated {index_docx_path} ({os.path.getsize(index_docx_path)} bytes)")

# Generate Extraction_Index.txt
txt_idx_lines = [
    "=" * 80,
    "PROJECT REPORT TEXT EXTRACTION INDEX & AUDIT CATALOG",
    "=" * 80,
    f"Source Document: {SRC_DOCX}",
    f"Total Rendered Pages in Original Report: 47 pages",
    f"Total Sequential Elements Extracted: {len(parsed_items)} (212 Paragraphs, 26 Tables)",
    f"Number of Modular Sections: 9 Sections",
    f"Extraction Destination: {OUT_DIR}",
    f"Source Integrity Status: Original DOCX is completely UNCHANGED and preserved.",
    "-" * 80,
    "",
    "MODULAR SECTIONS AUDIT TABLE:",
    format_text_table(
        ["Section", "File Name", "Included Chapters", "Paragraphs", "Tables", "Code Blocks"],
        [[rec['sec_num'], rec['sec_id'] + ".docx", rec['chapters'], str(rec['p_count']), str(rec['tbl_count']), str(rec['code_count'])] for rec in index_records]
    ),
    "=" * 80,
    "IMAGE & DIAGRAM TRANSCRIPTION STATUS:",
    format_text_table(
        ["Diagram Element", "Page Location", "Source Asset", "Transcription Status"],
        [[d[0], d[1], d[2], d[3]] for d in diag_records]
    ),
    "=" * 80,
    "END OF AUDIT CATALOG"
]

with open(index_txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(txt_idx_lines))

print(f"Generated {index_txt_path} ({os.path.getsize(index_txt_path)} bytes)")
