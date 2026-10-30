import docx

doc = docx.Document(r"D:\VIT study\BACSE202_DBMS_ProjectReport.docx")

print("=== SECTIONS ===")
for s_idx, s in enumerate(doc.sections):
    print(f"Section {s_idx}:")
    print(f"  start_type: {s.start_type}")
    print(f"  page_width: {s.page_width.inches}, page_height: {s.page_height.inches}")
    print(f"  top_margin: {s.top_margin.inches}, bottom_margin: {s.bottom_margin.inches}")
    print(f"  left_margin: {s.left_margin.inches}, right_margin: {s.right_margin.inches}")
    print(f"  different_first_page_header_footer: {s.different_first_page_header_footer}")
    header_p = [p.text for p in s.header.paragraphs if p.text.strip()]
    footer_p = [p.text for p in s.footer.paragraphs if p.text.strip()]
    print(f"  header: {header_p}")
    print(f"  footer: {footer_p}")

print("\n=== PARAGRAPHS 0 TO 70 WITH RUN STYLES ===")
for i in range(min(70, len(doc.paragraphs))):
    p = doc.paragraphs[i]
    style_name = p.style.name if p.style else "None"
    align = p.alignment
    sp_b = p.paragraph_format.space_before.pt if p.paragraph_format.space_before else None
    sp_a = p.paragraph_format.space_after.pt if p.paragraph_format.space_after else None
    line_sp = p.paragraph_format.line_spacing
    runs_info = []
    for r in p.runs:
        font_name = r.font.name
        font_sz = r.font.size.pt if r.font.size else None
        bold = r.font.bold
        color = r.font.color.rgb if r.font.color else None
        runs_info.append(f"{r.text[:30]!r}(fn={font_name}, sz={font_sz}, b={bold})")
    print(f"P{i:02d} [{style_name}, al={align}, sb={sp_b}, sa={sp_a}, ls={line_sp}]: {p.text[:60]!r}")
    if runs_info:
        print(f"     Runs: {', '.join(runs_info[:3])}")
