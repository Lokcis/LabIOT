import sqlite3

def insertar_usuario(documento, codigo, nombre, correo, telefono, carrera):
    conn = sqlite3.connect("laboratorio.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (documento, codigo_u, nombre, correo, telefono, carrera)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (documento, codigo, nombre, correo, telefono, carrera))
    conn.commit()
    conn.close()
    print(f"✅ Usuario {nombre} registrado con éxito.")

# Insertar un usuario de ejemplo
insertar_usuario(
    "12345678",
    "U2025001",
    "Juan Pérez",
    "juan.perez@uni.edu.co",
    "3101234567",
    "Ingeniería de Sistemas"
)
