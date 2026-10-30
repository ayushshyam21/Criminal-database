import docx

doc = docx.Document(r"D:\VIT study\BACSE202_DBMS_ProjectReport.docx")

print("=== TABLE 0 (TOC) SAMPLE ===")
for r in doc.tables[0].rows[:15]:
    print([c.text.strip() for c in r.cells])

print("\n=== TABLE 1 (LIST OF TABLES) SAMPLE ===")
for r in doc.tables[1].rows[:6]:
    print([c.text.strip() for c in r.cells])

print("\n=== TABLE 2 (LIST OF FIGURES) SAMPLE ===")
for r in doc.tables[2].rows[:6]:
    print([c.text.strip() for c in r.cells])

print("\n=== TABLE 3 (ABBREVIATIONS) SAMPLE ===")
for r in doc.tables[3].rows[:10]:
    print([c.text.strip() for c in r.cells])
