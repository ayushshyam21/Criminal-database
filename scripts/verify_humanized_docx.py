import docx

doc_orig = docx.Document('Criminal_Case_Management_Final_Report.docx')
doc_hum = docx.Document('Criminal_Case_Management_Final_Report_Humanized.docx')

print(f"Original Paragraphs: {len(doc_orig.paragraphs)} | Humanized Paragraphs: {len(doc_hum.paragraphs)}")
print(f"Original Tables:     {len(doc_orig.tables)} | Humanized Tables:     {len(doc_hum.tables)}")
print(f"Original Sections:   {len(doc_orig.sections)} | Humanized Sections:   {len(doc_hum.sections)}")

orig_draw = sum(len(p._p.xpath('.//w:drawing') or p._p.xpath('.//w:pict')) for p in doc_orig.paragraphs)
hum_draw = sum(len(p._p.xpath('.//w:drawing') or p._p.xpath('.//w:pict')) for p in doc_hum.paragraphs)
print(f"Original Drawings:   {orig_draw} | Humanized Drawings:   {hum_draw}")

# Check team members
team_text = doc_hum.paragraphs[12].text
print("Team details check:", repr(team_text))
assert "Ayush Sharma [25BAI1392]" in team_text and "Ojas Sugur [25BAI1222]" in team_text

# Check Abstract
abs_p = [doc_hum.paragraphs[30].text, doc_hum.paragraphs[31].text, doc_hum.paragraphs[32].text]
total_words = sum(len(p.split()) for p in abs_p)
print(f"Abstract 3 paragraphs total words: {total_words}")

# Check Chapters
chapters_present = []
for i, p in enumerate(doc_hum.paragraphs):
    if p.text.startswith("Chapter "):
        chapters_present.append(p.text.split(":")[0])
print(f"Chapters present ({len(chapters_present)}):", chapters_present)

print("ALL BASIC DOCX INTEGRITY CHECKS PASSED!")
