import docx
import pypdf
import os

pdf_path = r"D:\Criminal Database\Criminal_Case_Management_Final_Report.pdf"
docx_path = r"D:\Criminal Database\Criminal_Case_Management_Final_Report.docx"

print("======================================================================")
print("ACADEMIC REPORT VERIFICATION: DOCX & PDF INSPECTION")
print("======================================================================")

# 1. Inspect DOCX structure
doc = docx.Document(docx_path)
print(f"[DOCX] Total Paragraphs: {len(doc.paragraphs)}")
print(f"[DOCX] Total Tables: {len(doc.tables)}")
print(f"[DOCX] Total Sections: {len(doc.sections)}")

# Check images in docx
image_count = 0
for rel in doc.part.rels.values():
    if "image" in rel.target_ref:
        image_count += 1
print(f"[DOCX] Total Embedded Images: {image_count}")

# 2. Inspect PDF structure
reader = pypdf.PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"[PDF] Total Rendered Pages: {total_pages}")

print("\n--- FIRST 12 RENDERED PAGES IN PDF ---")
for i in range(min(12, total_pages)):
    page = reader.pages[i]
    text = page.extract_text()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    first_few = " | ".join(lines[:3]) if lines else "EMPTY / IMAGE ONLY"
    last_line = lines[-1] if lines else ""
    print(f"Page {i+1:02d}: {first_few[:70]}... [Footer/End: {last_line}]")

# Check Abstract length
abstract_paragraphs = []
is_in_abstract = False
for p in doc.paragraphs:
    if p.text.strip() == "ABSTRACT":
        is_in_abstract = True
        continue
    if is_in_abstract:
        if "Keywords:" in p.text or p.text.strip() == "ACKNOWLEDGEMENT":
            break
        if p.text.strip():
            abstract_paragraphs.append(p.text.strip())

full_abstract = " ".join(abstract_paragraphs)
words = full_abstract.split()
print(f"\n[ABSTRACT] Paragraphs count: {len(abstract_paragraphs)}")
print(f"[ABSTRACT] Total Word count: {len(words)} words")
print(f"[ABSTRACT] Meets 250-350 target: {250 <= len(words) <= 350}")

# Check Video link
video_link_found = any("Project Explanation Video: [INSERT VIDEO LINK]" in p.text for p in doc.paragraphs)
print(f"[COVER] Video link placeholder present: {video_link_found}")

# Check Team members
team_found = any("Ayush Sharma [25BAI1392]" in p.text for p in doc.paragraphs) and any("Ojas Sugur [25BAI1222]" in p.text for p in doc.paragraphs)
print(f"[AUTHORS] Team members verified: {team_found}")

# Check Preliminary Pages
has_decl = any("DECLARATION" in p.text for p in doc.paragraphs)
has_cert = any("CERTIFICATE" in p.text for p in doc.paragraphs)
has_abst = any("ABSTRACT" in p.text for p in doc.paragraphs)
has_ackn = any("ACKNOWLEDGEMENT" in p.text for p in doc.paragraphs)
has_toc  = any("TABLE OF CONTENTS" in p.text for p in doc.paragraphs)
has_lot  = any("LIST OF TABLES" in p.text for p in doc.paragraphs)
has_lof  = any("LIST OF FIGURES" in p.text for p in doc.paragraphs)
has_abbr = any("LIST OF ABBREVIATIONS AND NOMENCLATURE" in p.text for p in doc.paragraphs)

print(f"[CHECKLIST] Declaration: {has_decl}")
print(f"[CHECKLIST] Certificate: {has_cert}")
print(f"[CHECKLIST] Abstract: {has_abst}")
print(f"[CHECKLIST] Acknowledgement: {has_ackn}")
print(f"[CHECKLIST] Table of Contents: {has_toc}")
print(f"[CHECKLIST] List of Tables: {has_lot}")
print(f"[CHECKLIST] List of Figures: {has_lof}")
print(f"[CHECKLIST] List of Abbreviations: {has_abbr}")
