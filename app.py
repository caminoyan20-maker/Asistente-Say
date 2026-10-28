import json
import os
import urllib.request
import streamlit as st

DB_FILE = "usuarios.json"

# Lee las claves de forma segura desde los Secrets de Streamlit Cloud
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

# Configuración de página con diseño optimizado
st.set_page_config(
    page_title="SAY - Cyber Neon Search Engine v2.6",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inyección de Estilos Cyberpunk CSS (Adaptado del diseño v2.6)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

        .stApp {
            font-family: 'Rajdhani', sans-serif;
            background: radial-gradient(circle at 50% 25%, #180b33 0%, #0a0418 55%, #030108 100%);
            color: #ffffff;
        }

        /* Ocultar elementos predeterminados molestos de Streamlit para una vista más limpia de app nativa */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Título Estilo Neón SAY */
        .title-say {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.15em;
            color: #12edff;
            text-shadow: 
                0 0 5px #00f0ff,
                0 0 15px #00f0ff,
                0 0 30px #0088ff,
                0 0 50px #ec4899,
                0 0 80px #ec4899;
            -webkit-text-stroke: 1px #ff2a8d;
            text-align: center;
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 0px;
        }

        .cyber-subtitle {
            font-family: 'Share Tech Mono', monospace;
            text-align: center;
            color: #38bdf8;
            font-size: 0.8rem;
            letter-spacing: 0.2em;
            margin-bottom: 2rem;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.8);
        }

        /* Paneles HUD personalizados */
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
      continue  # Salta a la siguiente clave si hay algún límite o error

  return "❌ Lo sentimos, las claves del sistema están ocupadas temporalmente."


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

# Encabezado Visual Cyber Neon
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Cybernetic Neural Interface Search v2.6'
    " ]</div>",
    unsafe_allow_html=True,
)

usuarios = cargar_usuarios()

# Control de Autenticación con estilo integrado
if st.session_state.usuario_actual is None:
  st.markdown(
      '<div class="hud-panel">', unsafe_allow_html=True
  )  # Contenedor estilo HUD
  tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

  with tab1:
    st.subheader("Accede a tu cuenta")
    username_in = st.text_input("Usuario", key="login_user")
    password_in = st.text_input(
        "Contraseña", type="password", key="login_pass"
    )

    if st.button("Entrar", use_container_width=True):
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
  # Panel principal de usuario conectado
  col_info, col_btn = st.columns([3, 1])
  with col_info:
    st.markdown(
        f"👤 Sesión activa: **{st.session_state.usuario_actual}** | Conectado"
        " al núcleo IA."
    )
  with col_btn:
    if st.button("Cerrar Sesión", use_container_width=True):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Historial de chat integrado con la estética
  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Entrada de chat interactiva optimizada
  if prompt := st.chat_input("Escribe tu consulta o búsqueda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("SAY AI está procesando..."):
        respuesta = consultar_gemini_con_pool(prompt)
        st.markdown(respuesta)
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
    )
    
