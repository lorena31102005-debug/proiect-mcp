import streamlit as st
import requests
import time

# Configurare panou MCP pe tot ecranul
st.set_page_config(page_title="Sistem MCP - Interfață Robotică", layout="wide")

st.title("🤖 Integrare MCP cu Sisteme Robotice")
st.subheader("Platformă Demonstrativă pentru Monitorizare în Timp Real, Calcularea Rutei și Asistență AI")

# Link-ul tău din Firebase
FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

# Inițializare memorie Streamlit (Session State)
if "fata" not in st.session_state:
    st.session_state.fata = 150
    st.session_state.stanga = 150
    st.session_state.dreapta = 150
    st.session_state.ruta = "ANALIZĂ..."
    st.session_state.mesaje_chat = []

este_conectat = False
port_activ = "Deconectat"

# --- CITIRE DATE DIN FIREBASE CLOUD ---
try:
    raspuns = requests.get(FIREBASE_URL, timeout=1)
    if raspuns.status_code == 200 and raspuns.json():
        date = raspuns.json()
        
        timp_server = time.time()
        ultimul_semn = date.get("ultimul_semn_de_viata", 0)
        
        # Dacă releul de pe laptop a trimis date acum mai puțin de 2.5 secunde
        if timp_server - ultimul_semn < 2.5:
            st.session_state.fata = date.get("fata", 150)
            st.session_state.stanga = date.get("stanga", 150)
            st.session_state.dreapta = date.get("dreapta", 150)
            st.session_state.ruta = date.get("ruta", "ANALIZĂ...")
            este_conectat = True
            port_activ = "Cloud Firebase (Live)"
except Exception:
    pass

# Dacă laptopul de acasă e stins, resetăm interfața la 0 ca să arate deconectat
if not este_conectat:
    st.session_state.fata = 0
    st.session_state.stanga = 0
    st.session_state.dreapta = 0
    st.session_state.ruta = "SISTEM DECONECTAT (Laptop Offline)"

# --- INTERFAȚĂ GRAFICĂ ---
col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Modulul de Decizie MCP")
    if este_conectat:
        st.success(f"🟢 Hardware MCP: ACTIVAT (Sursă: {port_activ})")
        st.metric(label="RUTĂ OPTIMĂ DE NAVIGARE CALCULATĂ", value=st.session_state.ruta)
    else:
        st.error("🔴 ROBOT DECONECTAT")
        st.info("Laptopul de acasă sau programul din PyCharm este oprit. Barele au fost resetate la 0.")

with col2:
    st.header("📊 Distanța Măsurată")
    pct_fata = min(max(int(st.session_state.fata), 0), 150) / 150
    pct_stanga = min(max(int(st.session_state.stanga), 0), 150) / 150
    pct_dreapta = min(max(int(st.session_state.dreapta), 0), 150) / 150

    st.progress(pct_fata, text=f"Distanță Față: {st.session_state.fata} cm")
    st.progress(pct_stanga, text=f"Distanță Stânga: {st.session_state.stanga} cm")
    st.progress(pct_dreapta, text=f"Distanță Dreapta: {st.session_state.dreapta} cm")

st.divider()

# --- ASISTENT VIRTUAL AI ---
st.header("💬 Asistent Virtual AI - Algoritm MCP")

container_chat = st.container()
with container_chat:
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["rol"]):
            st.write(mesaj["text"])

intrebare_user = st.chat_input("Interoghează baza de date...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"rol": "user", "text": intrebare_user})

    q = intrebare_user.lower().strip()
    raspuns_ai = ""
    sinonime_hardware = ["conectat", "esp", "hardware", "port", "usb", "placa", "plăcuță", "cablu", "conexiune", "com3", "laptop", "online", "offline"]
    sinonime_distante = ["distant", "senzor", "vezi", "cm", "masor", "măsor", "centimetri", "valori", "radar",
                         "telemetrie", "citeste", "scanare", "scanarea", "mediu", "mediului", "sonar"]
    sinonime_stare = ["stare", "alerta", "alertă", "pericol", "obstacol", "siguranta", "siguranță", "bazaie", "bâzâie",
                      "led", "alarma"]
    sinonime_ruta = ["ruta", "rută", "directia", "direcția", "decizie", "incotro", "încotro", "virezi", "navigrezi",
                     "mergi", "drum", "timp real", "buna ruta", "bună rută", "evitare"]

    if any(cuv in q for cuv in sinonime_hardware):
        if este_conectat:
            raspuns_ai = f"Sistemul hardware este ONLINE și transmite date în Cloud prin {port_activ}."
        else:
            raspuns_ai = "Sistemul hardware este OFFLINE. Laptopul de acasă sau scriptul Python este oprit."
    elif any(cuv in q for cuv in sinonime_distante):
        if este_conectat:
            raspuns_ai = f"Telemetria curentă indică: Față: {st.session_state.fata} cm, Stânga: {st.session_state.stanga} cm, Dreapta: {st.session_state.dreapta} cm."
        else:
            raspuns_ai = "Robotul fiind deconectat, nu pot citi valorile curente ale senzorilor."
    elif any(cuv in q for cuv in sinonime_stare):
        if not este_conectat:
            raspuns_ai = "Sistemul este oprit. Nu se pot evalua riscurile în timp real."
        elif st.session_state.fata < 15 or st.session_state.stanga < 15 or st.session_state.dreapta < 15:
            raspuns_ai = "Alertă critică: Obstacol detectat sub 15 cm! Robotul caută o rută de ocolire."
        else:
            raspuns_ai = f"Stare Nominală: Zonele sunt sigure. Distanța frontală este de {st.session_state.fata} cm."
    elif any(cuv in q for cuv in sinonime_ruta):
        raspuns_ai = f"Direcția optimă selectată în mod dinamic: {st.session_state.ruta}."
    elif any(cuv in q for cuv in ["salut", "buna", "bună", "ce faci", "cine esti", "hello"]):
        raspuns_ai = "Salut! Sunt asistentul tău AI dedicat pentru monitorizarea sistemului hardware MCP de la distanță."
    else:
        raspuns_ai = "Solicitare procesată. Întreabă-mă chestiuni specifice despre senzori, starea hardware, rutele optime calculate sau starea de alertă."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    st.rerun()

# --- AUTO-REFRESH LIVE ---
time.sleep(0.4)
st.rerun()
