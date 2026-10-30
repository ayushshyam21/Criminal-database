import os
import docx

master_doc = docx.Document("Criminal_Case_Management_Final_Report.docx")

# Let's inspect paragraphs in Chapter 4 of master
print("Master Chapter 4 paragraphs:")
for i in range(69, 85):
    print(f"P{i:03d}: {master_doc.paragraphs[i].text[:70]}")
