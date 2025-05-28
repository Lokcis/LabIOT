import sqlite3
import pandas as pd  # Librería para manejar hojas de cálculo

# Conectarse a la base de datos SQLite
conn = sqlite3.connect("laboratorio.db")

# Ejecutar consulta SQL con JOIN para incluir información de usuario
df = pd.read_sql_query("""
SELECT r.id, u.documento, u.codigo_u, u.nombre, u.carrera,
       r.fecha, r.hora, r.estatus
FROM registros r
JOIN usuarios u ON r.usuario_id = u.id
ORDER BY r.id ASC
""", conn)

# Guardar como archivo Excel
df.to_excel("registros_laboratorio.xlsx", index=False)

conn.close()
print("✅ Registros exportados a registros_laboratorio.xlsx")
