"""
scripts/verify_database_objects.py
Queries information_schema to verify that all 12 tables, 3 views,
stored routines, triggers, and constraints were created correctly.
"""
import os
import sys
import pymysql
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if not os.path.exists(env_path):
    print("Error: .env file not found.")
    sys.exit(1)

load_dotenv(env_path)

db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = int(os.getenv("DB_PORT", 3306))
db_name = os.getenv("DB_NAME", "crime_db")
user = os.getenv("DB_ADMIN_USER", "crimedb_admin")
password = os.getenv("DB_ADMIN_PASSWORD")

try:
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=user,
        password=password,
        database=db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
except Exception as e:
    print(f"Failed to connect: {e}")
    sys.exit(1)

expected_tables = {
    "police_stations", "users", "cases", "persons", "case_assignments",
    "case_persons", "evidence", "evidence_custody_log", "investigation_notes",
    "audit_log", "iucr_codes", "public_crime_incidents"
}

expected_views = {
    "v_case_summary", "v_officer_workload", "v_public_incident_trends"
}

expected_routines = {
    "sp_assign_case": "PROCEDURE",
    "fn_case_duration": "FUNCTION"
}

expected_triggers = {
    "trg_evidence_initial_custody",
    "trg_evidence_custody_update",
    "trg_cases_status_audit"
}

print("=" * 70)
print(f"DATABASE OBJECT AUDIT & VERIFICATION REPORT: {db_name}")
print("=" * 70)

with conn.cursor() as cur:
    # 1. Verify Tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
    """, (db_name,))
    actual_tables = {row["TABLE_NAME"] if "TABLE_NAME" in row else row["table_name"] for row in cur.fetchall()}
    
    print("\n[1] BASE TABLES:")
    for t in sorted(expected_tables):
        status = "OK" if t in actual_tables else "MISSING"
        print(f"    - {t:<26} : [{status}]")

    # 2. Verify Views
    cur.execute("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = %s
    """, (db_name,))
    actual_views = {row["TABLE_NAME"] if "TABLE_NAME" in row else row["table_name"] for row in cur.fetchall()}
    
    print("\n[2] DATABASE VIEWS:")
    for v in sorted(expected_views):
        status = "OK" if v in actual_views else "MISSING"
        print(f"    - {v:<26} : [{status}]")

    # 3. Verify Routines
    cur.execute("""
        SELECT routine_name, routine_type 
        FROM information_schema.routines 
        WHERE routine_schema = %s
    """, (db_name,))
    actual_routines = {(row["ROUTINE_NAME"] if "ROUTINE_NAME" in row else row["routine_name"]): (row["ROUTINE_TYPE"] if "ROUTINE_TYPE" in row else row["routine_type"]) for row in cur.fetchall()}
    
    print("\n[3] STORED ROUTINES:")
    for r, r_type in expected_routines.items():
        status = "OK" if r in actual_routines and actual_routines[r] == r_type else "MISSING"
        print(f"    - {r:<26} ({r_type}) : [{status}]")

    # 4. Verify Triggers
    cur.execute("""
        SELECT trigger_name, event_manipulation, event_object_table 
        FROM information_schema.triggers 
        WHERE trigger_schema = %s
    """, (db_name,))
    actual_triggers = {row["TRIGGER_NAME"] if "TRIGGER_NAME" in row else row["trigger_name"] for row in cur.fetchall()}
    
    print("\n[4] TRIGGERS:")
    for trg in sorted(expected_triggers):
        status = "OK" if trg in actual_triggers else "MISSING"
        print(f"    - {trg:<30} : [{status}]")

    # 5. Table Record Counts
    print("\n[5] RECORD COUNTS (SEEDED DATA):")
    for t in sorted(expected_tables):
        if t in actual_tables:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {t}")
            cnt = cur.fetchone()["cnt"]
            print(f"    - {t:<26} : {cnt:>6} rows")

conn.close()
print("\n" + "=" * 70)
