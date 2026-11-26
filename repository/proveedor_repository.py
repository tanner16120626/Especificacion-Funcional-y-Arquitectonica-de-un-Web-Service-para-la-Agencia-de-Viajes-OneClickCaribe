"""Repositorio en memoria de proveedores."""
from typing import Optional

from repository.datos_iniciales import PROVEEDORES, copia


class ProveedorRepository:
    """Guarda y consulta proveedores en la base de datos temporal."""

    def __init__(self):
        self._proveedores = copia(PROVEEDORES)

    def buscar_por_nit(self, nit: str) -> Optional[dict]:
        nit = (nit or "").strip()
        return next((p for p in self._proveedores if p["nit"] == nit), None)

    def buscar_por_id(self, proveedor_id: str) -> Optional[dict]:
        return next((p for p in self._proveedores if p["proveedorId"] == proveedor_id), None)

    def cambiar_estado(self, proveedor_id: str, estado: str, motivo: str, fecha_cambio_estado: str) -> dict:
        """Cambia el estado del proveedor. El proveedor nunca se elimina."""
        proveedor = self.buscar_por_id(proveedor_id)
        proveedor["estado"] = estado
        proveedor["motivo"] = motivo
        proveedor["fechaCambioEstado"] = fecha_cambio_estado
        return proveedor

    def siguiente_proveedor_id(self) -> str:
        mayor = max((int(p["proveedorId"].split("-")[1]) for p in self._proveedores), default=0)
        return f"PRV-{mayor + 1:04d}"

    def guardar(self, proveedor: dict) -> dict:
        self._proveedores.append(proveedor)
        return proveedor


proveedor_repository = ProveedorRepository()
