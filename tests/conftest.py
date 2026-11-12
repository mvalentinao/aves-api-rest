import os
import tempfile
from datetime import date

# app.py arma la aplicación (y crea la base) al importarse; esa primera base va a una carpeta
# temporal para no crear avistamientos.db dentro del proyecto.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "import.db")

import pytest  # noqa: E402

from app import crear_aplicacion  # noqa: E402
from tests.relojes import RelojFijo  # noqa: E402

HOY = date(2026, 10, 21)


@pytest.fixture
def client(tmp_path):
    """Cliente HTTP con (1) una base SQLite nueva y vacía por cada prueba y
    (2) un reloj fijo en 2026-10-21 (stub), para que no dependa del día real.
    La aplicación se arma con la raíz de composición, igual que en producción."""
    return crear_aplicacion(str(tmp_path / "test.db"), RelojFijo(HOY)).test_client()


@pytest.fixture
def client_con_reloj_real(tmp_path):
    """Igual que `client`, pero con el cableado real de producción (RelojSistema)."""
    return crear_aplicacion(str(tmp_path / "test.db")).test_client()
