"""Borde (infraestructura): el reloj real, que implementa la interfaz del núcleo."""
from datetime import date

from avistamientos.nucleo.interfaces.reloj import Reloj


class RelojSistema(Reloj):
    """Implementación real, usada en producción."""

    def hoy(self) -> date:
        return date.today()
