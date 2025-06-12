import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, db

# Leer clave desde variable de entorno
firebase_b64 = os.environ.get("FIREBASE_KEY_BASE64")

if not firebase_b64:
    raise Exception("❌ Variable de entorno FIREBASE_KEY_BASE64 no configurada")

key_dict = json.loads(base64.b64decode(firebase_b64).decode("utf-8"))
cred = credentials.Certificate(key_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://siresu-1f1ca-default-rtdb.firebaseio.com/'
    })

db = db.reference("users")
