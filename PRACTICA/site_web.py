import streamlit as st
import requests
import json
import time

# Configurare panou MCP pe tot ecranul
st.set_page_config(page_title="Sistem MCP - Interfață Robotică", layout="wide")

st.title("🤖 Integrare MCP cu Sisteme Robotice")
st.subheader("Platformă Demonstrativă pentru Monitorizare în Timp Real, Calcularea Rutei și Asistență AI")

if "mesaje_chat" not in st.session_state:
    st.session_state.mesaje_chat = []

# --- PRELUARE DATE DIN SERVERUL CLOUD ---
URL_CLOUD = "https://jsonbin.io"
HEADERS = {"X-Master-Key": "$2a$10$7v1b8M3qZUPch9pUSfUPch_7jJdirPtUPch"}

try:
    raspuns = requests.get(URL_CLOUD, headers=HEADERS, timeout=1.0)
    date_cloud = raspuns.json()["record"]
    
    # Verificăm dacă datele sunt proaspete (să nu fie mai vechi de 10 secunde)
    if time.time() - date_cloud["timestamp"] < 10:
        fata = date_cloud["fata"]
        stanga = date_cloud["stanga"]
        dreapta = date_cloud["dreapta"]
        ruta = date_cloud["ruta"]
        este_conectat = True
    else:
        este_conectat = False
except Exception:
    este_conectat = False

if not este_conectat:
    fata = 135
    stanga = 150
    dreapta = 75
    ruta = "INAINTE (Simulare)"

# --- INTERFAȚĂ GRAFICĂ ---
col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Modulul de Decizie MCP")
    if este_conectat:
        st.success("Hardware MCP: ONLINE (Conexiune Cloud Activă)")
    else:
        st.info("Hardware MCP: MOD DEMONSTRATIV")
    st.metric(label="RUTĂ OPTIMĂ DE NAVIGARE CALCULATĂ", value=ruta)

with col2:
    st.header("📊 Distanța Măsurată")
    pct_fata = min(max(int(fata), 0), 150) / 150
    pct_stanga = min(max(int(stanga), 0), 150) / 150
    pct_dreapta = min(max(int(dreapta), 0), 150) / 150

    st.progress(pct_fata, text=f"Distanță Față: {fata} cm")
    st.progress(pct_stanga, text=f"Distanță Stânga: {stanga} cm")
    st.progress(pct_dreapta, text=f"Distanță Dreapta: {dreapta} cm")

st.divider()
st.header("💬 Asistent Virtual AI - Algoritm MCP")

for mesaj in st.session_state.mesaje_chat:
    with st.chat_message(mesaj["rol"]): st.write(mesaj["text"])

intrebare_user = st.chat_input("Interoghează baza de date...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"rol": "user", "text": intrebare_user})
    with st.chat_message("user"): st.write(intrebare_user)

    q = intrebare_user.lower().strip()
    raspuns_ai = ""
    if any(cuv in q for cuv in ["conectat", "hardware", "port", "usb"]):
        raspuns_ai = "Sistemul hardware este mapat prin baza de date securizată în Cloud." if este_conectat else "Modulul hardware este deconectat de la Cloud."
    elif any(cuv in q for cuv in ["senzor", "cm", "scanare"]):
        raspuns_ai = f"Telemetrie Cloud: Față: {fata} cm, Stânga: {stanga} cm, Dreapta: {dreapta} cm."
    elif any(cuv in q for cuv in ["salut", "buna", "hello"]):
        raspuns_ai = "Salut! Sunt asistentul tău AI."
    else:
        raspuns_ai = "Solicitare procesată în Cloud. Pune-mi întrebări despre distanțe sau hardware."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    with st.chat_message("assistant"): st.write(raspuns_ai)

# Refresh automat direct din codul standard o dată la o secundă
time.sleep(1.0)
st.rerun()
