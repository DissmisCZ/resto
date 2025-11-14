"""
RESTO - Database Module v3 - PostgreSQL Version
PostgreSQL database for KPI data management - CLOUD READY
Monthly KPI tracking with cloud persistence via Supabase:
- Departments (Bouda, Bistro as departments)
- Locations assigned to departments
- Operational Managers assigned to departments (multiple per department)
- Monthly KPI Data
"""

import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import io
import streamlit as st
from functools import lru_cache
import numpy as np

def safe_convert_id(value):
    """Safely convert any ID value to Python int (handles numpy, pandas types)"""
    if value is None:
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return int(value)
    if isinstance(value, bytes):
        return int.from_bytes(value, byteorder='little')
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Cannot convert {type(value).__name__} to int: {value}")

def get_connection():
    """Get PostgreSQL database connection from Streamlit secrets"""
    try:
        # Get connection string from Streamlit secrets
        conn_string = st.secrets["database"]["url"]
        conn = psycopg2.connect(conn_string, cursor_factory=psycopg2.extras.RealDictCursor)
        # Use RealDictCursor for dict-like row access (similar to sqlite3.Row)
        return conn
    except Exception as e:
        st.error(f"Chyba připojení k databázi: {str(e)}")
        raise

def init_database():
    """Initialize database with CORRECTED schema - PostgreSQL version"""
    conn = get_connection()
    cursor = conn.cursor()

    # === DEPARTMENTS (Oddělení) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            nazev TEXT NOT NULL UNIQUE,
            popis TEXT,
            vedouci TEXT,
            ma_vlastni_kpi BOOLEAN DEFAULT FALSE,
            aktivni BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === LOCATIONS (Lokality) - přiřazené oddělením ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            nazev TEXT NOT NULL UNIQUE,
            department_id INTEGER NOT NULL,
            popis TEXT,
            aktivni BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # === OPERATIONAL MANAGERS (Provozní) - přiřazení oddělení! ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operational_managers (
            id SERIAL PRIMARY KEY,
            jmeno TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            email TEXT,
            aktivni BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # === KPI DEFINITIONS (Definice KPI - 10 metrů) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_definitions (
            id SERIAL PRIMARY KEY,
            nazev TEXT NOT NULL UNIQUE,
            popis TEXT,
            jednotka TEXT,
            typ_vypoctu TEXT,
            aktivni BOOLEAN DEFAULT TRUE,
            poradi INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === KPI THRESHOLDS (Prahy pro bonus) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_thresholds (
            id SERIAL PRIMARY KEY,
            kpi_id INTEGER NOT NULL,
            min_hodnota REAL,
            max_hodnota REAL,
            operator TEXT NOT NULL,
            bonus_procento REAL NOT NULL,
            popis TEXT,
            poradi INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id)
        )
    """)

    # === MANAGER KPI ASSIGNMENTS (Přiřazení KPI k provozním) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager_kpi_assignments (
            id SERIAL PRIMARY KEY,
            manager_id INTEGER NOT NULL,
            kpi_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(manager_id, kpi_id),
            FOREIGN KEY (manager_id) REFERENCES operational_managers(id) ON DELETE CASCADE,
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
        )
    """)

    # === MONTHLY KPI DATA (Měsíční vstupní data) - KLÍČOVÁ TABULKA ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_kpi_data (
            id SERIAL PRIMARY KEY,
            mesic TEXT NOT NULL,
            location_id INTEGER NOT NULL,
            kpi_id INTEGER NOT NULL,
            hodnota REAL NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            poznamka TEXT,
            zdroj TEXT DEFAULT 'MANUAL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mesic, location_id, kpi_id),
            FOREIGN KEY (location_id) REFERENCES locations(id),
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id)
        )
    """)

    # === MONTHLY KPI EVALUATION (Vyhodnocení splnění) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_kpi_evaluation (
            id SERIAL PRIMARY KEY,
            mesic TEXT NOT NULL,
            location_id INTEGER NOT NULL,
            kpi_id INTEGER NOT NULL,
            hodnota REAL NOT NULL,
            splneno INTEGER DEFAULT 0,
            bonus_procento REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mesic, location_id, kpi_id),
            FOREIGN KEY (location_id) REFERENCES locations(id),
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id)
        )
    """)

    # === MONTHLY DEPARTMENT KPI DATA (Měsíční KPI data pro oddělení s vlastními KPI) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_department_kpi_data (
            id SERIAL PRIMARY KEY,
            mesic TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            kpi_id INTEGER NOT NULL,
            hodnota REAL NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            poznamka TEXT,
            zdroj TEXT DEFAULT 'MANUAL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mesic, department_id, kpi_id),
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id)
        )
    """)

    # === DEPARTMENT MONTHLY SUMMARY (Shrnutí oddělení za měsíc) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department_monthly_summary (
            id SERIAL PRIMARY KEY,
            mesic TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            celkovy_bonus REAL DEFAULT 0,
            aktivnich_kpi INTEGER DEFAULT 0,
            splnenych_kpi INTEGER DEFAULT 0,
            poznamka TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mesic, department_id),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # === SETTINGS ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            klic TEXT PRIMARY KEY,
            hodnota TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def insert_default_data():
    """Insert default data - CORRECTED STRUCTURE"""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if data already exists - skip if yes
    cursor.execute("SELECT COUNT(*) as count FROM departments")
    result = cursor.fetchone()
    if result['count'] > 0:
        cursor.close()
        conn.close()
        return  # Data already exists, skip

    # === INSERT DEPARTMENTS (OPRAVA: Bouda a Bistro jsou oddělení) ===
    departments = [
        ("Bouda", "Oddělení Bouda - Mercury & OC4Dvory", "Matěj, Thomas"),
        ("Bistro", "Oddělení Bistro", "Michael"),
    ]
    for nazev, popis, vedouci in departments:
        cursor.execute("""
            INSERT INTO departments (nazev, popis, vedouci)
            VALUES (%s, %s, %s)
            ON CONFLICT (nazev) DO NOTHING
        """, (nazev, popis, vedouci))

    conn.commit()

    # === INSERT LOCATIONS (Bound to departments) ===
    cursor.execute("SELECT id, nazev FROM departments ORDER BY id")
    depts = cursor.fetchall()
    dept_map = {row['nazev']: row['id'] for row in depts}  # nazev -> id

    locations = [
        ("Mercury", "Bouda"),           # Mercury patří do oddělení Bouda
        ("OC4Dvory", "Bouda"),          # OC4Dvory patří do oddělení Bouda
        ("Bistro", "Bistro"),           # Bistro patří do oddělení Bistro
    ]

    for nazev, dept_name in locations:
        if dept_name in dept_map:
            cursor.execute("""
                INSERT INTO locations (nazev, department_id, popis)
                VALUES (%s, %s, %s)
                ON CONFLICT (nazev) DO NOTHING
            """, (nazev, dept_map[dept_name], f"Lokalita {nazev}"))

    conn.commit()

    # === INSERT OPERATIONAL MANAGERS (OPRAVA: přiřazeni oddělení!) ===
    cursor.execute("SELECT id, nazev FROM departments ORDER BY id")
    depts = cursor.fetchall()
    dept_map = {row['nazev']: row['id'] for row in depts}

    operational_mgrs = [
        ("Matěj", "Bouda"),             # Matěj provozní v Boudě
        ("Thomas", "Bouda"),            # Thomas provozní v Boudě
        ("Michael", "Bistro"),          # Michael provozní v Bistrům
    ]

    for jmeno, dept_name in operational_mgrs:
        if dept_name in dept_map:
            cursor.execute("""
                INSERT INTO operational_managers (jmeno, department_id)
                VALUES (%s, %s)
            """, (jmeno, dept_map[dept_name]))

    conn.commit()

    # === INSERT KPI DEFINITIONS ===
    kpis = [
        ("Audit", "Provozní audit (%)", "%", "aggregated", 1),
        ("Hodnocení rozvozy", "Hodnocení od zákazníků - rozvozy (★)", "★", "average", 2),
        ("Hodnocení Google", "Hodnocení Google recenze (★)", "★", "average", 3),
        ("Čas přípravy", "Průměrný čas přípravy objednávky (min)", "min", "average", 4),
        ("Chybovost objednávek", "Procento chybných objednávek (%)", "%", "calculated", 5),
        ("Mystery shop", "Mystery shopping hodnocení (%)", "%", "aggregated", 6),
        ("Obratohodina", "Obrat na odpracovanou hodinu (Kč/h)", "Kč/h", "calculated", 7),
        ("Hodnocení zaměstnanců", "Interní hodnocení týmu (0-10)", "0-10", "average", 8),
        ("Zjištěná ztráta", "Zjištěná ztráta zboží (%)", "%", "aggregated", 9),
        ("Nezjištěná ztráta", "Nezjištěná ztráta zboží (%)", "%", "aggregated", 10),
    ]

    for nazev, popis, jednotka, typ_vypoctu, poradi in kpis:
        cursor.execute("""
            INSERT INTO kpi_definitions (nazev, popis, jednotka, typ_vypoctu, poradi)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (nazev) DO NOTHING
        """, (nazev, popis, jednotka, typ_vypoctu, poradi))

    conn.commit()

    # === INSERT KPI THRESHOLDS ===
    kpi_thresholds = [
        ("Audit", 85, None, "≥", 30, "≥85%"),
        ("Audit", 75, 84.99, "mezi", 15, "75-84%"),
        ("Audit", None, 75, "<", 0, "<75%"),
        ("Hodnocení rozvozy", 4.6, None, "≥", 10, "≥4.6★"),
        ("Hodnocení Google", 4.6, None, "≥", 5, "≥4.6★"),
        ("Čas přípravy", None, 10, "≤", 10, "≤10min"),
        ("Chybovost objednávek", None, 0.5, "<", 10, "<0.5%"),
        ("Mystery shop", 85, None, "≥", 15, "≥85%"),
        ("Obratohodina", 1250, None, "≥", 5, "≥1250 Kč/h"),
        ("Hodnocení zaměstnanců", 8, None, "≥", 5, "≥8/10"),
        ("Zjištěná ztráta", None, 0.5, "≤", 5, "≤0.5%"),
        ("Nezjištěná ztráta", None, 0.5, "≤", 5, "≤0.5%"),
    ]

    for kpi_nazev, min_val, max_val, operator, bonus, popis in kpi_thresholds:
        cursor.execute("SELECT id FROM kpi_definitions WHERE nazev = %s", (kpi_nazev,))
        result = cursor.fetchone()
        if result:
            kpi_id = result[0]
            cursor.execute("""
                INSERT INTO kpi_thresholds
                (kpi_id, min_hodnota, max_hodnota, operator, bonus_procento, popis, poradi)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """, (kpi_id, min_val, max_val, operator, bonus, popis))

    conn.commit()
    cursor.close()
    conn.close()

# ============ DEPARTMENTS FUNCTIONS ============

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_departments():
    """Get all active departments"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, nazev, vedouci, popis, aktivni
        FROM departments
        WHERE aktivni = TRUE
        ORDER BY nazev
    """, conn)
    conn.close()
    return df

def add_department(nazev, vedouci=None, popis=None):
    """Add new department"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO departments (nazev, vedouci, popis)
            VALUES (%s, %s, %s)
        """, (nazev, vedouci, popis))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Oddělení '{nazev}' přidáno"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

# ============ LOCATIONS FUNCTIONS ============

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_locations():
    """Get all active locations with department info"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            l.id, l.nazev, l.department_id, d.nazev as department,
            l.popis, l.aktivni
        FROM locations l
        JOIN departments d ON l.department_id = d.id
        WHERE l.aktivni = TRUE
        ORDER BY d.nazev, l.nazev
    """, conn)
    conn.close()
    return df

def get_locations_by_department(department_id):
    """Get all locations in a department"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nazev, popis
        FROM locations
        WHERE department_id = %s AND aktivni = TRUE
        ORDER BY nazev
    """, (department_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert to DataFrame
    if results:
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame(columns=['id', 'nazev', 'popis'])
    return df

def add_location(nazev, department_id, popis=None):
    """Add new location"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO locations (nazev, department_id, popis)
            VALUES (%s, %s, %s)
        """, (nazev, department_id, popis))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Lokalita '{nazev}' přidána"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def update_location_department(location_id, department_id):
    """Update location's department"""
    location_id = safe_convert_id(location_id)
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE locations
            SET department_id = %s
            WHERE id = %s
        """, (department_id, location_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lokalita přeřazena"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

# ============ OPERATIONAL MANAGERS FUNCTIONS ============

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_operational_managers():
    """Get all active operational managers"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            om.id, om.jmeno, om.department_id, d.nazev as department,
            om.email, om.aktivni
        FROM operational_managers om
        JOIN departments d ON om.department_id = d.id
        WHERE om.aktivni = TRUE
        ORDER BY d.nazev, om.jmeno
    """, conn)
    conn.close()
    return df

def get_operational_managers_by_department(department_id):
    """Get operational managers for a department"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, jmeno, email
        FROM operational_managers
        WHERE department_id = %s AND aktivni = TRUE
        ORDER BY jmeno
    """, (department_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    if results:
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame(columns=['id', 'jmeno', 'email'])
    return df

def add_operational_manager(jmeno, department_id, email=None):
    """Add new operational manager"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO operational_managers (jmeno, department_id, email)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (jmeno, department_id, email))
        new_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Provozní '{jmeno}' přidán", new_id
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e), None

