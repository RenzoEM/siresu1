import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar clave desde variable de entorno codificada en base64
FIREBASE_KEY_BASE64 = os.getenv("FIREBASE_KEY_BASE64")
if not FIREBASE_KEY_BASE64:
    raise Exception("❌ Variable de entorno FIREBASE_KEY_BASE64 no configurada")

# Decodificar y cargar credenciales
firebase_key_json = base64.b64decode(FIREBASE_KEY_BASE64).decode("utf-8")
cred_dict = json.loads(firebase_key_json)

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()
