import os
import tempfile
from datetime import date

# app.py llama a init_db() al importarse; esa primera base va a una carpeta
# temporal para no crear avistamientos.db dentro del proyecto.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "import.db")

import pytest  # noqa: E402

import app as app_module  # noqa: E402
from tests.relojes import RelojFijo  # noqa: E402
from validador import ValidadorDeAvistamiento  # noqa: E402

HOY = date(2026, 10, 21)


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Cliente HTTP con (1) una base SQLite nueva y vacía por cada prueba y
    (2) un reloj fijo en 2026-10-21 (stub), para que no dependa del día real."""
    monkeypatch.setattr(app_module, "DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setattr(app_module, "validador", ValidadorDeAvistamiento(RelojFijo(HOY)))
    app_module.init_db()
    return app_module.app.test_client()


@pytest.fixture
def client_con_reloj_real(tmp_path, monkeypatch):
    """Igual que `client`, pero deja el cableado real de producción (RelojSistema)."""
    monkeypatch.setattr(app_module, "DB_PATH", str(tmp_path / "test.db"))
    app_module.init_db()
    return app_module.app.test_client()
