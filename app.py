import base64
import json
import os
import urllib.parse
import urllib.request
import streamlit as st
import streamlit.components.v1 as components

DB_FILE = "usuarios.json"
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neural Core v3.8", page_icon="🤖", layout="centered"
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
    try:
      with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return {}
  return {}


def guardar_usuarios(usuarios):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(usuarios, f, indent=4)


def consultar_gemini_con_pool(mensaje, modo):
  if not MASTER_KEYS:
    return "❌ Error: Configura MASTER_KEYS en los Secrets de Streamlit."

  configs = {
      "🚀 Búsqueda Rápida": {"maxOutputTokens": 2000, "temperature": 0.5},
      "⚖️ Equilibrado": {"maxOutputTokens": 4000, "temperature": 0.7},
      "🔍 Profundo": {"maxOutputTokens": 6000, "temperature": 0.8},
      "🔬 Muy Minucioso": {"maxOutputTokens": 8192, "temperature": 0.3},
  }

  cfg = configs.get(
      modo, {"maxOutputTokens": 4000, "temperature": 0.7}
  )

  prompt_amplio = (
      "Actúa como SAY AI, un motor de búsqueda avanzado. Proporciona una"
      " respuesta exhaustiva, extensa, detallada y profunda sobre el siguiente"
      " tema, explicando conceptos con contexto completo, definiciones y"
      " estructura ordenada.\n\nConsulta: "
      + mensaje
  )

  # Modelos Flash solicitados: 3.5 y 3.8
  modelos_flash = ["gemini-3.5-flash", "gemini-3.8-flash"]

  ultimo_error = ""
  for api_key in MASTER_KEYS:
    for modelo in modelos_flash:
      url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key.strip()}"
      payload = {
          "contents": [{"role": "user", "parts": [{"text": prompt_amplio}]}],
          "generationConfig": {
              "temperature": cfg["temperature"],
              "maxOutputTokens": cfg["maxOutputTokens"],
          },
      }
      data_bytes = json.dumps(payload).encode("utf-8")
      req = urllib.request.Request(url, data=data_bytes, method="POST")
      req.add_header("Content-Type", "application/json")
      try:
        with urllib.request.urlopen(req, timeout=30) as response:
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
      except urllib.error.HTTPError as e:
        try:
          error_detalle = e.read().decode("utf-8")
        except Exception:
          error_detalle = str(e)
        ultimo_error = f"HTTP {e.code} ({modelo}): {error_detalle}"
        if e.code == 429:
          continue
        continue
      except Exception as e:
        ultimo_error = str(e)
        continue

  return f"🛑 DIAGNÓSTICO DE API: {ultimo_error}"


# Inicializar Estado de Sesión
if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

usuarios = cargar_usuarios()

# Encabezado Visual
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Interfaz Neural & Búsqueda Exhaustiva v3.8'
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
        st.success(f"¡Bienvenido de nuevo, {u_in}!")
        st.rerun()
      else:
        st.error("Credenciales inválidas o usuario no registrado.")

  with tab2:
    r_u = st.text_input("Nuevo Usuario", key="r_u")
    r_p = st.text_input("Contraseña nueva", type="password", key="r_p")
    if st.button("Crear Cuenta", use_container_width=True):
      if r_u and r_p:
        if r_u not in usuarios:
          usuarios[r_u] = {"password": r_p}
          guardar_usuarios(usuarios)
          st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
        else:
          st.error("El usuario ya existe.")
      else:
        st.error("Por favor completa todos los campos.")
  st.markdown("</div>", unsafe_allow_html=True)

