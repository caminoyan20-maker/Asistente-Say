import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"

# Lee las claves de forma segura desde los Secrets de Streamlit Cloud
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neon Voice v2.6",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS Cyberpunk y optimización visual
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

        .stApp {
            font-family: 'Rajdhani', sans-serif;
            background: radial-gradient(circle at 50% 25%, #180b33 0%, #0a0418 55%, #030108 100%);
            color: #ffffff;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Título Neón SAY */
        .title-say {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.15em;
            color: #12edff;
            text-shadow: 
                0 0 5px #00f0ff,
                0 0 15px #00f0ff,
                0 0 30px #0088ff,
                0 0 50px #ec4899;
            -webkit-text-stroke: 1px #ff2a8d;
            text-align: center;
            font-size: 3rem;
            font-weight: 900;
        }

        .cyber-subtitle {
            font-family: 'Share Tech Mono', monospace;
            text-align: center;
            color: #38bdf8;
            font-size: 0.75rem;
            letter-spacing: 0.25em;
            margin-bottom: 1.5rem;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.8);
        }

        .hud-panel {
            background: rgba(8, 14, 28, 0.92);
            border: 1px solid rgba(0, 240, 255, 0.5);
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.3), inset 0 0 15px rgba(0, 240, 255, 0.15);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(20px);
            font-family: 'Share Tech Mono', monospace;
        }

        .stChatMessage {
            background: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid rgba(0, 240, 255, 0.3) !important;
            border-radius: 12px !important;
            color: #e0f7fc !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


def cargar_usuarios():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {}


def guardar_usuarios(usuarios):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(usuarios, f, indent=4)


def consultar_gemini_con_pool(mensaje):
  if not MASTER_KEYS:
    return (
        "❌ Error: Configura tus claves en la sección 'Secrets' de Streamlit"
        " Cloud."
    )

  for api_key in MASTER_KEYS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"role": "user", "parts": [{"text": mensaje}]}]}
    data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
      with urllib.request.urlopen(req) as response:
        res_body = response.read().decode("utf-8")
        data = json.loads(res_body)
        return (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )
    except Exception:
      continue

  return "❌ Lo sentimos, las claves del sistema están ocupadas temporalmente."


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

# Encabezado Visual Cyber Neon
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Cybernetic Neural Interface & Voice v2.6'
    " ]</div>",
    unsafe_allow_html=True,
)

usuarios = cargar_usuarios()

# Control de Autenticación
if st.session_state.usuario_actual is None:
  st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
  tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

  with tab1:
    st.subheader("Accede a tu cuenta")
    username_in = st.text_input("Usuario", key="login_user")
    password_in = st.text_input(
        "Contraseña", type="password", key="login_pass"
    )

    if st.button("Entrar al Sistema", use_container_width=True):
      if (
          username_in in usuarios
          and usuarios[username_in]["password"] == password_in
      ):
        st.session_state.usuario_actual = username_in
        st.success(f"¡Bienvenido, {username_in}!")
        st.rerun()
      else:
        st.error("Usuario o contraseña incorrectos.")

  with tab2:
    st.subheader("Regístrate gratis")
    new_user = st.text_input("Nombre de usuario", key="reg_user")
    new_pass = st.text_input("Contraseña", type="password", key="reg_pass")

    if st.button("Crear Cuenta", use_container_width=True):
      if not new_user or not new_pass:
        st.warning("⚠️ Rellena todos los campos.")
      elif new_user in usuarios:
        st.error("❌ El usuario ya existe.")
      else:
        usuarios[new_user] = {"password": new_pass}
        guardar_usuarios(usuarios)
        st.success("✅ ¡Cuenta creada con éxito! Ve a Iniciar Sesión.")
  st.markdown("</div>", unsafe_allow_html=True)

else:
  # Barra superior de sesión
  col_info, col_btn = st.columns([3, 1])
  with col_info:
    st.markdown(
        f"👤 **Sesión:** `{st.session_state.usuario_actual}` | **Voz:** Activada"
    )
  with col_btn:
    if st.button("Cerrar Sesión", use_container_width=True):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Módulo flotante HTML/JS para el Micrófono (Speech-to-Text) y Lectura de voz (TTS)
  voice_control_html = """
    <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 15px;">
        <button id="micBtn" onclick="toggleListening()" style="background: linear-gradient(135deg, #00f0ff, #ec4899); border: none; border-radius: 9999px; color: white; padding: 10px 20px; font-weight: bold; cursor: pointer; font-family: 'Rajdhani', sans-serif; box-shadow: 0 0 15px rgba(0,240,255,0.5); display: flex; align-items: center; gap: 8px;">
            🎙️ <span id="micText">Hablar con SAY</span>
        </button>
    </div>
    <script>
        let recognition;
        function toggleListening() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert('Tu navegador no soporta reconocimiento de voz.');
                return;
            }
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.interimResults = false;
            
            const btnText = document.getElementById('micText');
            btnText.innerText = "Escuchando...";
            
            recognition.onresult = function(event) {
                const speechResult = event.results[0][0].transcript;
                btnText.innerText = "Hablar con SAY";
                // Redirige la consulta de voz directamente al backend de Streamlit
                window.parent.location.href = window.location.pathname + "?q=" + encodeURIComponent(speechResult);
            };
            
            recognition.onerror = function() {
                btnText.innerText = "Hablar con SAY";
            };
            
            recognition.onend = function() {
                btnText.innerText = "Hablar con SAY";
            };
            
            recognition.start();
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'es-ES';
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }
    </script>
    """
  components.html(voice_control_html, height=60, scrolling=False)

  # Capturar consulta por voz desde la URL si existe
  query_param = st.query_params.get("q", None)

  if "messages" not in st.session_state:
    st.session_state.messages = []

  # Si llegó una consulta por voz, procesarla automáticamente
  if query_param:
    prompt = query_param
    st.query_params.clear()
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("SAY AI está procesando..."):
        respuesta = consultar_gemini_con_pool(prompt)
        st.markdown(respuesta)
        # Script JS para que la app hable la respuesta automáticamente
        components.html(
            f"""
            <script>
                if (window.parent.speakText) {{
                    window.parent.speakText({json.dumps(respuesta)});
                }}
            </script>
            """,
            height=0,
        )
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
    )

  # Mostrar historial de chat existente
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Entrada de texto tradicional (por si prefieres escribir)
  if prompt := st.chat_input("Escribe tu consulta o usa el micrófono..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("SAY AI está procesando..."):
        respuesta = consultar_gemini_con_pool(prompt)
        st.markdown(respuesta)
        components.html(
            f"""
            <script>
                if (window.parent.speakText) {{
                    window.parent.speakText({json.dumps(respuesta)});
                }}
            </script>
            """,
            height=0,
        )
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
)
      
