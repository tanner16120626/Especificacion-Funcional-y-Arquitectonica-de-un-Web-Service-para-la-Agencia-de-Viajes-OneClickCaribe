"""Errores de negocio del dominio. El router los convierte en respuestas HTTP."""
from typing import Any


class ErrorNegocio(ValueError):
    """Una regla de negocio no se cumple. Se responde con código 400."""

    status_code = 400

    def __init__(self, mensaje: str, data: Any = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.data = data


class ConflictoError(ErrorNegocio):
    """El registro ya existe o el estado no permite la operación. Se responde con código 409."""

    status_code = 409


class NoEncontradoError(ErrorNegocio):
    """El recurso solicitado no existe. Se responde con código 404."""

    status_code = 404
