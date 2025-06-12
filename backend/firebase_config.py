import base64
import json
import os
import firebase_admin
from firebase_admin import credentials, db

# Ruta del archivo firebase_key.b64
key_path = os.path.join(os.path.dirname(__file__), "firebase_key.b64")
if not os.path.exists(key_path):
    raise Exception("❌ No se encontró el archivo firebase_key.b64")

# Leer el contenido base64 y decodificarlo
with open(key_path, "r") as f:
    firebase_key_base64 = f.read()

decoded_key = base64.b64decode(firebase_key_base64).decode("utf-8")
firebase_dict = json.loads(decoded_key)

# Inicializar Firebase si aún no está inicializado
FIREBASE_URL = "https://siresu-1f1ca-default-rtdb.firebaseio.com/"
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_URL
    })

# Referencia a la base de datos
ref = db.reference("users")

# Datos del usuario admin
admin_data = {
    "email": "admin@gmail.com",
    "password": "admin123",
    "role": "admin"
}

# Agregar el admin a la base de datos
ref.push(admin_data)

print("✅ Usuario admin creado exitosamente en Firebase.")
