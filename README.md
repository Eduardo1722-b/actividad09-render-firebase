# Actividad 09: Render + Firebase Firestore

Esta plantilla publica el árbol de decisión del notebook como una aplicación web en Render. La predicción se guarda en la colección `predicciones_actividad09` de Firestore.

## 1. Generar el modelo
Ejecuta el notebook `Actividad_09.ipynb` hasta la celda que exporta `miarbol.pkl`. Comprueba que el archivo exista.

## 2. Preparar Firebase
1. Crea un proyecto en https://console.firebase.google.com/
2. Habilita Cloud Firestore.
3. En Configuración del proyecto > Cuentas de servicio, genera una clave privada.
4. Copia el contenido completo del archivo JSON de la cuenta de servicio. No lo subas al repositorio ni lo compartas públicamente.

## 3. Subir a GitHub
Crea un repositorio privado y sube `app.py`, `requirements.txt`, `render.yaml`, `README.md` y `miarbol.pkl`. No subas las credenciales de Firebase.

## 4. Desplegar en Render
1. En https://render.com/ inicia sesión y elige **New > Web Service**.
2. Conecta el repositorio.
3. Render detectará `render.yaml`. Si no lo hace, configura:
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. En Environment, agrega `FIREBASE_CREDENTIALS_JSON` como variable secreta y pega el JSON completo de la cuenta de servicio.
5. Inicia el despliegue y espera que termine.

## 5. Probar
Abre la URL de Render. Aparecerá un formulario para ingresar los cinco valores. Pulsa **Predecir y guardar en Firebase**. También puedes enviar JSON a `POST /predecir`.

Ejemplo de JSON de prueba (valores ilustrativos):
```json
{
  "Age": 50,
  "Sex": 0,
  "RestingBP": 130,
  "Cholesterol": 220,
  "MaxHR": 150
}
```

Una respuesta correcta incluye `id_firebase`, `prediccion`, `resultado` y `guardado_en_firebase: true`. Luego verifica en Firebase Console > Firestore Database > `predicciones_actividad09`.

## Notas
- `miarbol.pkl` debe ser el modelo entrenado en tu notebook. Si el modelo fue entrenado con columnas u orden diferentes, ajusta la lista de entradas para que coincida exactamente con el entrenamiento.
- `Sex` se interpreta aquí como `0=M` y `1=F`, según la codificación asumida en la plantilla; verifica que coincida con tu notebook.
- No subas claves privadas al repositorio. Usa variables de entorno en Render.
- Es un ejercicio académico, no una herramienta de diagnóstico médico.
