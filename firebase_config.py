import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase_key.json")  # Usa tu archivo .json
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://siresu-1f1ca-default-rtdb.firebaseio.com/"  # Usa la URL exacta
})
