"""Raíz de composición: el único lugar que conoce todas las capas.

Aquí se eligen las implementaciones del borde (SQLite, reloj del sistema) y se
inyectan en el núcleo, que solo conoce interfaces. Para cambiar de base de
datos basta con cambiar esta función; el núcleo no se toca.

    python app.py     # levanta la API en http://127.0.0.1:5000
"""
import os

from avistamientos.infraestructura.reloj_sistema import RelojSistema
from avistamientos.infraestructura.repositorio_sqlite import RepositorioSqlite
from avistamientos.nucleo.interfaces.reloj import Reloj
from avistamientos.nucleo.servicios_aplicacion.servicio_avistamientos import ServicioDeAvistamientos
from avistamientos.nucleo.servicios_dominio.validador import ValidadorDeAvistamiento
from avistamientos.ui.api_flask import crear_app

DB_PATH = os.environ.get(
    "DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "avistamientos.db")
)


def crear_aplicacion(ruta_db: str = DB_PATH, reloj: Reloj = None):
    """Arma la aplicación completa. Las pruebas la llaman con una base temporal y un reloj fijo."""
    repositorio = RepositorioSqlite(ruta_db)
    repositorio.crear_esquema()
    validador = ValidadorDeAvistamiento(reloj or RelojSistema())
    servicio = ServicioDeAvistamientos(repositorio, validador)
    return crear_app(servicio)


app = crear_aplicacion()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
