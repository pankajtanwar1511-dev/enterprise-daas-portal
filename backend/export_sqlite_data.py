#!/usr/bin/env python3
"""
Export all data from SQLite database to JSON format for PostgreSQL import
"""
import sqlite3
import json
from pathlib import Path

def export_sqlite_to_json():
    """Export SQLite data to JSON files"""
    db_path = Path(__file__).parent / "governance_portal.db"
    output_dir = Path(__file__).parent / "sqlite_export"
    output_dir.mkdir(exist_ok=True)

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version';")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"📊 Found {len(tables)} tables to export")

    total_records = 0

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if rows:
            data = [dict(row) for row in rows]
            output_file = output_dir / f"{table}.json"

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            print(f"✅ {table}: {len(data)} records exported")
            total_records += len(data)
        else:
            print(f"⚠️  {table}: No data")

    conn.close()

    print(f"\n✅ Export complete!")
    print(f"📁 Location: {output_dir}")
    print(f"📊 Total records: {total_records}")

if __name__ == "__main__":
    export_sqlite_to_json()
