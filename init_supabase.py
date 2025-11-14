"""
Inicializace Supabase databáze - vytvoří tabulky a základní data
"""

import streamlit as st
import database_postgres as db

print("🚀 Inicializuji Supabase databázi...")
print()

# Vytvoří všechny tabulky
print("📊 Vytvářím tabulky...")
db.init_database()
print("✅ Tabulky vytvořeny")
print()

# Vloží základní data
print("📦 Vkládám základní data...")
db.insert_default_data()
print("✅ Data vložena")
print()

print("=" * 50)
print("🎉 Databáze úspěšně inicializována!")
print("=" * 50)
print()
print("Co bylo vytvořeno:")
print("  ✅ Oddělení: Bouda, Bistro")
print("  ✅ Lokality: Mercury, OC4Dvory, Bistro")
print("  ✅ Provozní: Matěj, Thomas, Michael")
print("  ✅ 10 KPI metrik s hranicemi")
print()
print("Můžeš nyní použít aplikaci!")
