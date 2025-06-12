from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from firebase_config import db
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://siresu1.vercel.app"])
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")

# Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")


def correo_valido(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.(com|org|net)$", email))


def contraseña_valida(password):
    return len(password) >= 8


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not correo_valido(username):
        return jsonify({"message": "Correo no válido"}), 400

    if not contraseña_valida(password):
        return jsonify({"message": "La contraseña debe tener al menos 8 caracteres"}), 400

    ref = db.reference("users")
    key = username.replace(".", "_").replace("@", "_at_")

    if ref.child(key).get():
        return jsonify({"message": "Usuario ya existe"}), 400

    ref.child(key).set({
        "password": password,
        "role": "cliente"
    })

    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not correo_valido(username) or not contraseña_valida(password):
        return jsonify({"message": "Credenciales inválidas"}), 400

    key = username.replace(".", "_").replace("@", "_at_")
    user = db.reference("users").child(key).get()

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

    if not correo_valido(email):
        return jsonify({"message": "Correo no válido"}), 400

    key = email.replace(".", "_").replace("@", "_at_")
    ref = db.reference("users")
    user_ref = ref.child(key)

    if not user_ref.get():
        user_ref.set({
            "password": "",
            "role": "cliente"
        })

    role = user_ref.get().get("role", "cliente")

    # Redirigir al frontend
    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
