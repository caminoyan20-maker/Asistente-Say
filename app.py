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

  ultimo_error = ""
  for api_key in MASTER_KEYS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
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
      except:
        error_detalle = str(e)
      ultimo_error = f"HTTP {e.code}: {error_detalle}"
      continue
    except Exception as e:
      ultimo_error = str(e)
      continue

  return f"🛑 DIAGNOSTICO DE API: {ultimo_error}"
    
