from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from firebase_config import db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://siresu1.onrender.com" , "https://siresu1.vercel.app"])
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")

# Blueprint para Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="https://siresu1.onrender.com/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Sanear correos para usarlos como claves válidas en Firebase
def sanitize_email(email):
    return email.replace(".", "_").replace("@", "_at_").replace("$", "_d_").replace("#", "_h_").replace("[", "_lb_").replace("]", "_rb_").replace("/", "_sl_")

def correo_valido(email):
    # Acepta correos tipo nombre@dominio.extension (cualquier TLD)
    return bool(re.match(r"[^@]+@[^@]+\.[a-zA-Z]{2,}$", email))


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
        return jsonify({"message": "Contraseña inválida"}), 400

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
        return jsonify({"message": "Correo no válido"}), 400
    if not contraseña_valida(password):
        return jsonify({"message": "Contraseña inválida"}), 400

    user_key = sanitize_email(username)
    user = db.reference("users").child(user_key).get()

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

    user_key = sanitize_email(email)
    ref = db.reference("users")
    user_ref = ref.child(user_key)
    user_data = user_ref.get()

    if not user_data:
        user_ref.set({
            "password": "",
            "role": "cliente"
        })
        role = "cliente"
    else:
        role = user_data.get("role", "cliente")

    # Redirige según el rol
    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
