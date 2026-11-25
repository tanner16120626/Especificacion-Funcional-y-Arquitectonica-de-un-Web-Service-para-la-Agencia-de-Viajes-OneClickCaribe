"""Repositorio en memoria de reservas."""
from typing import Optional

from repository.datos_iniciales import RESERVAS, copia


class ReservaRepository:
    """Guarda y consulta las reservas en la base de datos temporal."""

    def __init__(self):
        self._reservas = copia(RESERVAS)

    def buscar_por_venta(self, venta_id: str) -> Optional[dict]:
        return next((r for r in self._reservas if r["ventaId"] == venta_id), None)

    def siguiente_reserva_id(self) -> str:
        mayor = max((int(x["reservaId"].split("-")[1]) for x in self._reservas), default=0)
        return f"RES-{mayor + 1:05d}"

    def guardar(self, reserva: dict) -> dict:
        self._reservas.append(reserva)
        return reserva


reserva_repository = ReservaRepository()
