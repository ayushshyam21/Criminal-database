import docx

doc = docx.Document('Criminal_Case_Management_Final_Report.docx')

targets = [
    17, 18, 19, # Decl
    25, 26,     # Cert
    30, 31, 32, # Abstract
    36, 37, 38, # Ack
    49, 50, 51, 52, 53, 54, 55, # Ch 1
    57, 58, 59, 60, 61, 62, 63, 64, # Ch 2
    66, 68,     # Ch 3
    70,         # Ch 4 intro
    73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, # FR-1 to FR-12
    86, 87, 88, 89, 91, 94, # Ch 5
    96, 98, 103, # Ch 6
    108,        # Ch 7 intro
    126, 127, 128, 129, # Ch 8
    131, 133, 143, # Ch 9
    148, 159, 162, 165, 168, 171, # Ch 10
    174, 176,   # Ch 11
    178, 180,   # Ch 12
    182, 185,   # Ch 13
    187, 188, 189, 190, 191, # Ch 14
    193,        # Ch 15
    195, 196, 197, 198, 199 # Ch 16
]

with open('scripts/target_paragraphs.txt', 'w', encoding='utf-8') as f:
    for idx in targets:
        p = doc.paragraphs[idx]
        f.write(f"=== P{idx:03d} (runs={len(p.runs)}) ===\n")
        for r_i, r in enumerate(p.runs):
            f.write(f"  [Run {r_i}] (bold={r.bold}): {r.text}\n")
        f.write("\n")

print(f"Exported {len(targets)} target paragraphs.")
