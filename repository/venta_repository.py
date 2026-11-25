"""Repositorio en memoria de órdenes de venta."""
from typing import Optional

from repository.datos_iniciales import VENTAS, copia


class VentaRepository:
    """Guarda y consulta órdenes de venta en la base de datos temporal."""

    def __init__(self):
        self._ventas = copia(VENTAS)

    def buscar_por_id(self, venta_id: str) -> Optional[dict]:
        return next((v for v in self._ventas if v["ventaId"] == venta_id), None)

    def buscar_por_cotizacion(self, cotizacion_id: str) -> Optional[dict]:
        return next((v for v in self._ventas if v["cotizacionId"] == cotizacion_id), None)

    def siguiente_venta_id(self) -> str:
        mayor = max((int(v["ventaId"].split("-")[1]) for v in self._ventas), default=0)
        return f"VEN-{mayor + 1:05d}"

    def guardar(self, venta: dict) -> dict:
        self._ventas.append(venta)
        return venta

    def actualizar_pago(self, venta_id: str, total_aprobado: int, saldo_pendiente: int, estado: str) -> dict:
        venta = self.buscar_por_id(venta_id)
        venta.update({"totalAprobado": total_aprobado, "saldoPendiente": saldo_pendiente, "estado": estado})
        return venta


venta_repository = VentaRepository()
