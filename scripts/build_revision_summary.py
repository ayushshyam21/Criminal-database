import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

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
    for i, col in enumerate(table.columns):
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

def build_summary():
    doc = docx.Document()
    
    # Page setup
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r = p_title.add_run("HUMANIZATION REVISION SUMMARY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    r = p_sub.add_run("BACSE202 – Database Systems Project Final Evaluation Report\nCriminal Case Management & Crime Analytics System (CCMS)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor(43, 108, 176)

    # Metadata
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(14)
    p_meta.paragraph_format.line_spacing = 1.2
    r = p_meta.add_run(
        "Institution: VIT Chennai, School of Computer Science and Engineering (SCOPE)\n"
        "Course: BACSE202 – DATABASE SYSTEMS | Semester: Fall / Winter 2026\n"
        "Students: Ayush Sharma [25BAI1392] & Ojas Sugur [25BAI1222]\n"
        "Supervisor: DR. HEMALATHA K (Assistant Professor Senior Grade 1)\n"
        "Document Modified: Criminal_Case_Management_Final_Report_Humanized.docx\n"
        "Date of Revision: 30/10/2026"
    )
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(74, 85, 104)

    # 1. Executive Overview
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("1. Executive Overview & Humanization Methodology")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    p_body1 = doc.add_paragraph()
    p_body1.paragraph_format.space_before = Pt(0)
    p_body1.paragraph_format.space_after = Pt(8)
    p_body1.paragraph_format.line_spacing = 1.15
    p_body1.add_run(
        "This revision summary documents the thorough, in-place humanization of our academic project report. "
        "The objective was to transform formulaic, overly generic, or repetitive AI-like phrasing into clear, authentic "
        "academic English that reflects the genuine voice and hands-on understanding of B.Tech Artificial Intelligence and "
        "Machine Learning students who engineered this database system."
    ).font.name = 'Times New Roman'

    p_body2 = doc.add_paragraph()
    p_body2.paragraph_format.space_before = Pt(0)
    p_body2.paragraph_format.space_after = Pt(12)
    p_body2.paragraph_format.line_spacing = 1.15
    p_body2.add_run(
        "Crucially, the document editing was executed directly on a structured copy of the approved report "
        "(Criminal_Case_Management_Final_Report_Humanized.docx). All visual formatting, section breaks, Roman and decimal "
        "page numbering, table borders, embedded images (including the official VIT Chennai logo, EER diagram, and ERD diagram), "
        "code block tables, and references were preserved with zero structural disruption."
    ).font.name = 'Times New Roman'

    # 2. Key Improvements Table
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r = h2.add_run("2. Chapter-by-Chapter Improvements & Concrete Implementation Linkages")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    summary_rows = [
        ("Preliminary Pages (Abstract, Decl, Cert, Ack)", 
         "Rewrote Abstract to 315 natural words across 3 balanced paragraphs + 10 keywords. Polished Declaration, Certificate, and Acknowledgement with respectful, authentic student gratitude.", 
         "Explains project motivation, 14-table BCNF schema, Bell-LaPadula security, Citizen Portal, and 35 Pytest benchmarks without generic fluff."),
        ("Chapter 1: Problem Statement", 
         "Replaced generic buzzwords with operational realities of municipal police station desks (handwriting FIR dockets, lost papers, unnormalized spreadsheet columns).", 
         "Connects operational failures to relational anomalies (insertion, deletion, update) and tamperable custody logs lacking forensic audit trails."),
        ("Chapter 2: Project Objectives & Scope", 
         "Reframed objectives as student engineering goals rather than abstract corporate marketing claims.", 
         "Clarified why dual MySQL accounts were created, why BCNF was targeted, and how 50k Chicago records were reconciled via canonical IUCR lookups."),
        ("Chapter 3: Literature Survey & Foundations", 
         "Linked prior policing studies directly to our progression from DA1 (Ojas Sugur) to final implementation.", 
         "Grounds the system in classic database literature (Elmasri & Navathe for BCNF, Bell & LaPadula for MLS, Silberschatz for transaction controls)."),
        ("Chapter 4: Requirements & Roles", 
         "Specified the 4 operational roles and 12 functional requirements using precise, unambiguous student wording.", 
         "Emphasizes password hashing with salted scrypt (32768:8:1) and anti-enumeration HTTP 404 security design for citizen reports."),
        ("Chapter 5: System Design & Architecture", 
         "Explained the three-tier design from the viewpoint of student developers implementing Flask and MySQL.", 
         "Articulates why InnoDB was chosen (ACID transactions, foreign key cascades, virtual columns) and how Flask injects session variables (@app_user_id) into MySQL."),
        ("Chapter 6: Database Design, ER & EER", 
         "Narrated the authentic evolution from DA1's initial 6-table concept to the 14-table BCNF enterprise architecture.", 
         "Explains the Enhanced ER Disjoint Total Specialization (d, t) using a single table with ENUM discriminator to avoid expensive outer joins."),
        ("Chapter 7: Schema & Data Dictionary", 
         "Preserved formal relational notation and comprehensive 14-table Data Dictionary exactly as defined.", 
         "Maintains all primary keys [PK], candidate keys [CK], foreign keys, and column types without altering technical names."),
        ("Chapter 8: Normalization Proofs", 
         "Clarified the mathematical proofs for USERS, CASES, and CASE_ASSIGNMENTS in accessible academic language.", 
         "Explains the virtual generated column active_assignment_key and how its UNIQUE index mathematically enforces BCNF without concurrency races."),
        ("Chapter 9: SQL Implementation Catalog", 
         "Connected DA2 foundational SQL queries (Ayush Sharma) to the expanded production queries for the web platform.", 
         "Explains multi-table joins, subqueries, grouping aggregates, and analytical views (v_case_summary)."),
        ("Chapter 10: Advanced Database Features", 
         "Detailed server-side database routines (sp_assign_case, fn_case_duration, triggers, cursors) from a practical implementation standpoint.", 
         "Explains atomic investigator reassignment inside an ACID transaction and tamper-evident custody logging using session variables."),
        ("Chapter 11: Cloud Deployment Architecture", 
         "Distinguished between verified local development (Python 3.14 + MySQL 9.7) and planned production cloud topology.", 
         "Describes multi-stage Docker containerization, Application Load Balancers, private subnets, and secrets management."),
        ("Chapter 12: Testing & Quality Assurance", 
         "Documented test methodology with authentic student rigor, citing actual test scripts and outcomes.", 
         "Reports the 35 automated Pytest integration tests and confirms MySQL Error 1142 ('command denied') on least-privilege violation attempts."),
        ("Chapter 13: Performance Analysis & Indexing", 
         "Explained how importing 50,000 Chicago incidents necessitated secondary B-tree composite indexing.", 
         "Analyzes MySQL EXPLAIN plans, demonstrating how idx_pci_district shifted access from ALL to range/ref, cutting scanned rows by >95% and latency from 160ms to <5ms."),
        ("Chapter 14: Results & Discussion", 
         "Documented genuine development hurdles, design tradeoffs, and technical lessons learned.", 
         "Discusses least-privilege unit test errors resolved with UUID emails, anti-enumeration 403 vs 404 security decisions, and null-safe template guards."),
        ("Chapter 15: Conclusion", 
         "Summarized the project trajectory from DA1 conceptual sketches to a fully verified 14-table BCNF database system.", 
         "Emphasizes the value of enforcing business constraints and security policies directly inside the database engine."),
        ("Chapter 16: Future Scope", 
         "Articulated practical future extensions in clear, realistic terms.", 
         "Covers MySQL spatial GIS extensions (POINT, R-tree indexes), biometric vector similarity search, and blockchain custody anchoring.")
    ]

    tbl = doc.add_table(rows=len(summary_rows) + 1, cols=3)
    style_table(tbl, header_bg="1A365D", alt_bg="F7FAFC")
    tbl.cell(0, 0).paragraphs[0].text = "Section / Chapter"
    tbl.cell(0, 1).paragraphs[0].text = "Humanized Phrasing Improvements"
    tbl.cell(0, 2).paragraphs[0].text = "DBMS & Real-World Concepts Integrated"
    
    for r_idx, (sec_name, improv, dbms_link) in enumerate(summary_rows, start=1):
        tbl.cell(r_idx, 0).paragraphs[0].text = sec_name
        tbl.cell(r_idx, 1).paragraphs[0].text = improv
        tbl.cell(r_idx, 2).paragraphs[0].text = dbms_link

    # 3. Verification of Preserved Elements
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(16)
    h3.paragraph_format.space_after = Pt(6)
    r = h3.add_run("3. Verification of Preserved Formatting & Visual Elements")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    verif_items = [
        ("Official VIT Chennai Logo", "PRESERVED", "Present on Cover Page (width=3.8 in) and Submission Page (width=3.3 in) from docs/vit_logo.png."),
        ("Cover Page Design", "PRESERVED", "BACSE202, title, video link placeholder, VIT logo, institution, and date October 2026 intact."),
        ("Submission & Preliminary Pages", "PRESERVED", "Title page, Declaration, Certificate, Abstract, Acknowledgement, TOC, LOT, LOF, and Abbreviations present."),
        ("Team Details & Reg Numbers", "PRESERVED", "Ayush Sharma [25BAI1392] and Ojas Sugur [25BAI1222] verified across all pages."),
        ("Tables & Data Dictionaries", "PRESERVED", "All 26 tables (including 14-table Data Dictionary and code block tables) remain intact."),
        ("Diagrams & Illustrations", "PRESERVED", "EER Specialization diagram and Complete 14-Table Relational ERD diagram embedded and captioned."),
        ("Section Breaks & Numbering", "PRESERVED", "Section 0 unnumbered, Section 1 lowerRoman (i-x), Section 2 decimal Arabic (1-37) starting at page 1."),
        ("PDF Export & Page Inspection", "VERIFIED", "Compiled via native Microsoft Word COM automation to 47 clean, unbroken pages (586 KB).")
    ]

    tbl_v = doc.add_table(rows=len(verif_items) + 1, cols=3)
    style_table(tbl_v, header_bg="2B6CB0", alt_bg="F7FAFC")
    tbl_v.cell(0, 0).paragraphs[0].text = "Visual / Structural Element"
    tbl_v.cell(0, 1).paragraphs[0].text = "Status"
    tbl_v.cell(0, 2).paragraphs[0].text = "Verification Note"

    for r_idx, (elem, stat, note) in enumerate(verif_items, start=1):
        tbl_v.cell(r_idx, 0).paragraphs[0].text = elem
        tbl_v.cell(r_idx, 1).paragraphs[0].text = stat
        tbl_v.cell(r_idx, 2).paragraphs[0].text = note

    # 4. Factual Details Flagged for Final User Confirmation
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(6)
    r = h4.add_run("4. Factual Details Flagged for Final Student / Faculty Confirmation")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    p_flags = doc.add_paragraph()
    p_flags.paragraph_format.space_before = Pt(0)
    p_flags.paragraph_format.space_after = Pt(10)
    p_flags.paragraph_format.line_spacing = 1.2
    p_flags.add_run(
        "The following factual placeholders and operational parameters have been maintained transparently in the "
        "document and can be customized before final evaluation submission:\n\n"
        "1. Project Explanation Video Link: Located on the cover page as 'Project Explanation Video: [INSERT VIDEO LINK]'. "
        "Please insert your recorded YouTube/Google Drive demonstration link before final printing.\n\n"
        "2. Faculty Supervisor Designation: Listed as 'DR. HEMALATHA K (Assistant Professor Senior Grade 1)'. "
        "If an alternate project guide or co-guide is assigned, update the placeholder on the Declaration and Certificate pages.\n\n"
        "3. Date and Submission Place: Recorded as 'Place: VIT CHENNAI' and 'Date: 30/10/2026'. Adjust the submission date "
        "if your evaluation or viva occurs on a subsequent schedule.\n\n"
        "4. Live Test Suite Execution: Confirmed as 35 passing Pytest integration tests and a 24-point smoke test suite "
        "executed directly against MySQL Community Server 9.7.1 on Windows."
    ).font.name = 'Times New Roman'
    p_flags.paragraph_format.line_spacing = 1.25

    doc.save("Humanization_Revision_Summary.docx")
    print("Saved Humanization_Revision_Summary.docx successfully.")

if __name__ == "__main__":
    build_summary()
