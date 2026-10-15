"""
scripts/test_db_connection.py
Verifies local MySQL connectivity and privilege separation for crime_db.

Modes:
  Step C (Admin Connection Check):
    python scripts/test_db_connection.py --admin
    Verifies that crimedb_admin can connect to MySQL and the crime_db database.
    (Executed before schema creation; does not expect tables to exist).

  Step F (App Runtime Privilege Verification):
    python scripts/test_db_connection.py --runtime
    Verifies that crimedb_app has least-privilege runtime access and cannot write
    directly to audit ledgers or tamper with public reference data.
    (Executed after sql/12_runtime_privileges.sql is applied).

  Default (Auto-Detect):
    python scripts/test_db_connection.py
    Tests admin connectivity, detects whether tables exist, and runs runtime
    checks if the schema and runtime grants have been provisioned.
"""
import os
import sys
import argparse
import pymysql
from dotenv import load_dotenv

# Load .env file from project root
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if not os.path.exists(env_path):
    print("=" * 70)
    print("ACTION REQUIRED: '.env' file not found.")
    print("Please copy '.env.example' to '.env' and provide your database credentials.")
    print("=" * 70)
    sys.exit(1)

load_dotenv(env_path)

db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = int(os.getenv("DB_PORT", 3306))
db_name = os.getenv("DB_NAME", "crime_db")

admin_user = os.getenv("DB_ADMIN_USER", "crimedb_admin")
admin_pass = os.getenv("DB_ADMIN_PASSWORD")

app_user = os.getenv("DB_APP_USER", "crimedb_app")
app_pass = os.getenv("DB_APP_PASSWORD")


def test_admin_connection():
    """
    Step C: Tests administrative connectivity for crimedb_admin.
    Does NOT require tables to exist yet.
    """
    print("\n" + "=" * 70)
    print(f"[STEP C] TESTING MIGRATION / ADMIN ACCOUNT ('{admin_user}')")
    print(f"Target: {db_host}:{db_port} | Database: {db_name}")
    print("=" * 70)

    if not admin_pass or admin_pass == "YOUR_CHOSEN_ADMIN_PASSWORD_HERE":
        print(f"  [FAIL] DB_ADMIN_PASSWORD is empty or set to placeholder in .env.")
        return False

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=admin_user,
            password=admin_pass,
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() AS ver, CURRENT_USER() AS cur_usr, DATABASE() AS cur_db;")
            res = cur.fetchone()
            print("  [OK] Admin Connection Established Successfully!")
            print(f"       - MySQL Server Version : {res['ver']}")
            print(f"       - Authenticated As     : {res['cur_usr']}")
            print(f"       - Target Database      : {res['cur_db']}")

            # Check if tables exist yet
            cur.execute("SELECT COUNT(*) AS tbl_cnt FROM information_schema.tables WHERE table_schema = %s;", (db_name,))
            tbl_cnt = cur.fetchone()["tbl_cnt"]
            print(f"       - Existing Tables In DB: {tbl_cnt}")

        conn.close()
        return True
    except pymysql.MySQLError as e:
        print(f"  [FAIL] Admin Connection Failed: {e}")
        return False


