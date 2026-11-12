"""Pruebas de las dos piezas nuevas del refactor.

- Servicio de aplicación: gracias a la arquitectura de cebolla se prueba sin Flask
  ni SQLite, con un repositorio en memoria que implementa la interfaz del núcleo.
- Repositorio SQLite: se prueba directo, con un archivo temporal.
"""
from datetime import date

import pytest

from avistamientos.infraestructura.repositorio_sqlite import RepositorioSqlite
from avistamientos.nucleo.interfaces.repositorio_avistamientos import RepositorioDeAvistamientos
from avistamientos.nucleo.modelo_dominio.avistamiento import Avistamiento
from avistamientos.nucleo.servicios_aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.nucleo.servicios_aplicacion.servicio_avistamientos import ServicioDeAvistamientos
from avistamientos.nucleo.servicios_dominio.validador import ValidadorDeAvistamiento
from tests.relojes import RelojFijo

VALIDO = {"especie": "colibrí", "lugar": "Chingaza", "fecha": "2026-09-29", "observador": "Pablo"}


class RepositorioEnMemoria(RepositorioDeAvistamientos):
    """Fake: guarda en un diccionario. `perder_al_actualizar` simula que otro
    proceso borra el registro entre la revisión y la actualización."""

    def __init__(self, perder_al_actualizar=False):
        self.datos, self.siguiente = {}, 1
        self.perder_al_actualizar = perder_al_actualizar

    def listar(self):
        return list(self.datos.values())

    def obtener(self, id):
        return self.datos.get(id)

    def agregar(self, a):
        guardado = Avistamiento(a.especie, a.lugar, a.fecha, a.observador, id=self.siguiente)
        self.datos[self.siguiente] = guardado
        self.siguiente += 1
        return guardado

    def actualizar(self, id, a):
        if self.perder_al_actualizar or id not in self.datos:
            return None
        self.datos[id] = Avistamiento(a.especie, a.lugar, a.fecha, a.observador, id=id)
        return self.datos[id]

    def eliminar(self, id):
        return self.datos.pop(id, None) is not None

    def resumen_por_especie(self):
        return []


def servicio(repositorio=None):
    validador = ValidadorDeAvistamiento(RelojFijo(date(2026, 10, 21)))
    return ServicioDeAvistamientos(repositorio or RepositorioEnMemoria(), validador)


def test_registrar_guarda_sin_espacios_y_asigna_id_ignorando_el_del_cliente():
    s = servicio()
    a = s.registrar({**VALIDO, "especie": "  colibrí  ", "id": 500})
    assert a == Avistamiento("colibrí", "Chingaza", "2026-09-29", "Pablo", id=1)


def test_registrar_datos_invalidos_lanza_DatosInvalidos_y_no_guarda():
    repo = RepositorioEnMemoria()
    with pytest.raises(DatosInvalidos) as e:
        servicio(repo).registrar({**VALIDO, "especie": "ab"})
    assert e.value.errores == ["especie: debe tener entre 3 y 50 caracteres (tiene 2)"]
    assert repo.listar() == []


def test_actualizar_inexistente_responde_no_encontrado_aunque_los_datos_sean_invalidos():
    with pytest.raises(AvistamientoNoEncontrado):
        servicio().actualizar(7, {"lugar": "otro"})


def test_actualizar_si_el_registro_desaparece_a_mitad_de_camino_lanza_no_encontrado():
    repo = RepositorioEnMemoria(perder_al_actualizar=True)
    s = servicio(repo)
    s.registrar(VALIDO)
    with pytest.raises(AvistamientoNoEncontrado):
        s.actualizar(1, VALIDO)


def test_eliminar_inexistente_lanza_no_encontrado():
    with pytest.raises(AvistamientoNoEncontrado):
        servicio().eliminar(1)


@pytest.fixture
def repo_sqlite(tmp_path):
    repo = RepositorioSqlite(str(tmp_path / "repo.db"))
    repo.crear_esquema()
    return repo


def test_repositorio_actualizar_inexistente_devuelve_None(repo_sqlite):
    assert repo_sqlite.actualizar(1, Avistamiento("colibrí", "x", "2026-09-29", "Pablo")) is None


def test_repositorio_vaciar_borra_todo_y_reinicia_los_ids(repo_sqlite):
    nuevo = Avistamiento("colibrí", "Chingaza", "2026-09-29", "Pablo")
    repo_sqlite.agregar(nuevo)
    repo_sqlite.agregar(nuevo)
    repo_sqlite.vaciar()
    assert repo_sqlite.listar() == []
    assert repo_sqlite.agregar(nuevo).id == 1
