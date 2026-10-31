import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neural Core v3.0", page_icon="🤖", layout="centered"
)

# Estilos Cyber Neon avanzados con reproductor flotante
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


def consultar_gemini_con_pool(mensaje, modo):
  if not MASTER_KEYS:
    return "❌ Error: Configura tus claves maestras en los Secrets."

  # Configuración de tokens y temperatura según el modo seleccionado
  configs = {
      "🚀 Búsqueda Rápida": {"maxOutputTokens": 400, "temperature": 0.5},
      "⚖️ Equilibrado": {"maxOutputTokens": 1000, "temperature": 0.7},
      "🔍 Profundo": {"maxOutputTokens": 2000, "temperature": 0.8},
      "🔬 Muy Minucioso": {"maxOutputTokens": 4000, "temperature": 0.3},
  }

  cfg = configs.get(
      modo, {"maxOutputTokens": 1000, "temperature": 0.7}
  )

  for api_key in MASTER_KEYS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": mensaje}]}],
        "generationConfig": {
            "temperature": cfg["temperature"],
            "maxOutputTokens": cfg["maxOutputTokens"],
        },
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
      with urllib.request.urlopen(req, timeout=12) as response:
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
  return "❌ Las claves del sistema están ocupadas temporalmente."


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

usuarios = cargar_usuarios()

# Encabezado Visual
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Interfaz Neural & Búsqueda Eficiente v3.0'
    " ]</div>",
    unsafe_allow_html=True,
)

# Control de Autenticación
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
    r_p = st.text_input("Contraseña nueva", type="password", key="r_p")
    if st.button("Crear Cuenta", use_container_width=True):
      if r_u and r_p and r_u not in usuarios:
        usuarios[r_u] = {"password": r_p}
        guardar_usuarios(usuarios)
        st.success("¡Cuenta creada con éxito!")
      else:
        st.error("Verifica los datos.")
  st.markdown("</div>", unsafe_allow_html=True)

else:
  c_inf, c_btn = st.columns([3, 1])
  with c_inf:
    st.markdown(
        f"👤 **{st.session_state.usuario_actual}** | Núcleo de Búsqueda Activo"
    )
  with c_btn:
    if st.button("Salir"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Panel desplegable de Librería de Música Integrada
  with st.expander("🎵 Librería de Música & Audio Cyber Neon"):
    st.markdown(
        "Escucha tus pistas o música ambiental integrada mientras navegas en"
        " SAY:"
    )
    # Lista de reproducción con pistas libres de alta calidad / Lo-Fi Cyber
    musica_opciones = {
        "Synthwave Cyber Neon": (
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        ),
        "Ambient Space Lo-Fi": (
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        ),
        "Neural Chill Beats": (
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
        ),
    }
    pista_seleccionada = st.selectbox(
        "Selecciona pista musical:", list(musica_opciones.keys())
    )
    st.audio(musica_opciones[pista_seleccionada], format="audio/mp3")

  st.markdown("---")

  # Selector de Modo de Búsqueda Inteligente
  modo_busqueda = st.selectbox(
      "⚡ Selecciona el Nivel de Análisis:",
      [
          "🚀 Búsqueda Rápida",
          "⚖️ Equilibrado",
          "🔍 Profundo",
          "🔬 Muy Minucioso",
      ],
  )

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Cuadro de chat optimizado para texto veloz y eficiente
  if prompt := st.chat_input(
      "Escribe tu consulta en el motor de búsqueda de SAY..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner(f"SAY AI procesando en modo [{modo_busqueda}]..."):
        respuesta = consultar_gemini_con_pool(prompt, modo_busqueda)
        st.markdown(respuesta)
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
    )
    
