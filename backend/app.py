from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from firebase_config import db
from flask_dance.contrib.google import make_google_blueprint, google
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://siresu1.vercel.app"])
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")

# Config Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

# Validaciones
def correo_valido(email):
    return "@" in email and (email.endswith(".com") or email.endswith(".org") or email.endswith(".net"))

def contraseña_valida(password):
    return len(password) >= 8

import re

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not is_valid_email(username):
        return jsonify({"message": "Correo no válido"}), 400

    if len(password) < 8:
        return jsonify({"message": "La contraseña debe tener al menos 8 caracteres"}), 400

    ref = db.reference("users")
    if ref.child(username.replace(".", "_")).get():
        return jsonify({"message": "Usuario ya existe"}), 400

    ref.child(username.replace(".", "_")).set({
        "password": password,
        "role": "cliente"
    })
    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not correo_valido(username):
        return jsonify({"message": "Correo inválido"}), 400

    if not contraseña_valida(password):
        return jsonify({"message": "Contraseña inválida"}), 400

    user = db.child(username.replace(".", "_")).get()

    if user and user.get("password") == password:
        return jsonify({
            "message": "Login exitoso",
            "role": user.get("role")
        }), 200

    return jsonify({"message": "Usuario o contraseña incorrectos"}), 401


@app.route("/google-login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({"message": "Error al obtener datos de Google"}), 400

    info = resp.json()
    email = info["email"]

    if not is_valid_email(email):
        return jsonify({"message": "Correo no válido"}), 400

    ref = db.reference("users")
    user_ref = ref.child(email.replace(".", "_"))
    user_data = user_ref.get()

    if not user_data:
        user_ref.set({
            "password": "",  # sin contraseña porque viene de Google
            "role": "cliente"
        })
        role = "cliente"
    else:
        role = user_data.get("role", "cliente")

    # Redirigir según rol
    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
