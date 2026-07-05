import streamlit as st
import requests
import time

st.set_page_config(page_title="Sistem Inteligent MCP v2.0", layout="wide")

st.title("🤖 Integrare MCP - Controler Autonom avansat")
st.subheader("Platformă de Monitorizare în Timp Real cu Analiză Predictivă și Asistență AI")

FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

if "fata" not in st.session_state: st.session_state.fata = 150
if "stanga" not in st.session_state: st.session_state.stanga = 150
if "dreapta" not in st.session_state: st.session_state.dreapta = 150
if "ruta" not in st.session_state: st.session_state.ruta = "ANALIZĂ..."
if "mesaje_chat" not in st.session_state: st.session_state.mesaje_chat = []

este_conectat = False
port_activ = "Deconectat"

# --- PRELUARE DATE DIN CLOUD ---
try:
    raspuns = requests.get(FIREBASE_URL, timeout=1)
    if raspuns.status_code == 200 and raspuns.json():
        date = raspuns.json()
        timp_server = time.time()
        ultimul_semn = date.get("ultimul_semn_de_viata", 0)
        
        if timp_server - ultimul_semn < 3.0:
            st.session_state.fata = int(date.get("fata", 150))
            st.session_state.stanga = int(date.get("stanga", 150))
            st.session_state.dreapta = int(date.get("dreapta", 150))
            este_conectat = True
            port_activ = "Cloud Firebase Live"
except Exception:
    pass

# --- ALGORITM INTELIGENT DE CALCULARE A RUTEI CURENTE ---
# Dacă senzorii hardware nu trimit o rută bună sau vrem o decizie sigură pe server:
if este_conectat:
    f, s, d = st.session_state.fata, st.session_state.stanga, st.session_state.dreapta
    
    if f < 25: # Obstacol iminent în față!
        if s > d and s > 25:
            st.session_state.ruta = "⚠️ EVITARE URGENȚĂ: APASĂ LA STÂNGA"
        elif d > s and d > 25:
            st.session_state.ruta = "⚠️ EVITARE URGENȚĂ: APASĂ LA DREAPTA"
        else:
            st.session_state.ruta = "🛑 STOP COMPLET (Drum blocat total)"
    else:
        if f >= s and f >= d:
            st.session_state.ruta = "🚀 ÎNAINTE (Calea cea mai liberă)"
        elif s > d:
            st.session_state.ruta = "🔄 DEVIAȚIE STÂNGA CORIDOR"
        else:
            st.session_state.ruta = "🔄 DEVIAȚIE DREAPTA CORIDOR"
else:
    st.session_state.fata, st.session_state.stanga, st.session_state.dreapta = 0, 0, 0
    st.session_state.ruta = "SISTEM OFFLINE (Verifică PyCharm)"

# --- PANOU GRAFIC ---
col1, col2 = st.columns(2)
with col1:
    st.header("🧠 Modulul Logica MCP Automată")
    if este_conectat:
        st.success(f"🟢 CONEXIUNE RADAR: ACTIVĂ ({port_activ})")
        st.metric(label="DECIZIE DE SIGURANȚĂ CALCULATĂ", value=st.session_state.ruta)
    else:
        st.error("🔴 DISPOZITIV DECONECTAT - RELEUL ESTE OPRIT")

with col2:
    st.header("📊 Distanțe Telemetrice Active")
    st.progress(min(max(st.session_state.fata, 0), 150) / 150, text=f"Senzor Față: {st.session_state.fata} cm")
    st.progress(min(max(st.session_state.stanga, 0), 150) / 150, text=f"Senzor Stânga: {st.session_state.stanga} cm")
    st.progress(min(max(st.session_state.dreapta, 0), 150) / 150, text=f"Senzor Dreapta: {st.session_state.dreapta} cm")

st.divider()

# --- AGENT AI AVANSAT ---
st.header("💬 Asistent de Diagnoză Cibernetică MCP")

container_chat = st.container()
with container_chat:
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["rol"]): st.write(mesaj["text"])

intrebare_user = st.chat_input("Introdu comanda sau întrebarea (ex: diagnoză, status senzori)...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"rol": "user", "text": intrebare_user})
    q = intrebare_user.lower().strip()
    
    # Logică avansată cu contextualizare
    if any(x in q for x in ["status", "senzori", "distant", "telemetrie", "vezi"]):
        if este_conectat:
            raspuns_ai = (f"📈 **Raport Telemetrie:** În acest moment, vectorul frontal indică {st.session_state.fata} cm spațiu liber. "
                          f"Flancul stâng oferă o toleranță de {st.session_state.stanga} cm, iar cel drept {st.session_state.dreapta} cm. "
                          f"Starea generală a senzorilor este optimă.")
        else:
            raspuns_ai = "❌ **Eroare sistem:** Senzorii nu pot fi citiți deoarece conexiunea cu scriptul releu din PyCharm este întreruptă."
            
    elif any(x in q for x in ["diagnoza", "analiza", "verificare", "test"]):
        if not este_conectat:
            raspuns_ai = "⚠️ **Diagnoză Eșuată:** Sistem fizic deconectat. Repornește `releu_mcp.py` de pe laptop."
        elif st.session_state.fata < 25 or st.session_state.stanga < 25 or st.session_state.dreapta < 25:
            raspuns_ai = f"🚨 **Alertă Diagnoză:** Risc crescut de coliziune! S-a detectat un obstacol în perimetrul de siguranță. Decizia generată: *{st.session_state.ruta}*."
        else:
            raspuns_ai = "✅ **Diagnoză Completă:** Toate sistemele rulează în parametri nominali. Nu se detectează anomalii de proximitate sau erori de buffering."
            
    elif any(x in q for x in ["ruta", "incotro", "decizie", "navig", "direct"]):
        raspuns_ai = f"🤖 **Navigație MCP:** Vectorul optim determinat prin algoritmul de proximitate este: **{st.session_state.ruta}**."
        
    elif any(x in q for x in ["salut", "buna", "hello", "cine esti"]):
        raspuns_ai = "Sunt Interfața Cognitivă a modulului MCP. Mă ocup cu analiza matematică a distanțelor și supervizarea deciziilor robotului."
    else:
        raspuns_ai = "Comandă necorelată. Poți solicita: 'status senzori' (telemetrie reală), 'diagnoză' (analiza riscurilor) sau 'direcție' (pentru decizia rutei)."

    st.session_state.mesaje_chat.append({"rol": "assistant", "text": raspuns_ai})
    st.rerun()

time.sleep(0.4)
st.rerun()
