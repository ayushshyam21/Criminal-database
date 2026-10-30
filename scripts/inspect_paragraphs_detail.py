import docx

doc = docx.Document('Criminal_Case_Management_Final_Report.docx')
for i, p in enumerate(doc.paragraphs):
    drawings = p._p.xpath('.//w:drawing') or p._p.xpath('.//w:pict')
    breaks = p._p.xpath('.//w:br[@w:type="page"]')
    sect = p._p.xpath('.//w:sectPr')
    if drawings or breaks or sect or len(p.text.strip()) == 0:
        print(f'P{i:03d}: text={p.text[:30]!r}, draw={len(drawings)}, breaks={len(breaks)}, sect={len(sect)}')
