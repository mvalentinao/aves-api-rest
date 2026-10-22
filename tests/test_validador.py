"""Parte A: pruebas unitarias de la regla de negocio (ValidadorDeAvistamiento).

Técnicas: partición de equivalencia + análisis de valores límite sobre
`especie` (3 a 50 caracteres) y `fecha` (no posterior a hoy).
Doble: RelojFijo (stub) para que "hoy" sea siempre el mismo día.
Cada prueba sigue AAA (Arrange / Act / Assert).
"""
from datetime import date, timedelta

import pytest

from tests.relojes import RelojFijo
from validador import ValidadorDeAvistamiento

HOY = date(2026, 10, 21)

VALIDO = {
    "especie": "colibrí",
    "lugar": "Chingaza",
    "fecha": "2026-09-29",
    "observador": "Pablo",
}


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo(HOY))


def avistamiento(**cambios):
    return {**VALIDO, **cambios}


def texto_de(longitud):
    return "a" * longitud


# ---------------------------------------------------------------- caso base

def test_avistamiento_completo_y_correcto_no_devuelve_errores(validador):
    # Arrange
    datos = avistamiento()

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


# ------------------------------------------- especie: valores límite (3..50)

def test_especie_de_2_caracteres_es_rechazada_por_estar_bajo_el_minimo(validador):
    # Arrange
    datos = avistamiento(especie=texto_de(2))

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["especie: debe tener entre 3 y 50 caracteres (tiene 2)"]


def test_especie_de_3_caracteres_es_aceptada_en_el_limite_inferior(validador):
    # Arrange
    datos = avistamiento(especie=texto_de(3))

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_especie_de_50_caracteres_es_aceptada_en_el_limite_superior(validador):
    # Arrange
    datos = avistamiento(especie=texto_de(50))

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_especie_de_51_caracteres_es_rechazada_por_superar_el_maximo(validador):
    # Arrange
    datos = avistamiento(especie=texto_de(51))

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["especie: debe tener entre 3 y 50 caracteres (tiene 51)"]


@pytest.mark.parametrize("longitud", [4, 49])
def test_especie_justo_dentro_del_rango_es_aceptada(validador, longitud):
    # Arrange
    datos = avistamiento(especie=texto_de(longitud))

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


# ----------------------------------------- especie: particiones inválidas

def test_especie_vacia_es_rechazada_como_dato_faltante(validador):
    # Arrange
    datos = avistamiento(especie="")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["Faltan datos o son inválidos: especie"]


def test_especie_de_solo_espacios_es_rechazada_como_dato_faltante(validador):
    # Arrange
    datos = avistamiento(especie="     ")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["Faltan datos o son inválidos: especie"]


def test_especie_que_no_es_texto_es_rechazada(validador):
    # Arrange
    datos = avistamiento(especie=12345)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["Faltan datos o son inválidos: especie"]


def test_espacios_alrededor_de_la_especie_no_cuentan_para_el_largo(validador):
    # Arrange: 6 caracteres en bruto, pero solo 2 útiles ("ab")
    datos = avistamiento(especie="  ab  ")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["especie: debe tener entre 3 y 50 caracteres (tiene 2)"]


# ------------------------------------ fecha: valores límite respecto a "hoy"

def test_fecha_de_hoy_es_aceptada_en_el_limite(validador):
    # Arrange
    datos = avistamiento(fecha=HOY.isoformat())

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_fecha_de_ayer_es_aceptada_justo_antes_del_limite(validador):
    # Arrange
    datos = avistamiento(fecha=(HOY - timedelta(days=1)).isoformat())

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_fecha_de_manana_es_rechazada_por_ser_posterior_a_hoy(validador):
    # Arrange
    datos = avistamiento(fecha=(HOY + timedelta(days=1)).isoformat())

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["fecha: no puede ser posterior a hoy"]


def test_fecha_en_un_año_lejano_del_futuro_es_rechazada(validador):
    # Arrange
    datos = avistamiento(fecha="2999-12-31")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["fecha: no puede ser posterior a hoy"]


def test_el_resultado_depende_del_reloj_inyectado_y_no_del_dia_real():
    # Arrange: la misma fecha, dos relojes distintos (stub)
    datos = avistamiento(fecha="2026-10-21")
    reloj_el_mismo_dia = ValidadorDeAvistamiento(RelojFijo(date(2026, 10, 21)))
    reloj_un_dia_antes = ValidadorDeAvistamiento(RelojFijo(date(2026, 10, 20)))

    # Act
    errores_el_mismo_dia = reloj_el_mismo_dia.validar(datos)
    errores_un_dia_antes = reloj_un_dia_antes.validar(datos)

    # Assert
    assert errores_el_mismo_dia == []
    assert errores_un_dia_antes == ["fecha: no puede ser posterior a hoy"]


# ---------------------------------- fecha: particiones de formato inválido

@pytest.mark.parametrize(
    "fecha",
    [
        "29/09/2026",          # separador y orden equivocados
        "2026-9-29",           # sin cero a la izquierda (9 caracteres)
        "20260929",            # sin separadores
        "hoy",                 # no es una fecha
        "2026-09-29T10:00",    # trae hora
    ],
)
def test_fecha_con_formato_distinto_de_aaaa_mm_dd_es_rechazada(validador, fecha):
    # Arrange
    datos = avistamiento(fecha=fecha)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["fecha: debe tener el formato AAAA-MM-DD y ser una fecha real"]


@pytest.mark.parametrize("fecha", ["2026-02-30", "2026-13-01", "2025-02-29"])
def test_fecha_con_formato_correcto_pero_inexistente_es_rechazada(validador, fecha):
    # Arrange
    datos = avistamiento(fecha=fecha)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["fecha: debe tener el formato AAAA-MM-DD y ser una fecha real"]


def test_29_de_febrero_de_un_año_bisiesto_es_aceptado(validador):
    # Arrange
    datos = avistamiento(fecha="2024-02-29")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


# --------------------------------- otros campos y forma del cuerpo

@pytest.mark.parametrize("campo", ["especie", "lugar", "fecha", "observador"])
def test_campo_ausente_es_rechazado_y_el_mensaje_lo_nombra(validador, campo):
    # Arrange
    datos = {k: v for k, v in VALIDO.items() if k != campo}

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == [f"Faltan datos o son inválidos: {campo}"]


def test_lugar_y_observador_vacios_se_reportan_juntos(validador):
    # Arrange
    datos = avistamiento(lugar="  ", observador="")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["Faltan datos o son inválidos: lugar, observador"]


@pytest.mark.parametrize("cuerpo", [None, ["a", "b"], "texto", 42])
def test_cuerpo_que_no_es_un_objeto_json_es_rechazado(validador, cuerpo):
    # Arrange: el parámetro `cuerpo` ya es el dato de entrada

    # Act
    errores = validador.validar(cuerpo)

    # Assert
    assert errores == ["El cuerpo debe ser un objeto JSON"]


def test_varios_errores_a_la_vez_se_devuelven_todos(validador):
    # Arrange
    datos = avistamiento(especie="ab", fecha="2999-01-01", lugar="")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == [
        "Faltan datos o son inválidos: lugar",
        "especie: debe tener entre 3 y 50 caracteres (tiene 2)",
        "fecha: no puede ser posterior a hoy",
    ]
