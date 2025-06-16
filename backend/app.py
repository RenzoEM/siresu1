from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from firebase_config import db
from flask_dance.contrib.google import make_google_blueprint, google
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://siresu1.vercel.app"])
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")

# Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

def correo_valido(email):
    return "@" in email and email.endswith((".com", ".net", ".org", ".edu.pe"))

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

    user_doc = db.collection("users").document(username)
    if user_doc.get().exists:
        return jsonify({"message": "El usuario ya existe"}), 400

    user_doc.set({
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

    user_doc = db.collection("users").document(username).get()
    if user_doc.exists and user_doc.to_dict().get("password") == password:
        return jsonify({
            "message": "Login exitoso",
            "role": user_doc.to_dict().get("role", "cliente")
        }), 200

    return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

@app.route("/login/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({"message": "Error al obtener información de Google"}), 400

    info = resp.json()
    email = info["email"]

    if not correo_valido(email):
        return jsonify({"message": "Correo no válido"}), 400

    user_doc = db.collection("users").document(email)
    if not user_doc.get().exists:
        user_doc.set({
            "password": "",  # sin contraseña
            "role": "cliente"
        })

    role = user_doc.get().to_dict().get("role", "cliente")
    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
