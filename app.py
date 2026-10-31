import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neural Core v3.1", page_icon="🤖", layout="centered"
)

# Estilos Cyber Neon avanzados
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
    return "❌ Error: Configura MASTER_KEYS en los Secrets de Streamlit."

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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key.strip()}"
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
      with urllib.request.urlopen(req, timeout=10) as response:
        res_body = response.read().decode("utf-8")
        data = json.loads(res_body)
        texto_respuesta = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )
        if texto_respuesta:
          return texto_respuesta
    except Exception:
      continue

  return (
      "⚠️ Las API keys están experimentando alta demanda. Intenta de nuevo en"
      " un momento."
  )


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

usuarios = cargar_usuarios()

# Encabezado Visual
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Interfaz Neural & Multimedia Libre v3.1'
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
        f"👤 **{st.session_state.usuario_actual}** | Núcleo Multimedia Activo"
    )
  with c_btn:
    if st.button("Salir"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Panel de Reproductor Multimedia Libre (Web + Librería Local del Teléfono)
  with st.expander("🎧 Reproductor Multimedia & Música Libre"):
    tab_web, tab_local = st.tabs(
        ["🌐 Streaming / Web Audio", "📱 Música de mi Teléfono"]
    )

    with tab_web:
      st.markdown(
          "Pega el enlace directo de cualquier archivo de audio o música de la"
          " web:"
      )
      url_web_musica = st.text_input(
          "URL de audio (.mp3, .ogg, etc.):",
          placeholder="https://ejemplo.com/cancion.mp3",
      )
      if url_web_musica:
        st.audio(url_web_musica, format="audio/mp3")

    with tab_local:
      st.markdown(
          "Selecciona una canción directamente desde la memoria de tu"
          " dispositivo:"
      )
      musica_local = st.file_uploader(
          "Buscar archivo de música en el teléfono:",
          type=["mp3", "wav", "m4a", "aac", "ogg"],
          key="local_music_file",
      )
      if musica_local is not None:
        st.audio(musica_local, format="audio/mp3")
        st.success(f"Reproduciendo: {musica_local.name}")

  st.markdown("---")

  # Selector de Nivel de Análisis y Búsqueda Inteligente
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
      
