"""
scripts/import_chicago_data.py
CLI utility to ingest real public crime incident statistics from the City of Chicago Open Data API.

Usage:
  python scripts/import_chicago_data.py --limit 100
  python scripts/import_chicago_data.py --limit 500
  python scripts/import_chicago_data.py --limit 5000
"""
import sys
import os
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.chicago_importer import import_chicago_crimes


def main():
    parser = argparse.ArgumentParser(description="Ingest City of Chicago Open Crime Data.")
    parser.add_argument("--limit", type=int, default=500, help="Number of records to fetch (default: 500, max: 5000)")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0)")
    args = parser.parse_args()

    print("=" * 70)
    print("CITY OF CHICAGO OPEN CRIME DATA INGESTION UTILITY")
    print(f"Target Endpoint : https://data.cityofchicago.org/resource/ijzp-q8t2.json")
    print(f"Batch Limit     : {args.limit} records (Offset: {args.offset})")
    print("=" * 70)

    result = import_chicago_crimes(limit=args.limit, offset=args.offset)

    if result.get("success"):
        print(f"\n[SUCCESS] {result.get('message')}")
        print(f"  - Fetched from API   : {result.get('records_fetched')} records")
        print(f"  - Inserted to DB     : {result.get('records_inserted')} records")
        print(f"  - Skipped Duplicates : {result.get('duplicates_skipped')} records")
        print(f"  - Format Warnings    : {result.get('errors_encountered')} records")
    else:
        print(f"\n[FAILURE] Ingestion aborted.")
        print(f"  - Error Detail       : {result.get('error')}")
        sys.exit(1)

    print("=" * 70)


if __name__ == "__main__":
    main()
