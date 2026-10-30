import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"

MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neon Voice v2.6", page_icon="🤖", layout="centered"
)

# Estilos Cyber Neon
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

        .title-say {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.15em;
            color: #12edff;
            text-shadow: 0 0 10px #00f0ff, 0 0 20px #0088ff;
            text-align: center;
            font-size: 2.5rem;
            font-weight: 900;
        }

        .cyber-subtitle {
            font-family: 'Share Tech Mono', monospace;
            text-align: center;
            color: #38bdf8;
            font-size: 0.7rem;
            letter-spacing: 0.2em;
            margin-bottom: 1.5rem;
        }

        .hud-card {
            background: rgba(8, 14, 28, 0.95);
            border: 1px solid rgba(0, 240, 255, 0.4);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
        }
        
        .stChatMessage {
            background: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid rgba(0,240,255,0.3) !important;
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
    return "❌ Error: Configura tus claves en los Secrets."

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
  return "❌ Las claves están ocupadas temporalmente."


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

usuarios = cargar_usuarios()

# Encabezado
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Interfaz Neural & Voz Activa v2.6 ]</div>',
    unsafe_allow_html=True,
)

# Autenticación
if st.session_state.usuario_actual is None:
  st.markdown('<div class="hud-card">', unsafe_allow_html=True)
  tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

  with tab1:
    u_in = st.text_input("Usuario", key="l_u")
    p_in = st.text_input("Contraseña", type="password", key="l_p")
    if st.button("Entrar al Sistema", use_container_width=True):
      if u_in in usuarios and usuarios[u_in]["password"] == p_in:
        st.session_state.usuario_actual = u_in
        st.rerun()
      else:
        st.error("Credenciales inválidas.")

  with tab2:
    r_u = st.text_input("Nuevo Usuario", key="r_u")
    r_p = st.text_input("Nueva Contraseña", type="password", key="r_p")
    if st.button("Crear Cuenta", use_container_width=True):
      if r_u and r_p and r_u not in usuarios:
        usuarios[r_u] = {"password": r_p}
        guardar_usuarios(usuarios)
        st.success("¡Cuenta creada con éxito!")
      else:
        st.error("Verifica los datos.")
  st.markdown("</div>", unsafe_allow_html=True)

else:
  # Barra superior de sesión
  c_inf, c_btn = st.columns([3, 1])
  with c_inf:
    st.markdown(
        f"👤 **{st.session_state.usuario_actual}** | Núcleo de Voz Activo"
    )
  with c_btn:
    if st.button("Salir"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Panel de Voz Inteligente con manejo de estados persistentes
  voice_panel = """
    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px; margin-bottom: 15px;">
        <button id="recordBtn" onclick="toggleListening()" style="background: linear-gradient(135deg, #00f0ff, #ec4899); border: none; border-radius: 24px; color: white; padding: 12px 24px; font-weight: bold; cursor: pointer; font-family: 'Rajdhani', sans-serif; box-shadow: 0 0 20px rgba(0,240,255,0.5); display: flex; align-items: center; gap: 10px; font-size: 16px; width: 100%; max-width: 320px; justify-content: center;">
            🎙️ <span id="recStatus">ACTIVAR ESCUCHA DE VOZ</span>
        </button>
        <div id="liveText" style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #38bdf8; text-align: center; min-height: 20px;"></div>
    </div>
    <script>
        let recognition;
        let isListening = false;

        function toggleListening() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert('Tu dispositivo no soporta reconocimiento de voz nativo.');
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.interimResults = true; // Permite escuchar en tiempo real mientras hablas
            recognition.maxAlternatives = 1;

            const btn = document.getElementById('recordBtn');
            const statusSpan = document.getElementById('recStatus');
            const liveText = document.getElementById('liveText');

            recognition.onstart = function() {
                isListening = true;
                statusSpan.innerText = "ESCUCHANDO...";
                btn.style.background = "#ff2a8d";
                btn.style.boxShadow = "0 0 25px #ff2a8d";
                liveText.innerText = "Te escucho, habla ahora...";
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                
                if (interimTranscript) {
                    liveText.innerText = '🗣️ "' + interimTranscript + '"';
                }

                if (finalTranscript) {
                    liveText.innerText = '✅ Procesando: "' + finalTranscript + '"';
                    recognition.stop();
                    // Envía la consulta capturada de forma segura al backend
                    window.parent.location.href = window.location.pathname + "?voice_q=" + encodeURIComponent(finalTranscript);
                }
            };

            recognition.onerror = function(event) {
                statusSpan.innerText = "ACTIVAR ESCUCHA DE VOZ";
                btn.style.background = "linear-gradient(135deg, #00f0ff, #ec4899)";
                btn.style.boxShadow = "0 0 20px rgba(0,240,255,0.5)";
                liveText.innerText = "Error o silencio prolongado. Intenta de nuevo.";
                isListening = false;
            };

            recognition.onend = function() {
                if (isListening) {
                    statusSpan.innerText = "ACTIVAR ESCUCHA DE VOZ";
                    btn.style.background = "linear-gradient(135deg, #00f0ff, #ec4899)";
                    btn.style.boxShadow = "0 0 20px rgba(0,240,255,0.5)";
                    isListening = false;
                }
            };

            try {
                recognition.start();
            } catch(e) {
                recognition.stop();
            }
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'es-ES';
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }
    </script>
    """
  components.html(voice_panel, height=95, scrolling=False)

  if "messages" not in st.session_state:
    st.session_state.messages = []

  # Capturar la consulta de voz de forma limpia
  voice_param = st.query_params.get("voice_q", None)

  # Mostrar historial del chat
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  texto_a_procesar = None
  if voice_param:
    texto_a_procesar = voice_param
    st.query_params.clear()
    st.session_state.messages.append({"role": "user", "content": voice_param})
    with st.chat_message("user"):
      st.markdown(voice_param)

  # Entrada tradicional por texto como respaldo
  if prompt := st.chat_input("Escribe tu consulta o usa el botón de voz..."):
    texto_a_procesar = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

  # Procesar con la IA si hay texto nuevo
  if texto_a_procesar and (
      len(st.session_state.messages) > 0
      and st.session_state.messages[-1]["content"] == texto_a_procesar
      and st.session_state.messages[-1]["role"] == "user"
  ):
    with st.chat_message("assistant"):
      with st.spinner("SAY AI analizando tu solicitud..."):
        respuesta = consultar_gemini_con_pool(texto_a_procesar)
        st.markdown(respuesta)
        # Leer la respuesta automáticamente en voz alta (Text-to-Speech)
        safe_resp = json.dumps(respuesta)
        components.html(
            f"""
            <script>
                if (window.parent.speakText) {{
                    window.parent.speakText({safe_resp});
                }}
            </script>
            """,
            height=0,
        )
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
          )
      
