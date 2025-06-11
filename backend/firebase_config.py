import os, json, base64
import firebase_admin
from firebase_admin import credentials, db


firebase_key_b64 = os.getenv("FIREBASE_KEY_B64")
firebase_key_json = json.loads(base64.b64decode(firebase_key_b64))

cred = credentials.Certificate(firebase_key_json)
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://siresu-1f1ca-default-rtdb.firebaseio.com/"
})
