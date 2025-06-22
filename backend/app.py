from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from firebase_config import firestore_db
from flask_dance.contrib.google import make_google_blueprint, google
import os
import re
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://siresu1.vercel.app"])
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta")

# OAuth Google
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
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

    user_ref = firestore_db.collection("users").document(username)
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

    user_ref = firestore_db.collection("users").document(username)
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
        return jsonify({"message": "Correo inválido"}), 400

    user_ref = firestore_db.collection("users").document(email)
    user_doc = user_ref.get()

    if not user_doc.exists:
        user_ref.set({
            "password": "",
            "role": "cliente"
        })
        role = "cliente"
    else:
        role = user_doc.to_dict().get("role", "cliente")

    if role == "admin":
        return redirect("https://siresu1.vercel.app/admin.html")
    else:
        return redirect("https://siresu1.vercel.app/cliente.html")


@app.route("/reclamos", methods=["POST"])
def crear_reclamo():
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400

    try:
        firestore_db.collection("reclamos").add({
            "tipo": data.get("tipo"),
            "descripcion": data.get("descripcion"),
            "ubicacion": data.get("ubicacion"),
            "correo": data.get("correo", ""),
            "estado": "Pendiente",
            "fecha": datetime.now().isoformat()
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/crear-usuario", methods=["POST"])
def crear_usuario():
    data = request.get_json()
    correo = data.get("correo", "").strip()
    password = data.get("password", "").strip()
    rol = data.get("rol", "cliente").strip()

    if not correo or "@" not in correo or "." not in correo:
        return jsonify({"error": "Correo inválido"}), 400
    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400
    if rol not in ["cliente", "admin"]:
        return jsonify({"error": "Rol inválido"}), 400

    try:
        user_ref = firestore_db.collection("users").document(correo)
        if user_ref.get().exists:
            return jsonify({"error": "El usuario ya existe"}), 400

        user_ref.set({
            "password": password,
            "role": rol
        })
        return jsonify({"message": "Usuario creado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error al crear usuario: {str(e)}"}), 500



@app.route("/api/reclamos", methods=["GET"])
def obtener_reclamos():
    try:
        reclamos = firestore_db.collection("reclamos").stream()
        resultado = []
        for r in reclamos:
            data = r.to_dict()
            data["id"] = r.id
            resultado.append(data)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reclamos/<id>", methods=["PATCH"])
def actualizar_reclamo(id):
    data = request.get_json()
    nuevo_estado = data.get("estado")

    if nuevo_estado not in ["pendiente", "en proceso", "resuelto"]:
        return jsonify({"error": "Estado inválido"}), 400

    try:
        # Actualizar estado del reclamo
        doc_ref = firestore_db.collection("reclamos").document(id)
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "Reclamo no encontrado"}), 404

        reclamo = doc.to_dict()
        correo_cliente = reclamo.get("correo", "")
        doc_ref.update({"estado": nuevo_estado})

        # Guardar notificación en Firestore
        if correo_cliente:
            firestore_db.collection("notificaciones").add({
                "correo": correo_cliente,
                "mensaje": f"El estado de tu reclamo fue actualizado a: {nuevo_estado}",
                "fecha": datetime.now().isoformat()
            })


        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
