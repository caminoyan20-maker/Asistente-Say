import json
import os
import urllib.request
import streamlit as st

DB_FILE = "usuarios.json"

MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Oficial", page_icon="🤖", layout="centered"
)

# Estilos CSS limpios para evitar bloqueos
st.markdown(
    """
    <style>
        .stApp { background-color: #040209; color: #ffffff; font-family: sans-serif; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
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

if st.session_state.usuario_actual is None:
  st.markdown(
      "<h1 style='text-align: center; color: #00f0ff;'>SAY AI</h1>",
      unsafe_allow_html=True,
  )
  tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

  with tab1:
    u_in = st.text_input("Usuario", key="l_u")
    p_in = st.text_input("Contraseña", type="password", key="l_p")
    if st.button("Entrar", use_container_width=True):
      if u_in in usuarios and usuarios[u_in]["password"] == p_in:
        st.session_state.usuario_actual = u_in
        st.rerun()
      else:
        st.error("Credenciales incorrectas.")

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

else:
  col1, col2 = st.columns([3, 1])
  with col1:
    st.write(f"👤 **{st.session_state.usuario_actual}** | Online")
  with col2:
    if st.button("Salir"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("Procesando..."):
        respuesta = consultar_gemini_con_pool(prompt)
        st.markdown(respuesta)
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
    )
      
