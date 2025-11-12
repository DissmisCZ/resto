# RESTO v2 - KPI Dashboard

**Nezávislá webová aplikace pro správu měsíčních KPI v restauracích**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-orange)
![Status](https://img.shields.io/badge/status-production-brightgreen)

---

## 📋 Obsah

1. [O projektu](#o-projektu)
2. [Instalace](#instalace)
3. [Spuštění](#spuštění)
4. [Funkce](#funkce)
5. [Struktura dat](#struktura-dat)
6. [Užívání](#užívání)
7. [Troubleshooting](#troubleshooting)

---

## O projektu

RESTO v2 je **kompletně nezávislá** aplikace na Excelu pro správu operačních KPI restaurací.

### Klíčové rysy:
- ✅ **Měsíční KPI tracking** (ne denní)
- ✅ **Oddělení** (Matějovo, Thomasovo, Michaelovo)
- ✅ **Lokality** (Mercury, OC4Dvory, Bouda, Bistro)
- ✅ **Provozní manažeři**
- ✅ **10 KPI metriky** s automatickými bonusy
- ✅ **Dark theme** design
- ✅ **Import/Export** CSV data
- ✅ **Detailní porovnání** lokalit
- ✅ **Agregace bonusů** na úrovni oddělení

---

## Instalace

### Systemové Požadavky
- Windows 7+
- Python 3.8+ (ze https://python.org)

### Krok 1: Instalace Python Balíků

Dvakrát kliknout na soubor:
```
install_dependencies.bat
```

Nebo ručně v Command Prompt (cmd):
```bash
pip install -r requirements.txt
```

Okno se zavře automaticky po dobu instalace.

---

## Spuštění

### Testovací Spuštění (Fresh Database)
Dvakrát kliknout na:
```
run_resto_test.bat
```

Tímto se:
- Smaže stará databáze
- Vytvoří čerstvé demo data
- Spustí aplikaci na http://localhost:8501

**Ideální pro první vyzkoušení!**

### Běžné Spuštění (Production)
Dvakrát kliknout na:
```
run_resto_cz.bat
```

Aplikace se otevře na: http://localhost:8501

### Vypnutí Aplikace

Dvakrát kliknout na:
```
kill_resto.bat
```

Nebo v terminálu: `Ctrl+C`

---

## Funkce

### 📊 Přehled
- Měsíční shrnutí všech oddělení
- Metriky bonusů
- Přehled lokalit s expandery
- Tlačítko pro přepočet bonusů

### 📈 Detailní Přehled
- Filtrování dle oddělení
- Filtrování dle KPI
- Porovnávání lokalit
- Grafické vizualizace

### 👥 Porovnání Oddělení
- Tabulka všech oddělení
- Průměrné bonusy
- Počet lokalit
- Graf porovnání

### 📝 Zadání Dat
**Tab: Ruční vstup**
- Vybrat měsíc (YYYY-MM)
- Vybrat lokalitu
- Vyplnit 10 KPI hodnot
- Uložit

**Tab: Import CSV**
- Stáhnout šablonu
- Vyplnit v Excelu
- Nahrát CSV zpět

### ⚙️ Nastavení (ADMIN)
- Přehled oddělení
- Přehled lokalit
- Přehled KPI prahů
- ❌ Přidávání lokalit/oddělení zakázáno

### 📤 Import/Export
- Export dat za měsíc
- Hromadný import CSV

---

## Struktura Dat

### Hierarchie
```
ODDĚLENÍ
└── LOKALITY
    └── PROVOZNÍ MANAŽEŘI
        └── KPI (10 metrů)
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

## Užívání

### Jak zadat data za měsíc

1. Otevřít aplikaci: `run_resto_cz.bat`
2. Jít na: **📝 Zadání dat**
3. Tab: **📝 Ruční vstup** nebo **📥 Importovat CSV**
4. Vybrat měsíc (např. 2025-11)
5. Vybrat lokalitu (Mercury, OC4Dvory, Bouda, Bistro)
6. Vyplnit 10 KPI hodnot
7. Kliknout: **💾 Uložit data**

### Jak importovat hromadná data

1. Jít na: **📝 Zadání dat** → **📥 Importovat CSV**
2. Kliknout: **📥 Stáhnout šablonu CSV**
3. Vyplnit v Excelu:
   - Měsíc: 2025-11
   - Lokalita: Mercury, OC4Dvory, atd.
   - KPI: Audit, Hodnocení rozvozy, atd.
   - Hodnota: 85.5, 4.6, atd.
4. Uložit jako CSV (UTF-8)
5. Nahrát do aplikace: **📥 Importovat CSV**

### Jak vidět bonusy

1. Jít na: **📊 Přehled**
2. Vybrat měsíc v postranním panelu
3. Vidět bonusy za oddělení
4. Rozbalit lokality pro detail

### Jak porovnat lokality

1. Jít na: **📈 Detailní přehled**
2. Vybrat měsíc
3. Filtrovat dle oddělení (volitelně)
4. Filtrovat dle KPI (volitelně)
5. Vidět tabulku a graf porovnání

---

## 📂 Soubory & Struktura

```
RESTO/
├── app_cz.py                    # Hlavní aplikace
├── database.py                  # Databázový modul
├── resto_data.db               # SQLite databáze
├── requirements.txt             # Python balíky
├── run_resto_cz.bat            # Spuštění (production)
├── run_resto_test.bat          # Spuštění (test)
├── install_dependencies.bat    # Instalace balíků
├── kill_resto.bat              # Vypnutí aplikace
├── README.md                   # Tato dokumentace
├── README_CZ.md                # Podrobná dokumentace (CZ)
└── TODO.md                     # Technická dokumentace
```

---

## Technické Detaily

### Databáze
- **Typ**: SQLite3 (resto_data.db)
- **Tabulky**: 8 tabulek (departmenty, lokality, KPI data, evaluace, atd.)
- **Backup**: Zkopírovat `resto_data.db`

### Python Balíky
- `streamlit` - Web framework
- `pandas` - Data processing
- `plotly` - Grafy
- `openpyxl` - Excel soubory (pro import šablon)

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

Nebo spustit `install_dependencies.bat`

### Chyba: "Address already in use :8501"
**Řešení:**
1. Spustit `kill_resto.bat`
2. Čekat 5 sekund
3. Spustit aplikaci znovu

Nebo v Command Prompt:
```bash
netstat -ano | find ":8501"
taskkill /F /PID <PID>
```

### Databáze se neinicializuje
**Řešení:**
1. Smazat `resto_data.db`
2. Spustit `run_resto_test.bat`
3. Aplikace si vytvoří novou databázi

### CSV import selže
**Řešení:**
- Ověřit formát CSV (UTF-8)
- Zkontrolovat názvy lokalit:
  - Mercury
  - OC4Dvory
  - Bouda
  - Bistro
- Měsíc musí být YYYY-MM (např. 2025-11)

### Dark theme se nezobrazuje
**Řešení:**
1. Jít do Settings (⚙️ v Streamlitu)
2. Theme: Dark
3. Refresh (F5)

---

## 📞 Support & Dokumentace

### Podrobná Dokumentace
- **README_CZ.md** - Detailní návod (čeština)
- **TODO.md** - Technická dokumentace

### Často Kladené Otázky

**Q: Mohu přidat novou lokalitu?**
A: Ne, v UI. Lokality se spravují v `database.py` (admin).

**Q: Mohu měnit KPI prahy?**
A: V budoucnu. Zatím v `database.py`.

**Q: Jak zálohovat data?**
A: Zkopírovat soubor `resto_data.db`.

**Q: Mohu spustit na webu?**
A: Ano, na Streamlit Cloud nebo vlastním serveru.

---

## 📝 Verze

**Aktuální**: 2.0
**Poslední aktualizace**: 2025-11-10
**Status**: ✅ Production Ready

### Změny v 2.0
- ✅ Nezávislost na Excelu
- ✅ Měsíční KPI (ne denní)
- ✅ Dark theme
- ✅ Oddělení & Lokality & Provozní
- ✅ Detailní přehled
- ✅ Import/Export CSV

---

## 📄 Licence

Interní projekt. Všechna práva vyhrazena.

---

**Vytvořeno**: Claude Code
**Poslední úprava**: 2025-11-10
**Kontakt**: Admin RESTO
