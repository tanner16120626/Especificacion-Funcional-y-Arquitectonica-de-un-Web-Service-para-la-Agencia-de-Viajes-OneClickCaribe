"""Dominio de facturación: reglas de la consulta de la factura de la orden."""
from typing import Optional

from domain.errores import ConflictoError


class Factura:
    """Reglas de negocio de la factura de la orden de venta."""

    @staticmethod
    def validar_emitida(venta: dict, factura: Optional[dict]) -> None:
        """RN-53: la factura solo existe para órdenes pagadas en su totalidad."""
        if venta["estado"] != "pagada" or factura is None:
            raise ConflictoError("La factura se genera cuando la orden esté pagada en su totalidad")

    @staticmethod
    def presentar(factura: dict) -> dict:
        """Factura a nombre del cliente titular (RN-57), con el CUFE simulado (RN-51)."""
        return {
            "facturaId": factura["facturaId"],
            "numeroFactura": factura["numeroFactura"],
            "cufe": factura["cufe"],
            "ventaId": factura["ventaId"],
            "documentoCliente": factura["documentoCliente"],
            "nombreCliente": factura["nombreCliente"],
            "valorTotal": factura["valorTotal"],
            "fechaEmision": factura["fechaEmision"],
            "estado": factura["estado"],
        }
