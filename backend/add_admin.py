import os
import base64
import json
import firebase_admin
from firebase_admin import credentials, db

# Leer base64 desde el archivo .b64
firebase_b64_path = os.path.join("backend", "firebase_key.b64")

if not os.path.exists(firebase_b64_path):
    print("❌ No se encontró el archivo firebase_key.b64")
    exit(1)

with open(firebase_b64_path, "r") as f:
    base64_key = f.read().strip()

if not base64_key:
    print("❌ El archivo firebase_key.b64 está vacío")
    exit(1)

try:
    decoded_key = base64.b64decode(base64_key).decode('utf-8')
    key_dict = json.loads(decoded_key)
except Exception as e:
    print("❌ Error al decodificar la clave:", e)
    exit(1)

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://siresu-1f1ca-default-rtdb.firebaseio.com/'
        })
except Exception as e:
    print("❌ Error al inicializar Firebase:", e)
    exit(1)

try:
    ref = db.reference("users")
    admin_email = "admin123"
    admin_password = "admin123"

    if ref.child(admin_email).get():
        print("ℹ️ El usuario admin ya existe en Firebase.")
    else:
        ref.child(admin_email).set({
            "password": admin_password,
            "role": "admin"
        })
        print("✅ Usuario admin creado con éxito.")
except Exception as e:
    print("❌ Error al escribir en Firebase:", e)
