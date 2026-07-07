import streamlit as st
import requests
import time
import google.generativeai as genai

# Configurare titlu conform noilor cerințe ale proiectului
st.set_page_config(page_title="Platformă de Monitorizare în Timp Real", layout="wide")

st.title("🤖 Platformă de monitorizare în timp real cu analiza distanței, alegerea celei mai bune rute și asistență AI")
st.subheader("Sistem avansat de diagnoză și analiză contextuală asistat de Inteligență Artificială")

FIREBASE_URL = "https://proiect-mcp-default-rtdb.firebaseio.com/robot.json"

# CONFIGURARE CHEIE API GEMINI (Pune cheia ta reală aici)
GEMINI_API_KEY = "CHEIA_TA_API_REALA_AICI"
genai.configure(api_key=GEMINI_API_KEY)

# Inițializare variabile de sesiune
if "fata" not in st.session_state: st.session_state.fata = 150
if "stanga" not in st.session_state: st.session_state.stanga = 150
if "dreapta" not in st.session_state: st.session_state.dreapta = 150
if "ruta" not in st.session_state: st.session_state.ruta = "ANALIZĂ..."
if "mesaje_chat" not in st.session_state: st.session_state.mesaje_chat = []

este_conectat = False
port_activ = "Deconectat"

# Preluare date din Firebase
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
    st.session_state.ruta = "DISPOZITIV DECONECTAT (Verifică scriptul principal)"

# --- PANOU GRAFIC REZOLVAT (FĂRĂ RELEU) ---
col1, col2 = st.columns(2)
with col1:
    st.header("🧠 Modulul de Decizie")
    if este_conectat:
        st.success(f"🟢 Hardware Dispozitiv: ACTIVAT (Sursă: {port_activ})")
        st.metric(label="RUTĂ OPTIMĂ DE NAVIGARE CALCULATĂ", value=st.session_state.ruta)
    else:
        st.error("🔴 DISPOZITIV DECONECTAT - SISTEMUL ESTE OFFLINE")

with col2:
    st.header("📊 Distanța Măsurată")
    st.progress(min(max(st.session_state.fata, 0), 150) / 150, text=f"Distanță Față: {st.session_state.fata} cm")
    st.progress(min(max(st.session_state.stanga, 0), 150) / 150, text=f"Distanță Stânga: {st.session_state.stanga} cm")
    st.progress(min(max(st.session_state.dreapta, 0), 150) / 150, text=f"Distanță Dreapta: {st.session_state.dreapta} cm")

st.divider()

# --- ASISTENT VIRTUAL INTELIGENT (INTEGRARE LLM GEMINI) ---
st.header("💬 Asistent Virtual AI - Diagnoză Contextuală")

container_chat = st.container()
with container_chat:
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["rol"]): 
            st.markdown(mesaj["text"])

intrebare_user = st.chat_input("Adresează o întrebare tehnică asistentului AI...")
if intrebare_user:
    # 1. Adăugăm mesajul utilizatorului în istoric
    st.session_state.mesaje_chat.append({"role": "user", "text": intrebare_user})
    
    # 2. PROMPT ENGINEERING: Construim contextul dinamic pe care AI-ul îl va analiza
    prompt_sistem = f"""
    Tu ești Agentul AI de Navigare și Inginerul de Bord al unui robot autonom.
    
    STARE HARDWARE CURENTĂ:
    - Dispozitiv conectat: {este_conectat}
    - Distanță Față: {st.session_state.fata} cm
    - Distanță Stânga: {st.session_state.stanga} cm
    - Distanță Dreapta: {st.session_state.dreapta} cm
    - Rută hardware actuală: {st.session_state.ruta}
    
    REGULI DE RĂSPUNS:
    - Răspunde pe un ton tehnic, ingineresc, dar ușor de înțeles.
    - NU repeta doar cifrele brute. Analizează spațiul descris de ele (de exemplu: dacă e un colț strâmt, dacă e drum liber, de ce ruta aleasă e cea mai bună din punct de vedere geometric sau cinematic).
    - Dacă dispozitivul este deconectat, menționează că nu poți face o analiză în timp real deoarece sistemul este offline.
    """
    
    # 3. Trimitem totul către modelul AI
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        raspuns_ai = model.generate_content(f"{prompt_sistem}\n\nÎntrebare utilizator: {intrebare_user}")
        text_raspuns = raspuns_ai.text
    except Exception as e:
        text_raspuns = f"⚠️ Nu am putut contacta nucleul AI. Verifică cheia API. Detalii: {str(e)}"

    # 4. Salvăm răspunsul generat și dăm refresh fluid paginii
    st.session_state.mesaje_chat.append({"role": "assistant", "text": text_raspuns})
    st.rerun()

# Menținem auto-refresh-ul pentru sincronizarea live cu Firebase
time.sleep(0.3)
st.rerun()
