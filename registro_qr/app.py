from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def buscar_usuario(documento):
    conn = sqlite3.connect("laboratorio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE documento=?", (documento,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def obtener_ultimo_estatus(usuario_id):
    conn = sqlite3.connect("laboratorio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT estatus FROM registros WHERE usuario_id=? ORDER BY id DESC LIMIT 1", (usuario_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def registrar(documento):
    usuario_id = buscar_usuario(documento)
    if not usuario_id:
        return "❌ Usuario no registrado", False
    estatus_anterior = obtener_ultimo_estatus(usuario_id)
    nuevo_estatus = "Entrada" if estatus_anterior in [None, "Salida"] else "Salida"
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")
    conn = sqlite3.connect("laboratorio.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registros (usuario_id, fecha, hora, estatus) VALUES (?, ?, ?, ?)",
        (usuario_id, fecha, hora, nuevo_estatus)
    )
    conn.commit()
    conn.close()
    return f"✅ {nuevo_estatus} registrada para el documento {documento}", True

# Ruta para el formulario de registro de entrada/salida
@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""
    if request.method == "POST":
        documento = request.form["documento"]
        mensaje, exito = registrar(documento)
    return render_template("index.html", mensaje=mensaje)

# Nueva ruta para formulario de creación de usuario
@app.route("/nuevo_usuario", methods=["GET", "POST"])
def nuevo_usuario():
    mensaje = ""
    if request.method == "POST":
        # Recibir datos del formulario
        documento = request.form["documento"]
        codigo_u = request.form["codigo_u"]
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]
        carrera = request.form["carrera"]

        try:
            conn = sqlite3.connect("laboratorio.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (documento, codigo_u, nombre, correo, telefono, carrera)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (documento, codigo_u, nombre, correo, telefono, carrera))
            conn.commit()
            conn.close()
            mensaje = "✅ Usuario registrado correctamente"
        except sqlite3.IntegrityError:
            mensaje = "❌ Error: El documento ya está registrado"
    return render_template("nuevo_usuario.html", mensaje=mensaje)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
