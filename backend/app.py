from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from database import get_db_connection
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from siresu.backend.firebase_config import db
from firebase_config import db

app = Flask(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key")

# Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    ref = db.reference("users")
    if ref.child(username).get():
        return jsonify({"message": "Usuario ya existe"}), 400

    ref.child(username).set({
        "password": password,
        "role": "cliente"
    })
    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = db.reference("users").child(username).get()

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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (email, '', 'cliente'))
        conn.commit()
        role = "cliente"
    else:
        role = user["role"]

    cursor.close()
    conn.close()

    if role == "admin":
        return redirect("/admin.html")
    else:
        return redirect("/cliente.html")

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://siresu1.vercel.app"])  # CORS solo desde Vercel


    
    