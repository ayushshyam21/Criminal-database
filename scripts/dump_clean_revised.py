import os
import docx

revised_dir = r"D:\Criminal Database\Revised_Chapters"

with open("scripts/clean_revised_contents.txt", "w", encoding="utf-8") as out:
    for fname in sorted(os.listdir(revised_dir)):
        fpath = os.path.join(revised_dir, fname)
        doc = docx.Document(fpath)
        out.write(f"\n{'='*75}\nFILE: {fname}\n{'='*75}\n")
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip()
            # clean UI artifact text if present
            if "... See more" in t:
                t = t.split("... See more")[0].strip()
            if t:
                out.write(f"[{i:02d}] {t}\n\n")

print("Wrote clean revised contents to scripts/clean_revised_contents.txt")
