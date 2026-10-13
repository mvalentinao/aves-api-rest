import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # tildes legibles en las respuestas JSON
app.json.sort_keys = False  # mantiene el orden de los campos (id, especie, lugar, ...)

DB_PATH = os.environ.get(
    "DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "avistamientos.db")
)

CAMPOS = ("especie", "lugar", "fecha", "observador")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS avistamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                lugar TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observador TEXT NOT NULL
            )
            """
        )


def validar(datos):
    """Devuelve un mensaje de error si los datos no son válidos, o None si están bien."""
    if not isinstance(datos, dict):
        return "El cuerpo debe ser un objeto JSON"
    faltan = [
        c for c in CAMPOS
        if not isinstance(datos.get(c), str) or not datos[c].strip()
    ]
    if faltan:
        return "Faltan datos o son inválidos: " + ", ".join(faltan)
    fecha = datos["fecha"].strip()
    try:
        if len(fecha) != 10:
            raise ValueError
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return "La fecha debe tener el formato AAAA-MM-DD y ser una fecha real"
    return None


def buscar(conn, id):
    return conn.execute("SELECT * FROM avistamientos WHERE id = ?", (id,)).fetchone()


@app.get("/avistamientos")
def listar():
    with get_db() as conn:
        filas = conn.execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
    return jsonify([dict(f) for f in filas]), 200


@app.get("/avistamientos/resumen")
def resumen():
    with get_db() as conn:
        filas = conn.execute(
            "SELECT especie, COUNT(*) AS cantidad FROM avistamientos "
            "GROUP BY especie ORDER BY cantidad DESC, especie"
        ).fetchall()
    return jsonify([dict(f) for f in filas]), 200


@app.get("/avistamientos/<int:id>")
def ver(id):
    with get_db() as conn:
        fila = buscar(conn, id)
    if fila is None:
        return jsonify({"error": "Avistamiento no encontrado"}), 404
    return jsonify(dict(fila)), 200


@app.post("/avistamientos")
def crear():
    datos = request.get_json(silent=True)
    error = validar(datos)
    if error:
        return jsonify({"error": error}), 400
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
            tuple(datos[c].strip() for c in CAMPOS),
        )
        fila = buscar(conn, cur.lastrowid)
    return jsonify(dict(fila)), 201


@app.put("/avistamientos/<int:id>")
def actualizar(id):
    datos = request.get_json(silent=True)
    with get_db() as conn:
        if buscar(conn, id) is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        error = validar(datos)
        if error:
            return jsonify({"error": error}), 400
        conn.execute(
            "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
            tuple(datos[c].strip() for c in CAMPOS) + (id,),
        )
        fila = buscar(conn, id)
    return jsonify(dict(fila)), 200


@app.delete("/avistamientos/<int:id>")
def eliminar(id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
    if cur.rowcount == 0:
        return jsonify({"error": "Avistamiento no encontrado"}), 404
    return "", 204


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
