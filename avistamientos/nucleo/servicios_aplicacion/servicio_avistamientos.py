"""Servicio de aplicación: los casos de uso de la API.

Orquesta el modelo de dominio, el validador (servicio de dominio) y el
repositorio (por su interfaz). No sabe nada de HTTP, JSON, Flask ni SQLite:
recibe datos simples, devuelve objetos del dominio y lanza errores del núcleo.
"""
from typing import List

from avistamientos.nucleo.interfaces.repositorio_avistamientos import RepositorioDeAvistamientos
from avistamientos.nucleo.modelo_dominio.avistamiento import Avistamiento, ResumenDeEspecie
from avistamientos.nucleo.servicios_aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.nucleo.servicios_dominio.validador import ValidadorDeAvistamiento


class ServicioDeAvistamientos:
    def __init__(self, repositorio: RepositorioDeAvistamientos, validador: ValidadorDeAvistamiento):
        self._repositorio = repositorio
        self._validador = validador

    def listar(self) -> List[Avistamiento]:
        return self._repositorio.listar()

    def ver(self, id: int) -> Avistamiento:
        avistamiento = self._repositorio.obtener(id)
        if avistamiento is None:
            raise AvistamientoNoEncontrado()
        return avistamiento

    def registrar(self, datos) -> Avistamiento:
        self._exigir_validos(datos)
        return self._repositorio.agregar(Avistamiento.desde_datos(datos))

    def actualizar(self, id: int, datos) -> Avistamiento:
        # Primero se revisa que exista (404) y después los datos (400): es el
        # mismo orden que tenía la API antes del refactor.
        self.ver(id)
        self._exigir_validos(datos)
        actualizado = self._repositorio.actualizar(id, Avistamiento.desde_datos(datos))
        if actualizado is None:  # lo borraron entre la revisión y la actualización
            raise AvistamientoNoEncontrado()
        return actualizado

    def eliminar(self, id: int) -> None:
        if not self._repositorio.eliminar(id):
            raise AvistamientoNoEncontrado()

    def resumen(self) -> List[ResumenDeEspecie]:
        return self._repositorio.resumen_por_especie()

    def _exigir_validos(self, datos) -> None:
        errores = self._validador.validar(datos)
        if errores:
            raise DatosInvalidos(errores)
