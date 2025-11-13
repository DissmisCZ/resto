# RESTO v3.1 - KPI Dashboard Bouda Burgers

**Moderní webová aplikace pro správu měsíčních KPI v restauracích**

![Version](https://img.shields.io/badge/version-3.1-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-orange)
![Status](https://img.shields.io/badge/status-production-brightgreen)

---

## 📋 Obsah

1. [O projektu](#o-projektu)
2. [Nové ve v3.1](#nové-ve-v31)
3. [Instalace](#instalace)
4. [Spuštění](#spuštění)
5. [Funkce](#funkce)
6. [Autentizace](#autentizace)
7. [Struktura dat](#struktura-dat)
8. [Troubleshooting](#troubleshooting)

---

## O projektu

RESTO v3.1 je **kompletně nezávislá** aplikace pro správu operačních KPI restaurací Bouda Burgers s moderním designem a pokročilými funkcemi.

### Klíčové rysy:
- ✅ **Autentizace** - zabezpečené přihlášení
- ✅ **Light/Dark Mode** - přepínání barevných režimů
- ✅ **Moderní UI** - gradient nadpisy, karty s animacemi
- ✅ **Logo Bouda Burgers** - branding na login i v sidebaru
- ✅ **Měsíční KPI tracking**
- ✅ **Oddělení** (Matějovo, Thomasovo, Michaelovo)
- ✅ **Lokality** (Mercury, OC4Dvory, Bouda, Bistro)
- ✅ **Provozní manažeři** s přiřazením KPI
- ✅ **Dynamické KPI hranice** s bonusovým systémem
- ✅ **Porovnání měsíců** - trend analýza
- ✅ **Kompaktní sidebar** - vejde se na jeden screen
- ✅ **Import/Export** CSV data
- ✅ **Marketing KPI** placeholder

---

## Nové ve v3.1

### 🔐 Autentizace
- Zabezpečené přihlášení s heslem
- Konfigurace hesla přes `.streamlit/secrets.toml`
- Session management

### 🎨 Moderní Design
- **Light/Dark Mode** - přepínací tlačítka ☀️ | 🌙
- Gradient nadpisy (purple/violet)
- Karty s hover efekty a animacemi
- Shadows a smooth transitions
- Bílé pozadí (light) / Tmavé pozadí (dark)

### 🏢 Logo & Branding
- Logo Bouda Burgers na login page (180px)
- Logo v sidebaru (45px)
- Konzistentní branding napříč aplikací

### 📱 Kompaktní Sidebar
- Větší text (15px) pro lepší čitelnost
- Radio buttony zarovnané s textem (18px × 18px)
- Menší mezery (0.15rem gap)
- Vše se vejde na jeden screen

### 🎯 KPI Management
- **Přiřazení KPI k manažerům** - checkboxy pro výběr
- **Dynamické hranice KPI** - přidávání/editace/mazání
- **Bonusový systém** - procenta podle splnění

### 📊 Pokročilé Funkce
- **Porovnání měsíců** - selectbox pro výběr srovnávacího měsíce
- **Marketing KPI** - placeholder pro budoucí rozšíření
- **Binary ID fix** - opraveny všechny databázové ID konflikty

---

## Instalace

### Systemové Požadavky
- Windows 7+ / Linux / macOS
- Python 3.8+ (z https://python.org)

### Krok 1: Instalace Python Balíků

**Windows:**
```bash
install_dependencies.bat
```

**Linux/macOS:**
```bash
pip install -r requirements.txt
```

---

## 🌐 Cloud Deployment (NOVÉ v3.1!)

### Streamlit Cloud + Supabase PostgreSQL

RESTO v3.1 nyní podporuje **perzistentní cloudovou databázi** s Supabase!

**Výhody:**
- ✅ **Perzistence** - Data přetrvávají i po restartu aplikace
- ✅ **Zdarma** - 500MB PostgreSQL databáze zdarma
- ✅ **Zálohování** - Automatické denní zálohy
- ✅ **Přístup odkudkoli** - Aplikace dostupná 24/7 na webu

**Jak na to:**
1. Přečtěte si **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** - kompletní návod
2. Vytvořte Supabase projekt (2 minuty)
3. Migrujte data pomocí `migrate_sqlite_to_postgres.py`
4. Nasaďte na Streamlit Cloud

**Databázové možnosti:**
- **Lokální**: SQLite (`database.py`) - pro vývoj a testování
- **Cloud**: PostgreSQL (`database_postgres.py`) - pro produkci na Streamlit Cloud

---

## Spuštění

### Lokální Spuštění (Production)

**Windows:**
```bash
run_resto_cz.bat
```

**Linux/macOS:**
```bash
streamlit run app_cz.py
```

Aplikace se otevře na: http://localhost:8501

### Testovací Spuštění (Fresh Database)
```bash
run_resto_test.bat  # Windows
```

### Vypnutí Aplikace
```bash
kill_resto.bat  # Windows
```
Nebo v terminálu: `Ctrl+C`

---

## Funkce

### 🔐 Login Page
- Moderní design s logem Bouda Burgers
- Bílé pozadí, čistý layout
- Zabezpečené přihlášení
- Demo heslo: `resto2025` (změnit v produkci!)

### 📊 Přehled
- Měsíční shrnutí všech oddělení
- Metriky bonusů (průměr napříč lokalitami)
- Expandery s detaily KPI
- Barevné karty (zelená/oranžová/červená)
- Tlačítko "Přepočítat bonusy"

### 📈 Detail
- Filtrování dle oddělení
- Filtrování dle KPI
- Porovnávání lokalit
- Grafické vizualizace

### 👥 Porovnání
- Tabulka všech oddělení
- Průměrné bonusy
- Počet lokalit
- Graf porovnání

### 📝 Zadání
**Tab: Ruční vstup**
- Vybrat měsíc (YYYY-MM)
- Vybrat lokalitu
- Vyplnit KPI hodnoty
- Uložit data

**Tab: Import CSV**
- Stáhnout šablonu
- Vyplnit v Excelu
- Nahrát CSV zpět

### ⚙️ Admin
**Tab: Oddělení**
- Přehled oddělení
- Přehled lokalit

**Tab: Provozní**
- Přehled provozních manažerů
- **Přiřazení KPI** - checkboxy pro výběr KPI na manažera
- Správa provozních

**Tab: KPI Nastavení**
- Přehled KPI definic
- **Hranice KPI** - přidání/editace/mazání hraničních hodnot
- Bonusová procenta podle splnění

### 🚧 Marketing KPI
- Placeholder pro budoucí rozšíření
- Sekce v přípravě

---

## Autentizace

### Lokální Nastavení

Vytvořte soubor: `.streamlit/secrets.toml`

```toml
[passwords]
admin = "VaseSilneHeslo123!"
```

### Streamlit Cloud Nastavení

1. Jděte na: https://share.streamlit.io
2. Najděte svou aplikaci → **⋮** (3 tečky)
3. **Settings** → **Secrets**
4. Přidejte:

```toml
[passwords]
admin = "VaseSilneHeslo123!"
```

5. **Save** → Aplikace se automaticky restartuje

### Doporučení pro Heslo
✅ Minimálně 12 znaků
✅ Kombinace velkých/malých písmen
✅ Číslice
✅ Speciální znaky (!@#$%^&*)

**Příklady dobrých hesel:**
- `Resto@2025!Secure`
- `BoudaBurgers#KPI`
- `MySecure!Pass123`

❌ **Špatné heslo:** `123456`, `resto`, `password`

---

## Struktura Dat

### Hierarchie
```
ODDĚLENÍ
└── LOKALITY
    └── PROVOZNÍ MANAŽEŘI
        └── KPI (10 metrik)
            └── HRANICE (min/max/bonus)
```

### 10 KPI Metriky

| # | KPI | Jednotka | Cíl |
|---|-----|----------|-----|
| 1 | Audit | % | ≥85% |
| 2 | Hodnocení rozvozy | ★ | ≥4.6★ |
| 3 | Hodnocení Google | ★ | ≥4.6★ |
| 4 | Čas přípravy | min | ≤10 |
| 5 | Chybovost objednávek | % | <0.5% |
| 6 | Mystery shop | % | ≥85% |
| 7 | Obratohodina | Kč/h | ≥1250 |
| 8 | Hodnocení zaměstnanců | 0-10 | ≥8 |
| 9 | Zjištěná ztráta | % | ≤0.5% |
| 10 | Nezjištěná ztráta | % | ≤0.5% |

---

## 📂 Soubory & Struktura

```
RESTO/
├── app_cz.py                        # Hlavní aplikace
├── database.py                      # Databázový modul (SQLite - lokální)
├── database_postgres.py             # Databázový modul (PostgreSQL - cloud) ⭐ NOVÉ
├── migrate_sqlite_to_postgres.py   # Migrační skript SQLite → PostgreSQL ⭐ NOVÉ
├── assets/
│   └── logo.png                     # Logo Bouda Burgers
├── .streamlit/
│   └── secrets.toml                 # Hesla + database URL (NECOMMITOVAT!)
├── resto_data.db                   # SQLite databáze (lokální)
├── requirements.txt                 # Python balíky (s PostgreSQL závislostmi)
├── run_resto_cz.bat                # Spuštění (production)
├── run_resto_test.bat              # Spuštění (test)
├── install_dependencies.bat        # Instalace balíků
├── kill_resto.bat                  # Vypnutí aplikace
├── README.md                       # Tato dokumentace
├── SUPABASE_SETUP.md               # Návod pro cloud deployment ⭐ NOVÉ
├── ZMENA_HESLA.md                  # Návod pro změnu hesla
└── .gitignore                      # Git ignore pravidla
```

---

## Technické Detaily

### Databáze

**Lokální (SQLite3):**
- **Typ**: SQLite3 (resto_data.db)
- **Modul**: database.py
- **Použití**: Lokální vývoj a testování
- **Backup**: Zkopírovat `resto_data.db`

**Cloud (PostgreSQL):**
- **Typ**: PostgreSQL (Supabase)
- **Modul**: database_postgres.py
- **Použití**: Produkce na Streamlit Cloud
- **Backup**: Automatické denní zálohy Supabase

**Společné tabulky (10):**
  - departments
  - locations
  - operational_managers
  - kpi_definitions
  - kpi_thresholds (NOVÉ)
  - manager_kpi_assignments (NOVÉ)
  - monthly_kpi_data
  - monthly_kpi_evaluation
  - monthly_department_kpi_data
  - department_monthly_summary

### Python Balíky
- `streamlit` - Web framework
- `pandas` - Data processing
- `plotly` - Grafy
- `psycopg2-binary` - PostgreSQL driver (NOVÉ)
- `sqlalchemy` - Database toolkit (NOVÉ)

### Port
- **Default**: 8501
- Ke změně: Editovat `run_resto_cz.bat`

---

## 🐛 Troubleshooting

### Chyba: "ModuleNotFoundError: No module named 'streamlit'"
**Řešení:**
```bash
pip install -r requirements.txt
```

### Chyba: "Address already in use :8501"
**Řešení:**
1. Spustit `kill_resto.bat`
2. Čekat 5 sekund
3. Spustit aplikaci znovu

### Nelze se přihlásit
**Řešení:**
1. Zkontrolovat `.streamlit/secrets.toml`
2. Ověřit správné heslo
3. Restartovat aplikaci

### FOREIGN KEY constraint failed
**Řešení:**
1. Spustit "🔧 Opravit binární ID" v Admin
2. Restartovat aplikaci
3. Problém by měl být vyřešen

### Dark/Light mode nefunguje
**Řešení:**
1. Kliknout na tlačítko ☀️ nebo 🌙 v sidebaru
2. Počkat na reload
3. Refresh prohlížeč (F5)

---

## 📞 Support

### Často Kladené Otázky

**Q: Mohu přidat novou lokalitu?**
A: Ano, v budoucí verzi bude v Admin UI. Zatím v `database.py`.

**Q: Mohu měnit KPI prahy?**
A: Ano! V Admin → KPI Nastavení → KPI Hranice.

**Q: Jak změnit heslo?**
A: Editovat `.streamlit/secrets.toml` nebo nastavit v Streamlit Cloud Secrets.

**Q: Jak zálohovat data?**
A: Zkopírovat soubor `resto_data.db`.

**Q: Mohu spustit na webu?**
A: Ano! Postupujte podle **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** pro cloud deployment.

**Q: Jak migruji z lokální SQLite na cloud PostgreSQL?**
A: Spusťte `python migrate_sqlite_to_postgres.py` - viz **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)**.

**Q: Je Supabase databáze zdarma?**
A: Ano! Free tier nabízí 500MB PostgreSQL databáze zdarma, což je dostatečné pro RESTO aplikaci.

---

## 📝 Verze

**Aktuální**: 3.1
**Poslední aktualizace**: 2025-11-13
**Status**: ✅ Production Ready

### Změny v 3.1
- ✅ Autentizace s heslem
- ✅ Light/Dark Mode přepínač
- ✅ Moderní UI design (karty, animace, shadows)
- ✅ Logo Bouda Burgers
- ✅ Kompaktní sidebar (vejde se na screen)
- ✅ Přiřazení KPI k manažerům
- ✅ Dynamické KPI hranice
- ✅ Porovnání měsíců
- ✅ Binary ID fixes
- ✅ Marketing KPI placeholder
- ✅ **PostgreSQL podpora** - Supabase cloud databáze
- ✅ **Perzistentní data** - Data přetrvávají v cloudu
- ✅ **Migrační skript** - Automatický přenos dat SQLite → PostgreSQL
- ✅ **Cloud deployment ready** - Připraveno pro Streamlit Cloud

### Změny v 3.0
- ✅ Kompletní redesign UI
- ✅ Dark theme jako default
- ✅ Oddělení & Lokality & Provozní
- ✅ Detailní přehled
- ✅ Import/Export CSV

### Změny v 2.0
- ✅ Nezávislost na Excelu
- ✅ Měsíční KPI (ne denní)
- ✅ SQLite databáze

---

## 📄 Licence

Interní projekt Bouda Burgers. Všechna práva vyhrazena.

---

**Poslední úprava**: 2025-11-13