def get_manager_kpis(manager_id):
    """Get all KPIs assigned to a manager"""
    manager_id = safe_convert_id(manager_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT k.id, k.nazev, k.jednotka, k.popis
        FROM manager_kpi_assignments a
        JOIN kpi_definitions k ON a.kpi_id = k.id
        WHERE a.manager_id = %s AND k.aktivni = TRUE
        ORDER BY k.poradi
    """, (manager_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    if results:
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame(columns=['id', 'nazev', 'jednotka', 'popis'])
    return df

def set_manager_kpis(manager_id, kpi_ids):
    """Set all KPIs for a manager (replaces existing)"""
    manager_id = safe_convert_id(manager_id)
    kpi_ids = [safe_convert_id(k) for k in kpi_ids] if kpi_ids else []
    conn = get_connection()
    cursor = conn.cursor()
    try:

        # Remove all existing assignments
        cursor.execute("DELETE FROM manager_kpi_assignments WHERE manager_id = %s", (manager_id,))

        # Add new assignments
        for kpi_id in kpi_ids:
            cursor.execute("""
                INSERT INTO manager_kpi_assignments (manager_id, kpi_id)
                VALUES (%s, %s)
            """, (manager_id, kpi_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True, f"KPI nastavena ({len(kpi_ids)} vybraných)"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, f"Chyba: {str(e)}"

# ============ KPI DEFINITIONS & THRESHOLDS ============

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_kpi_definitions():
    """Get all active KPI definitions"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, nazev, popis, jednotka, typ_vypoctu, poradi
        FROM kpi_definitions
        WHERE aktivni = TRUE
        ORDER BY poradi
    """, conn)
    conn.close()
    return df

def get_kpi_thresholds(kpi_id=None):
    """Get KPI thresholds"""
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    if kpi_id:
        df = pd.read_sql_query("""
            SELECT t.*, k.nazev as kpi_nazev, k.jednotka
            FROM kpi_thresholds t
            JOIN kpi_definitions k ON t.kpi_id = k.id
            WHERE t.kpi_id = %s
            ORDER BY t.poradi
        """, conn, params=(kpi_id,))
    else:
        df = pd.read_sql_query("""
            SELECT t.*, k.nazev as kpi_nazev, k.jednotka
            FROM kpi_thresholds t
            JOIN kpi_definitions k ON t.kpi_id = k.id
            ORDER BY k.poradi, t.poradi
        """, conn)
    conn.close()
    return df

def calculate_bonus_for_value(kpi_id, hodnota):
    """Calculate bonus percentage for a KPI value based on thresholds"""
    kpi_id = safe_convert_id(kpi_id)
    if pd.isna(hodnota):
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT min_hodnota, max_hodnota, operator, bonus_procento
        FROM kpi_thresholds
        WHERE kpi_id = %s
        ORDER BY poradi
    """, (kpi_id,))

    thresholds = cursor.fetchall()
    cursor.close()
    conn.close()

    for threshold in thresholds:
        min_val, max_val, operator, bonus = threshold

        if operator == "≥" and min_val is not None:
            if hodnota >= min_val:
                return bonus
        elif operator == "≤" and max_val is not None:
            if hodnota <= max_val:
                return bonus
        elif operator == "<" and max_val is not None:
            if hodnota < max_val:
                return bonus
        elif operator == ">" and min_val is not None:
            if hodnota > min_val:
                return bonus
        elif operator == "mezi" and min_val is not None and max_val is not None:
            if min_val <= hodnota <= max_val:
                return bonus

    return 0

