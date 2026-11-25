"""Repositorio en memoria de las liquidaciones a proveedores."""
from typing import List

from repository.datos_iniciales import LIQUIDACIONES, copia


class LiquidacionRepository:
    """Guarda las liquidaciones a proveedores en la base de datos temporal."""

    def __init__(self):
        self._liquidaciones = copia(LIQUIDACIONES)

    def guardar_todas(self, liquidaciones: List[dict]) -> List[dict]:
        self._liquidaciones.extend(liquidaciones)
        return liquidaciones


liquidacion_repository = LiquidacionRepository()