else:
  c_inf, c_btn = st.columns([3, 1])
  with c_inf:
    st.markdown(
        f"👤 Sesión Activa: **{st.session_state.usuario_actual}** | Núcleo"
        " Exhaustivo Listo"
    )
  with c_btn:
    if st.button("Cerrar Sesión"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Panel de Reproductor Multimedia
  with st.expander("🎧 Reproductor Multimedia & Playlist Automática"):
    tab_web, tab_local = st.tabs(
        ["🌐 Buscador de Audio Web", "📱 Playlist Local Continua"]
    )

    with tab_web:
      st.markdown("Busca música en streaming directo:")
      query_audio = st.text_input(
          "Escribe artista o canción:",
          placeholder="Ej: Bad Bunny mix audio...",
      )
      if query_audio:
        encoded_q = urllib.parse.quote(query_audio)
        components.html(
            f"""
            <div style="background: rgba(8, 14, 28, 0.95); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 10px; padding: 12px; text-align: center;">
                <p style="color: #38bdf8; font-family: monospace; font-size: 11px; margin-bottom: 6px;">Sintonizando audio para: {query_audio}</p>
                <iframe width="100%" height="110" src="https://www.youtube.com/embed?listType=search&list={encoded_q}&autoplay=1" frameborder="0" allow="autoplay"></iframe>
            </div>
            """,
            height=140,
        )

    with tab_local:
      st.markdown(
          "Sube tu selección múltiple de canciones del teléfono. ¡Se"
          " reproducirán una tras otra automáticamente!"
      )
      archivos_locales = st.file_uploader(
          "Selecciona tus canciones locales:",
          type=["mp3", "wav", "m4a", "aac", "ogg"],
          accept_multiple_files=True,
          key="playlist_local",
      )

      if archivos_locales:
        st.success(
            f"🎶 Playlist cargada con éxito: {len(archivos_locales)} pistas en"
            " cola."
        )

        playlist_data = []
        for file in archivos_locales:
          b64_data = base64.b64encode(file.read()).decode("utf-8")
          playlist_data.append({"name": file.name, "data": b64_data})

        playlist_json = json.dumps(playlist_data)

        playlist_html = f"""
                <div style="background: rgba(8, 14, 28, 0.95); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 12px; padding: 15px; text-align: center;">
                    <div id="trackTitle" style="color: #00f0ff; font-family: 'Rajdhani', sans-serif; font-weight: bold; font-size: 14px; margin-bottom: 10px;">Preparando Playlist...</div>
                    <audio id="audioPlayer" controls autoplay style="width: 100%; filter: drop-shadow(0 0 5px rgba(0,240,255,0.5));"></audio>
                </div>
                <script>
                    const playlist = {playlist_json};
                    let currentIndex = 0;
                    const audioElem = document.getElementById('audioPlayer');
                    const titleElem = document.getElementById('trackTitle');

                    function loadTrack(index) {{
                        if (index >= playlist.length) {{
                            currentIndex = 0;
                        }}
                        const track = playlist[currentIndex];
                        titleElem.innerText = "▶ Reproduciendo: " + track.name;
                        audioElem.src = "data:audio/mp3;base64," + track.data;
                        audioElem.play().catch(e => console.log("Autoplay bloqueado:", e));
                    }}

                    audioElem.onended = function() {{
                        currentIndex++;
                        loadTrack(currentIndex);
                    }};

                    if (playlist.length > 0) {{
                        loadTrack(0);
                    }}
                </script>
                """
        components.html(playlist_html, height=130)

  st.markdown("---")

  # Selector de Nivel de Análisis y Panel de Voz Superior (Libre de Publicidad inferior)
  c_sel, c_voz = st.columns([2, 1])
  with c_sel:
    modo_busqueda = st.selectbox(
        "⚡ Nivel de Análisis:",
        [
            "🚀 Búsqueda Rápida",
            "⚖️ Equilibrado",
            "🔍 Profundo",
            "🔬 Muy Minucioso",
        ],
    )

  with c_voz:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    control_voz_html = """
        <div style="display: flex; gap: 8px; justify-content: flex-end;">
            <button onclick="startDictation()" title="Hablar" style="background: #12edff; color: #030108; border: none; padding: 8px 12px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 12px; font-family: 'Rajdhani', sans-serif; box-shadow: 0 0 8px #12edff;">🎤 Hablar</button>
            <button onclick="stopSpeaking()" title="Silenciar" style="background: #ff3366; color: #ffffff; border: none; padding: 8px 12px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 12px; font-family: 'Rajdhani', sans-serif;">⏹️ Silenciar</button>
        </div>
        <script>
            function startDictation() {
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    alert("Tu navegador no soporta voz.");
                    return;
                }
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'es-ES';
                recognition.interimResults = false;
                
                recognition.onresult = function(event) {
                    const text = event.results[0][0].transcript;
                    const chatInput = document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                    if (chatInput) {
                        chatInput.value = text;
                        chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                        setTimeout(() => {
                            chatInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                        }, 400);
                    }
                };
                recognition.start();
            }

            function stopSpeaking() {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
            }
        </script>
        """
    components.html(control_voz_html, height=45)

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "Escribe tu consulta detallada en el motor de búsqueda..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner(
          f"SAY AI generando información exhaustiva en modo [{modo_busqueda}]..."
      ):
        respuesta = consultar_gemini_con_pool(prompt, modo_busqueda)
        st.markdown(respuesta)

        # Reproducir la respuesta en voz alta automáticamente
        safe_text = (
            respuesta.replace('"', '\\"')
            .replace("\n", " ")
            .replace("'", "\\'")
        )
        components.html(
            f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance("{safe_text}");
                    utterance.lang = 'es-ES';
                    window.speechSynthesis.speak(utterance);
                }}
            </script>
            """,
            height=0,
        )

    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
            )
        
