import os
import json
from datetime import datetime, timezone

import joblib
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template_string

MODEL_PATH = os.getenv("MODEL_PATH", "miarbol.pkl")
model = joblib.load(MODEL_PATH)

# Configurar FIREBASE_CREDENTIALS_JSON en Render como variable de entorno.
firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
if not firebase_json:
    raise RuntimeError("Falta configurar FIREBASE_CREDENTIALS_JSON en Render.")

service_account_info = json.loads(firebase_json)
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Predicción - Actividad 09</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 18px; line-height: 1.5; }
    input { width: 100%; padding: 10px; margin: 5px 0 14px; box-sizing: border-box; }
    button { padding: 11px 16px; cursor: pointer; }
    .note { background: #f2f2f2; padding: 12px; border-radius: 8px; }
    pre { white-space: pre-wrap; background: #f6f6f6; padding: 12px; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>Predicción con árbol de decisión</h1>
  <p>Ingresa los cinco valores de entrada del modelo.</p>
  <form id="form">
    <label>Edad (Age)</label><input name="Age" type="number" min="1" max="120" value="50" required>
    <label>Sexo codificado (Sex: 0=M, 1=F según el notebook)</label><input name="Sex" type="number" min="0" max="1" step="1" value="0" required>
    <label>Presión arterial en reposo (RestingBP)</label><input name="RestingBP" type="number" min="0" max="300" value="130" required>
    <label>Colesterol (Cholesterol)</label><input name="Cholesterol" type="number" min="0" max="1000" value="220" required>
    <label>Frecuencia cardíaca máxima (MaxHR)</label><input name="MaxHR" type="number" min="0" max="300" value="150" required>
    <button type="submit">Predecir y guardar en Firebase</button>
  </form>
  <h2>Resultado</h2><pre id="result">Todavía no se ha realizado una predicción.</pre>
  <p class="note">Demostración académica. No usar para diagnóstico médico.</p>
<script>
document.getElementById('form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = Object.fromEntries(fd.entries());
  for (const k of Object.keys(payload)) payload[k] = Number(payload[k]);
  const out = document.getElementById('result');
  out.textContent = 'Procesando...';
  try {
    const res = await fetch('/predecir', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = 'Error: ' + err.message;
  }
});
</script>
</body>
</html>
"""

@app.get("/")
def inicio():
    return render_template_string(HTML)

@app.get("/health")
def health():
    return jsonify({"estado": "activo"})

@app.post("/predecir")
def predecir():
    try:
        datos = request.get_json(force=True)
        required = ["Age", "Sex", "RestingBP", "Cholesterol", "MaxHR"]
        if not isinstance(datos, dict) or any(k not in datos for k in required):
            return jsonify({"error": "Debes enviar Age, Sex, RestingBP, Cholesterol y MaxHR."}), 400

        valores = [[
            float(datos["Age"]),
            float(datos["Sex"]),
            float(datos["RestingBP"]),
            float(datos["Cholesterol"]),
            float(datos["MaxHR"]),
        ]]
        prediccion = int(model.predict(np.array(valores))[0])
        resultado = "Posible enfermedad cardíaca" if prediccion == 1 else "Sin indicios según el modelo"

        registro = {
            "entrada": {k: datos[k] for k in required},
            "prediccion": prediccion,
            "resultado": resultado,
            "modelo": "arbol_decision",
            "fecha": datetime.now(timezone.utc).isoformat(),
        }
        _, doc_ref = db.collection("predicciones_actividad09").add(registro)
        return jsonify({
            "id_firebase": doc_ref.id,
            "prediccion": prediccion,
            "resultado": resultado,
            "guardado_en_firebase": True
        })
    except Exception as exc:
        return jsonify({"error": f"No se pudo completar la predicción o guardarla: {str(exc)}"}), 500
