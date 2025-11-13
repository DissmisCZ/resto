# 🚀 Supabase + Streamlit Cloud Setup

Kompletní návod pro migraci RESTO v3 na cloudovou databázi Supabase s perzistentním uložením dat.

---

## 📋 Co potřebujete

- ✅ Funkční lokální RESTO aplikace s daty
- ✅ GitHub účet (pro Streamlit Cloud)
- ✅ Email (pro Supabase registraci)
- ✅ Internetové připojení

---

## 🎯 Celkový přehled

1. **Supabase** - Cloudová PostgreSQL databáze (ZDARMA, 500MB)
2. **Streamlit Cloud** - Hosting pro aplikaci (ZDARMA)
3. **Migrace** - Přenos dat z lokální SQLite do Supabase

---

## Krok 1: Vytvoření Supabase Projektu

### 1.1 Registrace

1. Jděte na: **https://supabase.com**
2. Klikněte na **"Start your project"**
3. Přihlaste se pomocí:
   - GitHub účtu (doporučeno)
   - Nebo email + heslo

### 1.2 Vytvoření Nového Projektu

1. Klikněte na **"New Project"**
2. Vyplňte údaje:
   - **Name**: `resto-kpi` (nebo libovolný název)
   - **Database Password**: **Vygenerujte silné heslo** (uložte si ho!)
   - **Region**: `Central EU (Frankfurt)` (nejbližší k ČR)
   - **Pricing Plan**: `Free` (500MB databáze zdarma)

3. Klikněte **"Create new project"**
4. ⏰ Počkejte 2-3 minuty než se projekt vytvoří

### 1.3 Získání Connection String

1. V Supabase projektu klikněte na **Settings** (ikona ozubeného kola)
2. V levém menu vyberte **Database**
3. Scrollujte dolů na sekci **"Connection string"**
4. Vyberte **"URI"** mode
5. Zkopírujte connection string - vypadá takto:

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

6. **DŮLEŽITÉ**: Nahraďte `[YOUR-PASSWORD]` za heslo které jste zadali při vytváření projektu

**Příklad finálního connection stringu:**
```
postgresql://postgres:MojeSupertajneHeslo123!@db.abcdefghijklmnop.supabase.co:5432/postgres
```

---

## Krok 2: Nastavení Lokální Aplikace

### 2.1 Aktualizace Secrets

Upravte soubor `.streamlit/secrets.toml`:

```toml
[passwords]
admin = "resto2025"

[database]
url = "postgresql://postgres:VaseHeslo@db.xxxxx.supabase.co:5432/postgres"
```

**⚠️ Použijte svůj vlastní connection string ze Step 1.3!**

### 2.2 Instalace Závislostí

**Windows:**
```bash
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
pip3 install -r requirements.txt
```

Nainstaluje se:
- `psycopg2-binary` - PostgreSQL driver
- `sqlalchemy` - Database toolkit

---

## Krok 3: Inicializace Databáze

Vytvoříme tabulky v Supabase PostgreSQL databázi.

### 3.1 Spusťte Python Console

**Windows:**
```bash
python
```

**Linux/macOS:**
```bash
python3
```

### 3.2 Vytvořte Tabulky

V Python konzoli:

```python
import streamlit as st
import database_postgres as db

# Vytvoří všechny tabulky
db.init_database()

# Vloží základní data (departments, locations, KPI definitions)
db.insert_default_data()

print("✅ Databáze inicializována!")
```

Stiskněte `Ctrl+D` nebo napište `exit()` pro ukončení.

---

## Krok 4: Migrace Dat

Přeneseme všechna vaše existující data z lokální SQLite do Supabase.

### 4.1 Spuštění Migrace

**Windows:**
```bash
python migrate_sqlite_to_postgres.py
```

**Linux/macOS:**
```bash
python3 migrate_sqlite_to_postgres.py
```

### 4.2 Co Se Děje Během Migrace

Skript přenese:
- ✅ Všechna oddělení (departments)
- ✅ Všechny lokality (locations)
- ✅ Všechny provozní manažery (operational_managers)
- ✅ KPI definice a hranice (kpi_definitions, kpi_thresholds)
- ✅ Přiřazení KPI k manažerům (manager_kpi_assignments)
- ✅ **Všechna měsíční KPI data** (monthly_kpi_data)
- ✅ Vyhodnocení bonusů (monthly_kpi_evaluation)
- ✅ Shrnutí oddělení (department_monthly_summary)

### 4.3 Výstup

Úspěšná migrace vypadá takto:

```
============================================================
🚀 RESTO v3 - SQLite → PostgreSQL Migration
============================================================

📡 Connecting to databases...
  ✅ Connected to SQLite
  ✅ Connected to PostgreSQL

📊 Starting migration...

  📦 Migrating departments... ✅ 2 rows migrated
  📦 Migrating locations... ✅ 3 rows migrated
  📦 Migrating operational_managers... ✅ 3 rows migrated
  📦 Migrating kpi_definitions... ✅ 10 rows migrated
  📦 Migrating kpi_thresholds... ✅ 12 rows migrated
  📦 Migrating monthly_kpi_data... ✅ 45 rows migrated
  ...

🔧 Resetting PostgreSQL sequences...
  ✅ departments: sequence set to 3
  ✅ locations: sequence set to 4
  ...

============================================================
✅ Migration Complete!
📊 Total rows migrated: 78
============================================================

🎉 Vaše data jsou nyní v Supabase PostgreSQL!
```

