import streamlit as st
import requests
import time

st.set_page_config(page_title="Sistem Inteligent MCP v2.0", layout="wide")

st.title("🤖 Integrare MCP - Controler Autonom avansat")
st.subheader("Platformă de Monitorizare în Timp Real cu Analiză Predictivă și Asistență AI")

FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

# Inițializare variabile de sesiune
if "fata" not in st.session_state: st.session_state.fata = 150
if "stanga" not in st.session_state: st.session_state.stanga = 150
if "dreapta" not in st.session_state: st.session_state.dreapta = 150
if "ruta" not in st.session_state: st.session_state.ruta = "ANALIZĂ..."
if "mesaje_chat" not in st.session_state: st.session_state.mesaje_chat = []

este_conectat = False
port_activ = "Deconectat"

# Preluare date din Firebase cu optimizare cache scurtă pentru eliminarea lag-ului
def preia_date_cloud():
    try:
        raspuns = requests.get(FIREBASE_URL, timeout=0.3)
        if raspuns.status_code == 200:
            return raspuns.json()
    except Exception:
        pass
    return None

date = preia_date_cloud()
if date:
    timp_server = time.time()
    ultimul_semn = date.get("ultimul_semn_de_viata", 0)
    
    # Toleranță de 5 secunde pentru semnalul live
    if timp_server - ultimul_semn < 5.0:
        st.session_state.fata = int(date.get("fata", 150))
        st.session_state.stanga = int(date.get("stanga", 150))
        st.session_state.dreapta = int(date.get("dreapta", 150))
        st.session_state.ruta = str(date.get("ruta", "INAINTE"))
        este_conectat = True
        port_activ = "Cloud Firebase Live"

# Dacă sistemul e deconectat, resetăm vizual distanțele
if not este_conectat:
    st.session_state.fata, st.session_state.stanga, st.session_state.dreapta = 0, 0, 0
    st.session_state.ruta = "SISTEM OFFLINE (Verifică PyCharm)"

# --- PANOU GRAFIC IDENTIC CU CEL INITIAL ---
col1, col2 = st.columns(2)
with col1:
    st.header("🧠 Modulul de Decizie MCP")
    if este_conectat:
        st.success(f"🟢 Hardware MCP: ACTIVAT (Sursă: {port_activ})")
        st.metric(label="RUTĂ OPTIMĂ DE NAVIGARE CALCULATĂ", value=st.session_state.ruta)
    else:
        st.error("🔴 DISPOZITIV DECONECTAT - RELEUL ESTE OPRIT")

with col2:
    st.header("📊 Distanța Măsurată")
    st.progress(min(max(st.session_state.fata, 0), 150) / 150, text=f"Distanță Față: {st.session_state.fata} cm")
    st.progress(min(max(st.session_state.stanga, 0), 150) / 150, text=f"Distanță Stânga: {st.session_state.stanga} cm")
    st.progress(min(max(st.session_state.dreapta, 0), 150) / 150, text=f"Distanță Dreapta: {st.session_state.dreapta} cm")

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
    
    if any(x in q for x in ["status", "senzori", "distant", "telemetrie", "vezi"]):
        if este_conectat:
            raspuns_ai = (f"📈 **Raport Telemetrie:** În acest moment, senzorul frontal indică {st.session_state.fata} cm. "
                          f"Flancul stâng oferă {st.session_state.stanga} cm, iar cel drept {st.session_state.dreapta} cm.")
        else:
            raspuns_ai = "❌ **Eroare:** Sistem fizic deconectat. Datele nu sunt disponibile."
            
    elif any(x in q for x in ["diagnoza", "analiza", "verificare"]):
        if not este_conectat:
            raspuns_ai = "⚠️ **Diagnoză imposibilă:** Robotul este offline."
        elif st.session_state.fata < 20 or st.session_state.stanga < 20 or st.session_state.dreapta < 20:
            raspuns_ai = f"🚨 **Alertă:** Distanță critică detectată! Ruta recomandată: *{st.session_state.ruta}*."
        else:
            raspuns_ai = "✅ **Diagnoză nominală:** Toți senzorii raportează distanțe sigure. Drumul este liber."
            
    elif any(x in q for x in ["ruta", "incotro", "decizie", "directie"]):
        raspuns_ai = f"🤖 **Navigație:** Decizia curentă a algoritmului este: **{st.session_state.ruta}**."
        
    elif any(x in q for x in ["salut", "buna", "hello"]):
        raspuns_ai = "Salut! Sunt interfața ta AI. Îmi poți cere o 'diagnoză' sau un status pentru senzori."
    else:
        raspuns_ai = "Comandă nerecunoscută. Încearcă: 'status senzori' sau 'diagnoză'."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    st.rerun()

# Pauză optimă (0.3s) pentru a elimina complet lag-ul de randare al browserului
time.sleep(0.3)
st.rerun()
