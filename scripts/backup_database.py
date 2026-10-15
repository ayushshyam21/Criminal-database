"""
scripts/backup_database.py
Creates a non-destructive logical SQL backup checkpoint of crime_db before applying upgrades.
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST", "127.0.0.1")
port = int(os.getenv("DB_PORT", 3306))
user = os.getenv("DB_ADMIN_USER", "crimedb_admin")
password = os.getenv("DB_ADMIN_PASSWORD", "")
database = os.getenv("DB_NAME", "crime_db")

conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database,
    charset="utf8mb4"
)

backup_file = "backup_checkpoint_pre_upgrade.sql"

with conn.cursor() as cur:
    cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
    base_tables = [r[0] for r in cur.fetchall()]
    
    cur.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW';")
    views = [r[0] for r in cur.fetchall()]

with open(backup_file, "w", encoding="utf-8") as f:
    f.write("-- =====================================================================\n")
    f.write(f"-- CHECKPOINT BACKUP: {database}\n")
    f.write("-- Created automatically before Citizen Portal & Security Classification upgrade\n")
    f.write("-- =====================================================================\n\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

    with conn.cursor() as cur:
        for t in base_tables:
            f.write(f"-- Structure and Data for table: {t}\n")
            cur.execute(f"SHOW CREATE TABLE `{t}`;")
            create_stmt = cur.fetchone()[1]
            f.write(f"{create_stmt};\n\n")

            cur.execute(f"SELECT * FROM `{t}`;")
            rows = cur.fetchall()
            if rows:
                cur.execute(f"DESCRIBE `{t}`;")
                cols = [c[0] for c in cur.fetchall()]
                cols_str = ", ".join([f"`{c}`" for c in cols])
                for r in rows:
                    vals = []
                    for v in r:
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        else:
                            escaped = pymysql.converters.escape_string(str(v))
                            vals.append(f"'{escaped}'")
                    f.write(f"INSERT INTO `{t}` ({cols_str}) VALUES ({', '.join(vals)});\n")
                f.write("\n")

        for v in views:
            f.write(f"-- View definition: {v}\n")
            cur.execute(f"SHOW CREATE VIEW `{v}`;")
            create_view = cur.fetchone()[1]
            f.write(f"{create_view};\n\n")

    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

conn.close()
print(f"Checkpoint backup successfully saved to {backup_file}")
