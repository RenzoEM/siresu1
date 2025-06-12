import os
import base64
import json
import firebase_admin
from firebase_admin import credentials, db

base64_key = os.environ.get("FIREBASE_KEY_BASE64")
if not base64_key:
    raise Exception("❌ Variable de entorno FIREBASE_KEY_BASE64 no configurada")

decoded_key = base64.b64decode(base64_key).decode('utf-8')
key_dict = json.loads(decoded_key)

cred = credentials.Certificate(key_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://siresu-1f1ca-default-rtdb.firebaseio.com/'
    })

admin_email = "admin@gmail.com"
admin_key = admin_email.replace('.', '_')
admin_data = {
    "password": "admin123",
    "role": "admin"
}

db.reference("users").child(admin_key).set(admin_data)
print("✅ Usuario admin creado correctamente")
