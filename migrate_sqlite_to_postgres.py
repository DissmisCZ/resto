"""
RESTO v3 - SQLite to PostgreSQL Migration Script
Migrates all data from local resto_data.db to Supabase PostgreSQL

Prerequisites:
1. Supabase project created with PostgreSQL database
2. Connection string added to .streamlit/secrets.toml
3. PostgreSQL tables created (run database_postgres.init_database() first)

Usage:
    python migrate_sqlite_to_postgres.py
"""

import sqlite3
import psycopg2
import pandas as pd
from pathlib import Path
import sys

# Configuration
SQLITE_DB = "resto_data.db"

def get_postgres_connection():
    """Get PostgreSQL connection from secrets file"""
    import streamlit as st
    try:
        conn_string = st.secrets["database"]["url"]
        return psycopg2.connect(conn_string)
    except Exception as e:
        print(f"❌ Chyba připojení k PostgreSQL: {str(e)}")
        print("\nOvěřte že máte:")
        print("1. .streamlit/secrets.toml s [database] url")
        print("2. Supabase projekt nastaven")
        sys.exit(1)

def get_sqlite_connection():
    """Get SQLite connection"""
    if not Path(SQLITE_DB).exists():
        print(f"❌ SQLite databáze '{SQLITE_DB}' nenalezena!")
        print("\nPokud máte databázi jinde, upravte SQLITE_DB v tomto skriptu.")
        sys.exit(1)

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_table(table_name, sqlite_conn, pg_conn, columns=None, transform_fn=None):
    """
    Migrate a table from SQLite to PostgreSQL

    Args:
        table_name: Name of the table
        sqlite_conn: SQLite connection
        pg_conn: PostgreSQL connection
        columns: List of columns to migrate (None = all)
        transform_fn: Optional function to transform each row
    """
    print(f"  📦 Migrating {table_name}...", end=" ")

    # Read from SQLite
    if columns:
        col_str = ", ".join(columns)
        query = f"SELECT {col_str} FROM {table_name}"
    else:
        query = f"SELECT * FROM {table_name}"

    df = pd.read_sql_query(query, sqlite_conn)

    if df.empty:
        print("⚠️  No data to migrate")
        return 0

    # Get column names
    cols = df.columns.tolist()

    # Prepare PostgreSQL insert
    pg_cursor = pg_conn.cursor()
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)
    insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

    # Insert rows
    inserted = 0
    for _, row in df.iterrows():
        try:
            values = [row[col] for col in cols]

            # Apply transformation if provided
            if transform_fn:
                values = transform_fn(values, cols)

            pg_cursor.execute(insert_query, values)
            inserted += 1
        except Exception as e:
            print(f"\n    ⚠️  Error inserting row: {str(e)}")
            continue

    pg_conn.commit()
    print(f"✅ {inserted} rows migrated")
    return inserted

def reset_sequences(pg_conn):
    """Reset PostgreSQL sequences to match current max IDs"""
    print("\n🔧 Resetting PostgreSQL sequences...")

    tables_with_sequences = [
        'departments',
        'locations',
        'operational_managers',
        'kpi_definitions',
        'kpi_thresholds',
        'manager_kpi_assignments',
        'monthly_kpi_data',
        'monthly_kpi_evaluation',
        'monthly_department_kpi_data',
        'department_monthly_summary'
    ]

    pg_cursor = pg_conn.cursor()

    for table in tables_with_sequences:
        try:
            # Get max ID
            pg_cursor.execute(f"SELECT MAX(id) FROM {table}")
            result = pg_cursor.fetchone()
            max_id = result[0] if result[0] is not None else 0

            # Reset sequence
            sequence_name = f"{table}_id_seq"
            pg_cursor.execute(f"SELECT setval('{sequence_name}', {max_id + 1}, false)")
            print(f"  ✅ {table}: sequence set to {max_id + 1}")
        except Exception as e:
            print(f"  ⚠️  {table}: {str(e)}")

    pg_conn.commit()

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 RESTO v3 - SQLite → PostgreSQL Migration")
    print("=" * 60)
    print()

    # Connect to databases
    print("📡 Connecting to databases...")
    sqlite_conn = get_sqlite_connection()
    pg_conn = get_postgres_connection()
    print("  ✅ Connected to SQLite")
    print("  ✅ Connected to PostgreSQL")
    print()

    # Migration order (respects foreign keys)
    print("📊 Starting migration...\n")

    total_migrated = 0

    # 1. Departments (no dependencies)
    total_migrated += migrate_table("departments", sqlite_conn, pg_conn)

    # 2. Locations (depends on departments)
    total_migrated += migrate_table("locations", sqlite_conn, pg_conn)

    # 3. Operational Managers (depends on departments)
    total_migrated += migrate_table("operational_managers", sqlite_conn, pg_conn)

    # 4. KPI Definitions (no dependencies)
    total_migrated += migrate_table("kpi_definitions", sqlite_conn, pg_conn)

    # 5. KPI Thresholds (depends on kpi_definitions)
    total_migrated += migrate_table("kpi_thresholds", sqlite_conn, pg_conn)

    # 6. Manager KPI Assignments (depends on managers and kpi_definitions)
    total_migrated += migrate_table("manager_kpi_assignments", sqlite_conn, pg_conn)

    # 7. Monthly KPI Data (depends on locations and kpi_definitions)
    total_migrated += migrate_table("monthly_kpi_data", sqlite_conn, pg_conn)

    # 8. Monthly KPI Evaluation (depends on locations and kpi_definitions)
    total_migrated += migrate_table("monthly_kpi_evaluation", sqlite_conn, pg_conn)

    # 9. Monthly Department KPI Data (depends on departments and kpi_definitions)
    total_migrated += migrate_table("monthly_department_kpi_data", sqlite_conn, pg_conn)

    # 10. Department Monthly Summary (depends on departments)
    total_migrated += migrate_table("department_monthly_summary", sqlite_conn, pg_conn)

    # 11. Settings (no dependencies)
    total_migrated += migrate_table("settings", sqlite_conn, pg_conn)

    # Reset sequences
    reset_sequences(pg_conn)

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

    # Summary
    print()
    print("=" * 60)
    print(f"✅ Migration Complete!")
    print(f"📊 Total rows migrated: {total_migrated}")
    print("=" * 60)
    print()
    print("🎉 Vaše data jsou nyní v Supabase PostgreSQL!")
    print("📝 Můžete nyní nasadit aplikaci na Streamlit Cloud.")
    print()
    print("⚠️  DŮLEŽITÉ: Zálohujte si resto_data.db před smazáním!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migrace přerušena uživatelem")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Chyba během migrace: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
