"""Modelo de dominio: el centro de la cebolla.

Aquí vive lo que el negocio entiende por "avistamiento". Este módulo no
importa nada del proyecto ni de Flask ni de SQLite: depende solo de sí mismo.
"""
from dataclasses import dataclass
from typing import Optional

# Constantes de la regla de negocio (las usa el validador).
CAMPOS = ("especie", "lugar", "fecha", "observador")
ESPECIE_MIN = 3
ESPECIE_MAX = 50


@dataclass(frozen=True)
class Avistamiento:
    """Un ave vista en un lugar, un día y por un observador.

    `id` es None mientras el avistamiento no se ha guardado; lo asigna el
    repositorio al guardarlo. `fecha` se maneja como texto AAAA-MM-DD, igual
    que en la API.
    """

    especie: str
    lugar: str
    fecha: str
    observador: str
    id: Optional[int] = None

    @classmethod
    def desde_datos(cls, datos: dict, id: Optional[int] = None) -> "Avistamiento":
        """Crea un avistamiento desde datos ya validados, sin espacios en los extremos.
        Ignora cualquier `id` que venga en los datos: el id lo asigna el sistema."""
        return cls(id=id, **{c: datos[c].strip() for c in CAMPOS})


@dataclass(frozen=True)
class ResumenDeEspecie:
    """Cuántos avistamientos hay de una especie."""

    especie: str
    cantidad: int
