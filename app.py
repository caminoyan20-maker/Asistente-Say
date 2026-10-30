import base64
import json
import os
import urllib.request
import streamlit.components.v1 as components
import streamlit as st

DB_FILE = "usuarios.json"
MASTER_KEYS = st.secrets.get("MASTER_KEYS", [])

st.set_page_config(
    page_title="SAY - Cyber Neon Voice v2.7", page_icon="🤖", layout="centered"
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


def consultar_gemini_con_pool(mensaje):
  if not MASTER_KEYS:
    return "❌ Error: Configura tus claves maestras en los Secrets."

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
  return "❌ Las claves del sistema están ocupadas temporalmente."


if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

usuarios = cargar_usuarios()

# Encabezado Visual
st.markdown('<h1 class="title-say">SAY</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cyber-subtitle">[ Interfaz Neural & Voz Directa v2.7'
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
        f"👤 **{st.session_state.usuario_actual}** | Enlace de Voz Activo"
    )
  with c_btn:
    if st.button("Salir"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Módulo de Botón de Voz Inteligente Cyber Neon (Sin cajas feas de subida)
  voice_hud_html = """
    <div style="background: rgba(8, 14, 28, 0.95); border: 1px solid rgba(0, 240, 255, 0.4); box-shadow: 0 0 15px rgba(0, 240, 255, 0.2); border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 15px;">
        <div style="font-family: 'Share Tech Mono', monospace; color: #38bdf8; font-size: 0.8rem; margin-bottom: 10px;">[ NÚCLEO DE VOZ TÁCTIL ]</div>
        <button id="micBtn" onclick="toggleRecord()" style="background: linear-gradient(135deg, #00f0ff, #ec4899); border: none; border-radius: 30px; color: white; padding: 12px 25px; font-weight: bold; cursor: pointer; font-family: 'Rajdhani', sans-serif; box-shadow: 0 0 20px rgba(0,240,255,0.5); font-size: 16px; width: 100%; max-width: 280px; transition: all 0.3s ease;">
            🎙️ <span id="micText">TOCAR PARA HABLAR</span>
        </button>
        <div id="micStatus" style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: #00f0ff; margin-top: 8px;">Sistema listo</div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let recording = false;

        async function toggleRecord() {
            const btn = document.getElementById('micBtn');
            const txt = document.getElementById('micText');
            const status = document.getElementById('micStatus');

            if (!recording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = async () => {
                        status.innerText = "Procesando audio neural...";
                        const audioBlob = new Blob(audioChunks, { type: 'audio/mp4' });
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = function() {
                            const base64Audio = reader.result.split(',')[1];
                            window.parent.location.href = window.location.pathname + "?voice_data=" + encodeURIComponent(base64Audio);
                        }
                    };

                    mediaRecorder.start();
                    recording = true;
                    txt.innerText = "GRABANDO... (Toca para detener)";
                    btn.style.background = "#ff2a8d";
                    btn.style.boxShadow = "0 0 25px #ff2a8d";
                    status.innerText = "Escuchando tu voz en vivo...";
                } catch (err) {
                    alert("Error al acceder al micrófono: " + err.message);
                }
            } else {
                mediaRecorder.stop();
                recording = false;
                txt.innerText = "TOCAR PARA HABLAR";
                btn.style.background = "linear-gradient(135deg, #00f0ff, #ec4899)";
                btn.style.boxShadow = "0 0 20px rgba(0,240,255,0.5)";
            }
        }
    </script>
    """
  components.html(voice_hud_html, height=140, scrolling=False)

  # Capturar audio enviado por JavaScript de forma invisible
  voice_base64_param = st.query_params.get("voice_data", None)
  texto_a_procesar = None

  if voice_base64_param:
    st.query_params.clear()
    with st.spinner("🎧 SAY AI analizando tu nota de voz directa..."):
      audio_bytes = base64.b64decode(voice_base64_param)
      for api_key in MASTER_KEYS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": (
                            "Escucha este audio y extrae únicamente la"
                            " pregunta o consulta principal formulada por el"
                            " usuario en español."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": "audio/mp4",
                            "data": voice_base64_param,
                        }
                    },
                ]
            }]
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
          with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            texto_a_procesar = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text")
            )
            break
        except Exception:
          continue

    if texto_a_procesar:
      st.session_state.messages.append(
          {"role": "user", "content": f"🎤 Nota de voz: {texto_a_procesar}"}
      )
      with st.chat_message("user"):
        st.markdown(f"🎤 Transcripción: **{texto_a_procesar}**")

      with st.spinner("SAY AI generando respuesta..."):
        respuesta = consultar_gemini_con_pool(texto_a_procesar)
        st.markdown(respuesta)
      st.session_state.messages.append(
          {"role": "assistant", "content": respuesta}
      )
      st.rerun()

  # Entrada tradicional de texto por respaldo
  if prompt := st.chat_input("O escribe tu consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("SAY AI analizando..."):
        respuesta = consultar_gemini_con_pool(prompt)
        st.markdown(respuesta)
    st.session_state.messages.append(
        {"role": "assistant", "content": respuesta}
          )
      
