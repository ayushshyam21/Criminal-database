import docx

doc = docx.Document('Criminal_Case_Management_Final_Report.docx')
print('Total Tables:', len(doc.tables))
for i, t in enumerate(doc.tables):
    rows = len(t.rows)
    cols = len(t.columns)
    first_cell = t.cell(0, 0).text.strip().replace('\n', ' ')[:40]
    print(f'T{i:02d}: {rows}x{cols} -> first cell: {first_cell!r}')
