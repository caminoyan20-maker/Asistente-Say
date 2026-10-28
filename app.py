import json
import os
import urllib.request
import streamlit as st

DB_FILE = "usuarios.json"

# --- TU BANCO MAESTRO DE CLAVES (Pega aquí tus 11 claves reales "AQ...") ---
MASTER_KEYS = [
    "AQUÍ_PEGA_TU_CLAVE_1_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_2_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_3_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_4_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_5_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_6_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_7_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_8_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_9_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_10_AQ...",
    "AQUÍ_PEGA_TU_CLAVE_11_AQ...",
]

st.set_page_config(
    page_title="SAY AI - Oficial", page_icon="🤖", layout="centered"
)


def cargar_usuarios():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
      return json.load(f)
  return {}


def guardar_usuarios(usuarios):
  with open(DB_FILE, "w") as f:
    json.dump(usuarios, f, indent=4)


# Rotación automática por el banco maestro de 11 claves
def consultar_gemini_con_pool(mensaje):
  if not MASTER_KEYS or "AQUÍ_PEGA" in MASTER_KEYS[0]:
    return (
        "❌ Error: Debes colocar tus 11 claves reales en la lista MASTER_KEYS"
        " del código."
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
      continue  # Si una clave se agota o falla, pasa a la siguiente automáticamente

  return "❌ Lo sentimos, las claves del sistema están ocupadas temporalmente."


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

st.title("🌐 SAY AI - Plataforma Oficial")
st.markdown(
    "Asistente inteligente con distribución automática de recursos para la"
    " comunidad."
)

usuarios = cargar_usuarios()

if st.session_state.usuario_actual is None:
  tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

  with tab1:
    st.subheader("Accede a tu cuenta")
    username_in = st.text_input("Usuario", key="login_user")
    password_in = st.text_input(
        "Contraseña", type="password", key="login_pass"
    )

    if st.button("Entrar"):
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

    if st.button("Crear Cuenta"):
      if not new_user or not new_pass:
        st.warning("⚠️ Rellena todos los campos.")
      elif new_user in usuarios:
        st.error("❌ El usuario ya existe.")
      else:
        usuarios[new_user] = {"password": new_pass}
        guardar_usuarios(usuarios)
        st.success("✅ ¡Cuenta creada con éxito! Ve a Iniciar Sesión.")

else:
  st.success(
      f"👤 Sesión activa: **{st.session_state.usuario_actual}** | Conectado al"
      " banco maestro de IA."
  )

  if st.button("Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

  st.markdown("---")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("Escribe tu mensaje..."):
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
      
