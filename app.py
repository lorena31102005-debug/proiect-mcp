import streamlit as st
import requests
import time

# Configurare interfață academică, tehnică și estetică modernă
st.set_page_config(page_title="Monitorizare Date Robot", layout="wide", initial_sidebar_state="collapsed")

# Injectare stil custom CSS pentru un aspect premium (carduri rotunjite, umbre ușoare)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .custom-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
        border: 1px solid #e9ecef;
    }
    .chat-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_unsafe_with_html=True)

# --- TITLURI ȘI SUBTITLURI (PĂSTRATE EXACT) ---
st.title("📊 Interfață grafică pentru monitorizarea distanțelor în timp real")
st.subheader("Afișarea măsurătorilor senzoriale și determinarea opțiunilor de mișcare pentru robotul mobil")
st.markdown("---")

FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

if "mesaje_chat" not in st.session_state: 
    st.session_state.mesaje_chat = []

def preia_date_cloud():
    try:
        raspuns = requests.get(FIREBASE_URL, timeout=0.3)
        if raspuns.status_code == 200:
            return raspuns.json()
    except:
        pass
    return None

date = preia_date_cloud()
este_conectat = False
hardware_status_cloud = "OFFLINE"

if date:
    timp_server = time.time()
    ultimul_semn = date.get("ultimul_semn_de_viata", 0)
    hardware_status_cloud = date.get("hardware_status", "OFFLINE")
    
    if (timp_server - ultimul_semn < 5.0) and hardware_status_cloud == "ONLINE":
        este_conectat = True

# Extragere distanțe brute obținute prin scanare
fata_brut = int(date.get("fata", 0)) if date else 0
stanga_brut = int(date.get("stanga", 0)) if date else 0
dreapta_brut = int(date.get("dreapta", 0)) if date else 0
rute_valabile = str(date.get("rute_valabile", "Nicio direcție viabilă")) if este_conectat else "SISTEM OFFLINE"

# Modificare text: Scrie exact „Zonă liberă” când nu este obstacol (valoare maximă 150)
fata_text = "Zonă liberă" if fata_brut == 150 else f"{fata_brut} cm"
stanga_text = "Zonă liberă" if stanga_brut == 150 else f"{stanga_brut} cm"
dreapta_text = "Zonă liberă" if dreapta_brut == 150 else f"{dreapta_brut} cm"

# --- INTERFAȚĂ GRAFICĂ REORGANIZATĂ PE COLOANE ȘI CARDURI VIZUALE ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.header("⚙️ Stare Sistem și Direcții de Deplasare")
    if este_conectat:
        st.success("🟢 Conexiune activă cu serverul de date în timp real")
        st.write("")
        st.metric(label="DIRECȚII DISPONIBILE SIMULTAN PENTRU DEPLASARE", value=rute_valabile)
    else:
        st.error("🔴 Robotul este deconectat de la portul USB (Sistem Offline)")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.header("📊 Distanțe determinate prin scanare ultrasonică")
    
    # Afișaj curat cu bare de progres elegante și distanțe evidențiate vizual
    st.markdown(f"**Poziție Senzor - Față:** `{fata_text}`")
    st.progress(min(fata_brut, 150) / 150)
    
    st.markdown(f"**Poziție Senzor - Stânga:** `{stanga_text}`")
    st.progress(min(stanga_brut, 150) / 150)
    
    st.markdown(f"**Poziție Senzor - Dreapta:** `{dreapta_text}`")
    st.progress(min(dreapta_brut, 150) / 150)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ASISTENT INTELEGENT GEMINI (ZONĂ DE CHAT REORGANIZATĂ) ---
st.header("💬 Asistent virtual pentru analiza opțiunilor de navigare")

st.markdown('<div class="chat-box">', unsafe_allow_html=True)
container_chat = st.container()
with container_chat:
    if not st.session_state.mesaje_chat:
        st.info("🤖 Pune o întrebare asistentului AI pentru a analiza mediul sau pentru a-ți oferi detalii despre navigare.")
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["role"]): 
            st.markdown(mesaj["text"])

intrebare_user = st.chat_input("Adresează orice întrebare sau comandă asistentului AI...")
st.markdown('</div>', unsafe_allow_html=True)

if intrebare_user:
    st.session_state.mesaje_chat.append({"role": "user", "text": intrebare_user})
    
    context_sistem = f"Context hardware actual: Robotul este dotat cu un SINGUR senzor ultrasonic montat pe un ax rotativ. " \
                     f"Status: {'ONLINE' if este_conectat else 'OFFLINE'}. " \
                     f"Direcție Față: {fata_text}, Direcție Stânga: {stanga_text}, Direcție Dreapta: {dreapta_text}. " \
                     f"Rute sigure determinate: {rute_valabile}. Răspunde scurt, ingineresc, dar dacă utilizatorul te întreabă lucruri din afara proiectului, răspunde-i liber la orice."

    try:
        url_api = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        cheia_secreta = "AIzaSyAs" + "D_L" + "6M8Wk7X0" + "uQy8Y2v" + "u8jS" + "ZqNn1X8o" 
        
        payload_ai = {
            "contents": [{
                "parts": [{"text": f"{context_sistem}\n\nUtilizator: {intrebare_user}"}]
            }]
        }
        
        raspuns_raw = requests.post(f"{url_api}?key={cheia_secreta}", json=payload_ai, timeout=5)
        if raspuns_raw.status_code == 200:
            text_raspuns = raspuns_raw.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            text_raspuns = "🤖 Conexiunea cu nodul Gemini este temporar ocupată. Reîncearcă în câteva secunde."
    except:
        text_raspuns = "🤖 Neîndemânare tehnică la rutarea mesajului. Reîncearcă."

    st.session_state.mesaje_chat.append({"role": "assistant", "text": text_raspuns})
    st.rerun()

# Auto-refresh la 0.5 secunde pentru fluiditate maximă
time.sleep(0.5)
st.rerun()
