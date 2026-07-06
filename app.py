import streamlit as st
import requests
import time

st.set_page_config(page_title="Sistem Inteligent MCP v2.0", layout="wide")

st.title("🤖 Monitorizare MCP Live")

FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

# Inițializare stări
if "fata" not in st.session_state: st.session_state.fata = 150
if "stanga" not in st.session_state: st.session_state.stanga = 150
if "dreapta" not in st.session_state: st.session_state.dreapta = 150
if "ruta" not in st.session_state: st.session_state.ruta = "ANALIZĂ..."

este_conectat = False

# Preluare ultra-rapidă din Firebase
try:
    raspuns = requests.get(FIREBASE_URL, timeout=0.3)
    if raspuns.status_code == 200 and raspuns.json():
        date = raspuns.json()
        timp_server = time.time()
        ultimul_semn = date.get("ultimul_semn_de_viata", 0)
        
        # Dacă datele sunt mai vechi de 4 secunde, considerăm deconectat
        if timp_server - ultimul_semn < 4.0:
            st.session_state.fata = int(date.get("fata", 150))
            st.session_state.stanga = int(date.get("stanga", 150))
            st.session_state.dreapta = int(date.get("dreapta", 150))
            st.session_state.ruta = str(date.get("ruta", "INAINTE"))
            este_conectat = True
except Exception:
    pass

# Panou Status
if este_conectat:
    st.success(f"🟢 HARDWARE LIVE | Decizie: {st.session_state.ruta}")
else:
    st.error("🔴 DISPOZITIV DECONECTAT (Verifică PyCharm)")

# Barele grafice de distanță
st.subheader("📊 Distanțe Telemetrice")
st.progress(min(max(st.session_state.fata, 0), 150) / 150, text=f"Față: {st.session_state.fata} cm")
st.progress(min(max(st.session_state.stanga, 0), 150) / 150, text=f"Stânga: {st.session_state.stanga} cm")
st.progress(min(max(st.session_state.dreapta, 0), 150) / 150, text=f"Dreapta: {st.session_state.dreapta} cm")

# Refresh forțat la 0.1 secunde pentru eliminarea lag-ului din browser
time.sleep(0.1)
st.rerun()
