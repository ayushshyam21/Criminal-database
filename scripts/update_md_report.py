import os

md_path = "docs/PROJECT_REPORT.md"
with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace Abstract in md
old_abs_fragment = "The Criminal Case Management & Crime Analytics System (CCMS) is an enterprise-grade relational database and analytical platform engineered to overcome the critical operational shortcomings"
new_abs_p1 = "Managing criminal case records in municipal police stations remains challenging when desks rely on paper diaries or unnormalized spreadsheets. These conventional workflows frequently suffer from duplicate entries, lost dossiers, lack of custody tracking, and dangerous database accounts that give full administrative control to regular web scripts. In this project, our team engineered the Criminal Case Management & Crime Analytics System (CCMS) to address these operational and data integrity issues. Built using Python Flask and MySQL Community Server 9.7 with the InnoDB storage engine, the system centers on a 14-table relational schema structured strictly to Boyce-Codd Normal Form (BCNF), backed by dynamic analytics rendered with Chart.js."

new_abs_p2 = "The core database tracks the complete lifecycle of criminal investigations, linking incidents to suspect, victim, and witness profiles while tracking physical evidence through an immutable chain-of-custody ledger automated by database triggers. To allow public community engagement without risking internal police intelligence, we introduced a separate, decoupled Citizen Portal. Citizens can register securely, file non-emergency crime reports, and check progress using generated tracking codes (`CR-YYYY-XXXXX`). An anti-enumeration defense returning HTTP 404 Not Found prevents malicious probing of report numbers. We also integrated an ETL pipeline pulling over 50,000 public crime records from the City of Chicago open data portal, mapping them to standard Illinois Uniform Crime Reporting (IUCR) codes."

new_abs_p3 = "System security combines a dual-account least-privilege database model with Bell-LaPadula Multi-Level Security across four tiers (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) alongside discretionary Need-to-Know assignment checks. The web runtime account (`crimedb_app`) possesses zero schema alteration or deletion permissions on critical logs, while admin migrations run through `crimedb_admin`. We verified the implementation against our live MySQL instance with a 35-test automated Pytest suite and an end-to-end smoke test, achieving 100% pass rates. Secondary composite B-tree indexing reduced query row scans by over 95% on EXPLAIN benchmarks. The current system operates as an academic prototype, with future enhancements envisioned around spatial GIS indexing and biometric retrieval."

new_kw = "**Keywords:** Criminal case management, relational databases, MySQL 9.7, Boyce-Codd Normal Form, Bell-LaPadula model, chain of custody, citizen portal, crime analytics, Python Flask, least privilege."

# Find abstract section and update
if "## ABSTRACT" in content:
    parts = content.split("## ABSTRACT")
    before_abs = parts[0]
    after_abs_full = parts[1]
    
    # split at ACKNOWLEDGEMENT
    abs_and_rest = after_abs_full.split("## ACKNOWLEDGEMENT")
    rest = abs_and_rest[1]
    
    new_abs_section = f"\n\n{new_abs_p1}\n\n{new_abs_p2}\n\n{new_abs_p3}\n\n{new_kw}\n\n---\n\n"
    content = before_abs + "## ABSTRACT" + new_abs_section + "## ACKNOWLEDGEMENT" + rest
    print("Updated Abstract in docs/PROJECT_REPORT.md")

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated docs/PROJECT_REPORT.md")
