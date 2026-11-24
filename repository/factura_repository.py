"""Repositorio en memoria de facturas."""
from typing import Optional

from repository.datos_iniciales import FACTURAS, copia


class FacturaRepository:
    """Consulta las facturas en la base de datos temporal."""

    def __init__(self):
        self._facturas = copia(FACTURAS)

    def buscar_por_venta(self, venta_id: str) -> Optional[dict]:
        return next((f for f in self._facturas if f["ventaId"] == venta_id), None)


factura_repository = FacturaRepository()
