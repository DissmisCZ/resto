"""
RESTO v3 - KPI Dashboard (REDESIGNED)
Structure based on Excel KPIProvozníActive.xlsx
Showing PROVOZNÍ (operational managers) results, not departments
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import database as db
import io

st.set_page_config(page_title="RESTO v3", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

# ============================================================================
# AUTHENTICATION
# ============================================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
    /* Login page styles */
    .login-page {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e8ba3 100%);
    }
    .login-card {
        background: white;
        max-width: 450px;
        width: 100%;
        padding: 50px 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        text-align: center;
    }
    .login-logo {
        width: 180px;
        height: 180px;
        margin: 0 auto 30px;
    }
    .login-logo img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    .login-title {
        color: #1e3c72;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .login-subtitle {
        color: #6c757d;
        font-size: 16px;
        margin-bottom: 35px;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 12px 15px;
        font-size: 16px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2a5298;
        box-shadow: 0 0 0 2px rgba(42,82,152,0.1);
    }
    .stButton > button {
        border-radius: 10px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 600;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center everything
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo
        try:
            st.image("assets/logo.png", width=180)
        except:
            st.markdown('<div style="text-align: center; font-size: 80px; margin-bottom: 20px;">🍔</div>', unsafe_allow_html=True)

        # Title
        st.markdown('<div class="login-title">Bouda Burgers</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">KPI Dashboard - Přihlášení</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Try to get password from secrets, fallback to demo password
        try:
            correct_password = st.secrets["passwords"]["admin"]
        except:
            correct_password = "resto2025"  # Default password if secrets not configured
            st.warning("⚠️ Používá se výchozí heslo")

        password = st.text_input("🔒 Heslo", type="password", key="login_password", label_visibility="collapsed", placeholder="Zadejte heslo")

        if st.button("🔓 Přihlásit se", use_container_width=True, type="primary"):
            if password == correct_password:
                st.session_state.authenticated = True
                st.success("✅ Přihlášení úspěšné!")
                st.rerun()
            else:
                st.error("❌ Nesprávné heslo!")

        # Show hint only in development
        if correct_password == "resto2025":
            st.markdown('<p style="text-align: center; margin-top: 25px; color: #999; font-size: 14px;">💡 Demo heslo: resto2025</p>', unsafe_allow_html=True)

    st.stop()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Theme CSS - apply directly based on dark_mode setting
is_dark = st.session_state.get('dark_mode', True)

if is_dark:
    # Dark mode
    st.markdown("""
<style>
/* Background and text */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0e1117 !important;
    color: #fafafa !important;
}

[data-testid="stSidebar"] {
    background-color: #262730 !important;
    border-right: 1px solid #30363d;
}

/* Compact sidebar */
[data-testid="stSidebar"] .element-container {
    margin-bottom: 0.5rem;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 0.3rem;
}

[data-testid="stSidebar"] .stRadio label {
    padding: 0.3rem 0;
    font-size: 14px;
}

[data-testid="stSidebar"] .stSelectbox label {
    font-size: 14px;
    margin-bottom: 0.25rem;
}

[data-testid="stSidebar"] hr {
    margin: 0.5rem 0;
}

[data-testid="stHeader"] {
    background-color: #0e1117 !important;
}

/* Text elements */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #fafafa !important;
}

[data-testid="stMarkdownContainer"] {
    color: #fafafa !important;
}

/* Buttons */
.stButton > button {
    background-color: #262730 !important;
    color: #fafafa !important;
    border: 1px solid #30363d !important;
}

.stButton > button:hover {
    background-color: #30363d !important;
    border-color: #40464d !important;
}

.stButton > button[kind="primary"] {
    background-color: #0e7490 !important;
    color: white !important;
    border: none !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #0891b2 !important;
}

.stButton > button[kind="secondary"] {
    background-color: #262730 !important;
    color: #fafafa !important;
}

/* Input fields */
input, textarea, [data-baseweb="input"] {
    background-color: #262730 !important;
    color: #fafafa !important;
    border-color: #30363d !important;
}

/* Selectbox */
[data-baseweb="select"] {
    background-color: #262730 !important;
    color: #fafafa !important;
    cursor: pointer;
}

[data-baseweb="select"] input {
    pointer-events: none;
    cursor: pointer;
    caret-color: transparent;
    color: #fafafa !important;
}

[data-baseweb="select"] > div {
    background-color: #262730 !important;
    color: #fafafa !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #fafafa !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label {
    color: #fafafa !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #262730 !important;
    padding: 10px;
    border-radius: 8px;
}

[data-testid="stMetric"] label {
    color: #a0a0a0 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #fafafa !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1f77b4 0%, #2a8fbc 100%);
    padding: 20px;
    border-radius: 8px;
    color: white;
    text-align: center;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.metric-card h2 {
    margin: 0;
    font-size: 2.5em;
    font-weight: bold;
}
.metric-card p {
    margin: 5px 0 0 0;
    font-size: 1.1em;
    opacity: 0.95;
}
.metric-good {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
}
.metric-bad {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
}
.metric-medium {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
}
.success-banner {
    background-color: #22c55e;
    color: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
    font-weight: bold;
    font-size: 1.1em;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 10px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #262730 !important;
    border: 1px solid #30363d !important;
}

[data-testid="stExpander"] summary {
    color: #fafafa !important;
}
</style>
""", unsafe_allow_html=True)
else:
    # Light mode
    st.markdown("""
<style>
/* Background and text */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}

[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    border-right: 1px solid #dee2e6;
}

/* Compact sidebar */
[data-testid="stSidebar"] .element-container {
    margin-bottom: 0.5rem;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 0.3rem;
}

[data-testid="stSidebar"] .stRadio label {
    padding: 0.3rem 0;
    font-size: 14px;
}

[data-testid="stSidebar"] .stSelectbox label {
    font-size: 14px;
    margin-bottom: 0.25rem;
}

[data-testid="stSidebar"] hr {
    margin: 0.5rem 0;
}

[data-testid="stHeader"] {
    background-color: #ffffff !important;
}

/* Text elements */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #1a1a1a !important;
}

[data-testid="stMarkdownContainer"] {
    color: #1a1a1a !important;
}

/* Buttons */
.stButton > button {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #d1d5db !important;
}

.stButton > button:hover {
    background-color: #f3f4f6 !important;
    border-color: #9ca3af !important;
}

.stButton > button[kind="primary"] {
    background-color: #0891b2 !important;
    color: white !important;
    border: none !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #0e7490 !important;
}

.stButton > button[kind="secondary"] {
    background-color: #f3f4f6 !important;
    color: #1a1a1a !important;
}

/* Input fields */
input, textarea, [data-baseweb="input"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border-color: #d1d5db !important;
}

/* Selectbox */
[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    cursor: pointer;
}

[data-baseweb="select"] input {
    pointer-events: none;
    cursor: pointer;
    caret-color: transparent;
    color: #1a1a1a !important;
}

[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #1a1a1a !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label {
    color: #1a1a1a !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #f8f9fa !important;
    padding: 10px;
    border-radius: 8px;
}

