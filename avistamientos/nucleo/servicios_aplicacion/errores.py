"""Errores que el núcleo comunica hacia afuera. La capa de UI decide cómo mostrarlos."""


class DatosInvalidos(Exception):
    """Los datos no cumplen la regla de negocio. `errores` es la lista de mensajes."""

    def __init__(self, errores):
        super().__init__("; ".join(errores))
        self.errores = list(errores)


class AvistamientoNoEncontrado(Exception):
    """No existe un avistamiento con el id pedido."""
