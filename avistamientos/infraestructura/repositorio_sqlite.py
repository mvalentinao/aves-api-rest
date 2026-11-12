"""Borde (infraestructura): implementación del repositorio con SQLite.

Esta clase implementa `RepositorioDeAvistamientos` (interfaz del núcleo), así
que el acoplamiento va de afuera hacia adentro: el núcleo no sabe que existe.
Todo lo que menciona `sqlite3` o SQL está en este archivo.
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from avistamientos.nucleo.interfaces.repositorio_avistamientos import RepositorioDeAvistamientos
from avistamientos.nucleo.modelo_dominio.avistamiento import Avistamiento, ResumenDeEspecie


def _a_avistamiento(fila) -> Avistamiento:
    return Avistamiento(
        id=fila["id"],
        especie=fila["especie"],
        lugar=fila["lugar"],
        fecha=fila["fecha"],
        observador=fila["observador"],
    )


class RepositorioSqlite(RepositorioDeAvistamientos):
    def __init__(self, ruta_db: str):
        self._ruta_db = ruta_db

    @contextmanager
    def _conexion(self):
        """Abre la base, confirma (commit) al salir del bloque y cierra la conexión.
        Con `with sqlite3.connect()` a secas la conexión se confirma pero no se cierra."""
        conn = sqlite3.connect(self._ruta_db)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def crear_esquema(self) -> None:
        """Crea la tabla si no existe. No es parte de la interfaz del núcleo: es un
        detalle de SQLite que solo conoce quien arma la aplicación."""
        with self._conexion() as conn:
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

    def vaciar(self) -> None:
        """Borra todo y reinicia los ids. Solo lo usa `seed.py --reiniciar`."""
        with self._conexion() as conn:
            conn.execute("DELETE FROM avistamientos")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'avistamientos'")

    # --- implementación de la interfaz del núcleo ---

    def listar(self) -> List[Avistamiento]:
        with self._conexion() as conn:
            filas = conn.execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
        return [_a_avistamiento(f) for f in filas]

    def obtener(self, id: int) -> Optional[Avistamiento]:
        with self._conexion() as conn:
            fila = self._buscar(conn, id)
        return None if fila is None else _a_avistamiento(fila)

    def agregar(self, avistamiento: Avistamiento) -> Avistamiento:
        with self._conexion() as conn:
            cur = conn.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
                (avistamiento.especie, avistamiento.lugar, avistamiento.fecha, avistamiento.observador),
            )
            fila = self._buscar(conn, cur.lastrowid)
        return _a_avistamiento(fila)

    def actualizar(self, id: int, avistamiento: Avistamiento) -> Optional[Avistamiento]:
        with self._conexion() as conn:
            cur = conn.execute(
                "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
                (avistamiento.especie, avistamiento.lugar, avistamiento.fecha, avistamiento.observador, id),
            )
            if cur.rowcount == 0:
                return None
            fila = self._buscar(conn, id)
        return _a_avistamiento(fila)

    def eliminar(self, id: int) -> bool:
        with self._conexion() as conn:
            cur = conn.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
        return cur.rowcount > 0

    def resumen_por_especie(self) -> List[ResumenDeEspecie]:
        with self._conexion() as conn:
            filas = conn.execute(
                "SELECT especie, COUNT(*) AS cantidad FROM avistamientos "
                "GROUP BY especie ORDER BY cantidad DESC, especie"
            ).fetchall()
        return [ResumenDeEspecie(especie=f["especie"], cantidad=f["cantidad"]) for f in filas]

    @staticmethod
    def _buscar(conn, id):
        return conn.execute("SELECT * FROM avistamientos WHERE id = ?", (id,)).fetchone()
