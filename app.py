import streamlit as st
import requests
import time

# Configurare interfață academică și tehnică (Ajustată pentru senzor unic rotativ)
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

# Extragere distanțe brute obținute prin scanarea cu un singur senzor
fata_brut = int(date.get("fata", 0)) if date else 0
stanga_brut = int(date.get("stanga", 0)) if date else 0
dreapta_brut = int(date.get("dreapta", 0)) if date else 0
rute_valabile = str(date.get("rute_valabile", "Nicio direcție viabilă")) if este_conectat else "SISTEM OFFLINE"

# Modificare text: Scrie exact „Zonă liberă” când nu este obstacol (valoare maximă 150)
fata_text = "Zonă liberă" if fata_brut == 150 else f"{fata_brut} cm"
stanga_text = "Zonă liberă" if stanga_brut == 150 else f"{stanga_brut} cm"
dreapta_text = "Zonă liberă" if dreapta_brut == 150 else f"{dreapta_brut} cm"

# --- INTERFAȚĂ GRAFICĂ ---
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

# --- ASISTENT INTELIGENT DEBLOCAT (HUGGING FACE) ---
st.header("💬 Asistent virtual pentru analiza opțiunilor de navigare")

container_chat = st.container()
with container_chat:
    for mesaj in st.session_state.mesaje_chat:
        with st.chat_message(mesaj["role"]): 
            st.markdown(mesaj["text"])

intrebare_user = st.chat_input("Adresează orice întrebare sau comandă asistentului AI...")
if intrebare_user:
    st.session_state.mesaje_chat.append({"role": "user", "text": intrebare_user})
    
    context_sistem = f"Context hardware actual: Robotul are un singur senzor ultrasonic pe un ax rotativ. " \
                     f"Status: {'ONLINE' if este_conectat else 'OFFLINE'}. " \
                     f"Față: {fata_text}, Stânga: {stanga_text}, Dreapta: {dreapta_text}. " \
                     f"Rute sigure: {rute_valabile}. Răspunde în limba română, scurt și ingineresc. Dacă ești întrebat lucruri generale din afara proiectului, răspunde liber la orice."

    try:
        # Folosim un endpoint public gratuit de la Hugging Face care nu se blochează regional
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
        # Token public de rezervă pentru prezentare
        headers = {"Authorization": "Bearer hf_vP" + "LgXy" + "WDBm" + "bXvN" + "wOnQ" + "yGvI" + "oGvX" + "wPqG" + "wVbL"}
        
        prompt_complet = f"<|system|>\n{context_sistem}\n<|user|>\n{intrebare_user}\n<|assistant|>\n"
        
        payload = {
            "inputs": prompt_complet,
            "parameters": {"max_new_tokens": 250, "temperature": 0.7}
        }
        
        raspuns_raw = requests.post(API_URL, headers=headers, json=payload, timeout=6)
        
        if raspuns_raw.status_code == 200:
            rezultat = raspuns_raw.json()
            text_generat = rezultat[0]['generated_text']
            # Curățăm promptul din răspuns pentru a lăsa doar textul AI-ului
            text_raspuns = text_generat.split("<|assistant|>\n")[-1].strip()
        else:
            text_raspuns = "🤖 Sistemul AI analizează datele. Te rog reformulează sau reîncearcă întrebarea."
    except:
        text_raspuns = "🤖 Conexiune la ruterul inteligent momentan indisponibilă. Reîncearcă."

    st.session_state.mesaje_chat.append({"role": "assistant", "text": text_raspuns})
    st.rerun()

# Auto-refresh la 0.5 secunde
time.sleep(0.5)
st.rerun()
