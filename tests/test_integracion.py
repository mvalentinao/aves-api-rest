"""Parte B: pruebas de integración por HTTP.

Ejercitan la aplicación Flask completa (rutas + validador + SQLite real) con el
cliente de pruebas. No hay nada externo que simular: la única dependencia de
fuera es la base de datos, y es un archivo SQLite temporal distinto en cada
prueba (ver fixture `client`), así que las pruebas son independientes entre sí.
Se verifica el cuerpo completo de la respuesta y el efecto sobre el estado
(un GET posterior).
"""
import pytest

VALIDO = {
    "especie": "colibrí",
    "lugar": "Chingaza",
    "fecha": "2026-09-29",
    "observador": "Pablo",
}


def registrar(client, **cambios):
    return client.post("/avistamientos", json={**VALIDO, **cambios})


# ----------------------------------------------------- GET /avistamientos

def test_listar_sin_registros_responde_200_y_lista_vacia(client):
    # Arrange: base vacía (la deja el fixture)

    # Act
    r = client.get("/avistamientos")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == []


def test_listar_con_dos_registros_responde_200_con_ambos_completos_y_en_orden(client):
    # Arrange
    registrar(client)
    registrar(client, especie="águila", lugar="Sumapaz")

    # Act
    r = client.get("/avistamientos")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == [
        {"id": 1, **VALIDO},
        {"id": 2, **VALIDO, "especie": "águila", "lugar": "Sumapaz"},
    ]


# ------------------------------------------------- GET /avistamientos/{id}

def test_ver_un_registro_existente_responde_200_con_el_cuerpo_completo(client):
    # Arrange
    registrar(client)

    # Act
    r = client.get("/avistamientos/1")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == {"id": 1, **VALIDO}


def test_ver_un_id_inexistente_responde_404_con_mensaje(client):
    # Arrange: base vacía

    # Act
    r = client.get("/avistamientos/999")

    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


# ---------------------------------------------------- POST /avistamientos

def test_crear_un_avistamiento_valido_responde_201_y_luego_se_puede_consultar(client):
    # Arrange: base vacía

    # Act
    r = registrar(client)
    consulta = client.get("/avistamientos/1")

    # Assert
    assert r.status_code == 201
    assert r.get_json() == {"id": 1, **VALIDO}
    assert consulta.status_code == 200
    assert consulta.get_json() == r.get_json()


def test_crear_guarda_los_textos_sin_espacios_sobrantes(client):
    # Arrange
    datos = {
        "especie": "  colibrí  ",
        "lugar": " Chingaza ",
        "fecha": " 2026-09-29 ",
        "observador": "  Pablo",
    }

    # Act
    r = client.post("/avistamientos", json=datos)

    # Assert
    assert r.status_code == 201
    assert r.get_json() == {"id": 1, **VALIDO}


def test_crear_ignora_el_id_que_manda_el_cliente_y_asigna_uno_propio(client):
    # Arrange
    datos = {**VALIDO, "id": 500}

    # Act
    r = client.post("/avistamientos", json=datos)

    # Assert
    assert r.status_code == 201
    assert r.get_json() == {"id": 1, **VALIDO}
    assert client.get("/avistamientos/500").status_code == 404


@pytest.mark.parametrize("campo", ["especie", "lugar", "fecha", "observador"])
def test_crear_sin_un_campo_responde_400_nombra_el_campo_y_no_guarda_nada(client, campo):
    # Arrange
    datos = {k: v for k, v in VALIDO.items() if k != campo}

    # Act
    r = client.post("/avistamientos", json=datos)

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {"error": f"Faltan datos o son inválidos: {campo}"}
    assert client.get("/avistamientos").get_json() == []


def test_crear_con_especie_de_2_caracteres_responde_400_y_no_guarda_nada(client):
    # Arrange
    datos = {**VALIDO, "especie": "ab"}

    # Act
    r = client.post("/avistamientos", json=datos)

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {"error": "especie: debe tener entre 3 y 50 caracteres (tiene 2)"}
    assert client.get("/avistamientos").get_json() == []


def test_crear_con_especie_de_50_caracteres_responde_201(client):
    # Arrange
    especie = "a" * 50

    # Act
    r = registrar(client, especie=especie)

    # Assert
    assert r.status_code == 201
    assert r.get_json() == {"id": 1, **VALIDO, "especie": especie}


def test_crear_con_fecha_de_manana_responde_400_y_con_la_de_hoy_responde_201(client):
    # Arrange: el fixture fija "hoy" en 2026-10-21

    # Act
    manana = registrar(client, fecha="2026-10-22")
    hoy = registrar(client, fecha="2026-10-21")

    # Assert
    assert manana.status_code == 400
    assert manana.get_json() == {"error": "fecha: no puede ser posterior a hoy"}
    assert hoy.status_code == 201
    assert [a["fecha"] for a in client.get("/avistamientos").get_json()] == ["2026-10-21"]


