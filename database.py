import sqlite3

DB_NAME = "mapoteca_ca.db"


def conectar_db():
    return sqlite3.connect(DB_NAME)


def crear_tabla():
    conn = conectar_db()
    cursor = conn.cursor()

    # 1. Crear tabla si no existe (incluye 'ubicacion' y 'cantidad')
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS hojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_hoja TEXT NOT NULL,
            numero_hoja TEXT NOT NULL,
            departamento TEXT,
            edicion TEXT,
            tipo TEXT,
            escala TEXT,
            provincia TEXT,
            ubicacion TEXT,
            cantidad INTEGER DEFAULT 1,
            obs TEXT
        )
    """
    )

    # 2. Migraciones automáticas por si la tabla fue creada previamente sin estas columnas
    try:
        cursor.execute("ALTER TABLE hojas ADD COLUMN ubicacion TEXT")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    try:
        cursor.execute(
            "ALTER TABLE hojas ADD COLUMN cantidad INTEGER DEFAULT 1"
        )
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    conn.commit()
    conn.close()


def obtener_registros():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre_hoja, numero_hoja, departamento, edicion, tipo, escala, provincia, ubicacion, cantidad, obs FROM hojas"
    )
    filas = cursor.fetchall()
    conn.close()

    return [
        {
            "id": f[0],
            "nombre_hoja": f[1],
            "numero_hoja": f[2],
            "departamento": f[3],
            "edicion": f[4],
            "tipo": f[5],
            "escala": f[6],
            "provincia": f[7],
            "ubicacion": f[8],
            "cantidad": f[9],
            "obs": f[10],
        }
        for f in filas
    ]


def guardar_registro(
    nombre,
    num_hoja,
    depto,
    edicion,
    tipo,
    escala,
    provincia,
    ubicacion,
    cantidad,
    obs,
):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO hojas (nombre_hoja, numero_hoja, departamento, edicion, tipo, escala, provincia, ubicacion, cantidad, obs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            nombre,
            num_hoja,
            depto,
            edicion,
            tipo,
            escala,
            provincia,
            ubicacion,
            cantidad,
            obs,
        ),
    )
    conn.commit()
    conn.close()


def eliminar_registros_por_ids(ids_a_eliminar):
    if not ids_a_eliminar:
        return
    conn = conectar_db()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(ids_a_eliminar))
    query = f"DELETE FROM hojas WHERE id IN ({placeholders})"
    cursor.execute(query, ids_a_eliminar)
    conn.commit()
    conn.close()