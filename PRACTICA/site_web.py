import streamlit as st
import serial
import serial.tools.list_ports
import json
import time
import threading

# Configurare panou MCP pe tot ecranul
st.set_page_config(page_title="Sistem MCP - Interfață Robotică", layout="wide")

st.title("🤖 Integrare MCP cu Sisteme Robotice")
st.subheader("Platformă Demonstrativă pentru Monitorizare în Timp Real, Calcularea Rutei și Asistență AI")

# Inițializare memorie Streamlit
if "fata" not in st.session_state:
    st.session_state.fata = 150
    st.session_state.stanga = 150
    st.session_state.dreapta = 150
    st.session_state.ruta = "ANALIZĂ..."
    st.session_state.mesaje_chat = []

# --- RECEPTOR INTERNET CORECTAT (PENTRU RELEU) ---
query_params = st.query_params.to_dict()

if "fata" in query_params:
    try:
        st.session_state.fata = int(query_params["fata"])
        st.session_state.stanga = int(query_params["stanga"])
        st.session_state.dreapta = int(query_params["dreapta"])
        st.session_state.ruta = str(query_params["ruta"])
        este_conectat = True
        port_activ = "Internet (Releu Activ)"
    except Exception:
        este_conectat = False
else:
    # --- CODUL MULTI-THREAD CARE RULEAZĂ PE LOCAL ---
    @st.cache_resource
    def porneste_colectorul_serial():
        sertar_date = {
            "fata": 150, "stanga": 150, "dreapta": 150, "ruta": "ANALIZĂ...",
            "conectat": False, "port": "Niciunul"
        }
        def bucla_citire_fundal():
            ser = None
            while True:
                if ser is None or not ser.is_open:
                    porturi = list(serial.tools.list_ports.comports())
                    port_gasit = None
                    for p in porturi:
                        if any(driver in p.description.upper() for driver in ["CH340", "CP210", "USB", "SERIAL", "CH34X"]):
                            port_gasit = p.device
                            break
                    if port_gasit:
                        try:
                            ser = serial.Serial(port_gasit, 115200, timeout=0.1)
                            sertar_date["conectat"] = True
                            sertar_date["port"] = port_gasit
                        except Exception:
                            ser = None
                            sertar_date["conectat"] = False
                    else:
                        sertar_date["conectat"] = False
                else:
                    try:
                        if ser.in_waiting > 0:
                            linie = ser.readline().decode('utf-8', errors='ignore').strip()
                            if linie.startswith('{') and linie.endswith('}'):
                                date_json = json.loads(linie)
                                f = int(date_json["fata"])
                                s = int(date_json["stanga"])
                                d = int(date_json["dreapta"])
                                if 2 <= f <= 300: sertar_date["fata"] = f
                                if 2 <= s <= 300: sertar_date["stanga"] = s
                                if 2 <= d <= 300: sertar_date["dreapta"] = d
                                sertar_date["ruta"] = str(date_json["ruta"])
                    except Exception:
                        try: ser.close()
                        except Exception: pass
                        ser = None
                        sertar_date["conectat"] = False
                time.sleep(0.03)

        t = threading.Thread(target=bucla_citire_fundal, daemon=True)
        t.start()
        return sertar_date

    buffer_hardware = porneste_colectorul_serial()
    este_conectat = buffer_hardware["conectat"]
    port_activ = buffer_hardware["port"]

    if este_conectat:
        st.session_state.fata = buffer_hardware["fata"]
        st.session_state.stanga = buffer_hardware["stanga"]
        st.session_state.dreapta = buffer_hardware["dreapta"]
        st.session_state.ruta = buffer_hardware["ruta"]
    else:
        st.session_state.fata = 135
        st.session_state.stanga = 150
        st.session_state.dreapta = 75
        st.session_state.ruta = "INAINTE (Simulare)"

# --- INTERFAȚĂ GRAFICĂ ---
col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Modulul de Decizie MCP")
    if este_conectat:
        st.success(f"Hardware MCP: ACTIVAT (Sursă: {port_activ})")
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

for mesaj in st.session_state.mesaje_chat:
    with st.chat_message(mesaj["rol"]): st.write(mesaj["text"])

intrebare_user = st.chat_input("Interoghează baza de date...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"rol": "user", "text": intrebare_user})
    with st.chat_message("user"): st.write(intrebare_user)

    q = intrebare_user.lower().strip()
    raspuns_ai = ""
    sinonime_hardware = ["conectat", "esp", "hardware", "port", "usb", "placa", "plăcuță", "cablu", "conexiune", "com3"]
    sinonime_distante = ["distant", "senzor", "vezi", "cm", "masor", "măsor", "centimetri", "valori", "radar", "telemetrie", "citeste", "scanare", "scanarea", "mediu", "mediului", "sonar"]
    sinonime_stare = ["stare", "alerta", "alertă", "pericol", "obstacol", "siguranta", "siguranță", "bazaie", "bâzâie", "led", "alarma"]
    sinonime_ruta = ["ruta", "rută", "directia", "direcția", "decizie", "incotro", "încotro", "virezi", "navigrezi", "mergi", "drum", "timp real", "buna ruta", "bună rută", "evitare"]

    if any(cuv in q for cuv in sinonime_hardware):
        if este_conectat: raspuns_ai = f"Sistemul hardware ESP32 este online."
        else: raspuns_ai = "Modulul hardware nu este detectat în portul USB."
    elif any(cuv in q for cuv in sinonime_distante):
        raspuns_ai = f"Telemetria curentă indică: Față: {st.session_state.fata} cm, Stânga: {st.session_state.stanga} cm, Dreapta: {st.session_state.dreapta} cm."
    elif any(cuv in q for cuv in sinonime_stare):
        if st.session_state.fata < 15 or st.session_state.stanga < 15 or st.session_state.dreapta < 15:
            raspuns_ai = "Alertă critică: Obstacol detectat sub 15 cm!"
        else:
            raspuns_ai = f"Stare Nominală: Distanța frontală este sigură ({st.session_state.fata} cm)."
    elif any(cuv in q for cuv in sinonime_ruta):
        raspuns_ai = f"Direcția optimă selectată de algoritm: {st.session_state.ruta}."
    elif any(cuv in q for cuv in ["salut", "buna", "bună", "ce faci", "cine esti", "hello"]):
        raspuns_ai = "Salut! Sunt asistentul tău AI pentru monitorizarea sistemului MCP."
    else:
        raspuns_ai = "Solicitare procesată. Întreabă-mă despre senzori, hardware, rute sau alerte."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    with st.chat_message("assistant"): st.write(raspuns_ai)

time.sleep(0.05)
st.rerun()

