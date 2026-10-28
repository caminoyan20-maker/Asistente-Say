import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"

# Lee las claves de forma segura desde los Secrets de Streamlit Cloud
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neon Search Engine v2.6",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ocultar elementos predeterminados de Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #040209; }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


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

if "messages" not in st.session_state:
  st.session_state.messages = []

usuarios = cargar_usuarios()

# Pantalla de Login / Registro
if st.session_state.usuario_actual is None:
  st.markdown(
      """
        <div style="max-width: 400px; margin: 40px auto; padding: 20px; background: rgba(8, 14, 28, 0.92); border: 1px solid #00f0ff; border-radius: 15px; color: #fff; font-family: sans-serif; box-shadow: 0 0 20px rgba(0,240,255,0.3);">
            <h2 style="text-align: center; color: #00f0ff; font-family: monospace;">SAY AI - ACCESS</h2>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col1, col2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
  with col1:
    u_in = st.text_input("Usuario", key="l_u")
    p_in = st.text_input("Contraseña", type="password", key="l_p")
    if st.button("Entrar al Sistema", use_container_width=True):
      if u_in in usuarios and usuarios[u_in]["password"] == p_in:
        st.session_state.usuario_actual = u_in
        st.rerun()
      else:
        st.error("Credenciales inválidas.")
  with col2:
    r_u = st.text_input("Nuevo Usuario", key="r_u")
    r_p = st.text_input("Nueva Contraseña", type="password", key="r_p")
    if st.button("Crear Cuenta", use_container_width=True):
      if r_u and r_p and r_u not in usuarios:
        usuarios[r_u] = {"password": r_p}
        guardar_usuarios(usuarios)
        st.success("¡Cuenta creada! Ya puedes iniciar sesión.")
      else:
        st.error("Verifica los datos o el usuario ya existe.")

else:
  # Captura la consulta si se envió
  query_param = st.query_params.get("q", None)

  respuesta_html = ""
  if query_param:
    with st.spinner("Procesando con la IA..."):
      respuesta_texto = consultar_gemini_con_pool(query_param)
      st.session_state.messages.append(
          {"user": query_param, "ai": respuesta_texto}
      )
      st.query_params.clear()

  # Construir historial para mostrar en la interfaz HTML
  historial_html = ""
  if st.session_state.messages:
    for item in reversed(st.session_state.messages):
      historial_html += f"""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(0,240,255,0.4); border-radius: 12px; padding: 12px; margin-bottom: 12px; text-align: left;">
                <div style="color: #ff2a8d; font-weight: bold; font-size: 13px; margin-bottom: 4px;">> {item['user']}</div>
                <div style="color: #e0f7fc; font-family: monospace; font-size: 13px; white-space: pre-wrap;">{item['ai']}</div>
            </div>
            """

  # Interfaz Cyberpunk Completa
  cyberpunk_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAY - Cyber Neon Search Engine v2.6</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; user-select: none; }}
            body {{
                font-family: 'Rajdhani', sans-serif;
                background-color: #040209;
                color: #ffffff;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 10px;
            }}
            .neon-outer-frame {{
                position: relative;
                width: 100%;
                max-width: 900px;
                min-height: 90vh;
                border-radius: 28px;
                border: 1.5px solid rgba(0, 240, 255, 0.3);
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.35), 0 0 40px rgba(236, 72, 153, 0.25);
                background: radial-gradient(circle at 50% 25%, #180b33 0%, #0a0418 55%, #030108 100%);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: space-between;
                padding: 1.5rem;
            }}
            .title-say {{
                font-family: 'Orbitron', sans-serif;
                letter-spacing: 0.15em;
                color: #12edff;
                text-shadow: 0 0 5px #00f0ff, 0 0 15px #00f0ff, 0 0 30px #0088ff, 0 0 50px #ec4899;
                -webkit-text-stroke: 1.5px #ff2a8d;
            }}
            .search-bar-container {{
                position: relative;
                background: rgba(8, 20, 42, 0.65);
                backdrop-filter: blur(16px);
                border-radius: 9999px;
                border: 1px solid rgba(0, 240, 255, 0.6);
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.35);
                display: flex;
                align-items: center;
                padding: 0.5rem 1rem;
                width: 100%;
                max-width: 700px;
            }}
            .search-input {{
                background: transparent;
                color: #e0f7fc;
                font-size: 1.1rem;
                font-weight: 600;
                outline: none;
                width: 100%;
                border: none;
                padding: 5px 10px;
            }}
            .gem-button {{
                background: linear-gradient(135deg, rgba(0, 240, 255, 0.9) 0%, rgba(236, 72, 153, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.9);
                clip-path: polygon(15% 0%, 85% 0%, 100% 50%, 85% 100%, 15% 100%, 0% 50%);
                cursor: pointer;
                padding: 8px 18px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }}
            .results-container {{
                width: 100%;
                max-width: 700px;
                max-height: 40vh;
                overflow-y: auto;
                margin-top: 15px;
            }}
            ::-webkit-scrollbar {{ width: 5px; }}
            ::-webkit-scrollbar-thumb {{ background: #00f0ff; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="neon-outer-frame">
            <div style="text-align: center; width: 100%;">
                <span style="color: #00f0ff; font-family: monospace; font-size: 11px;">USUARIO: {st.session_state.usuario_actual} // SISTEMA ONLINE</span>
                <h1 class="title-say text-5xl sm:text-7xl font-black mt-1">SAY</h1>
                <span style="font-family: 'Share Tech Mono'; color: #38bdf8; font-size: 10px; letter-spacing: 0.25em;">[ Cybernetic Neural Interface Search v2.6 ]</span>
            </div>

            <!-- Área de Resultados y Chat de la IA -->
            <div class="results-container">
                {historial_html}
            </div>

            <!-- Formulario de Búsqueda -->
            <div style="width: 100%; display: flex; flex-direction: column; align-items: center; margin-top: 10px;">
                <form id="searchForm" class="search-bar-container" onsubmit="enviarConsulta(event)">
                    <input type="text" id="searchInput" class="search-input" placeholder="Escribe tu consulta o pregunta..." autocomplete="off" required />
                    <button type="submit" class="gem-button">ENVIAR</button>
                </form>
            </div>

            <div style="font-family: 'Share Tech Mono'; font-size: 10px; color: rgba(0,240,255,0.6); margin-top: 10px;">
                NÚCLEO DE IA ACTIVO // CONECTADO A MASTER KEYS
            </div>
        </div>

        <script>
            function enviarConsulta(event) {{
                event.preventDefault();
                const query = document.getElementById('searchInput').value;
                if(query) {{
                    window.parent.location.href = window.location.pathname + "?q=" + encodeURIComponent(query);
                }}
            }}
        </script>
    </body>
    </html>
    """
  components.html(cyberpunk_html, height=750, scrolling=True)
    
