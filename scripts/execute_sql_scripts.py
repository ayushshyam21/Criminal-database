"""
scripts/execute_sql_scripts.py
Executes the crime_db database foundation scripts in exact dependency order
using the crimedb_admin account configured in .env.

Supports resumption via --from flag to safely resume after partial migrations:
  python scripts/execute_sql_scripts.py --from 04_stored_routines.sql
"""
import os
import sys
import re
import argparse
import pymysql
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if not os.path.exists(env_path):
    print("Error: .env file not found. Copy .env.example to .env and configure credentials.")
    sys.exit(1)

load_dotenv(env_path)

db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = int(os.getenv("DB_PORT", 3306))
db_name = os.getenv("DB_NAME", "crime_db")
admin_user = os.getenv("DB_ADMIN_USER", "crimedb_admin")
admin_pass = os.getenv("DB_ADMIN_PASSWORD")

if not admin_pass or admin_pass == "YOUR_CHOSEN_ADMIN_PASSWORD_HERE":
    print("Error: Valid DB_ADMIN_PASSWORD not configured in .env.")
    sys.exit(1)

scripts_in_order = [
    "01_schema.sql",
    "02_lookup_data.sql",
    "03_views.sql",
    "04_stored_routines.sql",
    "05_triggers.sql",
    "06_indexes.sql",
    "07_seed_fictional.sql"
]

sql_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sql"))

# Command-line argument parsing for resume capability
parser = argparse.ArgumentParser(description="Execute crime_db database foundation scripts in order.")
parser.add_argument(
    "--from",
    dest="start_from",
    default=None,
    help="Resume execution from a specific migration script (e.g. --from 04_stored_routines.sql)"
)
parser.add_argument(
    "--only",
    dest="only_script",
    default=None,
    help="Execute only a single specified script (e.g. --only 04_stored_routines.sql)"
)
args = parser.parse_args()

if args.start_from:
    target_basename = os.path.basename(args.start_from)
    if target_basename not in scripts_in_order:
        print(f"Error: Specified script '{args.start_from}' not found in migration sequence.")
        print(f"Available migration scripts: {', '.join(scripts_in_order)}")
        sys.exit(1)
    start_idx = scripts_in_order.index(target_basename)
    skipped_scripts = scripts_in_order[:start_idx]
    scripts_in_order = scripts_in_order[start_idx:]
    print("=" * 70)
    print(f"[RESUME MODE ENABLED]")
    print(f"Skipping completed scripts : {', '.join(skipped_scripts)}")
    print(f"Resuming execution from    : {target_basename}")
    print(f"Pending scripts to execute : {', '.join(scripts_in_order)}")
    print("=" * 70)
elif args.only_script:
    target_basename = os.path.basename(args.only_script)
    if target_basename not in scripts_in_order:
        print(f"Error: Specified script '{args.only_script}' not recognized.")
        print(f"Available migration scripts: {', '.join(scripts_in_order)}")
        sys.exit(1)
    scripts_in_order = [target_basename]
    print("=" * 70)
    print(f"[TARGETED SINGLE SCRIPT MODE]: Executing '{target_basename}' only")
    print("=" * 70)


def parse_sql_statements(content):
    """
    Parses SQL content handling DELIMITER $$ statements for stored routines and triggers.
    """
    statements = []
    delimiter = ";"
    current = []
    
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        
        # Check for DELIMITER change
        if stripped.upper().startswith("DELIMITER"):
            parts = stripped.split()
            if len(parts) >= 2:
                delimiter = parts[1]
            continue
            
        if delimiter == ";":
            if stripped.endswith(";"):
                current.append(line[:line.rfind(";")])
                stmt = "\n".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(line)
        else:
            # Multi-character delimiter (e.g. $$)
            if delimiter in line:
                idx = line.find(delimiter)
                current.append(line[:idx])
                stmt = "\n".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(line)
                
    remaining = "\n".join(current).strip()
    if remaining:
        statements.append(remaining)
        
    return statements


print("=" * 70)
print(f"DATABASE INITIALIZATION & MIGRATION RUNNER")
print(f"Connecting to {db_host}:{db_port} as '{admin_user}'...")
print("=" * 70)

try:
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=admin_user,
        password=admin_pass,
        database=db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)

with conn.cursor() as cursor:
    for script_name in scripts_in_order:
        script_path = os.path.join(sql_dir, script_name)
        if not os.path.exists(script_path):
            print(f"[SKIP] File not found: {script_name}")
            continue
            
        print(f"\nExecuting: {script_name}...")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        statements = parse_sql_statements(content)
        executed_count = 0
        for stmt in statements:
            clean_stmt = stmt.strip()
            # Skip pure comments or empty statements
            if not clean_stmt or clean_stmt.startswith("--") or clean_stmt.startswith("/*"):
                # Check if it contains actual code beyond leading comment
                lines = [l for l in clean_stmt.splitlines() if not l.strip().startswith("--") and not l.strip().startswith("/*")]
                if not "".join(lines).strip():
                    continue
            try:
                cursor.execute(clean_stmt)
                executed_count += 1
            except Exception as err:
                print("\n" + "!" * 70)
                print(f"MIGRATION HALTED ON ERROR IN: {script_name}")
                print(f"Database Error: {err}")
                print(f"Failed Statement:\n{clean_stmt}")
                print("!" * 70)
                conn.close()
                sys.exit(1)
                
        print(f"  [DONE] {executed_count} statements executed successfully.")

conn.close()
print("\n" + "=" * 70)
print("[STEP D COMPLETE] ALL FOUNDATION OBJECTS & SEED DATA CREATED")
print("NEXT STEP (STEP E):")
print("  Run 'sql/12_runtime_privileges.sql' as root / database administrator")
print("  to grant least-privilege permissions to 'crimedb_app'.")
print("=" * 70)