[data-testid="stMetric"] label {
    color: #6c757d !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #1a1a1a !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1f77b4 0%, #2a8fbc 100%);
    padding: 20px;
    border-radius: 8px;
    color: white;
    text-align: center;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.metric-card h2 {
    margin: 0;
    font-size: 2.5em;
    font-weight: bold;
    color: white !important;
}
.metric-card p {
    margin: 5px 0 0 0;
    font-size: 1.1em;
    opacity: 0.95;
    color: white !important;
}
.metric-good {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
}
.metric-bad {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
}
.metric-medium {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
}
.success-banner {
    background-color: #22c55e;
    color: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
    font-weight: bold;
    font-size: 1.1em;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 10px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
}

[data-testid="stExpander"] summary {
    color: #1a1a1a !important;
}
</style>
""", unsafe_allow_html=True)

# Init DB
db.init_database()
db.insert_default_data()

@st.cache_data(ttl=60)
def get_managers():
    return db.get_operational_managers()

@st.cache_data(ttl=60)
def get_locs():
    return db.get_locations()

@st.cache_data(ttl=60)
def get_kpis():
    return db.get_kpi_definitions()

def format_month(m):
    """Convert YYYY-MM to Czech month name"""
    try:
        dt = datetime.strptime(m, "%Y-%m")
        months = {1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben", 5: "Květen", 6: "Červen",
                 7: "Červenec", 8: "Srpen", 9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"}
        return f"{months[dt.month]} {dt.year}"
    except:
        return m

def month_to_string(dt):
    """Convert date object to YYYY-MM string"""
    return dt.strftime("%Y-%m")

def safe_int_id(value):
    """Safely convert ID to integer (handles bytes from pandas)"""
    if isinstance(value, bytes):
        return int.from_bytes(value, byteorder='little')
    return int(value)

# Initialize session state for persistent messages
if 'save_message' not in st.session_state:
    st.session_state.save_message = None
if 'save_message_type' not in st.session_state:
    st.session_state.save_message_type = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Default: dark mode

# SIDEBAR
with st.sidebar:
    # Logo and title
    col_logo, col_space = st.columns([1, 3])
    with col_logo:
        try:
            st.image("assets/logo.png", width=60)
        except:
            st.markdown('<div style="font-size: 50px; text-align: center;">🍔</div>', unsafe_allow_html=True)

    st.markdown('<h3 style="margin-top: -10px; font-size: 18px; font-weight: bold;">Bouda Burgers</h3>', unsafe_allow_html=True)
    st.markdown('<p style="margin-top: -15px; font-size: 12px; color: #666;">KPI Dashboard v3</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Category selector - compact
    category = st.radio("📁 Kategorie", [
        "Provozní KPI",
        "Marketing KPI",
        "⚙️ Admin"
    ], horizontal=False)

    st.markdown("---")

    # Page navigation based on category
    if category == "Provozní KPI":
        page = st.radio("📌 Navigace", [
            "📊 Přehled",
            "📈 Detailní přehled",
            "👥 Porovnání",
            "📝 Zadání dat"
        ])
    elif category == "Marketing KPI":
        page = "Marketing KPI"
        st.info("🚧 Sekce v přípravě\n\nMarketing KPI budou přidány v budoucí verzi.")
    else:  # Admin
        page = "⚙️ Admin"

    st.markdown("---")

    # Month selector - using selectbox
    months = db.get_all_months_with_data()
    if months:
        default_month_str = months[0]  # Latest month
    else:
        default_month_str = date.today().strftime("%Y-%m")

    # Create options with formatted month names
    month_options = {format_month(m): m for m in months} if months else {format_month(default_month_str): default_month_str}

    selected_formatted = st.selectbox(
        "📅 Hlavní měsíc:",
        options=list(month_options.keys()),
        index=0,
        key="main_month_select"
    )
    selected_month = month_options[selected_formatted]

    # Comparison month selector (only for Provozní KPI pages)
    if category == "Provozní KPI":
        st.markdown("---")
        comparison_options = ["❌ Žádné porovnání"] + [f"🔄 vs {format_month(m)}" for m in months if m != selected_month]

        if len(months) > 1:
            # Try to select previous month as default
            selected_month_idx = months.index(selected_month) if selected_month in months else 0
            if selected_month_idx < len(months) - 1:
                default_comparison_idx = 1  # Previous month
            else:
                default_comparison_idx = 0  # No comparison
        else:
            default_comparison_idx = 0

        comparison_selection = st.selectbox(
            "📊 Porovnat s měsícem:",
            options=comparison_options,
            index=default_comparison_idx,
            key="comparison_month_select"
        )

        if comparison_selection == "❌ Žádné porovnání":
            comparison_month = None
        else:
            # Extract month from selection
            comparison_formatted = comparison_selection.replace("🔄 vs ", "")
            comparison_month = month_options.get(comparison_formatted)
    else:
        comparison_month = None

    st.caption(f"Zvolený měsíc: {format_month(selected_month)}")
    if comparison_month:
        st.caption(f"Porovnání: {format_month(comparison_month)}")
    st.caption(f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    # Logout button
    st.markdown("---")
    if st.button("🚪 Odhlásit se", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # Theme switch buttons at bottom
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True, type="primary" if not st.session_state.get('dark_mode', True) else "secondary"):
            st.session_state.dark_mode = False
            st.rerun()
    with col2:
        if st.button("🌙 Dark", use_container_width=True, type="primary" if st.session_state.get('dark_mode', True) else "secondary"):
            st.session_state.dark_mode = True
            st.rerun()


# ============================================================================
# PAGE 1: PŘEHLED - PROVOZNÍ RESULTS (like Excel sheets)
# ============================================================================
if page == "📊 Přehled":
    st.title("📊 Přehled KPI - Provozní")

    st.markdown(f"### Měsíc: **{format_month(selected_month)}**")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Přepočítat bonusy", use_container_width=True):
            db.calculate_monthly_kpi_evaluation(selected_month)
            db.calculate_department_summary(selected_month)
            st.success("✅ Bonusy přepočítány")
            st.rerun()

    st.markdown("---")

    # Get all managers
    managers = get_managers()

    if managers.empty:
        st.warning("Žádní provozní manažeři v databázi")
    else:
        # Display each manager's results (like Excel Výsledky sheets)
        for _, manager in managers.iterrows():
            st.markdown(f"### 👤 {manager['jmeno']} ({manager['department']})")

            # Get locations for this manager's department
            locs_in_dept = db.get_locations_by_department(manager['department_id'])

            if locs_in_dept.empty:
                st.info(f"Žádné lokality pro oddělení {manager['department']}")
                continue

            # Calculate total bonus for this manager across all locations in department
            total_bonus = 0
            total_kpis = 0
            met_kpis = 0

            for _, loc in locs_in_dept.iterrows():
                eval_data = db.get_monthly_kpi_evaluation(selected_month, loc['id'])
                if not eval_data.empty:
                    total_bonus += eval_data['bonus_procento'].sum()
                    total_kpis += len(eval_data)
                    met_kpis += eval_data['splneno'].sum()

            avg_bonus = total_bonus / len(locs_in_dept) if len(locs_in_dept) > 0 else 0

            # Display bonus card
            if avg_bonus >= 50:
                color_class = "metric-good"
            elif avg_bonus >= 30:
                color_class = "metric-medium"
            else:
                color_class = "metric-bad"

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"""
                    <div class="metric-card {color_class}">
                        <h2>{avg_bonus:.1f}%</h2>
                        <p>Celkový bonus</p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.metric("Splněno KPI", f"{met_kpis}/{total_kpis}")
            with col3:
                st.metric("Počet lokalit", len(locs_in_dept))

            # Show details for each location
            with st.expander(f"📋 Detaily KPI pro {manager['jmeno']}", expanded=False):
                for _, loc in locs_in_dept.iterrows():
                    st.markdown(f"**📍 {loc['nazev']}**")

                    eval_data = db.get_monthly_kpi_evaluation(selected_month, loc['id'])

                    if eval_data.empty:
                        st.info(f"ℹ️ Žádná data pro {loc['nazev']} v {format_month(selected_month)}")
                    else:
                        # Display KPI table like Excel
                        cols = st.columns([3, 1, 1, 1, 1])
                        with cols[0]: st.markdown("**Ukazatel**")
                        with cols[1]: st.markdown("**Průměr**")
                        with cols[2]: st.markdown("**Jednotka**")
                        with cols[3]: st.markdown("**Splněno?**")
                        with cols[4]: st.markdown("**Bonus**")
                        st.divider()

                        for _, row in eval_data.iterrows():
                            cols = st.columns([3, 1, 1, 1, 1])
                            with cols[0]: st.text(row['kpi_nazev'])
                            with cols[1]: st.text(f"{row['hodnota']:.2f}")
                            with cols[2]: st.text(row['jednotka'])
                            with cols[3]: st.text("ANO ✅" if row['splneno'] else "NE ❌")
                            with cols[4]: st.text(f"{row['bonus_procento']:.0f}%")

                    st.markdown("---")


# ============================================================================
# PAGE 2: DETAILNÍ PŘEHLED - Detailed view with filters
# ============================================================================
elif page == "📈 Detailní přehled":
    st.title("📈 Detailní Přehled KPI")

    st.markdown(f"### Měsíc: **{format_month(selected_month)}**")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        managers = get_managers()
        manager_options = ["Všichni"] + managers['jmeno'].tolist()
        selected_manager = st.selectbox("Provozní:", manager_options)

    with col2:
        kpis = get_kpis()
        kpi_options = ["Všechny"] + kpis['nazev'].tolist()
        selected_kpi = st.selectbox("KPI:", kpi_options)

    st.markdown("---")

    # Get evaluation data
    eval_data = db.get_monthly_kpi_evaluation(selected_month)

    if eval_data.empty:
        st.warning(f"⚠️ Žádná data pro {format_month(selected_month)}")
        st.info("💡 **Co udělat:**\n1. Přejděte do 'Zadání dat' a zadejte data\n2. Zajistěte že máte definované KPI hranice v 'Nastavení > KPI Hranice'\n3. Přejděte do 'Nastavení > Debug' a klikněte na 'Přepočítat bonusy'")
    else:
        # Join with managers data
        locs = get_locs()
        managers = get_managers()

        # Merge to get manager names
        eval_with_manager = eval_data.merge(
            locs[['id', 'nazev', 'department_id']],
            left_on='location_id',
            right_on='id',
            suffixes=('', '_loc')
        )
        eval_with_manager = eval_with_manager.merge(
            managers[['department_id', 'jmeno']],
            on='department_id',
            suffixes=('', '_mgr')
        )

        # Apply filters
        if selected_manager != "Všichni":
            eval_with_manager = eval_with_manager[eval_with_manager['jmeno'] == selected_manager]

        if selected_kpi != "Všechny":
            eval_with_manager = eval_with_manager[eval_with_manager['kpi_nazev'] == selected_kpi]

        if eval_with_manager.empty:
            st.warning("Žádná data odpovídající filtrům")
        else:
            # Display table
            st.markdown("### 📊 Tabulka výsledků")

            display_df = eval_with_manager[[
                'jmeno', 'nazev', 'kpi_nazev', 'hodnota', 'jednotka', 'splneno', 'bonus_procento'
            ]].copy()
            display_df.columns = ['Provozní', 'Lokalita', 'KPI', 'Hodnota', 'Jednotka', 'Splněno', 'Bonus (%)']
            display_df['Splněno'] = display_df['Splněno'].map({1: '✅ ANO', 0: '❌ NE'})

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Chart - Bonus comparison
            st.markdown("### 📈 Graf porovnání bonusů")

            if selected_kpi == "Všechny":
                # Group by manager and calculate AVERAGE bonus (not sum!)
                # This is correct because manager's bonus is average of all their locations
                bonus_summary = eval_with_manager.groupby('jmeno').agg({
                    'bonus_procento': 'mean',
                    'location_id': 'count'  # Number of locations
                }).reset_index()
                bonus_summary.columns = ['Provozní', 'Průměrný bonus (%)', 'Počet lokalit']
                bonus_summary['Průměrný bonus (%)'] = bonus_summary['Průměrný bonus (%)'].round(1)

                fig = px.bar(
                    bonus_summary,
                    x='Provozní',
                    y='Průměrný bonus (%)',
                    title='Průměrný bonus provozních (ze všech lokalit)',
                    color='Průměrný bonus (%)',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    hover_data=['Počet lokalit']
                )
            else:
                # Show selected KPI across managers
                fig = px.bar(
                    eval_with_manager,
                    x='jmeno',
                    y='bonus_procento',
                    color='splneno',
                    title=f'{selected_kpi} - porovnání',
                    labels={'jmeno': 'Provozní', 'bonus_procento': 'Bonus (%)', 'splneno': 'Splněno'},
                    color_discrete_map={1: 'green', 0: 'red'}
                )

            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE 3: POROVNÁNÍ - Comparisons between managers
# ============================================================================
elif page == "👥 Porovnání":
    st.title("👥 Porovnání Provozních")

    st.markdown(f"### Měsíc: **{format_month(selected_month)}**")

    managers = get_managers()
    eval_data = db.get_monthly_kpi_evaluation(selected_month)

    if eval_data.empty:
        st.warning(f"⚠️ Žádná data pro {format_month(selected_month)}")
        st.info("💡 **Co udělat:**\n1. Přejděte do 'Zadání dat' a zadejte data\n2. Zajistěte že máte definované KPI hranice v 'Nastavení > KPI Hranice'\n3. Přejděte do 'Nastavení > Debug' a klikněte na 'Přepočítat bonusy'")
    else:
        # Calculate summary for each manager
        locs = get_locs()

        summary_data = []
        for _, manager in managers.iterrows():
            # Get locations for this manager's department
            locs_in_dept = locs[locs['department_id'] == manager['department_id']]

            total_bonus = 0
            total_kpis = 0
            met_kpis = 0

            for _, loc in locs_in_dept.iterrows():
                loc_eval = eval_data[eval_data['location_id'] == loc['id']]
                if not loc_eval.empty:
                    total_bonus += loc_eval['bonus_procento'].sum()
                    total_kpis += len(loc_eval)
                    met_kpis += loc_eval['splneno'].sum()

            avg_bonus = total_bonus / len(locs_in_dept) if len(locs_in_dept) > 0 else 0
            success_rate = (met_kpis / total_kpis * 100) if total_kpis > 0 else 0

            summary_data.append({
                'Provozní': manager['jmeno'],
                'Oddělení': manager['department'],
                'Počet lokalit': len(locs_in_dept),
                'Celkový bonus (%)': round(avg_bonus, 1),
                'Splněno KPI': met_kpis,
                'Celkem KPI': total_kpis,
                'Úspěšnost (%)': round(success_rate, 1)
            })

        summary_df = pd.DataFrame(summary_data)

        # Display summary table
        st.markdown("### 📊 Přehledová tabulka")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Celkové bonusy")
            fig1 = px.bar(
                summary_df,
                x='Provozní',
                y='Celkový bonus (%)',
                color='Celkový bonus (%)',
                color_continuous_scale=['red', 'yellow', 'green'],
                text='Celkový bonus (%)'
            )
            fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("### 📊 Úspěšnost KPI")
            fig2 = px.bar(
                summary_df,
                x='Provozní',
                y='Úspěšnost (%)',
                color='Úspěšnost (%)',
                color_continuous_scale=['red', 'yellow', 'green'],
                text='Úspěšnost (%)'
            )
            fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)

        # Detailed KPI breakdown
        st.markdown("### 📋 Detailní rozpis KPI")

        # Create pivot table for each KPI showing performance across managers
        kpis = get_kpis()

        for _, kpi in kpis.iterrows():
            with st.expander(f"📌 {kpi['nazev']} ({kpi['jednotka']})"):
                kpi_data = []

                for _, manager in managers.iterrows():
                    locs_in_dept = locs[locs['department_id'] == manager['department_id']]

                    for _, loc in locs_in_dept.iterrows():
                        kpi_eval = eval_data[
                            (eval_data['location_id'] == loc['id']) &
                            (eval_data['kpi_id'] == kpi['id'])
                        ]

                        if not kpi_eval.empty:
                            row = kpi_eval.iloc[0]
                            kpi_data.append({
                                'Provozní': manager['jmeno'],
                                'Lokalita': loc['nazev'],
                                'Hodnota': row['hodnota'],
                                'Splněno': '✅ ANO' if row['splneno'] else '❌ NE',
                                'Bonus (%)': row['bonus_procento']
                            })

                if kpi_data:
                    kpi_df = pd.DataFrame(kpi_data)
                    st.dataframe(kpi_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Žádná data pro toto KPI")


# ============================================================================
# PAGE 4: ZADÁNÍ DAT - IMPROVED DATA ENTRY
# ============================================================================
elif page == "📝 Zadání dat":
    st.title("📝 Zadání Měsíčních KPI Dat")

    # Display persistent save message
    if st.session_state.save_message:
        if st.session_state.save_message_type == "success":
            st.markdown(f'<div class="success-banner">{st.session_state.save_message}</div>', unsafe_allow_html=True)
        elif st.session_state.save_message_type == "error":
            st.error(st.session_state.save_message)

        # Clear message after displaying
        if st.button("✖ Zavřít zprávu"):
            st.session_state.save_message = None
            st.session_state.save_message_type = None
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Ruční vstup - Lokality", "📝 Ruční vstup - Oddělení", "📥 CSV Import", "📥 Excel Import"])

    # TAB 1: Manual input - IMPROVED
    with tab1:
        st.markdown("### Zadejte data pro lokalitu")

        col1, col2 = st.columns(2)
        with col1:
            # Generate list of months from Jan 2023 to 3 months in future
            start_date = date(2023, 1, 1)
            end_date = date.today() + relativedelta(months=3)

            months_for_input = []
            current = start_date
            while current <= end_date:
                months_for_input.append(current.strftime("%Y-%m"))
                current += relativedelta(months=1)

            # Reverse so newest months are first
            months_for_input = sorted(months_for_input, reverse=True)

            month_options_input = {format_month(m): m for m in months_for_input}

            selected_formatted_input = st.selectbox(
                "Vyberte měsíc:",
                options=list(month_options_input.keys()),
                index=0,
                key="input_month_picker"
            )
            selected_input_month = month_options_input[selected_formatted_input]

        with col2:
            locations = get_locs()
            selected_location = st.selectbox("Lokalita:", locations['nazev'].tolist(), key="input_location")

        st.markdown("---")
        location_id = safe_int_id(locations[locations['nazev'] == selected_location]['id'].values[0])

        # Debug: Show location ID
        with st.expander("🔍 Debug Info"):
            st.code(f"Lokalita: {selected_location}\nLocation ID: {location_id} (typ: {type(location_id).__name__})")
            # Show if location exists in DB
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nazev, aktivni FROM locations WHERE id = ?", (int(location_id),))
            loc_check = cursor.fetchone()
            if loc_check:
                st.success(f"✅ Lokalita nalezena v DB: {loc_check['nazev']} (aktivni={loc_check['aktivni']})")
            else:
                st.error(f"❌ Lokalita ID {location_id} NEEXISTUJE v databázi!")
            conn.close()

        # Get existing data for this month/location OR show zeros
        existing_data = db.get_monthly_kpi_by_location_month(selected_input_month, location_id)

        kpi_defs = get_kpis()
        input_data = {}

        st.markdown(f"**Zadávání dat pro: {selected_location} - {format_month(selected_input_month)}**")

        if not existing_data.empty:
            st.info("ℹ️ Zobrazena existující data - můžete je upravit a přepsat")
        else:
            st.info("ℹ️ Žádná data pro tento měsíc - zadejte nová data")

        for _, kpi in kpi_defs.iterrows():
            # Get existing value or default to 0
            existing_value = existing_data[existing_data['kpi_id'] == kpi['id']]['hodnota'].values
            default_val = float(existing_value[0]) if len(existing_value) > 0 else 0.0

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{kpi['nazev']}** - {kpi['popis']}")
            with col2:
                value = st.number_input(
                    f"({kpi['jednotka']})",
                    value=default_val,
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    label_visibility="collapsed",
                    key=f"kpi_{location_id}_{kpi['id']}_{selected_input_month}"
                )
                input_data[kpi['id']] = value

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Uložit / Přepsat data", use_container_width=True, type="primary"):
                errors = []
                for kpi_id, value in input_data.items():
                    success, msg = db.add_monthly_kpi_data(selected_input_month, location_id, kpi_id, value)
                    if not success:
                        errors.append(msg)

                if errors:
                    st.session_state.save_message = f"❌ Chyby při ukládání: {', '.join(errors)}"
                    st.session_state.save_message_type = "error"
                else:
                    db.calculate_monthly_kpi_evaluation(selected_input_month, location_id)
                    st.session_state.save_message = f"✅ DATA ÚSPĚŠNĚ ULOŽENA pro {selected_location} - {format_month(selected_input_month)}"
                    st.session_state.save_message_type = "success"

                st.rerun()

        with col2:
            if st.button("🗑️ Smazat data tohoto měsíce", use_container_width=True, type="secondary"):
                if not existing_data.empty:
                    success, msg = db.delete_monthly_kpi_data(selected_input_month, location_id)
                    if success:
                        st.session_state.save_message = f"✅ DATA SMAZÁNA pro {selected_location} - {format_month(selected_input_month)}"
                        st.session_state.save_message_type = "success"
                    else:
                        st.session_state.save_message = f"❌ Chyba při mazání: {msg}"
                        st.session_state.save_message_type = "error"
                    st.rerun()
                else:
                    st.warning("Žádná data ke smazání")

        with col3:
            if st.button("🔄 Resetovat formulář", use_container_width=True):
                st.rerun()

    # TAB 2: Manual input for Departments with own KPI
    with tab2:
        st.markdown("### Zadejte data pro oddělení s vlastními KPI")

        # Get departments with own KPI
        depts_with_kpi = db.get_departments_with_vlastni_kpi()
        depts_with_kpi = depts_with_kpi[depts_with_kpi['ma_vlastni_kpi'] == 1]

        if depts_with_kpi.empty:
            st.warning("⚠️ Žádné oddělení nemá nastavené vlastní KPI. Nastavte to v Admin panelu.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                # Generate list of months from Jan 2023 to 3 months in future
                start_date = date(2023, 1, 1)
                end_date = date.today() + relativedelta(months=3)

                months_for_dept_input = []
                current = start_date
                while current <= end_date:
                    months_for_dept_input.append(current.strftime("%Y-%m"))
                    current += relativedelta(months=1)

                # Reverse so newest months are first
                months_for_dept_input = sorted(months_for_dept_input, reverse=True)

                month_options_dept = {format_month(m): m for m in months_for_dept_input}

                selected_formatted_dept = st.selectbox(
                    "Vyberte měsíc:",
                    options=list(month_options_dept.keys()),
                    index=0,
                    key="dept_input_month_picker"
                )
                selected_dept_month = month_options_dept[selected_formatted_dept]

            with col2:
                selected_department = st.selectbox("Oddělení:", depts_with_kpi['nazev'].tolist(), key="input_department")

            st.markdown("---")
            department_id = safe_int_id(depts_with_kpi[depts_with_kpi['nazev'] == selected_department]['id'].values[0])

            # Get existing data for this month/department OR show zeros
            existing_dept_data = db.get_monthly_department_kpi_data(selected_dept_month, department_id)

            kpi_defs = get_kpis()
            dept_input_data = {}

            st.markdown(f"**Zadávání dat pro: {selected_department} - {format_month(selected_dept_month)}**")

            if not existing_dept_data.empty:
                st.info("ℹ️ Zobrazena existující data - můžete je upravit a přepsat")
            else:
                st.info("ℹ️ Žádná data pro tento měsíc - zadejte nová data")

            for _, kpi in kpi_defs.iterrows():
                # Get existing value or default to 0
                existing_value = existing_dept_data[existing_dept_data['kpi_id'] == kpi['id']]['hodnota'].values
                default_val = float(existing_value[0]) if len(existing_value) > 0 else 0.0

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{kpi['nazev']}** - {kpi['popis']}")
                with col2:
                    value = st.number_input(
                        f"({kpi['jednotka']})",
                        value=default_val,
                        min_value=0.0,
                        step=0.1,
                        format="%.2f",
                        label_visibility="collapsed",
                        key=f"dept_kpi_{department_id}_{kpi['id']}_{selected_dept_month}"
                    )
                    dept_input_data[kpi['id']] = value

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("💾 Uložit / Přepsat data", use_container_width=True, type="primary", key="save_dept_data"):
                    errors = []
                    for kpi_id, value in dept_input_data.items():
                        success, msg = db.add_monthly_department_kpi_data(selected_dept_month, department_id, kpi_id, value)
                        if not success:
                            errors.append(msg)

                    if errors:
                        st.session_state.save_message = f"❌ Chyby při ukládání: {', '.join(errors)}"
                        st.session_state.save_message_type = "error"
                    else:
                        # Calculate bonuses and summaries
                        db.calculate_department_summary(selected_dept_month)
                        st.session_state.save_message = f"✅ DATA ÚSPĚŠNĚ ULOŽENA pro {selected_department} - {format_month(selected_dept_month)}"
                        st.session_state.save_message_type = "success"

                    st.rerun()

            with col2:
                if st.button("🗑️ Smazat data tohoto měsíce", use_container_width=True, type="secondary", key="delete_dept_data"):
                    if not existing_dept_data.empty:
                        # Delete all KPI data for this department/month
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                UPDATE monthly_department_kpi_data
                                SET status = 'DELETED'
                                WHERE mesic = ? AND department_id = ?
                            """, (selected_dept_month, department_id))
                            conn.commit()
                            conn.close()
                            st.session_state.save_message = f"✅ DATA SMAZÁNA pro {selected_department} - {format_month(selected_dept_month)}"
                            st.session_state.save_message_type = "success"
                        except Exception as e:
                            conn.close()
                            st.session_state.save_message = f"❌ Chyba při mazání: {str(e)}"
                            st.session_state.save_message_type = "error"

                        st.rerun()
                    else:
                        st.warning("Žádná data k smazání")

            with col3:
                if st.button("🔄 Resetovat formulář", use_container_width=True, key="reset_dept_form"):
                    st.rerun()

    # TAB 3: CSV Import
    with tab3:
        st.markdown("### CSV Import")

        if st.button("📥 Stáhnout šablonu CSV"):
            template = db.generate_import_template()
            st.download_button(
                label="Stáhnout",
                data=template.to_csv(index=False),
                file_name="KPI_template.csv",
                mime="text/csv"
            )

        uploaded_csv = st.file_uploader("Nahrát CSV:", type=['csv'])
        if uploaded_csv:
            csv_content = uploaded_csv.read().decode('utf-8')
            imported, errors = db.import_monthly_data_csv(csv_content)

            if imported > 0:
                st.session_state.save_message = f"✅ IMPORTOVÁNO {imported} záznamů"
                st.session_state.save_message_type = "success"

            if errors:
                st.warning(f"⚠️ {len(errors)} chyb:")
                for e in errors[:10]:
                    st.caption(e)

    # TAB 4: Excel Import
    with tab4:
        st.markdown("### Excel Import")

        if st.button("📥 Stáhnout šablonu Excel"):
            template = db.generate_import_template()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                template.to_excel(writer, sheet_name='KPI Data', index=False)
            output.seek(0)

            st.download_button(
                label="Stáhnout",
                data=output.getvalue(),
                file_name="KPI_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        uploaded_excel = st.file_uploader("Nahrát Excel:", type=['xlsx', 'xls'])
        if uploaded_excel:
            imported, errors = db.import_monthly_data_excel(uploaded_excel)

            if imported > 0:
                st.session_state.save_message = f"✅ IMPORTOVÁNO {imported} záznamů z Excelu"
                st.session_state.save_message_type = "success"

            if errors:
                st.warning(f"⚠️ {len(errors)} chyb:")
                for e in errors[:10]:
                    st.caption(e)


# ============================================================================
# MARKETING KPI - PLACEHOLDER
# ============================================================================
elif page == "Marketing KPI":
    st.title("📢 Marketing KPI")

    st.info("🚧 **V přípravě**\n\nTato sekce bude obsahovat:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Plánované metriky:")
        st.markdown("""
        - **Social Media**
          - Dosah příspěvků
          - Engagement rate
          - Nové sledující

        - **Online Marketing**
          - Web traffic
          - Konverzní poměr
          - CTR kampaní

        - **Brand Awareness**
          - Zmínky značky
          - Review skóre
          - Net Promoter Score
        """)

    with col2:
        st.markdown("### ⏱️ Časový plán:")
        st.markdown("""
        - **Q1 2025**: Návrh struktury
        - **Q2 2025**: Implementace sběru dat
        - **Q3 2025**: Spuštění sledování

        💡 Máte návrhy na metriky?
        Kontaktujte administrátora.
        """)

    st.markdown("---")
    st.warning("⚠️ Sekce je dočasně nedostupná. Vraťte se prosím později.")


# ============================================================================
# PAGE 5: ADMIN
# ============================================================================
elif page == "⚙️ Admin":
    st.title("⚙️ Admin Panel")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Oddělení", "Lokality", "Provozní", "KPI Definice", "KPI Hranice", "🔍 Debug"])

    # TAB 1: Departments
    with tab1:
        st.markdown("### Oddělení")
        depts = db.get_departments_with_vlastni_kpi()

        # Display departments with custom KPI indicator
        display_depts = depts.copy()
        display_depts['ma_vlastni_kpi'] = display_depts['ma_vlastni_kpi'].apply(lambda x: '✅ Ano' if x else '❌ Ne')
        st.dataframe(display_depts[['nazev', 'vedouci', 'ma_vlastni_kpi']],
                    use_container_width=True, hide_index=True,
                    column_config={
                        'nazev': 'Název',
                        'vedouci': 'Vedoucí',
                        'ma_vlastni_kpi': 'Vlastní KPI'
                    })

        st.markdown("---")
        st.markdown("#### ➕ Přidat oddělení")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_dept_name = st.text_input("Název:", key="new_dept_name")
        with col2:
            new_dept_vedouci = st.text_input("Vedoucí:", key="new_dept_vedouci")
        with col3:
            if st.button("➕ Přidat", key="add_dept_btn"):
                success, msg = db.add_department(new_dept_name, new_dept_vedouci)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.markdown("#### ⚙️ Nastavit vlastní KPI pro oddělení")
        st.info("📌 Pokud má oddělení vlastní KPI, můžete zadávat hodnoty ručně. Jinak se počítá průměr z lokalit.")

        if len(depts) > 0:
            # Create a form with checkboxes for each department
            st.markdown("**Zaškrtněte oddělení s vlastními KPI:**")

            # Store checkbox states
            vlastni_kpi_changes = {}

            # Display each department with checkbox
            for idx, dept in depts.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{dept['nazev']}** ({dept['vedouci']})")
                with col2:
                    has_vlastni = st.checkbox(
                        "Vlastní KPI",
                        value=bool(dept['ma_vlastni_kpi']),
                        key=f"dept_vlastni_kpi_{dept['id']}",
                        label_visibility="collapsed"
                    )
                    vlastni_kpi_changes[dept['id']] = has_vlastni

            st.markdown("---")
            if st.button("💾 Uložit všechna nastavení", type="primary", key="save_all_vlastni_kpi_btn"):
                success_count = 0
                error_count = 0
                for dept_id, has_vlastni in vlastni_kpi_changes.items():
                    success, msg = db.update_department_vlastni_kpi(dept_id, has_vlastni)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1

                if error_count == 0:
                    st.success(f"✅ Nastavení uloženo pro {success_count} oddělení")
                    st.rerun()
                else:
                    st.error(f"⚠️ Uloženo: {success_count}, Chyby: {error_count}")
        else:
            st.warning("Žádná oddělení k nastavení")

        st.markdown("---")
        st.markdown("#### 🧹 Vyčistit duplikáty")
        st.warning("⚠️ Použijte pokud vidíte duplicitní záznamy (stejné oddělení/lokality/provozní více krát)")
        if st.button("🧹 Vyčistit databázi", type="secondary", key="cleanup_db_btn"):
            success, msg = db.cleanup_duplicates()
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")
        st.markdown("#### 🗑️ Smazat oddělení")
        col1, col2 = st.columns(2)
        with col1:
            if len(depts) > 0:
                del_dept = st.selectbox("Vyberte oddělení ke smazání:", depts['nazev'].tolist(), key="del_dept_select")
                del_dept_id = safe_int_id(depts[depts['nazev'] == del_dept]['id'].values[0])
        with col2:
            if st.button("🗑️ Smazat", key="del_dept_btn"):
                success, msg = db.delete_department(del_dept_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # TAB 2: Locations
    with tab2:
        st.markdown("### Lokality")
        locs = get_locs()
        st.dataframe(locs[['nazev', 'department']], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### ➕ Přidat lokalitu")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_loc_name = st.text_input("Název lokality:", key="new_loc_name")
        with col2:
            depts = db.get_departments()
            new_loc_dept = st.selectbox("Oddělení:", depts['nazev'].tolist(), key="add_loc_dept")
            dept_id = safe_int_id(depts[depts['nazev'] == new_loc_dept]['id'].values[0])
        with col3:
            if st.button("➕ Přidat lokalitu", key="add_loc_btn"):
                success, msg = db.add_location(new_loc_name, dept_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.markdown("#### 🔄 Přeřadit lokalitu do jiného oddělení")
        col1, col2, col3 = st.columns(3)
        with col1:
            if len(locs) > 0:
                loc_to_move = st.selectbox("Lokalita:", locs['nazev'].tolist(), key="move_loc")
                loc_id = safe_int_id(locs[locs['nazev'] == loc_to_move]['id'].values[0])
        with col2:
            new_dept = st.selectbox("Nové oddělení:", depts['nazev'].tolist(), key="move_dept")
            new_dept_id = safe_int_id(depts[depts['nazev'] == new_dept]['id'].values[0])
        with col3:
            if st.button("🔄 Přeřadit", key="move_loc_btn"):
                success, msg = db.update_location_department(loc_id, new_dept_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.markdown("#### 🗑️ Smazat lokalitu")
        col1, col2 = st.columns(2)
        with col1:
            if len(locs) > 0:
                del_loc = st.selectbox("Vyberte lokalitu ke smazání:", locs['nazev'].tolist(), key="del_loc_select")
                del_loc_id = safe_int_id(locs[locs['nazev'] == del_loc]['id'].values[0])
        with col2:
            if st.button("🗑️ Smazat", key="del_loc_btn"):
                success, msg = db.delete_location(del_loc_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # TAB 3: Operational Managers
    with tab3:
        st.markdown("### Provozní")
        mgrs = get_managers()
        st.dataframe(mgrs[['jmeno', 'department']], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### ➕ Přidat provozního")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_mgr_name = st.text_input("Jméno provozního:", key="new_mgr_name")
        with col2:
            depts = db.get_departments()
            new_mgr_dept = st.selectbox("Oddělení:", depts['nazev'].tolist(), key="add_mgr_dept")
            dept_id = safe_int_id(depts[depts['nazev'] == new_mgr_dept]['id'].values[0])
        with col3:
            if st.button("➕ Přidat provozního", key="add_mgr_btn"):
                success, msg, new_mgr_id = db.add_operational_manager(new_mgr_name, dept_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.markdown("#### 🎯 Nastavit KPI pro provozního")

        if len(mgrs) > 0:
            selected_mgr = st.selectbox(
                "Vyberte provozního:",
                mgrs['jmeno'].tolist(),
                key="mgr_kpi_select"
            )
            selected_mgr_id = safe_int_id(mgrs[mgrs['jmeno'] == selected_mgr]['id'].values[0])

            # Get all KPIs
            all_kpis = db.get_all_kpi_definitions()

            if not all_kpis.empty:
                # Get currently assigned KPIs
                assigned_kpis = db.get_manager_kpis(selected_mgr_id)
                assigned_kpi_ids = assigned_kpis['id'].tolist() if not assigned_kpis.empty else []

                st.markdown("**Vyberte KPI která se budou sledovat:**")

                # Create checkboxes for each KPI
                selected_kpi_ids = []
                for _, kpi in all_kpis.iterrows():
                    kpi_id = safe_int_id(kpi['id'])
                    is_checked = kpi_id in assigned_kpi_ids

                    if st.checkbox(
                        f"{kpi['nazev']} ({kpi['jednotka']}) - {kpi['popis'][:50]}..." if len(str(kpi['popis'])) > 50 else f"{kpi['nazev']} ({kpi['jednotka']})",
                        value=is_checked,
                        key=f"mgr_kpi_{selected_mgr_id}_{kpi_id}"
                    ):
                        selected_kpi_ids.append(kpi_id)

                if st.button("💾 Uložit výběr KPI", key="save_mgr_kpi_btn", type="primary"):
                    success, msg = db.set_manager_kpis(selected_mgr_id, selected_kpi_ids)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

                # Show current assignments
                if not assigned_kpis.empty:
                    st.info(f"✅ Aktuálně přiřazeno: {', '.join(assigned_kpis['nazev'].tolist())}")
                else:
                    st.warning("⚠️ Žádná KPI nejsou přiřazena - vyberte aspoň jedno")
            else:
                st.warning("⚠️ Nejdříve vytvořte KPI v tabu 'KPI Definice'")
        else:
            st.info("Nejdříve přidejte provozního")

        st.markdown("---")
        st.markdown("#### 🗑️ Smazat provozního")
        col1, col2 = st.columns(2)
        with col1:
            if len(mgrs) > 0:
                del_mgr = st.selectbox("Vyberte provozního ke smazání:", mgrs['jmeno'].tolist(), key="del_mgr_select")
                del_mgr_id = safe_int_id(mgrs[mgrs['jmeno'] == del_mgr]['id'].values[0])
        with col2:
            if st.button("🗑️ Smazat", key="del_mgr_btn"):
                success, msg = db.delete_operational_manager(del_mgr_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # TAB 4: KPI Definitions
    with tab4:
        st.markdown("### KPI Definice")
        kpis = db.get_all_kpi_definitions()
        if not kpis.empty:
            st.dataframe(kpis[['nazev', 'popis', 'jednotka', 'typ_vypoctu', 'poradi']],
                        use_container_width=True, hide_index=True)
        else:
            st.info("Zatím nejsou definována žádná KPI")

        st.markdown("---")
        st.markdown("#### ➕ Přidat nové KPI")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_kpi_nazev = st.text_input("Název KPI:", key="new_kpi_nazev")
        with col2:
            new_kpi_jednotka = st.text_input("Jednotka:", key="new_kpi_jednotka", help="Např. %, Kč, ks")
        with col3:
            new_kpi_typ = st.selectbox("Typ výpočtu:", ["vyšší = lepší", "nižší = lepší", "cílová hodnota"], key="new_kpi_typ")
        with col4:
            new_kpi_poradi = st.number_input("Pořadí:", min_value=1, value=1, key="new_kpi_poradi")

        new_kpi_popis = st.text_area("Popis KPI:", key="new_kpi_popis")

        if st.button("➕ Přidat KPI", key="add_kpi_btn"):
            success, msg, kpi_id = db.add_kpi_definition(new_kpi_nazev, new_kpi_popis,
                                                         new_kpi_jednotka, new_kpi_typ, new_kpi_poradi)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")
        st.markdown("#### ✏️ Upravit KPI")
        if not kpis.empty:
            col1, col2 = st.columns(2)
            with col1:
                edit_kpi = st.selectbox("Vyberte KPI k úpravě:", kpis['nazev'].tolist(), key="edit_kpi_select")
                edit_kpi_id = safe_int_id(kpis[kpis['nazev'] == edit_kpi]['id'].values[0])
                edit_kpi_data = kpis[kpis['id'] == edit_kpi_id].iloc[0]

            with col2:
                st.caption(f"Úprava KPI: **{edit_kpi}**")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                edit_kpi_nazev = st.text_input("Nový název:", value=edit_kpi_data['nazev'], key="edit_kpi_nazev")
            with col2:
                edit_kpi_jednotka = st.text_input("Jednotka:", value=edit_kpi_data['jednotka'] or "", key="edit_kpi_jednotka")
            with col3:
                typ_options = ["vyšší = lepší", "nižší = lepší", "cílová hodnota"]
                current_typ_idx = typ_options.index(edit_kpi_data['typ_vypoctu']) if edit_kpi_data['typ_vypoctu'] in typ_options else 0
                edit_kpi_typ = st.selectbox("Typ výpočtu:", typ_options, index=current_typ_idx, key="edit_kpi_typ")
            with col4:
                edit_kpi_poradi = st.number_input("Pořadí:", min_value=1, value=int(edit_kpi_data['poradi'] or 1), key="edit_kpi_poradi")

            edit_kpi_popis = st.text_area("Popis:", value=edit_kpi_data['popis'] or "", key="edit_kpi_popis")

            if st.button("✏️ Uložit změny", key="save_kpi_btn"):
                success, msg = db.update_kpi_definition(edit_kpi_id, edit_kpi_nazev, edit_kpi_popis,
                                                       edit_kpi_jednotka, edit_kpi_typ, edit_kpi_poradi)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.markdown("#### 🗑️ Smazat KPI")
        if not kpis.empty:
            col1, col2 = st.columns(2)
            with col1:
                del_kpi = st.selectbox("Vyberte KPI ke smazání:", kpis['nazev'].tolist(), key="del_kpi_select")
                del_kpi_id = safe_int_id(kpis[kpis['nazev'] == del_kpi]['id'].values[0])
            with col2:
                if st.button("🗑️ Smazat KPI", key="del_kpi_btn"):
                    success, msg = db.delete_kpi_definition(del_kpi_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # TAB 5: KPI Thresholds
    with tab5:
        st.markdown("### ⚙️ KPI Hranice a Bonusy")
        st.info("💡 Můžete přidat více hranic pro jedno KPI (např. ≥85% = 10%, ≥95% = 20%)")

        # Select KPI to manage thresholds
        kpis = db.get_all_kpi_definitions()
        if kpis.empty:
            st.warning("⚠️ Nejdříve musíte vytvořit KPI definice v předchozím tabu")
        else:
            selected_kpi_name = st.selectbox("🎯 Vyberte KPI:", kpis['nazev'].tolist(), key="threshold_kpi_select")
            selected_kpi_id = safe_int_id(kpis[kpis['nazev'] == selected_kpi_name]['id'].values[0])

            selected_kpi_jednotka = kpis[kpis['id'] == selected_kpi_id]['jednotka'].values[0]

            st.markdown(f"#### 📋 Hranice pro: **{selected_kpi_name}** ({selected_kpi_jednotka})")

            # Debug info
            with st.expander("🔍 Debug Info"):
                st.code(f"KPI: {selected_kpi_name}\nKPI ID: {selected_kpi_id} (typ: {type(selected_kpi_id).__name__})")
                # Verify KPI exists
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, nazev, aktivni FROM kpi_definitions WHERE id = ?", (selected_kpi_id,))
                kpi_check = cursor.fetchone()
                if kpi_check:
                    st.success(f"✅ KPI nalezeno v DB: {kpi_check['nazev']} (aktivni={kpi_check['aktivni']})")
                else:
                    st.error(f"❌ KPI ID {selected_kpi_id} NEEXISTUJE!")

                # Check existing thresholds
                cursor.execute("SELECT id, kpi_id, operator, min_hodnota, bonus_procento FROM kpi_thresholds WHERE kpi_id = ?", (selected_kpi_id,))
                raw_thresholds = cursor.fetchall()
                if raw_thresholds:
                    st.write(f"Hranice v DB: {len(raw_thresholds)}")
                    for t in raw_thresholds[:3]:
                        st.text(f"  ID {t['id']}: kpi_id={t['kpi_id']} (typ={type(t['kpi_id']).__name__}), {t['operator']} {t['min_hodnota']} → {t['bonus_procento']}%")
                else:
                    st.warning("Žádné hranice v DB")
                conn.close()

            # Display existing thresholds
            thresholds = db.get_kpi_thresholds(selected_kpi_id)
            if not thresholds.empty:
                st.success(f"✅ Nalezeno {len(thresholds)} hranic pro toto KPI")
                display_cols = ['min_hodnota', 'max_hodnota', 'operator', 'bonus_procento', 'popis', 'poradi']
                st.dataframe(thresholds[display_cols], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Zatím nejsou definovány hranice pro toto KPI - přidejte první hranici níže")

            st.markdown("---")
            st.markdown("#### ➕ Přidat novou hranici")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                new_threshold_operator = st.selectbox("Operátor:", ["≥", "≤", ">", "<", "mezi"], key="new_threshold_op")
            with col2:
                new_threshold_min = st.number_input("Min hodnota:", value=0.0, key="new_threshold_min")
            with col3:
                if new_threshold_operator == "mezi":
                    new_threshold_max = st.number_input("Max hodnota:", value=100.0, key="new_threshold_max")
                else:
                    new_threshold_max = None
                    st.caption("(nepotřebné)")
            with col4:
                new_threshold_bonus = st.number_input("Bonus %:", min_value=0.0, max_value=100.0, value=10.0, key="new_threshold_bonus")

            col1, col2 = st.columns(2)
            with col1:
                new_threshold_popis = st.text_input("Popis hranice:", key="new_threshold_popis")
            with col2:
                new_threshold_poradi = st.number_input("Pořadí:", min_value=1, value=1, key="new_threshold_poradi")

            if st.button("➕ Přidat hranici", key="add_threshold_btn"):
                success, msg, threshold_id = db.add_kpi_threshold(
                    selected_kpi_id, new_threshold_operator, new_threshold_bonus,
                    new_threshold_min, new_threshold_max, new_threshold_popis, new_threshold_poradi
                )
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown("---")
            if not thresholds.empty:
                st.markdown("#### ✏️ Upravit existující hranici")
                col1, col2 = st.columns(2)
                with col1:
                    threshold_edit_descriptions = [f"{row['operator']} {row['min_hodnota']}" +
                                                  (f" - {row['max_hodnota']}" if pd.notna(row['max_hodnota']) else "") +
                                                  f" → {row['bonus_procento']}%"
                                                  for _, row in thresholds.iterrows()]
                    edit_threshold_idx = st.selectbox("Vyberte hranici k úpravě:",
                                                     range(len(threshold_edit_descriptions)),
                                                     format_func=lambda x: threshold_edit_descriptions[x],
                                                     key="edit_threshold_select")
                    edit_threshold_data = thresholds.iloc[edit_threshold_idx]
                    edit_threshold_id = edit_threshold_data['id']

                with col2:
                    st.caption(f"Úprava hranice: **{threshold_edit_descriptions[edit_threshold_idx]}**")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    edit_op = st.selectbox("Operátor:", ["≥", "≤", ">", "<", "mezi"],
                                          index=["≥", "≤", ">", "<", "mezi"].index(edit_threshold_data['operator']) if edit_threshold_data['operator'] in ["≥", "≤", ">", "<", "mezi"] else 0,
                                          key="edit_threshold_op")
                with col2:
                    edit_min = st.number_input("Min hodnota:", value=float(edit_threshold_data['min_hodnota'] or 0.0), key="edit_threshold_min")
                with col3:
                    if edit_op == "mezi":
                        edit_max = st.number_input("Max hodnota:", value=float(edit_threshold_data['max_hodnota'] or 100.0), key="edit_threshold_max")
                    else:
                        edit_max = None
                        st.caption(f"Max: {edit_threshold_data['max_hodnota'] if pd.notna(edit_threshold_data['max_hodnota']) else 'N/A'}")
                with col4:
                    edit_bonus = st.number_input("Bonus %:", min_value=0.0, max_value=100.0,
                                                 value=float(edit_threshold_data['bonus_procento']), key="edit_threshold_bonus")

                col1, col2 = st.columns(2)
                with col1:
                    edit_desc = st.text_input("Popis:", value=edit_threshold_data['popis'] or "", key="edit_threshold_popis")
                with col2:
                    edit_poradi = st.number_input("Pořadí:", min_value=1, value=int(edit_threshold_data['poradi'] or 1), key="edit_threshold_poradi")

                if st.button("✏️ Uložit změny hranice", key="save_threshold_btn"):
                    success, msg = db.update_kpi_threshold(edit_threshold_id, edit_min, edit_max, edit_op, edit_bonus, edit_desc, edit_poradi)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("---")
            if not thresholds.empty:
                st.markdown("#### 🗑️ Smazat hranici")
                col1, col2 = st.columns(2)
                with col1:
                    threshold_descriptions = [f"{row['operator']} {row['min_hodnota']}" +
                                            (f" - {row['max_hodnota']}" if pd.notna(row['max_hodnota']) else "") +
                                            f" → {row['bonus_procento']}%"
                                            for _, row in thresholds.iterrows()]
                    del_threshold_idx = st.selectbox("Vyberte hranici ke smazání:",
                                                    range(len(threshold_descriptions)),
                                                    format_func=lambda x: threshold_descriptions[x],
                                                    key="del_threshold_select")
                    del_threshold_id = thresholds.iloc[del_threshold_idx]['id']
                with col2:
                    if st.button("🗑️ Smazat hranici", key="del_threshold_btn"):
                        success, msg = db.delete_kpi_threshold(del_threshold_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # TAB 6: Debug & Diagnostics
    with tab6:
        st.markdown("### 🔍 Diagnostika")

        # Get database statistics
        conn = db.get_connection()
        cursor = conn.cursor()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📁 Základní tabulky")
            cursor.execute("SELECT COUNT(*) FROM departments WHERE aktivni = 1")
            dept_count = cursor.fetchone()[0]
            st.metric("Oddělení", dept_count)

            cursor.execute("SELECT COUNT(*) FROM locations WHERE aktivni = 1")
            loc_count = cursor.fetchone()[0]
            st.metric("Lokality", loc_count)

            cursor.execute("SELECT COUNT(*) FROM operational_managers WHERE aktivni = 1")
            mgr_count = cursor.fetchone()[0]
            st.metric("Provozní", mgr_count)

        with col2:
            st.markdown("#### 📊 KPI")
            cursor.execute("SELECT COUNT(*) FROM kpi_definitions WHERE aktivni = 1")
            kpi_count = cursor.fetchone()[0]
            st.metric("KPI Definice", kpi_count)

            cursor.execute("SELECT COUNT(*) FROM kpi_thresholds")
            threshold_count = cursor.fetchone()[0]
            st.metric("KPI Hranice", threshold_count)

        with col3:
            st.markdown("#### 💾 Data")
            cursor.execute("SELECT COUNT(*) FROM monthly_kpi_data WHERE status = 'ACTIVE'")
            data_count = cursor.fetchone()[0]
            st.metric("Měsíční data (lokality)", data_count)

            cursor.execute("SELECT COUNT(*) FROM monthly_department_kpi_data WHERE status = 'ACTIVE'")
            dept_data_count = cursor.fetchone()[0]
            st.metric("Měsíční data (oddělení)", dept_data_count)

            cursor.execute("SELECT COUNT(*) FROM monthly_kpi_evaluation")
            eval_count = cursor.fetchone()[0]
            if eval_count == 0 and data_count > 0:
                st.metric("⚠️ Vyhodnocení bonusů", eval_count, delta="Chybí výpočet!", delta_color="off")
            else:
                st.metric("Vyhodnocení bonusů", eval_count)

        st.markdown("---")
        st.markdown("#### 📋 Ukázková Data")

        # Show sample data
        st.markdown("**Oddělení:**")
        cursor.execute("SELECT nazev, vedouci, ma_vlastni_kpi FROM departments WHERE aktivni = 1 LIMIT 5")
        depts_data = cursor.fetchall()
        if depts_data:
            st.write(pd.DataFrame(depts_data, columns=['Název', 'Vedoucí', 'Vlastní KPI']))
        else:
            st.warning("⚠️ Žádná oddělení!")

        st.markdown("**Lokality:**")
        cursor.execute("""
            SELECT l.nazev, d.nazev as oddeleni
            FROM locations l
            JOIN departments d ON l.department_id = d.id
            WHERE l.aktivni = 1
            LIMIT 5
        """)
        locs_data = cursor.fetchall()
        if locs_data:
            st.write(pd.DataFrame(locs_data, columns=['Lokalita', 'Oddělení']))
        else:
            st.warning("⚠️ Žádné lokality!")

        st.markdown("**KPI Definice:**")
        cursor.execute("SELECT nazev, jednotka, typ_vypoctu FROM kpi_definitions WHERE aktivni = 1 LIMIT 5")
        kpis_data = cursor.fetchall()
        if kpis_data:
            st.write(pd.DataFrame(kpis_data, columns=['Název', 'Jednotka', 'Typ']))
        else:
            st.warning("⚠️ Žádná KPI!")

        st.markdown("**Měsíční Data (RAW - bez JOIN):**")
        cursor.execute("""
            SELECT id, mesic, location_id, kpi_id, hodnota, status
            FROM monthly_kpi_data
            WHERE status = 'ACTIVE'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        raw_data = cursor.fetchall()
        if raw_data:
            st.write(pd.DataFrame(raw_data, columns=['ID', 'Měsíc', 'Location ID', 'KPI ID', 'Hodnota', 'Status']))

            # Check if those IDs exist in related tables
            st.markdown("**🔍 Kontrola foreign keys:**")
            for row in raw_data[:3]:  # Check first 3 records
                record_id, mesic, loc_id, kpi_id, hodnota, status = row

                # Check if location exists and is active
                cursor.execute("SELECT id, nazev, aktivni FROM locations WHERE id = ?", (loc_id,))
                loc_result = cursor.fetchone()

                # Check if KPI exists and is active
                cursor.execute("SELECT id, nazev, aktivni FROM kpi_definitions WHERE id = ?", (kpi_id,))
                kpi_result = cursor.fetchone()

                st.text(f"Záznam #{record_id} ({mesic}):")
                if loc_result:
                    st.text(f"  ✓ Lokalita ID {loc_id}: {loc_result[1]} (aktivni={loc_result[2]})")
                else:
                    st.error(f"  ✗ Lokalita ID {loc_id} NEEXISTUJE!")

                if kpi_result:
                    st.text(f"  ✓ KPI ID {kpi_id}: {kpi_result[1]} (aktivni={kpi_result[2]})")
                else:
                    st.error(f"  ✗ KPI ID {kpi_id} NEEXISTUJE!")
        else:
            st.warning("⚠️ Žádná měsíční data!")

        st.markdown("---")
        st.markdown("**Měsíční Data (s JOIN - pro porovnání):**")
        cursor.execute("""
            SELECT m.id, m.mesic, l.nazev as lokalita, k.nazev as kpi, m.hodnota
            FROM monthly_kpi_data m
            JOIN locations l ON m.location_id = l.id AND l.aktivni = 1
            JOIN kpi_definitions k ON m.kpi_id = k.id AND k.aktivni = 1
            WHERE m.status = 'ACTIVE'
            ORDER BY m.created_at DESC
            LIMIT 10
        """)
        monthly_data = cursor.fetchall()
        if monthly_data:
            st.write(pd.DataFrame(monthly_data, columns=['ID', 'Měsíc', 'Lokalita', 'KPI', 'Hodnota']))
        else:
            st.warning("⚠️ JOIN nevrátil žádná data! Problém s foreign keys nebo aktivni=0")

        st.markdown("---")
        st.markdown("#### 🔍 Analýza problémů")

        problems = []
        warnings = []

        # Check if thresholds exist
        cursor.execute("SELECT COUNT(*) FROM kpi_thresholds")
        threshold_count = cursor.fetchone()[0]
        if threshold_count == 0:
            problems.append("❌ **Žádné KPI hranice!** Bez hranic se nemohou počítat bonusy.")
            st.error("⚠️ KRITICKÝ PROBLÉM: Nejsou definované hranice pro KPI! Přejděte na tab 'KPI Hranice' a nastavte pravidla pro bonusy.")
        else:
            st.success(f"✅ Nalezeno {threshold_count} hranic pro výpočet bonusů")

        # Check if data needs recalculation
        cursor.execute("SELECT COUNT(*) FROM monthly_kpi_data WHERE status = 'ACTIVE'")
        data_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM monthly_kpi_evaluation")
        eval_count = cursor.fetchone()[0]

        if data_count > 0 and eval_count == 0:
            problems.append("❌ **Chybí vyhodnocení!** Máte data ale nebyla spočítána.")
            st.error("⚠️ DATA NEBYLA VYHODNOCENA! Klikněte na tlačítko níže pro přepočítání.")
        elif data_count > eval_count:
            warnings.append(f"⚠️ Máte více dat ({data_count}) než vyhodnocení ({eval_count}). Doporučujeme přepočítat.")
            st.warning(f"⚠️ Počet dat ({data_count}) neodpovídá počtu vyhodnocení ({eval_count}). Přepočítejte bonusy.")

        st.markdown("---")
        st.markdown("#### 🔧 Opravy databáze")

        # Check for orphaned records
        cursor.execute("""
            SELECT DISTINCT m.location_id
            FROM monthly_kpi_data m
            WHERE m.location_id NOT IN (SELECT id FROM locations)
            LIMIT 10
        """)
        orphaned_locations = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT m.kpi_id
            FROM monthly_kpi_data m
            WHERE m.kpi_id NOT IN (SELECT id FROM kpi_definitions)
            LIMIT 10
        """)
        orphaned_kpis = cursor.fetchall()

        if orphaned_locations or orphaned_kpis:
            st.error("🚨 PROBLÉM: Nalezeny osiřelé záznamy!")
            if orphaned_locations:
                loc_ids = [str(row[0]) for row in orphaned_locations]
                st.warning(f"⚠️ Měsíční data odkazují na neexistující lokality: {', '.join(loc_ids)}")
            if orphaned_kpis:
                kpi_ids = [str(row[0]) for row in orphaned_kpis]
                st.warning(f"⚠️ Měsíční data odkazují na neexistující KPI: {', '.join(kpi_ids)}")
            st.info("💡 Použijte tlačítko 'Vyčistit osiřelé záznamy' níže")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔧 OPRAVIT BINÁRNÍ ID", key="fix_binary_btn", type="secondary"):
                with st.spinner("Opravuji datové typy..."):
                    success, msg = db.fix_binary_ids()
                if success:
                    st.success(f"✅ {msg}")
                    st.info("💡 Nyní klikněte na 'Přepočítat bonusy' níže")
                else:
                    st.error(f"❌ {msg}")

        with col2:
            if st.button("🧹 VYČISTIT OSIŘELÉ", key="clean_orphaned_btn", type="secondary"):
                with st.spinner("Čistím osiřelé záznamy..."):
                    # Delete records with non-existent foreign keys
                    cursor.execute("""
                        DELETE FROM monthly_kpi_data
                        WHERE location_id NOT IN (SELECT id FROM locations)
                        OR kpi_id NOT IN (SELECT id FROM kpi_definitions)
                    """)
                    conn.commit()
                    deleted = cursor.rowcount
                st.success(f"✅ Smazáno {deleted} osiřelých záznamů")
                st.rerun()

        with col3:
            st.caption("🔧 Tlačítka pro opravy:")
            st.caption("• Binární ID → Integer")
            st.caption("• Osiřelé → Smazat")

        st.markdown("---")
        st.markdown("#### 🔄 Akce")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("♻️ PŘEPOČÍTAT VŠECHNY BONUSY", key="recalc_all_btn", type="primary"):
                months = db.get_all_months_with_data()
                if months:
                    with st.spinner("Počítám bonusy..."):
                        for month in months:
                            db.calculate_monthly_kpi_evaluation(month)
                            db.calculate_department_summary(month)
                    st.success(f"✅ Úspěšně přepočítáno {len(months)} měsíců!")
                    st.rerun()
                else:
                    st.warning("Žádná data k přepočítání")

        with col2:
            st.caption("💡 Použijte pokud:")
            st.caption("• Se nezobrazují bonusy")
            st.caption("• Změnili jste hranice KPI")
            st.caption("• Přidali jste nová data")

        conn.close()
