import os
import docx

revised_dir = r"D:\Criminal Database\Revised_Chapters"
with open("scripts/revised_inspection.txt", "w", encoding="utf-8") as out:
    for fname in sorted(os.listdir(revised_dir)):
        fpath = os.path.join(revised_dir, fname)
        doc = docx.Document(fpath)
        out.write(f"\n{'='*70}\nFILE: {fname} (Paragraphs: {len(doc.paragraphs)}, Tables: {len(doc.tables)})\n{'='*70}\n")
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip().replace("\n", " ")
            if t:
                out.write(f"P{i:02d}: {t}\n")
        for t_idx, t in enumerate(doc.tables):
            out.write(f"\n--- TABLE {t_idx} ({len(t.rows)}x{len(t.columns)}) ---\n")
            for r_idx, r in enumerate(t.rows):
                row_str = " | ".join(c.text.strip().replace("\n", " ") for c in r.cells)
                out.write(f"  Row {r_idx}: {row_str}\n")

print("Dumped revised inspection to scripts/revised_inspection.txt")
