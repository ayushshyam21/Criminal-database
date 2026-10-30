import os
import docx

revised_dir = r"D:\Criminal Database\Revised_Chapters"
master_path = r"D:\Criminal Database\Criminal_Case_Management_Final_Report.docx"

master_doc = docx.Document(master_path)
print(f"Master Doc: {len(master_doc.paragraphs)} paragraphs, {len(master_doc.tables)} tables.")

for fname in sorted(os.listdir(revised_dir)):
    fpath = os.path.join(revised_dir, fname)
    rdoc = docx.Document(fpath)
    print(f"\n--- {fname} ---")
    print(f"Paragraphs: {len(rdoc.paragraphs)}, Tables: {len(rdoc.tables)}")
    # Print non-header paragraphs
    meaningful_p = [p.text.strip() for p in rdoc.paragraphs if p.text.strip() and not p.text.startswith("0") and not p.text.startswith("Project:") and not p.text.startswith("=")]
    print(f"Meaningful paragraphs: {len(meaningful_p)}")
    for mp in meaningful_p[:3]:
        print("   Sample:", mp[:65])
