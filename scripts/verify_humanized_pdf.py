import os
from pypdf import PdfReader

pdf_path = "Criminal_Case_Management_Final_Report_Humanized.pdf"
print(f"File size: {os.path.getsize(pdf_path)} bytes")

reader = PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"Total Rendered Pages: {total_pages}")

# Print preview of first 12 pages
for i in range(min(12, total_pages)):
    txt = reader.pages[i].extract_text() or ""
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    first_line = lines[0] if lines else "EMPTY"
    last_line = lines[-1] if lines else "EMPTY"
    print(f"Page {i+1:02d}: {first_line[:40]}... [Footer/End: {last_line[-40:]}]")

# Check for key phrases in pages
full_text = " ".join((page.extract_text() or "") for page in reader.pages)
assert "Ayush Sharma [25BAI1392]" in full_text
assert "Ojas Sugur [25BAI1222]" in full_text
assert "DR. HEMALATHA K" in full_text
assert "BACSE202" in full_text
assert "Boyce-Codd Normal Form" in full_text
assert "sp_assign_case" in full_text
assert "fn_case_duration" in full_text
assert "trg_evidence_custody_update" in full_text
assert "CR-YYYY-XXXXX" in full_text
assert "City of Chicago" in full_text
assert "35" in full_text

print("\n[VERIFICATION PASSED] PDF contains all required content, signatures, and code artifacts.")