---

## Krok 5: Test Lokální Aplikace

### 5.1 Spuštění Aplikace

**Windows:**
```bash
streamlit run app_cz.py
```

**Linux/macOS:**
```bash
streamlit run app_cz.py
```

### 5.2 Ověření

1. Přihlaste se pomocí hesla (`resto2025`)
2. Zkontrolujte **📊 Přehled** - měli byste vidět všechna vaše oddělení
3. Zkontrolujte **📝 Zadání** - měli byste vidět všechna měsíční data
4. Zkuste přidat nová KPI data - měla by se uložit do Supabase!

**✅ Pokud vše funguje, můžete pokračovat na Streamlit Cloud deployment.**

---

## Krok 6: Deployment na Streamlit Cloud

### 6.1 Push Kódu na GitHub

1. **Inicializujte Git** (pokud ještě není):

```bash
git init
git add .
git commit -m "RESTO v3.1 - PostgreSQL + Supabase ready"
```

2. **Vytvořte GitHub repository**:
   - Jděte na: https://github.com/new
   - Název: `resto-v3`
   - Typ: **Private** (doporučeno pro citlivá data)
   - Klikněte **"Create repository"**

3. **Push kódu**:

```bash
git remote add origin https://github.com/VASE-JMENO/resto-v3.git
git branch -M main
git push -u origin main
```

### 6.2 Nasazení na Streamlit Cloud

1. Jděte na: **https://share.streamlit.io**
2. Přihlaste se pomocí GitHub účtu
3. Klikněte **"New app"**
4. Vyplňte:
   - **Repository**: `VASE-JMENO/resto-v3`
   - **Branch**: `main`
   - **Main file path**: `app_cz.py`
   - **App URL**: `resto-kpi` (nebo vlastní název)

5. Klikněte **"Advanced settings"**
6. V **"Secrets"** přidejte:

```toml
[passwords]
admin = "VaseSilneHeslo2025!"

[database]
url = "postgresql://postgres:VaseSupabaseHeslo@db.xxxxx.supabase.co:5432/postgres"
```

**⚠️ ZMĚŇTE heslo pro produkci! Nepoužívejte `resto2025`**

7. Klikněte **"Deploy!"**
8. ⏰ Počkejte 2-3 minuty než se aplikace nasadí

---

## Krok 7: Ověření Cloudové Aplikace

### 7.1 Přístup

Po nasazení dostanete URL:
```
https://resto-kpi.streamlit.app
```

### 7.2 Test

1. ✅ Přihlaste se pomocí nového hesla
2. ✅ Zkontrolujte všechna data
3. ✅ Přidejte testovací KPI data
4. ✅ Restartujte aplikaci (⋮ → Reboot app)
5. ✅ **Data by měla přetrvat!** (perzistence funguje)

---

## 🎉 Hotovo!

Vaše aplikace nyní běží na:
- **Streamlit Cloud** - aplikace dostupná 24/7
- **Supabase PostgreSQL** - data uložena trvale v cloudu

### Výhody

✅ **Perzistence** - Data se nikdy neztratí
✅ **Rychlost** - Supabase má rychlé SSD disky
✅ **Zálohování** - Supabase automaticky zálohuje každý den
✅ **Škálovatelnost** - 500MB zdarma, rozšiřitelné při růstu
✅ **Bezpečnost** - SSL šifrování, přístupová hesla

---

## 📊 Další Kroky

### Pravidelná Záloha

Doporučujeme pravidelně exportovat data:

1. V aplikaci jděte na **📝 Zadání → Import CSV**
2. Stáhněte šablonu s vašimi daty
3. Uložte lokálně jako zálohu

### Monitoring

Sledujte využití Supabase:
1. Jděte na Supabase Dashboard
2. Klikněte na **Reports**
3. Sledujte:
   - Počet řádků v tabulkách
   - Velikost databáze (z 500MB free limitu)
   - API requesty

---

## 🆘 Troubleshooting

### Problém: "Connection refused"

**Řešení:**
1. Zkontrolujte connection string v secrets.toml
2. Ověřte že heslo neobsahuje speciální znaky (nebo je escapněte)
3. Zkontrolujte že Supabase projekt je "Active" (ne "Paused")

### Problém: "No module named 'psycopg2'"

**Řešení:**
```bash
pip install psycopg2-binary
```

### Problém: "Table does not exist"

**Řešení:**
Spusťte inicializaci databáze:
```python
import database_postgres as db
db.init_database()
db.insert_default_data()
```

### Problém: "Authentication failed"

**Řešení:**
1. Zkontrolujte heslo v connection stringu
2. Reset hesla v Supabase: Settings → Database → Database password → Reset

### Problém: Streamlit Cloud app nefunguje

**Řešení:**
1. Zkontrolujte "Logs" v Streamlit Cloud
2. Ověřte že secrets jsou správně nastaveny
3. Reboot aplikaci: ⋮ → Reboot app

---

## 📞 Podpora

### Supabase Dokumentace
- https://supabase.com/docs

### Streamlit Cloud Dokumentace
- https://docs.streamlit.io/streamlit-community-cloud

### PostgreSQL Dokumentace
- https://www.postgresql.org/docs/

---

**Datum vytvoření**: 2025-11-13
**Verze**: RESTO v3.1
**Status**: ✅ Production Ready
