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

# Configuración de Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")


# Función para validar correos y contraseñas
def correo_valido(email):
    return "@" in email and (email.endswith(".com") or email.endswith(".org") or email.endswith(".net"))

def contraseña_valida(password):
    return len(password) >= 8


# Registro normal
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not correo_valido(username):
        return jsonify({"message": "Correo no válido"}), 400

    if not contraseña_valida(password):
        return jsonify({"message": "La contraseña debe tener al menos 8 caracteres"}), 400

    user_ref = db.child("users").child(username.replace(".", "_"))
    if user_ref.get():
        return jsonify({"message": "Usuario ya existe"}), 400

    user_ref.set({
        "password": password,
        "role": "cliente"
    })
    return jsonify({"message": "Registro exitoso"}), 201


# Login normal
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not correo_valido(username):
        return jsonify({"message": "Correo inválido"}), 400

    if not contraseña_valida(password):
        return jsonify({"message": "Contraseña inválida"}), 400

    user_ref = db.child("users").child(username.replace(".", "_"))
    user = user_ref.get()

    if user and user.get("password") == password:
        return jsonify({
            "message": "Login exitoso",
            "role": user.get("role")
        }), 200

    return jsonify({"message": "Usuario o contraseña incorrectos"}), 401


# Login con Google
@app.route("/google-login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({"message": "Error al obtener datos de Google"}), 400

    info = resp.json()
    email = info.get("email")

    if not correo_valido(email):
        return jsonify({"message": "Correo de Google no válido"}), 400

    user_ref = db.child("users").child(email.replace(".", "_"))
    user_data = user_ref.get()

    if not user_data:
        user_ref.set({
            "password": "",  # Vacío porque es login con Google
            "role": "cliente"
        })
        role = "cliente"
    else:
        role = user_data.get("role", "cliente")

    # Redirección por rol
    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
