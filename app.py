import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"

# Lee las claves de forma segura desde los Secrets de Streamlit Cloud
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

# Configuración de página en modo ancho para aprovechar toda la pantalla en la APK
st.set_page_config(
    page_title="SAY - Cyber Neon Search Engine v2.6",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ocultar elementos nativos de Streamlit para que parezca una app nativa total
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

usuarios = cargar_usuarios()

# Control de sesión simple si no ha iniciado sesión
if st.session_state.usuario_actual is None:
  st.markdown(
      """
        <div style="max-width: 400px; margin: 50px auto; padding: 20px; background: rgba(8, 14, 28, 0.92); border: 1px solid #00f0ff; border-radius: 15px; color: #fff; font-family: sans-serif; box-shadow: 0 0 20px rgba(0,240,255,0.3);">
            <h2 style="text-align: center; color: #00f0ff; font-family: monospace;">SAY AI - ACCESS</h2>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col1, col2 = st.tabs(["Iniciar Sesión", "Registrarse"])
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
  # Manejo de consulta de IA mediante parámetros de URL o interfaz limpia incrustada
  query_param = st.query_params.get("q", None)
  if query_param:
    respuesta = consultar_gemini_con_pool(query_param)
    st.write(respuesta)
    if st.button("Volver al buscador"):
      st.query_params.clear()
      st.rerun()
  else:
    # Aquí incrustamos tu código HTML/CSS/JS exacto adaptado para renderizar la interfaz cibernética completa
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
                    height: 100vh;
                    overflow: hidden;
                }}
                .neon-outer-frame {{
                    position: relative;
                    width: 100%;
                    max-width: 1000px;
                    height: 90vh;
                    border-radius: 28px;
                    border: 1.5px solid rgba(0, 240, 255, 0.3);
                    box-shadow: 0 0 20px rgba(0, 240, 255, 0.35), 0 0 40px rgba(236, 72, 153, 0.25);
                    background: radial-gradient(circle at 50% 25%, #180b33 0%, #0a0418 55%, #030108 100%);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: space-between;
                    padding: 2rem;
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
                    padding: 0.75rem 1.5rem;
                    width: 100%;
                    max-width: 700px;
                }}
                .search-input {{
                    background: transparent;
                    color: #e0f7fc;
                    font-size: 1.2rem;
                    font-weight: 600;
                    outline: none;
                    width: 100%;
                    border: none;
                }}
                .gem-button {{
                    background: linear-gradient(135deg, rgba(0, 240, 255, 0.9) 0%, rgba(236, 72, 153, 0.9) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.9);
                    clip-path: polygon(15% 0%, 85% 0%, 100% 50%, 85% 100%, 15% 100%, 0% 50%);
                    cursor: pointer;
                    padding: 10px 20px;
                    color: white;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="neon-outer-frame">
                <div style="text-align: center; width: 100%;">
                    <span style="color: #00f0ff; font-family: monospace; font-size: 12px;">USUARIO: {st.session_state.usuario_actual} // SISTEMA ONLINE</span>
                    <h1 class="title-say text-6xl sm:text-7xl font-black mt-2">SAY</h1>
                    <span style="font-family: 'Share Tech Mono'; color: #38bdf8; font-size: 11px; letter-spacing: 0.3em;">[ Cybernetic Neural Interface Search v2.6 ]</span>
                </div>

                <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
                    <form id="searchForm" class="search-bar-container" onsubmit="enviarConsulta(event)">
                        <input type="text" id="searchInput" class="search-input" placeholder="Escribe tu consulta o pregunta..." autocomplete="off" required />
                        <button type="submit" class="gem-button">ENVIAR</button>
                    </form>
                </div>

                <div style="font-family: 'Share Tech Mono'; font-size: 10px; color: rgba(0,240,255,0.6);">
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
    components.html(cyberpunk_html, height=650, scrolling=False)
    
