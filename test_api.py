import os
import tempfile

# La base de datos de import (app.py llama a init_db al importarse) va a una carpeta temporal.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "import.db")

import pytest

import app as app_module

VALIDO = {
    "especie": "colibrí",
    "lugar": "Chingaza",
    "fecha": "2026-09-29",
    "observador": "Pablo",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Cliente de pruebas con una base de datos vacía y aislada por cada prueba."""
    monkeypatch.setattr(app_module, "DB_PATH", str(tmp_path / "test.db"))
    app_module.init_db()
    return app_module.app.test_client()


def crear(client, **cambios):
    return client.post("/avistamientos", json={**VALIDO, **cambios})


# --- GET /avistamientos ---

def test_listar_vacio(client):
    r = client.get("/avistamientos")
    assert r.status_code == 200
    assert r.get_json() == []


def test_listar_devuelve_los_registrados(client):
    crear(client)
    crear(client, especie="águila")
    r = client.get("/avistamientos")
    assert r.status_code == 200
    assert [a["especie"] for a in r.get_json()] == ["colibrí", "águila"]


# --- GET /avistamientos/{id} ---

def test_ver_existente(client):
    creado = crear(client).get_json()
    r = client.get(f"/avistamientos/{creado['id']}")
    assert r.status_code == 200
    assert r.get_json() == creado


def test_ver_inexistente_404(client):
    r = client.get("/avistamientos/999")
    assert r.status_code == 404
    assert "error" in r.get_json()


# --- POST /avistamientos ---

def test_crear_201_y_asigna_id(client):
    r = crear(client)
    assert r.status_code == 201
    datos = r.get_json()
    assert isinstance(datos["id"], int)
    assert {k: datos[k] for k in VALIDO} == VALIDO


def test_crear_ignora_id_enviado_por_el_cliente(client):
    r = client.post("/avistamientos", json={**VALIDO, "id": 500})
    assert r.status_code == 201
    assert r.get_json()["id"] != 500


@pytest.mark.parametrize("campo", list(VALIDO))
def test_crear_sin_un_campo_400(client, campo):
    datos = {k: v for k, v in VALIDO.items() if k != campo}
    r = client.post("/avistamientos", json=datos)
    assert r.status_code == 400
    assert campo in r.get_json()["error"]


def test_crear_campo_vacio_400(client):
    assert crear(client, lugar="   ").status_code == 400


@pytest.mark.parametrize("fecha", ["29/09/2026", "2026-9-29", "hoy", "2026-09-29T10:00", "2026-99-99", "2026-02-30"])
def test_crear_fecha_con_formato_malo_400(client, fecha):
    assert crear(client, fecha=fecha).status_code == 400


def test_crear_sin_json_400(client):
    r = client.post("/avistamientos", data="no es json", content_type="text/plain")
    assert r.status_code == 400


def test_crear_json_que_no_es_objeto_400(client):
    assert client.post("/avistamientos", json=["a", "b"]).status_code == 400


# --- PUT /avistamientos/{id} ---

def test_actualizar_200(client):
    id_ = crear(client).get_json()["id"]
    r = client.put(f"/avistamientos/{id_}", json={**VALIDO, "lugar": "Jardín Botánico"})
    assert r.status_code == 200
    assert r.get_json()["lugar"] == "Jardín Botánico"
    assert client.get(f"/avistamientos/{id_}").get_json()["lugar"] == "Jardín Botánico"


def test_actualizar_inexistente_404(client):
    assert client.put("/avistamientos/999", json=VALIDO).status_code == 404


def test_actualizar_con_datos_incompletos_400_y_no_modifica(client):
    id_ = crear(client).get_json()["id"]
    r = client.put(f"/avistamientos/{id_}", json={"lugar": "otro"})
    assert r.status_code == 400
    assert client.get(f"/avistamientos/{id_}").get_json()["lugar"] == "Chingaza"


# --- DELETE /avistamientos/{id} ---

def test_eliminar_204_y_ya_no_existe(client):
    id_ = crear(client).get_json()["id"]
    assert client.delete(f"/avistamientos/{id_}").status_code == 204
    assert client.get(f"/avistamientos/{id_}").status_code == 404


def test_eliminar_inexistente_404(client):
    assert client.delete("/avistamientos/999").status_code == 404


# --- GET /avistamientos/resumen (bonus) ---

def test_resumen_vacio(client):
    r = client.get("/avistamientos/resumen")
    assert r.status_code == 200
    assert r.get_json() == []


def test_resumen_cuenta_por_especie(client):
    crear(client, especie="águila")
    crear(client, especie="águila")
    crear(client, especie="águila")
    crear(client, especie="colibrí")
    r = client.get("/avistamientos/resumen")
    assert r.status_code == 200
    # Ordenado de mayor a menor cantidad
    assert r.get_json() == [
        {"especie": "águila", "cantidad": 3},
        {"especie": "colibrí", "cantidad": 1},
    ]
