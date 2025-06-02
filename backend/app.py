from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from database import get_db_connection
import os
from dotenv import load_dotenv

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
    role = data.get("role", "cliente")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (username, password, role))
        conn.commit()
        return jsonify({"message": "Registro exitoso"}), 201
    except Exception as e:
        return jsonify({"message": "Usuario ya existe"}), 400
    finally:
        cursor.close()
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({
            "message": "Login exitoso",
            "role": user["role"]
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


@app.route("/create-admin", methods=["POST"])
def create_admin():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'admin')",
                       (username, password))
        conn.commit()
        return jsonify({"message": "Admin creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"message": "Error al crear admin"}), 400
    finally:
        cursor.close()
        conn.close()


@app.route("/crear-admin-inicial", methods=["GET"])
def crear_admin_inicial():
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       ("admin@gmail.com", "admin123", "admin"))
        conn.commit()
        return "✅ Admin creado exitosamente", 200
    except Exception as e:
        return f"❌ Error al crear admin: {str(e)}", 400
    finally:
        cursor.close()
        conn.close()


@app.route("/crear-admin-secundario", methods=["GET"])
def crear_admin_secundario():
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       ("admin2@gmail.com", "admin456", "admin"))
        conn.commit()
        return "✅ Admin secundario creado con éxito", 200
    except Exception as e:
        return f"❌ Error al crear admin: {str(e)}", 400
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
from flask_cors import CORS

CORS(app)  # Permite desde cualquier origen
CORS(app, origins=["https://siresu1.vercel.app"])

    
    