"""
scripts/run_upgrade_migrations.py
Executes scripts 13_classification_clearance.sql and 14_citizen_portal.sql
using the crimedb_admin credentials configured in .env.
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
admin_user = os.getenv("DB_ADMIN_USER", "crimedb_admin")
admin_pass = os.getenv("DB_ADMIN_PASSWORD")

sql_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sql"))
target_scripts = [
    "13_classification_clearance.sql",
    "14_citizen_portal.sql"
]


def parse_sql_statements(content):
    statements = []
    delimiter = ";"
    current = []
    
    for line in content.splitlines():
        stripped = line.strip()
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


def run_migrations():
    print(f"Connecting to {db_host}:{db_port}/{db_name} as '{admin_user}'...")
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=admin_user,
        password=admin_pass,
        database=db_name,
        charset='utf8mb4',
        autocommit=False
    )
    
    try:
        with conn.cursor() as cursor:
            for script_name in target_scripts:
                script_path = os.path.join(sql_dir, script_name)
                print(f"\n--- Executing {script_name} ---")
                if not os.path.exists(script_path):
                    print(f"Error: {script_path} not found.")
                    return False
                
                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                statements = parse_sql_statements(content)
                print(f"Found {len(statements)} statements to execute.")
                
                for idx, stmt in enumerate(statements, 1):
                    # Skip empty comments
                    clean_stmt = "\n".join([l for l in stmt.splitlines() if not l.strip().startswith("--")]).strip()
                    if not clean_stmt:
                        continue
                    try:
                        cursor.execute(clean_stmt)
                        conn.commit()
                    except pymysql.err.OperationalError as e:
                        # 1060: Duplicate column name, 1061: Duplicate key name
                        if e.args[0] in (1060, 1061):
                            print(f"Skipping already applied change: {e.args[1]}")
                            conn.rollback()
                        else:
                            print(f"Statement {idx} failed:\n{clean_stmt[:120]}...\nError: {e}")
                            conn.rollback()
                            raise
                    except Exception as e:
                        print(f"Statement {idx} failed:\n{clean_stmt[:120]}...\nError: {e}")
                        conn.rollback()
                        raise
                print(f"Successfully executed {script_name}")
                
        print("\nAll target migrations executed successfully.")
        return True
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
