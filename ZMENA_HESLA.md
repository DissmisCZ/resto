# 🔐 Rychlý návod: Změna hesla

## 📍 Kde změnit heslo?

### Lokálně (na vašem PC):

**Soubor:** `.streamlit/secrets.toml`

```toml
[passwords]
admin = "NOVEHESLO123"
```

✅ Uložte soubor a restartujte aplikaci

---

### Na Streamlit Cloud (produkce):

1. **Jděte na:** https://share.streamlit.io
2. **Najděte svou aplikaci** → Klikněte na **⋮** (3 tečky)
3. **Settings** → **Secrets** (v menu vlevo)
4. **Změňte heslo:**

```toml
[passwords]
admin = "NOVEHESLO123"
```

5. **Save** → Aplikace se automaticky restartuje

---

## 💡 Doporučení pro silné heslo:

✅ Minimálně 12 znaků
✅ Kombinace velkých/malých písmen
✅ Číslice
✅ Speciální znaky (!@#$%^&*)

**Příklady dobrých hesel:**
- `Resto@2025!Secure`
- `KPI#Dashboard2025`
- `MyResto!Pass123`

❌ **Špatné heslo:** `123456`, `resto`, `password`

---

## 🔄 Po změně hesla:

1. ✅ Aplikace se automaticky restartuje
2. ✅ Staré heslo přestane fungovat
3. ✅ Sdělte nové heslo oprávněným uživatelům

---

## 🆘 Zapomněli jste heslo?

### Lokálně:
Podívejte se do `.streamlit/secrets.toml`

### Na Streamlit Cloud:
1. Settings → Secrets
2. Vidíte aktuální heslo
3. Můžete ho změnit

---

**Tip:** Uložte si heslo do password manageru (např. LastPass, 1Password, Bitwarden)
