from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from firebase_config import db
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")
CORS(app, origins=["https://siresu1.vercel.app"])

# Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="https://siresu1.onrender.com/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")


def es_correo_valido(email):
    return bool(re.match(r"^[^@]+@[^@]+\.(com|net|org)$", email))


def es_contraseña_valida(password):
    return len(password) >= 8


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not es_correo_valido(username):
        return jsonify({"message": "Correo no válido"}), 400
    if not es_contraseña_valida(password):
        return jsonify({"message": "Contraseña muy corta"}), 400

    user_key = username.replace(".", "_")
    if db.child(user_key).get():
        return jsonify({"message": "Usuario ya existe"}), 400

    db.child(user_key).set({
        "password": password,
        "role": "cliente"
    })
    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not es_correo_valido(username):
        return jsonify({"message": "Correo inválido"}), 400
    if not es_contraseña_valida(password):
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
        return jsonify({"message": "Error con Google"}), 400

    email = resp.json().get("email")
    user_key = email.replace(".", "_")
    user = db.child(user_key).get()

    if not user:
        db.child(user_key).set({
            "password": "",
            "role": "cliente"
        })
        role = "cliente"
    else:
        role = user.get("role", "cliente")

    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