# ============ MONTHLY KPI DATA FUNCTIONS ============

def add_monthly_kpi_data(mesic, location_id, kpi_id, hodnota, poznamka=None, zdroj="MANUAL"):
    """Add or update monthly KPI data"""
    location_id = safe_convert_id(location_id)
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Convert to int to be safe
        location_id = int(location_id)
        kpi_id = int(kpi_id)

        # Verify location and KPI exist
        cursor.execute("SELECT id FROM locations WHERE id = %s AND aktivni = TRUE", (location_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False, f"Lokalita ID {location_id} neexistuje nebo není aktivní"

        cursor.execute("SELECT id FROM kpi_definitions WHERE id = %s AND aktivni = TRUE", (kpi_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False, f"KPI ID {kpi_id} neexistuje nebo není aktivní"

        cursor.execute("""
            INSERT INTO monthly_kpi_data
            (mesic, location_id, kpi_id, hodnota, poznamka, zdroj, status, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE', CURRENT_TIMESTAMP)
            ON CONFLICT(mesic, location_id, kpi_id)
            DO UPDATE SET
                hodnota = EXCLUDED.hodnota,
                poznamka = EXCLUDED.poznamka,
                updated_at = CURRENT_TIMESTAMP,
                zdroj = EXCLUDED.zdroj
        """, (mesic, location_id, kpi_id, float(hodnota), poznamka, zdroj))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Data uložena"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, f"Chyba: {str(e)}"

def get_monthly_kpi_data(mesic=None, location_id=None, kpi_id=None):
    """Get monthly KPI data with filters"""
    location_id = safe_convert_id(location_id)
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()

    query = """
        SELECT
            d.id, d.mesic, d.location_id, l.nazev as location,
            d.kpi_id, k.nazev as kpi_nazev, k.jednotka,
            d.hodnota, d.status, d.poznamka, d.zdroj,
            d.created_at, d.updated_at
        FROM monthly_kpi_data d
        JOIN locations l ON d.location_id = l.id
        JOIN kpi_definitions k ON d.kpi_id = k.id
        WHERE d.status = 'ACTIVE'
    """

    params = []
    if mesic:
        query += " AND d.mesic = %s"
        params.append(mesic)
    if location_id:
        query += " AND d.location_id = %s"
        params.append(location_id)
    if kpi_id:
        query += " AND d.kpi_id = %s"
        params.append(kpi_id)

    query += " ORDER BY d.mesic DESC, l.nazev, k.poradi"

    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if results:
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame(columns=['id', 'mesic', 'location_id', 'location', 'kpi_id', 'kpi_nazev', 'jednotka', 'hodnota', 'status', 'poznamka', 'zdroj', 'created_at', 'updated_at'])
    return df

def get_monthly_kpi_by_location_month(mesic, location_id):
    """Get all KPI data for a location in a month"""
    location_id = safe_convert_id(location_id)
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            d.kpi_id, k.nazev, k.jednotka, k.poradi,
            d.hodnota, d.poznamka
        FROM monthly_kpi_data d
        JOIN kpi_definitions k ON d.kpi_id = k.id
        WHERE d.mesic = %s AND d.location_id = %s AND d.status = 'ACTIVE'
        ORDER BY k.poradi
    """, conn, params=(mesic, location_id))
    conn.close()
    return df

def delete_monthly_kpi_data(mesic, location_id):
    """Delete all KPI data for a location in a month"""
    location_id = safe_convert_id(location_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Delete from monthly_kpi_data
        cursor.execute("""
            DELETE FROM monthly_kpi_data
            WHERE mesic = %s AND location_id = %s
        """, (mesic, location_id))

        # Also delete evaluation data
        cursor.execute("""
            DELETE FROM monthly_kpi_evaluation
            WHERE mesic = %s AND location_id = %s
        """, (mesic, location_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Data smazána"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, f"Chyba při mazání: {str(e)}"

# ============ MONTHLY EVALUATION & BONUS CALCULATION ============

def calculate_monthly_kpi_evaluation(mesic, location_id=None):
    """Calculate KPI evaluation and bonuses for a month"""
    location_id = safe_convert_id(location_id)
    conn = get_connection()
    cursor = conn.cursor()

    if location_id:
        cursor.execute("""
            SELECT d.location_id, d.kpi_id, d.hodnota
            FROM monthly_kpi_data d
            WHERE d.mesic = %s AND d.location_id = %s AND d.status = 'ACTIVE'
        """, (mesic, location_id))
    else:
        cursor.execute("""
            SELECT d.location_id, d.kpi_id, d.hodnota
            FROM monthly_kpi_data d
            WHERE d.mesic = %s AND d.status = 'ACTIVE'
        """, (mesic,))

    evaluations = cursor.fetchall()

    for row in evaluations:
        loc_id, kpi_id, value = row
        bonus = calculate_bonus_for_value(kpi_id, value)
        splneno = 1 if bonus > 0 else 0

        cursor.execute("""
            INSERT INTO monthly_kpi_evaluation
            (mesic, location_id, kpi_id, hodnota, splneno, bonus_procento, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(mesic, location_id, kpi_id)
            DO UPDATE SET
                hodnota = EXCLUDED.hodnota,
                splneno = EXCLUDED.splneno,
                bonus_procento = EXCLUDED.bonus_procento,
                updated_at = CURRENT_TIMESTAMP
        """, (mesic, loc_id, kpi_id, value, splneno, bonus))

    conn.commit()
    cursor.close()
    conn.close()

def get_monthly_kpi_evaluation(mesic, location_id=None):
    """Get KPI evaluation for a month"""
    location_id = safe_convert_id(location_id)
    conn = get_connection()

    query = """
        SELECT
            e.mesic, e.location_id, l.nazev as location,
            e.kpi_id, k.nazev as kpi_nazev, k.jednotka,
            e.hodnota, e.splneno, e.bonus_procento
        FROM monthly_kpi_evaluation e
        LEFT JOIN locations l ON e.location_id = l.id
        LEFT JOIN kpi_definitions k ON e.kpi_id = k.id
        WHERE e.mesic = %s
    """

    params = [mesic]
    if location_id:
        query += " AND e.location_id = %s"
        params.append(location_id)

    query += " ORDER BY l.nazev, k.poradi"

    cursor = conn.cursor()


    cursor.execute(query, tuple(params) if params else ())


    results = cursor.fetchall()


    cursor.close()


    conn.close()


    


    if results:


        df = pd.DataFrame(results)


    else:


        df = pd.DataFrame()


    return df

def get_department_monthly_summary(mesic=None, department_id=None):
    """Get department monthly KPI summary"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()

    query = """
        SELECT
            s.mesic, s.department_id, d.nazev as department,
            s.celkovy_bonus, s.aktivnich_kpi, s.splnenych_kpi
        FROM department_monthly_summary s
        JOIN departments d ON s.department_id = d.id
        WHERE 1=1
    """

    params = []
    if mesic:
        query += " AND s.mesic = %s"
        params.append(mesic)
    if department_id:
        query += " AND s.department_id = %s"
        params.append(department_id)

    query += " ORDER BY s.mesic DESC, d.nazev"

    cursor = conn.cursor()


    cursor.execute(query, tuple(params) if params else ())


    results = cursor.fetchall()


    cursor.close()


    conn.close()


    


    if results:


        df = pd.DataFrame(results)


    else:


        df = pd.DataFrame()


    return df

def calculate_monthly_department_kpi_evaluation(mesic, department_id=None):
    """Calculate KPI evaluation and bonuses for departments with own KPI"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()

    if department_id:
        cursor.execute("""
            SELECT d.department_id, d.kpi_id, d.hodnota
            FROM monthly_department_kpi_data d
            WHERE d.mesic = %s AND d.department_id = %s AND d.status = 'ACTIVE'
        """, (mesic, department_id))
    else:
        cursor.execute("""
            SELECT d.department_id, d.kpi_id, d.hodnota
            FROM monthly_department_kpi_data d
            WHERE d.mesic = %s AND d.status = 'ACTIVE'
        """, (mesic,))

    evaluations = cursor.fetchall()

    for row in evaluations:
        dept_id, kpi_id, value = row
        bonus = calculate_bonus_for_value(kpi_id, value)
        splneno = 1 if bonus > 0 else 0

        # Store evaluation in department_monthly_summary or create separate table if needed
        # For now, we'll calculate summary directly

    conn.commit()
    cursor.close()
    conn.close()

def calculate_department_summary(mesic):
    """Calculate department monthly summary - handles both own KPI and location averages"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, ma_vlastni_kpi FROM departments WHERE aktivni = TRUE")
    departments = cursor.fetchall()

    for dept_row in departments:
        dept_id, ma_vlastni_kpi = dept_row

        if ma_vlastni_kpi:
            # Department has own KPI - calculate from monthly_department_kpi_data
            cursor.execute("""
                SELECT d.kpi_id, d.hodnota
                FROM monthly_department_kpi_data d
                WHERE d.mesic = %s AND d.department_id = %s AND d.status = 'ACTIVE'
            """, (mesic, dept_id))

            kpi_data = cursor.fetchall()
            total_bonus = 0
            total_active = len(kpi_data)
            total_met = 0

            for kpi_id, hodnota in kpi_data:
                bonus = calculate_bonus_for_value(kpi_id, hodnota)
                total_bonus += bonus
                if bonus > 0:
                    total_met += 1

        else:
            # Department uses average from locations
            cursor.execute("""
                SELECT id FROM locations
                WHERE department_id = %s AND aktivni = TRUE
            """, (dept_id,))
            locations = cursor.fetchall()

            total_bonus = 0
            total_active = 0
            total_met = 0

            for loc_row in locations:
                loc_id = loc_row['id']

                cursor.execute("""
                    SELECT
                        SUM(bonus_procento) as total_bonus,
                        COUNT(*) as kpi_count,
                        SUM(splneno) as met_count
                    FROM monthly_kpi_evaluation
                    WHERE mesic = %s AND location_id = %s
                """, (mesic, loc_id))

                result = cursor.fetchone()
                if result and result[0]:
                    total_bonus += result[0]
                    total_active += result[1] or 0
                    total_met += result[2] or 0

            if locations:
                # Average across locations
                avg_bonus = total_bonus / len(list(locations)) if locations else 0
                total_bonus = avg_bonus

        # Save summary
        if total_active > 0 or not ma_vlastni_kpi:
            cursor.execute("""
                INSERT INTO department_monthly_summary
                (mesic, department_id, celkovy_bonus, aktivnich_kpi, splnenych_kpi)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(mesic, department_id)
                DO UPDATE SET
                    celkovy_bonus = EXCLUDED.celkovy_bonus,
                    aktivnich_kpi = EXCLUDED.aktivnich_kpi,
                    splnenych_kpi = EXCLUDED.splnenych_kpi
            """, (mesic, dept_id, total_bonus, total_active, total_met))

    conn.commit()
    cursor.close()
    conn.close()

# ============ IMPORT/EXPORT FUNCTIONS ============

def generate_import_template():
    """Generate a CSV template for importing monthly data"""
    data = {
        "Měsíc (YYYY-MM)": ["2025-11", "2025-11", "2025-11", "2025-11", "2025-11", "2025-11"],
        "Lokalita": ["Mercury", "Mercury", "OC4Dvory", "OC4Dvory", "Bistro", "Bistro"],
        "KPI": ["Audit", "Chybovost objednávek", "Audit", "Mystery shop", "Audit", "Hodnocení rozvozy"],
        "Hodnota": [85.5, 0.3, 78.0, 88.0, 92.0, 4.7],
        "Poznámka": ["Dobrý audit", "", "Potřeba zlepšit", "", "", ""]
    }
    df = pd.DataFrame(data)
    return df

def generate_import_template_excel():
    """Generate Excel template"""
    df = generate_import_template()
    # Návrat jako BytesIO (pro download)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='KPI Data', index=False)
    output.seek(0)
    return output.getvalue()

def import_monthly_data_csv(csv_content):
    """Import monthly KPI data from CSV"""
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        conn = get_connection()
        cursor = conn.cursor()

        imported = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                mesic = str(row.get("Měsíc (YYYY-MM)", "")).strip()
                location_name = str(row.get("Lokalita", "")).strip()
                kpi_name = str(row.get("KPI", "")).strip()
                value = float(row.get("Hodnota", 0))
                poznamka = str(row.get("Poznámka", ""))

                # Get IDs
                cursor.execute("SELECT id FROM locations WHERE nazev = %s", (location_name,))
                loc_result = cursor.fetchone()
                if not loc_result:
                    errors.append(f"Řada {idx+2}: Lokalita '{location_name}' nebyla nalezena")
                    continue

                location_id = loc_result[0]

                cursor.execute("SELECT id FROM kpi_definitions WHERE nazev = %s", (kpi_name,))
                kpi_result = cursor.fetchone()
                if not kpi_result:
                    errors.append(f"Řada {idx+2}: KPI '{kpi_name}' nebyla nalezena")
                    continue

                kpi_id = kpi_result[0]

                # Insert data
                cursor.execute("""
                    INSERT INTO monthly_kpi_data
                    (mesic, location_id, kpi_id, hodnota, poznamka, zdroj)
                    VALUES (%s, %s, %s, %s, %s, 'IMPORT')
                    ON CONFLICT(mesic, location_id, kpi_id)
                    DO UPDATE SET
                        hodnota = EXCLUDED.hodnota,
                        poznamka = EXCLUDED.poznamka,
                        updated_at = CURRENT_TIMESTAMP,
                        zdroj = 'IMPORT'
                """, (mesic, location_id, kpi_id, value, poznamka if poznamka else None))

                imported += 1

            except Exception as e:
                errors.append(f"Řada {idx+2}: {str(e)}")

        conn.commit()
        cursor.close()
        conn.close()

        return imported, errors

    except Exception as e:
        return 0, [f"Chyba při čtení CSV: {str(e)}"]

def import_monthly_data_excel(excel_file):
    """Import monthly KPI data from Excel"""
    try:
        df = pd.read_excel(excel_file)
        # Převedi na CSV string a použi existující funkcí
        csv_content = df.to_csv(index=False)
        return import_monthly_data_csv(csv_content)
    except Exception as e:
        return 0, [f"Chyba při čtení Excel: {str(e)}"]

def get_all_months_with_data():
    """Get all months that have KPI data"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT DISTINCT mesic
        FROM monthly_kpi_data
        WHERE status = 'ACTIVE'
        ORDER BY mesic DESC
    """, conn)
    conn.close()

    if df.empty:
        return []
    return sorted(df['mesic'].unique().tolist(), reverse=True)

# ============ DELETE FUNCTIONS ============

def delete_department(department_id):
    """Soft delete department (set aktivni=FALSE)"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if department has locations or managers
        cursor.execute("SELECT COUNT(*) as count FROM locations WHERE department_id = %s AND aktivni = TRUE", (department_id,))
        loc_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM operational_managers WHERE department_id = %s AND aktivni = TRUE", (department_id,))
        mgr_count = cursor.fetchone()['count']

        if loc_count > 0 or mgr_count > 0:
            cursor.close()
            conn.close()
            return False, f"Nelze smazat oddělení s aktivními lokalitami ({loc_count}) nebo provozními ({mgr_count})"

        cursor.execute("UPDATE departments SET aktivni = FALSE WHERE id = %s", (department_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Oddělení smazáno"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def delete_location(location_id):
    """Soft delete location (set aktivni=FALSE)"""
    location_id = safe_convert_id(location_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE locations SET aktivni = FALSE WHERE id = %s", (location_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Lokalita smazána"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def delete_operational_manager(manager_id):
    """Soft delete operational manager (set aktivni=FALSE)"""
    manager_id = safe_convert_id(manager_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE operational_managers SET aktivni = FALSE WHERE id = %s", (manager_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Provozní smazán"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

# ============ KPI DEFINITIONS CRUD ============

def add_kpi_definition(nazev, popis=None, jednotka=None, typ_vypoctu=None, poradi=None):
    """Add new KPI definition"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if poradi is None:
            cursor.execute("SELECT MAX(poradi) as max FROM kpi_definitions")
            result = cursor.fetchone()
            max_poradi = result['max'] if result['max'] is not None else 0
            poradi = max_poradi + 1

        cursor.execute("""
            INSERT INTO kpi_definitions (nazev, popis, jednotka, typ_vypoctu, poradi)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (nazev, popis, jednotka, typ_vypoctu, poradi))
        new_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"KPI '{nazev}' přidáno", new_id
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e), None

def update_kpi_definition(kpi_id, nazev=None, popis=None, jednotka=None, typ_vypoctu=None, poradi=None):
    """Update KPI definition"""
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []

        if nazev is not None:
            updates.append("nazev = %s")
            params.append(nazev)
        if popis is not None:
            updates.append("popis = %s")
            params.append(popis)
        if jednotka is not None:
            updates.append("jednotka = %s")
            params.append(jednotka)
        if typ_vypoctu is not None:
            updates.append("typ_vypoctu = %s")
            params.append(typ_vypoctu)
        if poradi is not None:
            updates.append("poradi = %s")
            params.append(poradi)

        if not updates:
            cursor.close()
            conn.close()
            return False, "Žádné změny"

        params.append(kpi_id)
        query = f"UPDATE kpi_definitions SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True, "KPI upraveno"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def delete_kpi_definition(kpi_id):
    """Soft delete KPI definition (set aktivni=FALSE)"""
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE kpi_definitions SET aktivni = FALSE WHERE id = %s", (kpi_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "KPI smazáno"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def get_all_kpi_definitions(include_inactive=False):
    """Get all KPI definitions (including inactive if specified)"""
    conn = get_connection()
    if include_inactive:
        query = "SELECT * FROM kpi_definitions ORDER BY poradi, nazev"
    else:
        query = "SELECT * FROM kpi_definitions WHERE aktivni = TRUE ORDER BY poradi, nazev"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============ KPI THRESHOLDS CRUD ============

def add_kpi_threshold(kpi_id, operator, bonus_procento, min_hodnota=None, max_hodnota=None, popis=None, poradi=None):
    """Add new KPI threshold"""
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Convert to int to be safe
        kpi_id = int(kpi_id)

        # Verify KPI exists
        cursor.execute("SELECT id FROM kpi_definitions WHERE id = %s AND aktivni = TRUE", (kpi_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False, f"KPI ID {kpi_id} neexistuje nebo není aktivní", None

        if poradi is None:
            cursor.execute("SELECT MAX(poradi) as max FROM kpi_thresholds WHERE kpi_id = %s", (kpi_id,))
            result = cursor.fetchone()
            max_poradi = result['max'] if result['max'] is not None else 0
            poradi = max_poradi + 1

        cursor.execute("""
            INSERT INTO kpi_thresholds (kpi_id, min_hodnota, max_hodnota, operator, bonus_procento, popis, poradi)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (kpi_id, min_hodnota, max_hodnota, operator, bonus_procento, popis, poradi))
        new_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Hranice přidána", new_id
    except Exception as e:
        cursor.close()
        conn.close()
        return False, f"Chyba: {str(e)}", None

def update_kpi_threshold(threshold_id, min_hodnota, max_hodnota, operator, bonus_procento, popis, poradi):
    """Update KPI threshold - updates all fields"""
    threshold_id = safe_convert_id(threshold_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE kpi_thresholds
            SET min_hodnota = %s,
                max_hodnota = %s,
                operator = %s,
                bonus_procento = %s,
                popis = %s,
                poradi = %s
            WHERE id = %s
        """, (min_hodnota, max_hodnota, operator, bonus_procento, popis, poradi, threshold_id))

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return False, "Hranice nenalezena"

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Hranice upravena"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, f"Chyba: {str(e)}"

def delete_kpi_threshold(threshold_id):
    """Delete KPI threshold"""
    threshold_id = safe_convert_id(threshold_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM kpi_thresholds WHERE id = %s", (threshold_id,))

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return False, "Hranice nenalezena"

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Hranice smazána"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, f"Chyba: {str(e)}"

# ============ DEPARTMENT VLASTNI KPI FUNCTIONS ============

def update_department_vlastni_kpi(department_id, ma_vlastni_kpi):
    """Update whether department has own KPI values"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE departments
            SET ma_vlastni_kpi = %s
            WHERE id = %s
        """, (ma_vlastni_kpi, department_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Nastavení vlastních KPI upraveno"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def add_monthly_department_kpi_data(mesic, department_id, kpi_id, hodnota, poznamka=None, zdroj="MANUAL"):
    """Add or update monthly KPI data for department with own KPI"""
    department_id = safe_convert_id(department_id)
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO monthly_department_kpi_data (mesic, department_id, kpi_id, hodnota, poznamka, zdroj, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(mesic, department_id, kpi_id) DO UPDATE SET
                hodnota = EXCLUDED.hodnota,
                poznamka = EXCLUDED.poznamka,
                zdroj = EXCLUDED.zdroj,
                updated_at = CURRENT_TIMESTAMP
        """, (mesic, department_id, kpi_id, hodnota, poznamka, zdroj))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Data uložena"
    except Exception as e:
        cursor.close()
        conn.close()
        return False, str(e)

def get_monthly_department_kpi_data(mesic, department_id=None):
    """Get monthly KPI data for department(s) with own KPI"""
    department_id = safe_convert_id(department_id)
    conn = get_connection()
    if department_id:
        query = """
            SELECT d.mesic, d.department_id, dept.nazev as department_nazev,
                   d.kpi_id, k.nazev as kpi_nazev, d.hodnota, d.poznamka, d.zdroj
            FROM monthly_department_kpi_data d
            JOIN departments dept ON d.department_id = dept.id
            JOIN kpi_definitions k ON d.kpi_id = k.id
            WHERE d.mesic = %s AND d.department_id = %s AND d.status = 'ACTIVE'
            ORDER BY k.poradi
        """
        cursor = conn.cursor()
        cursor.execute(query, (mesic, department_id))
        results = cursor.fetchall()
        cursor.close()
        if results:
            df = pd.DataFrame(results)
        else:
            df = pd.DataFrame(columns=['mesic', 'department_id', 'department_nazev', 'kpi_id', 'kpi_nazev', 'hodnota', 'poznamka', 'zdroj'])
    else:
        query = """
            SELECT d.mesic, d.department_id, dept.nazev as department_nazev,
                   d.kpi_id, k.nazev as kpi_nazev, d.hodnota, d.poznamka, d.zdroj
            FROM monthly_department_kpi_data d
            JOIN departments dept ON d.department_id = dept.id
            JOIN kpi_definitions k ON d.kpi_id = k.id
            WHERE d.mesic = %s AND d.status = 'ACTIVE'
            ORDER BY dept.nazev, k.poradi
        """
        cursor = conn.cursor()
        cursor.execute(query, (mesic,))
        results = cursor.fetchall()
        cursor.close()
        if results:
            df = pd.DataFrame(results)
        else:
            df = pd.DataFrame(columns=['mesic', 'department_id', 'department_nazev', 'kpi_id', 'kpi_nazev', 'hodnota', 'poznamka', 'zdroj'])
    conn.close()
    return df

def get_department_kpi_value(mesic, department_id, kpi_id):
    """
    Get KPI value for department - either own value or average from locations
    Returns: (hodnota, zdroj) where zdroj is 'VLASTNI' or 'PRUMER_Z_LOKALIT'
    """
    department_id = safe_convert_id(department_id)
    kpi_id = safe_convert_id(kpi_id)
    conn = get_connection()
    cursor = conn.cursor()

    # Check if department has own KPI
    cursor.execute("SELECT ma_vlastni_kpi FROM departments WHERE id = %s", (department_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        conn.close()
        return None, None

    ma_vlastni_kpi = result[0]

    if ma_vlastni_kpi:
        # Get own KPI value
        cursor.execute("""
            SELECT hodnota
            FROM monthly_department_kpi_data
            WHERE mesic = %s AND department_id = %s AND kpi_id = %s AND status = 'ACTIVE'
        """, (mesic, department_id, kpi_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0], 'VLASTNI'
        else:
            return None, None
    else:
        # Calculate average from locations
        cursor.execute("""
            SELECT AVG(mkd.hodnota) as prumer
            FROM monthly_kpi_data mkd
            JOIN locations l ON mkd.location_id = l.id
            WHERE mkd.mesic = %s AND l.department_id = %s AND mkd.kpi_id = %s
                  AND mkd.status = 'ACTIVE' AND l.aktivni = TRUE
        """, (mesic, department_id, kpi_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result[0] is not None:
            return result[0], 'PRUMER_Z_LOKALIT'
        else:
            return None, None

def get_departments_with_vlastni_kpi():
    """Get list of departments that have own KPI values"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, nazev, vedouci, ma_vlastni_kpi
        FROM departments
        WHERE aktivni = TRUE
        ORDER BY nazev
    """, conn)
    conn.close()
    return df
