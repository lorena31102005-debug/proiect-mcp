import streamlit as st
import requests
import time

st.set_page_config(page_title="Monitorizare Date Robot", layout="wide")

st.title("📊 Interfață grafică pentru monitorizarea distanțelor în timp real")
st.subheader("Afișarea măsurătorilor senzoriale și determinarea opțiunilor de mișcare pentru robotul mobil")

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

fata_brut = int(date.get("fata", 0)) if date else 0
stanga_brut = int(date.get("stanga", 0)) if date else 0
dreapta_brut = int(date.get("dreapta", 0)) if date else 0
rute_valabile = str(date.get("rute_valabile", "Nicio direcție viabilă")) if este_conectat else "SISTEM OFFLINE"

fata_text = "Zonă liberă" if fata_brut == 150 else f"{fata_brut} cm"
stanga_text = "Zonă liberă" if stanga_brut == 150 else f"{stanga_brut} cm"
dreapta_text = "Zonă liberă" if dreapta_brut == 150 else f"{dreapta_brut} cm"

col1, col2 = st.columns(2)
with col1:
    st.header("⚙️ Stare Sistem și Direcții de Deplasare")
    if este_conectat:
        st.success("🟢 Conexiune activă cu serverul de date în timp real")
        st.metric(label="DIRECȚII DISPONIBILE SIMULTAN PENTRU DEPLASARE", value=rute_valabile)
    else:
        st.error("🔴 Robotul este deconectat de la portul USB (Sistem Offline)")

with col2:
    st.header("📊 Distanțe determinate prin scanare ultrasonică")
    st.progress(min(fata_brut, 150) / 150, text=f"Poziție Senzor - Față: {fata_text}")
    st.progress(min(stanga_brut, 150) / 150, text=f"Poziție Senzor - Stânga: {stanga_text}")
    st.progress(min(dreapta_brut, 150) / 150, text=f"Poziție Senzor - Dreapta: {dreapta_text}")

st.divider()

st.header("💬 Asistent virtual pentru analiza opțiunilor de navigare")

container_chat = st.container()
with container_chat:
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["role"]):
            st.markdown(mesaj["text"])

intrebare_user = st.chat_input("Adresează orice întrebare sau comandă asistentului AI...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"role": "user", "text": intrebare_user})
    context_sistem = f"Robotul mobil cu un singur senzor rotativ. Status: {'ONLINE' if este_conectat else 'OFFLINE'}. Fata: {fata_text}, Stanga: {stanga_text}, Dreapta: {dreapta_text}. Rute: {rute_valabile}. Răspunde scurt în română."
    
    try:
        CHEIE_API = st.secrets["GEMINI_KEY"]
        
        # URL corectat complet conform noilor cerințe v1beta
        url_api = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        antete = {
            "Content-Type": "application/json",
            "x-goog-api-key": CHEIE_API
        }
        
        payload_ai = {"contents": [{"parts": [{"text": f"{context_sistem}\n\nUtilizator: {intrebare_user}"}]}]}
        
        raspuns_raw = requests.post(url_api, json=payload_ai, headers=antete, timeout=5)
        if raspuns_raw.status_code == 200:
            text_raspuns = raspuns_raw.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            text_raspuns = f"🤖 Serverul Google a răspuns cu codul {raspuns_raw.status_code}. Te rog verifică cheia din Secrets."
    except Exception as e:
        text_raspuns = "🤖 Nu s-a putut citi variabila GEMINI_KEY din Secrets."

    st.session_state.mesaje_chat.append({"role": "assistant", "text": text_raspuns})
    st.rerun()

time.sleep(0.5)
st.rerun()
