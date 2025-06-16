import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore

# Leer y decodificar la clave base64
key_base64 = os.getenv("FIREBASE_KEY_BASE64")
if not key_base64:
    raise Exception("❌ Variable de entorno FIREBASE_KEY_BASE64 no configurada")

firebase_json = base64.b64decode(key_base64).decode("utf-8")

# Inicializar la app Firebase con credenciales
cred = credentials.Certificate(eval(firebase_json))
firebase_admin.initialize_app(cred)

firestore_db = firestore.client()
