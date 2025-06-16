from flask import Flask, request, jsonify, redirect, url_for
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

# OAuth Google
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")


def correo_valido(email):
    return re.match(r"^[^@]+@[^@]+\.(com|org|net|edu|pe)$", email)


def contraseña_valida(password):
    return len(password) >= 8


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not correo_valido(username):
        return jsonify({"message": "Correo inválido"}), 400

    if not contraseña_valida(password):
        return jsonify({"message": "La contraseña debe tener al menos 8 caracteres"}), 400

    user_ref = db.collection("users").document(username)
    if user_ref.get().exists:
        return jsonify({"message": "Usuario ya existe"}), 400

    user_ref.set({
        "password": password,
        "role": "admin" if username == "admin@gmail.com" else "cliente"
    })
    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not correo_valido(username):
        return jsonify({"message": "Correo inválido"}), 400

    if not contraseña_valida(password):
        return jsonify({"message": "Contraseña inválida"}), 400

    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"message": "Usuario no encontrado"}), 404

    user_data = user_doc.to_dict()
    if user_data.get("password") != password:
        return jsonify({"message": "Contraseña incorrecta"}), 401

    return jsonify({
        "message": "Login exitoso",
        "role": user_data.get("role", "cliente")
    }), 200


@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({"message": "Error al obtener datos de Google"}), 400

    info = resp.json()
    email = info.get("email")

    if not correo_valido(email):
        return jsonify({"message": "Correo de Google inválido"}), 400

    user_ref = db.collection("users").document(email)
    user_doc = user_ref.get()

    if not user_doc.exists:
        user_ref.set({
            "password": "",
            "role": "cliente"
        })
        role = "cliente"
    else:
        role = user_doc.to_dict().get("role", "cliente")

    # Redirigir según rol
    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    return redirect("https://siresu1.vercel.app/cliente.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
