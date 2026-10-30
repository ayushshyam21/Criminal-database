import docx
import re

doc = docx.Document(r"D:\VIT study\BACSE202_DBMS_ProjectReport.docx")
for idx in [5, 16]:
    p = doc.paragraphs[idx]
    xml = p._element.xml
    matches = re.findall(r'r:embed="([^"]+)"', xml)
    for rid in matches:
        target = doc.part.rels[rid].target_ref
        print(f"P{idx} rid={rid} target={target}")
