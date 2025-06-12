import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, db

key_b64 = os.getenv("FIREBASE_KEY_B64")

if not key_b64:
    raise Exception("❌ Variable de entorno FIREBASE_KEY_B64 no configurada")

key_json = json.loads(base64.b64decode(key_b64))
cred = credentials.Certificate(key_json)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://siresu-1f1ca-default-rtdb.firebaseio.com/"
    })

db = db.reference("users")
