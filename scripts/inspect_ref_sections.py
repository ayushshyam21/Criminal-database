import docx

doc = docx.Document(r"D:\VIT study\BACSE202_DBMS_ProjectReport.docx")

print(f"Total sections: {len(doc.sections)}")
for idx, sec in enumerate(doc.sections):
    print(f"--- Section {idx} ---")
    print("start_type:", sec.start_type)
    print("page_width:", sec.page_width.inches, "page_height:", sec.page_height.inches)
    print("different_first_page_header_footer:", sec.different_first_page_header_footer)
    sectPr = sec._sectPr
    # find pgNumType
    pgNumTypes = sectPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pgNumType')
    for pnt in pgNumTypes:
        print("pgNumType:", pnt.attrib)
    # headers and footers
    header_xml = sec.header._element.xml[:150]
    footer_xml = sec.footer._element.xml[:150]
    print("header text:", [p.text for p in sec.header.paragraphs if p.text.strip()])
    print("footer text:", [p.text for p in sec.footer.paragraphs if p.text.strip()])