def test_runtime_privileges():
    """
    Step F: Tests least-privilege runtime security for crimedb_app.
    Executed AFTER sql/12_runtime_privileges.sql has been run.
    """
    print("\n" + "=" * 70)
    print(f"[STEP F] TESTING RUNTIME LEAST-PRIVILEGE SECURITY ('{app_user}')")
    print(f"Target: {db_host}:{db_port} | Database: {db_name}")
    print("=" * 70)

    if not app_pass or app_pass == "YOUR_CHOSEN_APP_PASSWORD_HERE":
        print(f"  [FAIL] DB_APP_PASSWORD is empty or set to placeholder in .env.")
        return False

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=app_user,
            password=app_pass,
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        print(f"  [FAIL] Runtime user connection failed: {e}")
        print("  HINT: Did you execute 'sql/12_runtime_privileges.sql' as root in Step E?")
        return False

    all_passed = True
    with conn.cursor() as cur:
        # 1. Connection check
        cur.execute("SELECT CURRENT_USER() AS cur_usr, DATABASE() AS cur_db;")
        res = cur.fetchone()
        print(f"  [OK] Connected as runtime user: {res['cur_usr']}")

        # 2. Permitted operational query (SELECT on cases)
        try:
            cur.execute("SELECT COUNT(*) AS cnt FROM cases;")
            cnt = cur.fetchone()["cnt"]
            print(f"  [OK] Permitted DML (SELECT on cases): Verified ({cnt} rows)")
        except pymysql.MySQLError as e:
            print(f"  [FAIL] Expected SELECT on cases failed: {e}")
            all_passed = False

        # 3. Prohibited DDL (DROP TABLE must be denied)
        try:
            cur.execute("DROP TABLE IF EXISTS _unauthorized_test_table;")
            print("  [WARN] Least Privilege Violation: crimedb_app has DROP TABLE privilege!")
            all_passed = False
        except pymysql.MySQLError as e:
            if e.args[0] in (1142, 1044, 1227):
                print(f"  [OK] Least Privilege Confirmed: DROP TABLE correctly denied (Error {e.args[0]})")
            else:
                print(f"  [WARN] Unexpected error on DROP TABLE: {e}")

        # 4. Prohibited direct INSERT on immutable audit_log
        try:
            cur.execute("INSERT INTO audit_log (table_name, record_id, operation_type) VALUES ('test', 1, 'INSERT');")
            print("  [WARN] Security Violation: crimedb_app can directly INSERT into audit_log!")
            all_passed = False
        except pymysql.MySQLError as e:
            if e.args[0] in (1142, 1044, 1227):
                print(f"  [OK] Audit Immutability Confirmed: Direct INSERT to audit_log denied (Error {e.args[0]})")
            else:
                print(f"  [WARN] Unexpected error on audit_log insert: {e}")

        # 5. Prohibited direct INSERT on immutable evidence_custody_log
        try:
            cur.execute("INSERT INTO evidence_custody_log (evidence_id, to_location, handled_by) VALUES (1, 'vault', 1);")
            print("  [WARN] Security Violation: crimedb_app can directly INSERT into evidence_custody_log!")
            all_passed = False
        except pymysql.MySQLError as e:
            if e.args[0] in (1142, 1044, 1227):
                print(f"  [OK] Custody Immutability Confirmed: Direct INSERT to evidence_custody_log denied (Error {e.args[0]})")
            else:
                print(f"  [WARN] Unexpected error on custody log insert: {e}")

        # 6. Prohibited UPDATE on read-only public_crime_incidents
        try:
            cur.execute("UPDATE public_crime_incidents SET primary_type = 'TAMPERED' WHERE incident_id = 1;")
            print("  [WARN] Security Violation: crimedb_app can UPDATE public_crime_incidents!")
            all_passed = False
        except pymysql.MySQLError as e:
            if e.args[0] in (1142, 1044, 1227):
                print(f"  [OK] Public Data Integrity Confirmed: UPDATE on public_crime_incidents denied (Error {e.args[0]})")
            else:
                print(f"  [WARN] Unexpected error on public_crime_incidents update: {e}")

        # 7. Prohibited UPDATE on read-only iucr_codes reference table
        try:
            cur.execute("UPDATE iucr_codes SET description = 'TAMPERED' WHERE iucr_code = '0110';")
            print("  [WARN] Security Violation: crimedb_app can UPDATE iucr_codes!")
            all_passed = False
        except pymysql.MySQLError as e:
            if e.args[0] in (1142, 1044, 1227):
                print(f"  [OK] Reference Lookup Integrity Confirmed: UPDATE on iucr_codes denied (Error {e.args[0]})")
            else:
                print(f"  [WARN] Unexpected error on iucr_codes update: {e}")

        # 8. Permitted VIEW access
        try:
            cur.execute("SELECT COUNT(*) AS cnt FROM v_case_summary;")
            cnt = cur.fetchone()["cnt"]
            print(f"  [OK] View Access Confirmed: SELECT on v_case_summary ({cnt} rows)")
        except pymysql.MySQLError as e:
            print(f"  [FAIL] Expected SELECT on v_case_summary failed: {e}")
            all_passed = False

        # 9. Permitted Stored Function execution
        try:
            cur.execute("SELECT fn_case_duration(1) AS duration;")
            dur = cur.fetchone()["duration"]
            print(f"  [OK] Stored Routine Confirmed: fn_case_duration(1) returned {dur} days")
        except pymysql.MySQLError as e:
            print(f"  [FAIL] Expected EXECUTE on fn_case_duration failed: {e}")
            all_passed = False

    conn.close()
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Verify MySQL connectivity and privilege separation.")
    parser.add_argument("--admin", "--step-c", action="store_true", help="Run only Step C: test crimedb_admin connection")
    parser.add_argument("--runtime", "--step-f", action="store_true", help="Run only Step F: test crimedb_app runtime least-privilege permissions")
    args = parser.parse_args()

    if args.admin:
        success = test_admin_connection()
        sys.exit(0 if success else 1)

    if args.runtime:
        success = test_runtime_privileges()
        sys.exit(0 if success else 1)

    # Default mode: smart auto-detect
    admin_ok = test_admin_connection()
    if not admin_ok:
        sys.exit(1)

    # Check if tables exist before deciding to run runtime test
    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=admin_user,
            password=admin_pass,
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM information_schema.tables WHERE table_schema = %s AND table_name = 'cases';", (db_name,))
            cases_exist = cur.fetchone()["cnt"] > 0
        conn.close()
    except Exception:
        cases_exist = False

    if not cases_exist:
        print("\n" + "=" * 70)
        print("[STATUS] Step C Admin Connection check PASSED.")
        print("Schema tables have not been created yet.")
        print("NEXT STEPS:")
        print("  1. Run Step D: python scripts/execute_sql_scripts.py")
        print("  2. Run Step E: execute sql/12_runtime_privileges.sql as root")
        print("  3. Run Step F: python scripts/test_db_connection.py --runtime")
        print("=" * 70)
        sys.exit(0)

    # If tables exist, run the Step F checks
    runtime_ok = test_runtime_privileges()
    if runtime_ok:
        print("\n" + "=" * 70)
        print("ALL CONNECTION AND LEAST-PRIVILEGE SECURITY CHECKS PASSED!")
        print("=" * 70)
    sys.exit(0 if runtime_ok else 1)


if __name__ == "__main__":
    main()
