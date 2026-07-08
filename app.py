import streamlit as st
import requests
import time
import difflib

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
    
    # Intențiile utilizatorului procesate prin NLP local
    intrebare_curata = intrebare_user.lower().strip()
    
    # Matrice de răspunsuri dinamice bazate pe starea curentă a senzorilor
    if any(cuvant in intrebare_curata for cuvant in ["salut", "buna", "hei", "hello"]):
        text_raspuns = "🤖 Salut! Sunt asistentul tău de navigare. Cu ce te pot ajuta astăzi în monitorizarea robotului?"
        
    elif any(cuvant in intrebare_curata for cuvant in ["fata", "față", "obstacol", "obiect"]):
        text_raspuns = f"🤖 Analiza senzorului frontal: În față avem o distanță de {fata_text}. "
        if fata_brut < 40:
            text_raspuns += "Atenție, spațiul este critic! Robotul trebuie să oprească sau să vireze."
        else:
            text_raspuns += "Drumul înainte este relativ sigur."
            
    elif any(cuvant in intrebare_curata for cuvant in ["stanga", "stânga", "dreapta"]):
        text_raspuns = f"🤖 Analiza laterală în timp real: În stânga senzorul indică {stanga_text}, iar în dreapta avem {dreapta_text}."
        
    elif any(cuvant in intrebare_curata for cuvant in ["status", "conectat", "online", "functional", "stare"]):
        if este_conectat:
            text_raspuns = f"🤖 Sistemul este ONLINE. Conexiunea cu Firebase este stabilă, iar rutele recomandate acum sunt: {rute_valabile}."
        else:
            text_raspuns = "🤖 În prezent sistemul hardware este OFFLINE. Verifică conexiunea cablului USB la robot."
            
    elif any(cuvant in intrebare_curata for cuvant in ["incotro", "încotro", "unde", "ruta", "navig", "deplas", "miscare", "mișcare"]):
        if not este_conectat:
            text_raspuns = "🤖 Robotul fiind offline, nu pot calcula rute sigure în acest moment."
        else:
            text_raspuns = f"🤖 Pe baza analizei spațiale, senzorii recomandă direcțiile: **{rute_valabile}**. "
            if "Nicio" in rute_valabile:
                text_raspuns += "Suntem blocați complet, recomand retragerea cu spatele!"
            elif len(rute_valabile.split(",")) > 1:
                text_raspuns += "Ai opțiuni multiple libere, poți continua deplasarea cu încredere."
            else:
                text_raspuns += f"Urmează strict calea către {rute_valabile}."
    else:
        # Răspuns inteligent implicit (Fallback) care combină toate datele dinamice
        text_raspuns = f"🤖 Am analizat solicitarea ta. Date curente: Față ({fata_text}), Stânga ({stanga_text}), Dreapta ({dreapta_text}). Status: {'ONLINE' if este_conectat else 'OFFLINE'}. Direcții optime: {rute_valabile}."

    st.session_state.mesaje_chat.append({"role": "assistant", "text": text_raspuns})
    st.rerun()

time.sleep(0.5)
st.rerun()
