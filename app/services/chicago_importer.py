"""
app/services/chicago_importer.py
Robust, repeatable importer for the City of Chicago Open Crime Dataset (ijzp-q8t2).
Uses the administrative/migration credentials (crimedb_admin) from .env to perform
bulk insertion into public_crime_incidents, preserving the strict read-only runtime
boundary of crimedb_app.
"""
import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
import pymysql
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(basedir, ".env"))


def get_admin_connection():
    """Returns a connection authenticated as crimedb_admin for bulk dataset ingestion."""
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    db_name = os.getenv("DB_NAME", "crime_db")
    user = os.getenv("DB_ADMIN_USER", "crimedb_admin")
    password = os.getenv("DB_ADMIN_PASSWORD")
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def import_chicago_crimes(limit=500, offset=0):
    """
    Imports public crime incidents from the City of Chicago Socrata Open Data API.
    
    Parameters:
        limit (int): Number of incidents to fetch (default 500, clamped to 1-5000).
        offset (int): Offset for pagination.
        
    Returns:
        dict: Import execution statistics and status.
    """
    limit = max(1, min(limit, 5000))
    endpoint = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
    
    params = {
        "$limit": limit,
        "$offset": offset,
        "$order": "date DESC"
    }
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    
    headers = {
        "User-Agent": "CriminalCaseManagement-CrimeAnalytics/1.0",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status != 200:
                return {
                    "success": False,
                    "error": f"API returned HTTP status {response.status}",
                    "records_fetched": 0,
                    "records_inserted": 0
                }
            raw_data = response.read().decode("utf-8")
            records = json.loads(raw_data)
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Network or endpoint error: {e.reason}",
            "records_fetched": 0,
            "records_inserted": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse API response: {str(e)}",
            "records_fetched": 0,
            "records_inserted": 0
        }

    if not isinstance(records, list) or not records:
        return {
            "success": True,
            "message": "No new records returned by API.",
            "records_fetched": 0,
            "records_inserted": 0,
            "duplicates_skipped": 0
        }

    try:
        conn = get_admin_connection()
    except Exception as e:
        return {
            "success": False,
            "error": f"Administrative connection failed: {str(e)}",
            "records_fetched": len(records),
            "records_inserted": 0
        }

    inserted_count = 0
    duplicate_count = 0
    error_count = 0

    with conn.cursor() as cur:
        # Cache canonical IUCR codes
        cur.execute("SELECT iucr_code FROM iucr_codes;")
        valid_iucr_codes = set(row["iucr_code"] for row in cur.fetchall())

        # Collect existing source_ids
        source_ids = [int(r["id"]) for r in records if r.get("id") and r["id"].isdigit()]
        existing_source_ids = set()
        if source_ids:
            format_strings = ",".join(["%s"] * len(source_ids))
            cur.execute(f"SELECT source_id FROM public_crime_incidents WHERE source_id IN ({format_strings});", tuple(source_ids))
            existing_source_ids = set(row["source_id"] for row in cur.fetchall())

        insert_sql = """
            INSERT INTO public_crime_incidents (
                source_id, case_number, incident_date, block,
                source_iucr_code, source_primary_type, source_description,
                canonical_iucr_code, location_description, arrest_made,
                domestic, beat, district, ward, community_area,
                fbi_code, latitude, longitude, incident_year,
                updated_on, imported_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                NOW(), NOW()
            ) ON DUPLICATE KEY UPDATE updated_on = NOW();
        """

        batch_params = []
        for r in records:
            try:
                raw_id = r.get("id")
                if not raw_id or not raw_id.isdigit():
                    continue
                source_id = int(raw_id)
                if source_id in existing_source_ids:
                    duplicate_count += 1
                    continue

                raw_date = r.get("date")
                if raw_date:
                    incident_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00").split(".")[0])
                else:
                    incident_date = datetime.utcnow()

                raw_iucr = r.get("iucr", "").strip()
                formatted_iucr = raw_iucr.zfill(4) if (raw_iucr and len(raw_iucr) < 4) else raw_iucr
                canonical_code = formatted_iucr if formatted_iucr in valid_iucr_codes else None

                lat = float(r["latitude"]) if r.get("latitude") else None
                lon = float(r["longitude"]) if r.get("longitude") else None
                year = int(r.get("year", incident_date.year))

                params_tuple = (
                    source_id,
                    r.get("case_number"),
                    incident_date.strftime("%Y-%m-%d %H:%M:%S"),
                    r.get("block"),
                    raw_iucr,
                    r.get("primary_type", "OTHER OFFENSE"),
                    r.get("description"),
                    canonical_code,
                    r.get("location_description"),
                    1 if (r.get("arrest") == "true" or r.get("arrest") is True) else 0,
                    1 if (r.get("domestic") == "true" or r.get("domestic") is True) else 0,
                    r.get("beat"),
                    r.get("district"),
                    int(r["ward"]) if r.get("ward") and str(r["ward"]).isdigit() else None,
                    r.get("community_area"),
                    r.get("fbi_code"),
                    lat,
                    lon,
                    year
                )
                batch_params.append(params_tuple)
                existing_source_ids.add(source_id)
            except Exception:
                error_count += 1

        if batch_params:
            try:
                cur.executemany(insert_sql, batch_params)
                inserted_count = len(batch_params)
            except Exception as e:
                conn.close()
                return {
                    "success": False,
                    "error": f"Database insertion failed: {str(e)}",
                    "records_fetched": len(records),
                    "records_inserted": 0
                }

    conn.close()
    return {
        "success": True,
        "message": f"Successfully ingested {inserted_count} Chicago crime incidents.",
        "records_fetched": len(records),
        "records_inserted": inserted_count,
        "duplicates_skipped": duplicate_count,
        "errors_encountered": error_count
    }