def test_crear_con_varios_errores_responde_400_con_todos_los_mensajes(client):
    # Arrange
    datos = {**VALIDO, "especie": "ab", "fecha": "2999-01-01"}

    # Act
    r = client.post("/avistamientos", json=datos)

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {
        "error": "especie: debe tener entre 3 y 50 caracteres (tiene 2); "
                 "fecha: no puede ser posterior a hoy"
    }


def test_crear_sin_cuerpo_json_responde_400(client):
    # Arrange
    cuerpo, tipo = "esto no es json", "text/plain"

    # Act
    r = client.post("/avistamientos", data=cuerpo, content_type=tipo)

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {"error": "El cuerpo debe ser un objeto JSON"}


def test_crear_con_un_json_que_no_es_objeto_responde_400(client):
    # Arrange
    cuerpo = ["a", "b"]

    # Act
    r = client.post("/avistamientos", json=cuerpo)

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {"error": "El cuerpo debe ser un objeto JSON"}


def test_con_el_reloj_real_una_fecha_del_año_2999_se_rechaza_y_una_del_2000_se_acepta(
    client_con_reloj_real,
):
    # Arrange: cableado de producción (RelojSistema), sin stub.
    # Se usan fechas muy lejanas para que la prueba no dependa del día en que se corra.
    client = client_con_reloj_real

    # Act
    futura = registrar(client, fecha="2999-12-31")
    pasada = registrar(client, fecha="2000-01-01")

    # Assert
    assert futura.status_code == 400
    assert pasada.status_code == 201


# ------------------------------------------------- PUT /avistamientos/{id}

def test_actualizar_un_registro_existente_responde_200_y_el_cambio_queda_guardado(client):
    # Arrange
    registrar(client)
    nuevo = {**VALIDO, "lugar": "Jardín Botánico", "fecha": "2026-09-30"}

    # Act
    r = client.put("/avistamientos/1", json=nuevo)
    consulta = client.get("/avistamientos/1")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == {"id": 1, **nuevo}
    assert consulta.get_json() == {"id": 1, **nuevo}


def test_actualizar_un_id_inexistente_responde_404(client):
    # Arrange: base vacía

    # Act
    r = client.put("/avistamientos/999", json=VALIDO)

    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


def test_actualizar_con_datos_invalidos_responde_400_y_no_modifica_el_registro(client):
    # Arrange
    registrar(client)
    invalido = {**VALIDO, "especie": "ab", "lugar": "Otro lugar"}

    # Act
    r = client.put("/avistamientos/1", json=invalido)

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {"error": "especie: debe tener entre 3 y 50 caracteres (tiene 2)"}
    assert client.get("/avistamientos/1").get_json() == {"id": 1, **VALIDO}


def test_actualizar_con_fecha_futura_responde_400_y_no_modifica_el_registro(client):
    # Arrange
    registrar(client)

    # Act
    r = client.put("/avistamientos/1", json={**VALIDO, "fecha": "2026-10-22"})

    # Assert
    assert r.status_code == 400
    assert r.get_json() == {"error": "fecha: no puede ser posterior a hoy"}
    assert client.get("/avistamientos/1").get_json() == {"id": 1, **VALIDO}


def test_actualizar_un_id_inexistente_con_datos_invalidos_responde_404_antes_que_400(client):
    # Arrange: el recurso no existe y además el cuerpo es inválido

    # Act
    r = client.put("/avistamientos/999", json={"lugar": "otro"})

    # Assert
    assert r.status_code == 404


# ---------------------------------------------- DELETE /avistamientos/{id}

def test_eliminar_un_registro_existente_responde_204_sin_cuerpo_y_luego_da_404(client):
    # Arrange
    registrar(client)

    # Act
    r = client.delete("/avistamientos/1")
    consulta = client.get("/avistamientos/1")

    # Assert
    assert r.status_code == 204
    assert r.data == b""
    assert consulta.status_code == 404


def test_eliminar_un_registro_no_afecta_a_los_demas(client):
    # Arrange
    registrar(client)
    registrar(client, especie="águila")

    # Act
    client.delete("/avistamientos/1")

    # Assert
    assert client.get("/avistamientos").get_json() == [{"id": 2, **VALIDO, "especie": "águila"}]


def test_eliminar_un_id_inexistente_responde_404(client):
    # Arrange: base vacía

    # Act
    r = client.delete("/avistamientos/999")

    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


# ------------------------------------------- GET /avistamientos/resumen

def test_resumen_sin_registros_responde_200_y_lista_vacia(client):
    # Arrange: base vacía

    # Act
    r = client.get("/avistamientos/resumen")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == []


def test_resumen_cuenta_por_especie_de_mayor_a_menor(client):
    # Arrange
    for especie in ["águila", "águila", "águila", "colibrí"]:
        registrar(client, especie=especie)

    # Act
    r = client.get("/avistamientos/resumen")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == [
        {"especie": "águila", "cantidad": 3},
        {"especie": "colibrí", "cantidad": 1},
    ]
