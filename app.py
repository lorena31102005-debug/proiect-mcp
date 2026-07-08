import streamlit as st
import requests
import time
import google.generativeai as genai

# Configurare interfață academică și tehnică (Conform cerințelor stabilite)
st.set_page_config(page_title="Monitorizare Date Robot", layout="wide")

st.title("📊 Interfață grafică pentru monitorizarea distanțelor în timp real")
st.subheader("Afișarea măsurătorilor senzoriale și determinarea opțiunilor de mișcare pentru robotul mobil")

FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

# ⚠️ ÎNLOCUIEȘTE CU CHEIA TA REALĂ GEMINI DIN GOOGLE AI STUDIO
GEMINI_API_KEY = "CHEIA_TA_API_REALA_AICI"
genai.configure(api_key=GEMINI_API_KEY)

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
    
    # Confirmare conexiune dacă scriptul local trimite date (toleranță 5 secunde)
    if (timp_server - ultimul_semn < 5.0) and hardware_status_cloud == "ONLINE":
        este_conectat = True

# Extragere distanțe brute
fata_brut = int(date.get("fata", 0)) if date else 0
stanga_brut = int(date.get("stanga", 0)) if date else 0
dreapta_brut = int(date.get("dreapta", 0)) if date else 0
rute_valabile = str(date.get("rute_valabile", "Nicio direcție viabilă")) if este_conectat else "SISTEM OFFLINE"

# Modificare text: Scrie exact „Zonă liberă” când nu este obstacol (valoarea 150)
fata_text = "Zonă liberă" if fata_brut == 150 else f"{fata_brut} cm"
stanga_text = "Zonă liberă" if stanga_brut == 150 else f"{stanga_brut} cm"
dreapta_text = "Zonă liberă" if dreapta_brut == 150 else f"{dreapta_brut} cm"

# --- INTERFAȚĂ GRAFICĂ DEFINITIVĂ ---
col1, col2 = st.columns(2)
with col1:
    st.header("⚙️ Stare Sistem și Direcții de Deplasare")
    if este_conectat:
        st.success("🟢 Conexiune activă cu serverul de date în timp real")
        st.metric(label="DIRECȚII DISPONIBILE SIMULTAN PENTRU DEPLASARE", value=rute_valabile)
    else:
        st.error("🔴 Robotul este deconectat de la portul USB (Sistem Offline)")

with col2:
    st.header("📊 Distanțe determinate de senzorii ultrasonici")
    # Barele de progres: când e "Zonă liberă", calculul dă 150/150 = 1.0 (Bara se umple 100%)
    st.progress(min(fata_brut, 150) / 150, text=f"Senzor Față: {fata_text}")
    st.progress(min(stanga_brut, 150) / 150, text=f"Senzor Stânga: {stanga_text}")
    st.progress(min(dreapta_brut, 150) / 150, text=f"Senzor Dreapta: {dreapta_text}")

st.divider()

# --- ASISTENT VIRTUAL INTELIGENT REPARAT ---
st.header("💬 Asistent virtual pentru analiza opțiunilor de navigare")

container_chat = st.container()
with container_chat:
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["role"]): 
            st.markdown(mesaj["text"])

intrebare_user = st.chat_input("Adresează o întrebare despre opțiunile de mișcare ale robotului...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"role": "user", "text": intrebare_user})
    
    prompt_sistem = f"""
    Tu ești o componentă software configurată ca asistent tehnic pentru un model de robot mobil dotat cu senzori ultrasonici.
    
    DATE REALE DIN ACHIZIȚIA CURENTĂ:
    - Status conexiune hardware: {"ONLINE" if este_conectat else "OFFLINE"}
    - Distanță Citită Față: {fata_text}
    - Distanță Citită Stânga: {stanga_text}
    - Distanță Citită Dreapta: {dreapta_text}
    - Direcții considerate libere geometric în acest moment: {rute_valabile}
    
    REGULI DE COMPORTAMENT ÎN CHAT:
    1. Adoptă un limbaj simplu, concis, strict ingineresc. Fără cuvinte comerciale nerealiste.
    2. Dacă o distanță este afișată ca fiind 'Zonă liberă', explică faptul că în acea direcție nu sunt detectate obstacole pe o rază de 1.5 metri.
    3. Oferă suport bazat strict pe valorile numerice de mai sus, analizând toate opțiunile de mișcare în mod simultan.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        raspuns_ai = model.generate_content(f"{prompt_sistem}\n\nComandă utilizator: {intrebare_user}")
        text_raspuns = raspuns_ai.text
    except Exception as e:
        text_raspuns = f"⚠️ Asistentul virtual a întâmpinat o eroare la generare. Detalii tehnice: {str(e)}"

    st.session_state.mesaje_chat.append({"role": "assistant", "text": text_raspuns})
    st.rerun()

# Auto-refresh la jumătate de secundă pentru sincronizarea datelor în timp real
time.sleep(0.5)
st.rerun()
