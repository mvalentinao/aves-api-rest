"""Interfaz del repositorio: primer anillo alrededor del modelo de dominio.

Define cómo se guardan y se recuperan los avistamientos, sin decir con qué
tecnología. La implementación (SQLite) vive en el borde, en `infraestructura`.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from avistamientos.nucleo.modelo_dominio.avistamiento import Avistamiento, ResumenDeEspecie


class RepositorioDeAvistamientos(ABC):
    @abstractmethod
    def listar(self) -> List[Avistamiento]:
        """Todos los avistamientos, ordenados por id."""

    @abstractmethod
    def obtener(self, id: int) -> Optional[Avistamiento]:
        """El avistamiento con ese id, o None si no existe."""

    @abstractmethod
    def agregar(self, avistamiento: Avistamiento) -> Avistamiento:
        """Guarda un avistamiento nuevo y lo devuelve con el id asignado."""

    @abstractmethod
    def actualizar(self, id: int, avistamiento: Avistamiento) -> Optional[Avistamiento]:
        """Reemplaza los datos del avistamiento `id`. Devuelve el resultado, o None si no existe."""

    @abstractmethod
    def eliminar(self, id: int) -> bool:
        """Borra el avistamiento. Devuelve False si no existía."""

    @abstractmethod
    def resumen_por_especie(self) -> List[ResumenDeEspecie]:
        """Cantidad por especie, de mayor a menor cantidad y, en empate, por nombre de especie."""
