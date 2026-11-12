"""Servicio de dominio: la regla de negocio de un avistamiento.

Vive en el núcleo. Depende del modelo de dominio y de la interfaz `Reloj`
(que también es del núcleo), nunca de Flask ni de SQLite. El reloj entra por
el constructor (inyección de dependencias) para que las pruebas puedan fijar
"hoy" con un stub; la implementación real está en `infraestructura`.
"""
from datetime import datetime

from avistamientos.nucleo.interfaces.reloj import Reloj
from avistamientos.nucleo.modelo_dominio.avistamiento import CAMPOS, ESPECIE_MAX, ESPECIE_MIN


class ValidadorDeAvistamiento:
    """Un avistamiento es válido si cumple todas estas reglas:

    - especie, lugar, fecha y observador son texto no vacío (tras quitar espacios).
    - la especie tiene entre 3 y 50 caracteres (tras quitar espacios).
    - la fecha tiene formato AAAA-MM-DD, es una fecha real y no es posterior a hoy.
    """

    def __init__(self, reloj: Reloj):
        self._reloj = reloj

    def validar(self, datos) -> list:
        """Devuelve la lista de errores. Lista vacía = avistamiento válido."""
        if not isinstance(datos, dict):
            return ["El cuerpo debe ser un objeto JSON"]

        errores = []
        faltan = [
            c for c in CAMPOS
            if not isinstance(datos.get(c), str) or not datos[c].strip()
        ]
        if faltan:
            errores.append("Faltan datos o son inválidos: " + ", ".join(faltan))

        if "especie" not in faltan:
            largo = len(datos["especie"].strip())
            if not ESPECIE_MIN <= largo <= ESPECIE_MAX:
                errores.append(
                    f"especie: debe tener entre {ESPECIE_MIN} y {ESPECIE_MAX} "
                    f"caracteres (tiene {largo})"
                )

        if "fecha" not in faltan:
            error_fecha = self._validar_fecha(datos["fecha"].strip())
            if error_fecha:
                errores.append(error_fecha)

        return errores

    def _validar_fecha(self, texto):
        try:
            if len(texto) != 10:
                raise ValueError
            fecha = datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            return "fecha: debe tener el formato AAAA-MM-DD y ser una fecha real"
        if fecha > self._reloj.hoy():
            return "fecha: no puede ser posterior a hoy"
        return None
