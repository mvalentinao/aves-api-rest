"""Interfaz del reloj. La define el núcleo; la implementa el borde."""
from abc import ABC, abstractmethod
from datetime import date


class Reloj(ABC):
    """Lo único que la regla de negocio necesita saber es qué día es hoy."""

    @abstractmethod
    def hoy(self) -> date:
        ...
