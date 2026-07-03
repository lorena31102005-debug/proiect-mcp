import streamlit as st
import serial
import serial.tools.list_ports
import json
import time

# Configurare panou MCP pe tot ecranul
st.set_page_config(page_title="Sistem MCP - Interfață Robotică", layout="wide")

st.title("🤖 Monitorizare Centru de Comandă MCP")
st.subheader("Sistem Robotic Demonstrativ pentru Scanare Multidirecțională și Rutare Autonomă")

# Inițializare memorie Streamlit (Session State)
if "fata" not in st.session_state:
    st.session_state.fata = 150
    st.session_state.stanga = 150
    st.session_state.dreapta = 150
    st.session_state.ruta = "ANALIZĂ..."
    st.session_state.mesaje_chat = []


# --- INIȚIALIZARE PORT SERIAL STABIL ---
@st.cache_resource
def initializare_port_serial():
    porturi = list(serial.tools.list_ports.comports())
    port_gasit = "COM3"
    for p in porturi:
        if any(driver in p.description.upper() for driver in ["CH340", "CP210", "USB", "SERIAL"]):
            port_gasit = p.device
            break
    try:
        ser = serial.Serial(port_gasit, 115200, timeout=0.05)
        return ser, port_gasit, True
    except:
        return None, port_gasit, False


conexiune_usb, port_activ, este_conectat = initializare_port_serial()

# --- PRELUARE DATE DIN SENSUL ESP32 -> PYTHON ---
if este_conectat and conexiune_usb:
    try:
        if conexiune_usb.in_waiting > 0:
            linie = conexiune_usb.readline().decode('utf-8', errors='ignore').strip()
            if linie.startswith('{') and linie.endswith('}'):
                date = json.loads(linie)
                st.session_state.fata = int(date["fata"])
                st.session_state.stanga = int(date["stanga"])
                st.session_state.dreapta = int(date["dreapta"])
                st.session_state.ruta = str(date["ruta"])
        conexiune_usb.reset_input_buffer()
    except:
        este_conectat = False

if not este_conectat:
    st.session_state.fata = 135
    st.session_state.stanga = 150
    st.session_state.dreapta = 75
    st.session_state.ruta = "INAINTE (Simulare)"

# --- INTERFAȚĂ GRAFICĂ ---
col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Modulul de Decizie MCP")
    if este_conectat:
        st.success(f"Hardware MCP: ACTIVAT (Port: {port_activ})")
    else:
        st.info("Hardware MCP: MOD DEMONSTRATIV")

    st.metric(label="RUTĂ OPTIMĂ DE NAVIGARE CALCULATĂ", value=st.session_state.ruta)

with col2:
    st.header("📊 Distanța Măsurată")
    pct_fata = min(max(int(st.session_state.fata), 0), 150) / 150
    pct_stanga = min(max(int(st.session_state.stanga), 0), 150) / 150
    pct_dreapta = min(max(int(st.session_state.dreapta), 0), 150) / 150

    st.progress(pct_fata, text=f"Distanță Față: {st.session_state.fata} cm")
    st.progress(pct_stanga, text=f"Distanță Stânga: {st.session_state.stanga} cm")
    st.progress(pct_dreapta, text=f"Distanță Dreapta: {st.session_state.dreapta} cm")

st.divider()
st.header("💬 Asistent Virtual AI - Algoritm MCP")

# Afișare istoric chat
for mesaj in st.session_state.mesaje_chat:
    with st.chat_message(mesaj["rol"]): st.write(mesaj["text"])

intrebare_user = st.chat_input("Interoghează baza de date...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"rol": "user", "text": intrebare_user})
    with st.chat_message("user"):
        st.write(intrebare_user)

    q = intrebare_user.lower().strip()
    raspuns_ai = ""

    # 1. MATRICE SINONIME: HARDWARE / CONEXIUNE
    sinonime_hardware = ["conectat", "esp", "hardware", "port", "usb", "placa", "plăcuță", "cablu", "conexiune", "com3"]

    # 2. MATRICE SINONIME: DISTANTE / TELEMETRIE / SCANARE
    sinonime_distante = ["distant", "senzor", "vezi", "cm", "masor", "măsor", "centimetri", "valori", "radar",
                         "telemetrie", "citeste", "scanare", "scanarea", "mediu", "mediului", "sonar"]

    # 3. MATRICE SINONIME: STARE / ALERTE / SIGURANTA
    sinonime_stare = ["stare", "alerta", "alertă", "pericol", "obstacol", "siguranta", "siguranță", "bazaie", "bâzâie",
                      "led", "alarma"]

    # 4. MATRICE SINONIME: RUTA / DECIZIE / TIMP REAL
    sinonime_ruta = ["ruta", "rută", "directia", "direcția", "decizie", "incotro", "încotro", "virezi", "navigrezi",
                     "mergi", "drum", "timp real", "buna ruta", "bună rută", "evitare"]

    # --- VERIFICARE SEMANTICĂ FLEXIBILĂ ---
    if any(cuv in q for cuv in sinonime_hardware):
        if este_conectat:
            raspuns_ai = f"Sistemul hardware ESP32 este complet mapat și detectat online [INDEX]. Legătura serială este securizată activ pe portul {port_activ} la viteza de transmisie de 115200 baud."
        else:
            raspuns_ai = "În acest moment, modulul hardware nu este detectat fizic pe portul USB [INDEX]. Interfața Streamlit rulează în regim de simulare academică stabilă."

    elif any(cuv in q for cuv in sinonime_distante):
        raspuns_ai = f"Sistemul execută scanarea liniară a mediului prin deplasarea unghiulară a senzorului ultrasonic [INDEX]. Telemetria curentă indică: Sectorul Central (Față): {st.session_state.fata} cm, Flancul Stâng: {st.session_state.stanga} cm, iar Flancul Drept: {st.session_state.dreapta} cm."

    elif any(cuv in q for cuv in sinonime_stare):
        if st.session_state.fata < 15 or st.session_state.stanga < 15 or st.session_state.dreapta < 15:
            raspuns_ai = f"Stare de Urgență: A fost detectat un obstacol în perimetrul critic de siguranță sub 15 cm (Față curentă: {st.session_state.fata} cm) [INDEX]. Actuatoarele periferice (buzzerul și LED-ul) sunt declanșate automat."
        else:
            raspuns_ai = f"Stare Nominală: Sistemul rulează în parametri optimi de siguranță [INDEX]. Distanța frontală este curată ({st.session_state.fata} cm), iar indicatorul optic LED verde confirmă absența pericolelor."

    elif any(cuv in q for cuv in sinonime_ruta):
        raspuns_ai = f"Calculul rutei optime în timp real este asigurat de algoritmul ierarhic MCP, procesat la fiecare împrospătare a ecranului [INDEX]. Analiza curentă a selectat: {st.session_state.ruta}."

    elif any(cuv in q for cuv in ["salut", "buna", "bună", "ce faci", "cine esti", "cine ești", "hello"]):
        raspuns_ai = "Salut! Sunt Agentul AI integrat în arhitectura software a Centrului de Comandă MCP [INDEX]. Sunt programat să îți ofer rapoarte telemetrice live, stări de alertă sau decizii vectoriale de navigare [INDEX]."

    else:
        raspuns_ai = "Solicitare generală procesată [INDEX]. Pentru a vă oferi un răspuns exact din baza de date a robotului, vă rog să mă întrebați despre: scanarea mediului, calcularea rutei în timp real, starea alertelor sau conexiunea hardware [INDEX]."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    with st.chat_message("assistant"):
        st.write(raspuns_ai)

time.sleep(0.04)
st.rerun()

