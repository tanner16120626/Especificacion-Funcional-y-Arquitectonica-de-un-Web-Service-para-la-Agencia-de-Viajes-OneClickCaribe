"""Repositorio en memoria de pagos."""
from typing import List, Optional

from repository.datos_iniciales import PAGOS, copia


class PagoRepository:
    """Guarda y consulta los pagos en la base de datos temporal."""

    def __init__(self):
        self._pagos = copia(PAGOS)

    def buscar_por_clave(self, clave_idempotencia: str) -> Optional[dict]:
        return next((p for p in self._pagos if p["claveIdempotencia"] == clave_idempotencia), None)

    def buscar_por_transaccion(self, transaccion_id: str) -> Optional[dict]:
        return next((p for p in self._pagos if p["transaccionId"] == transaccion_id), None)

    def actualizar_estado(self, pago_id: str, estado: str) -> dict:
        pago = next(p for p in self._pagos if p["pagoId"] == pago_id)
        pago["estado"] = estado
        return pago

    def listar_por_venta(self, venta_id: str) -> List[dict]:
        return [p for p in self._pagos if p["ventaId"] == venta_id]

    def total_pse_pendiente(self, venta_id: str) -> int:
        """Suma de los pagos PSE de la orden que esperan la confirmación del banco."""
        return sum(p["monto"] for p in self._pagos
                   if p["ventaId"] == venta_id and p["medioPago"] == "pse" and p["estado"] == "pendiente")

    def siguiente_pago_id(self) -> str:
        mayor = max((int(p["pagoId"].split("-")[1]) for p in self._pagos), default=0)
        return f"PAG-{mayor + 1:05d}"

    def siguiente_transaccion_id(self) -> str:
        mayor = max((int(p["transaccionId"].split("-")[1]) for p in self._pagos), default=0)
        return f"TRX-{mayor + 1}"

    def guardar(self, pago: dict) -> dict:
        self._pagos.append(pago)
        return pago


pago_repository = PagoRepository()
