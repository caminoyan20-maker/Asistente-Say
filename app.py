import http.server
import json
import os
import socketserver
import urllib.request
import webbrowser

PORT = 8080
DB_FILE = "usuarios.json"

# --- TU BANCO MAESTRO DE CLAVES ---
MASTER_KEYS = [
    "AQ.Ab8RN6IGiVcgqZ_bqMxCg1R4xd9IVfYKRDUnt9IFQw8oPeGUWw",
    # Agrega aquí el resto de tus claves "AQ..." separadas por coma
]

# Código HTML que se creará automáticamente en tu teléfono
html_code = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAY AI - Oficial</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #4CAF50; }
        input, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 5px; border: none; box-sizing: border-box; }
        input { background: #2b2b2b; color: #fff; }
        button { background: #4CAF50; color: white; font-weight: bold; cursor: pointer; }
        #chat-box { height: 280px; overflow-y: auto; background: #2b2b2b; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .msg { margin: 8px 0; padding: 10px; border-radius: 5px; line-height: 1.4; }
        .user { background: #0b5ed7; text-align: right; }
        .bot { background: #333; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 SAY AI - Oficial</h1>
        <div id="auth-section">
            <h3>Acceso a la Plataforma</h3>
            <input type="text" id="username" placeholder="Nombre de usuario">
            <input type="password" id="password" placeholder="Contraseña">
            <button onclick="login()">Iniciar Sesión / Registrarse</button>
        </div>
        <div id="chat-section" class="hidden">
            <p>Usuario: <b id="user-display"></b> | <span style="color: #4CAF50;">● Sistema Activo</span></p>
            <div id="chat-box"></div>
            <input type="text" id="user-msg" placeholder="Escribe tu consulta...">
            <button onclick="sendMsg()">Enviar</button>
        </div>
    </div>
    <script>
        async function login() {
            const u = document.getElementById('username').value.trim();
            const p = document.getElementById('password').value.trim();
            if(!u || !p) { alert("Completa todos los campos"); return; }
            const res = await fetch('/auth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if(data.success) {
                document.getElementById('auth-section').classList.add('hidden');
                document.getElementById('chat-section').classList.remove('hidden');
                document.getElementById('user-display').innerText = u;
            } else {
                alert(data.msg || "Error en el acceso");
            }
        }
        async function sendMsg() {
            const msgInput = document.getElementById('user-msg');
            const text = msgInput.value.trim();
            if(!text) return;
            const box = document.getElementById('chat-box');
            box.innerHTML += `<div class="msg user"><b>Tú:</b><br>${text}</div>`;
            msgInput.value = "";
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            box.innerHTML += `<div class="msg bot"><b>SAY AI:</b><br>${data.reply}</div>`;
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""

# Generar el archivo index.html automáticamente
with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_code)


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
    return "❌ Error: No hay claves maestras configuradas."

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


class CustomHandler(http.server.SimpleHTTPRequestHandler):

  def do_POST(self):
    content_length = int(self.headers.get("Content-Length", 0))
    post_data = json.loads(self.rfile.read(content_length).decode("utf-8"))

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()

    if self.path == "/auth":
      usuarios = cargar_usuarios()
      u = post_data["username"]
      p = post_data["password"]

      if u in usuarios:
        if usuarios[u]["password"] == p:
          response = {"success": True}
        else:
          response = {"success": False, "msg": "Contraseña incorrecta"}
      else:
        usuarios[u] = {"password": p}
        guardar_usuarios(usuarios)
        response = {"success": True}

      self.wfile.write(json.dumps(response).encode("utf-8"))

    elif self.path == "/chat":
      reply = consultar_gemini_con_pool(post_data["message"])
      self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))


print(f"🚀 Servidor Oficial Activo en http://localhost:{PORT}")
webbrowser.open(f"http://localhost:{PORT}")

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
  httpd.serve_forever()
