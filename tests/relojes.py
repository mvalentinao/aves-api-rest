"""Dobles de prueba para el reloj."""
from datetime import date

from validador import Reloj


class RelojFijo(Reloj):
    """STUB: siempre responde el mismo día, para que la regla "no posterior a hoy"
    dé el mismo resultado hoy, mañana o dentro de un año."""

    def __init__(self, hoy: date):
        self._hoy = hoy

    def hoy(self) -> date:
        return self._hoy
