"""Repositorio en memoria de facturas."""
from typing import Optional

from repository.datos_iniciales import FACTURAS, copia


class FacturaRepository:
    """Guarda y consulta las facturas en la base de datos temporal."""

    def __init__(self):
        self._facturas = copia(FACTURAS)

    def buscar_por_venta(self, venta_id: str) -> Optional[dict]:
        return next((f for f in self._facturas if f["ventaId"] == venta_id), None)

    def siguiente_factura_id(self) -> str:
        mayor = max((int(x["facturaId"].split("-")[1]) for x in self._facturas), default=0)
        return f"FAC-{mayor + 1:05d}"

    def guardar(self, factura: dict) -> dict:
        self._facturas.append(factura)
        return factura


factura_repository = FacturaRepository()
