"""Repositorio en memoria de reservas."""
from typing import Optional

from repository.datos_iniciales import RESERVAS, copia


class ReservaRepository:
    """Consulta las reservas en la base de datos temporal."""

    def __init__(self):
        self._reservas = copia(RESERVAS)

    def buscar_por_venta(self, venta_id: str) -> Optional[dict]:
        return next((r for r in self._reservas if r["ventaId"] == venta_id), None)


reserva_repository = ReservaRepository()
