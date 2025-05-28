import sqlite3  # Módulo para manejar bases de datos SQLite en Python

# Conexión a la base de datos (se crea el archivo si no existe)
conn = sqlite3.connect('laboratorio.db')
cursor = conn.cursor()  # Objeto para ejecutar comandos SQL

# Crear tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único por usuario
    documento TEXT NOT NULL UNIQUE,         -- Documento único
    codigo_u TEXT NOT NULL,                 -- Código institucional de la universidad
    nombre TEXT NOT NULL,                   -- Nombre completo del estudiante
    correo TEXT NOT NULL,                   -- Correo electrónico
    telefono TEXT NOT NULL,                 -- Número de teléfono
    carrera TEXT NOT NULL                   -- Carrera o programa académico
)
''')

# Crear tabla de registros de entrada/salida
cursor.execute('''
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- ID único por registro
    usuario_id INTEGER NOT NULL,            -- Relación con la tabla de usuarios
    fecha TEXT NOT NULL,                    -- Fecha del registro (AAAA-MM-DD)
    hora TEXT NOT NULL,                     -- Hora del registro (HH:MM:SS)
    estatus TEXT NOT NULL,                  -- "Entrada" o "Salida"
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) -- Llave foránea
)
''')

conn.commit()   # Guardar cambios en la base de datos
conn.close()    # Cerrar conexión
print("✅ Base de datos creada con las tablas 'usuarios' y 'registros'")
