import streamlit as st
import requests
import time

# Configurare panou MCP pe tot ecranul
st.set_page_config(page_title="Sistem MCP - Interfață Robotică", layout="wide")

st.title("🤖 Integrare MCP cu Sisteme Robotice")
st.subheader("Platformă Demonstrativă pentru Monitorizare în Timp Real, Calcularea Rutei și Asistență AI")

# Acesta este "sertarul" comun unde ESP32 pune datele, iar Python le citește
DWEET_THING_NAME = "proiect_mcp_esp32_2026_xyz"

# Inițializare memorie Streamlit
if "fata" not in st.session_state:
    st.session_state.fata = 150
    st.session_state.stanga = 150
    st.session_state.dreapta = 150
    st.session_state.ruta = "ANALIZĂ..."
    st.session_state.mesaje_chat = []


# --- PRELUARE DATE DIN CLOUD ---
def preia_date_cloud():
    try:
        url = f"https://dweet.io/get/latest/dweet/for/{DWEET_THING_NAME}"
        raspuns = requests.get(url, timeout=2)
        if raspuns.status_code == 200:
            date = raspuns.json()
            if "with" in date and len(date["with"]) > 0:
                continut = date["with"][0]["content"]
                return continut, True
    except Exception:
        pass
    return None, False


date_hardware, este_conectat = preia_date_cloud()

if este_conectat and date_hardware:
    # Salvăm datele primite prin Wi-Fi de la ESP32
    st.session_state.fata = int(date_hardware.get("fata", 150))
    st.session_state.stanga = int(date_hardware.get("stanga", 150))
    st.session_state.dreapta = int(date_hardware.get("dreapta", 150))
    st.session_state.ruta = str(date_hardware.get("ruta", "NECUNOSCUT"))
    port_activ = "Conexiune Cloud (Hotspot Activ)"
else:
    # Dacă ESP32 este scos din priză sau nu are net
    port_activ = "Deconectat"

# --- INTERFAȚĂ GRAFICĂ ---
col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Modulul de Decizie MCP")
    if este_conectat:
        st.success(f"Hardware MCP: ONLINE (Sursă: {port_activ})")
    else:
        st.error("Hardware MCP: OFFLINE (Aștept conexiune de la ESP32...)")

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

# Afișarea istoricului de chat
for mesaj in st.session_state.mesaje_chat:
    with st.chat_message(mesaj["rol"]):
        st.write(mesaj["text"])

# Logica de răspuns pentru AI
intrebare_user = st.chat_input("Interoghează baza de date...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"rol": "user", "text": intrebare_user})
    with st.chat_message("user"):
        st.write(intrebare_user)

    q = intrebare_user.lower().strip()
    raspuns_ai = ""

    if any(cuv in q for cuv in ["conectat", "esp", "hardware", "port"]):
        if este_conectat:
            raspuns_ai = "Sistemul hardware ESP32 este online și comunică prin Cloud."
        else:
            raspuns_ai = "Modulul hardware nu este detectat activ în Cloud."
    elif any(cuv in q for cuv in ["distant", "senzor", "cm", "valori"]):
        raspuns_ai = f"Telemetria curentă indică: Față: {st.session_state.fata} cm, Stânga: {st.session_state.stanga} cm, Dreapta: {st.session_state.dreapta} cm."
    elif any(cuv in q for cuv in ["stare", "alerta", "pericol", "obstacol"]):
        if st.session_state.fata < 15 or st.session_state.stanga < 15 or st.session_state.dreapta < 15:
            raspuns_ai = "Alertă critică: Obstacol detectat sub 15 cm!"
        else:
            raspuns_ai = f"Stare Nominală: Distanța frontală este sigură ({st.session_state.fata} cm)."
    elif any(cuv in q for cuv in ["ruta", "directia", "decizie"]):
        raspuns_ai = f"Direcția optimă selectată de algoritm: {st.session_state.ruta}."
    else:
        raspuns_ai = "Solicitare procesată. Întreabă-mă despre senzori, hardware, rute sau alerte."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    with st.chat_message("assistant"):
        st.write(raspuns_ai)

# Actualizează pagina automat și rapid ca să prinzi mișcarea fluidă a motorului
time.sleep(1)
st.rerun()
