"""Prueba de arquitectura: la regla de la cebolla, comprobada sobre el código.

Regla (Palermo, 2008): el acoplamiento va hacia el centro. Una capa puede
depender de las capas más internas, nunca de las más externas. Esta prueba lee
los `import` de cada archivo de `avistamientos/` (sin ejecutarlos) y falla si
alguna capa importa algo que no le corresponde.
"""
import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent / "avistamientos"
PAQUETE = "avistamientos"

# Capa -> capas del proyecto que puede importar (además de ella misma).
PERMITIDO = {
    "nucleo.modelo_dominio": set(),
    "nucleo.interfaces": {"nucleo.modelo_dominio"},
    "nucleo.servicios_dominio": {"nucleo.modelo_dominio", "nucleo.interfaces"},
    "nucleo.servicios_aplicacion": {
        "nucleo.modelo_dominio", "nucleo.interfaces", "nucleo.servicios_dominio",
    },
    "infraestructura": {"nucleo.modelo_dominio", "nucleo.interfaces"},
    "ui": {
        "nucleo.modelo_dominio", "nucleo.interfaces",
        "nucleo.servicios_dominio", "nucleo.servicios_aplicacion",
    },
}

# Librerías de las que el núcleo no puede depender.
TECNOLOGIAS_DEL_BORDE = {"flask", "sqlite3", "werkzeug"}
CAPAS_DEL_NUCLEO = [c for c in PERMITIDO if c.startswith("nucleo.")]


def capa_de(modulo: str):
    """'avistamientos.nucleo.interfaces.reloj' -> 'nucleo.interfaces'."""
    partes = modulo.split(".")
    if partes[0] != PAQUETE:
        return None
    for capa in PERMITIDO:
        if ".".join(partes[1:]).startswith(capa):
            return capa
    return None


def modulos_importados(codigo: str):
    for nodo in ast.walk(ast.parse(codigo)):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                yield alias.name
        elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
            yield nodo.module


def violaciones(capa: str, codigo: str):
    malas = []
    for modulo in modulos_importados(codigo):
        raiz = modulo.split(".")[0]
        if capa in CAPAS_DEL_NUCLEO and raiz in TECNOLOGIAS_DEL_BORDE:
            malas.append(f"{modulo} (el núcleo no puede usar {raiz})")
        destino = capa_de(modulo)
        if modulo.split(".")[0] == PAQUETE and destino is None and modulo != PAQUETE:
            malas.append(f"{modulo} (no pertenece a ninguna capa conocida)")
        elif destino is not None and destino != capa and destino not in PERMITIDO[capa]:
            malas.append(f"{modulo} (la capa {capa} no puede depender de {destino})")
    return malas


def archivos_por_capa():
    for capa in PERMITIDO:
        for archivo in sorted((RAIZ / Path(*capa.split("."))).glob("*.py")):
            if archivo.name != "__init__.py":
                yield pytest.param(capa, archivo, id=f"{capa}/{archivo.name}")


@pytest.mark.parametrize("capa, archivo", list(archivos_por_capa()))
def test_cada_archivo_solo_depende_de_capas_mas_internas(capa, archivo):
    assert violaciones(capa, archivo.read_text(encoding="utf-8")) == []


def test_todos_los_archivos_del_paquete_pertenecen_a_una_capa():
    en_capas = {a for _, a in (p.values for p in archivos_por_capa())}
    todos = {a for a in RAIZ.rglob("*.py") if a.name != "__init__.py"}
    assert todos - en_capas == set()


# --- la prueba de arquitectura debe detectar las violaciones reales ---

def test_detecta_que_el_nucleo_importe_sqlite():
    assert violaciones("nucleo.servicios_aplicacion", "import sqlite3\n")


def test_detecta_que_el_dominio_importe_una_capa_externa():
    codigo = "from avistamientos.infraestructura.repositorio_sqlite import RepositorioSqlite\n"
    assert violaciones("nucleo.servicios_dominio", codigo)


def test_detecta_que_la_ui_dependa_de_la_infraestructura():
    codigo = "from avistamientos.infraestructura.reloj_sistema import RelojSistema\n"
    assert violaciones("ui", codigo)
