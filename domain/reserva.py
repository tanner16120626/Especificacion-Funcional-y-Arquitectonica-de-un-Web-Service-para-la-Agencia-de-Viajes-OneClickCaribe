"""Dominio de reservas: reglas de la consulta de la reserva confirmada."""
from typing import Optional

from domain.errores import ConflictoError


class Reserva:
    """Reglas de negocio de la reserva de la orden de venta."""

    @staticmethod
    def validar_confirmada(venta: dict, reserva: Optional[dict]) -> None:
        """RN-61: la reserva solo existe para órdenes pagadas en su totalidad (RN-45)."""
        if venta["estado"] != "pagada" or reserva is None or reserva["estado"] != "confirmada":
            raise ConflictoError("La reserva se confirma cuando la orden esté pagada en su totalidad")

    @staticmethod
    def presentar(reserva: dict) -> dict:
        """Reserva con un localizador por servicio (RN-62)."""
        return {
            "reservaId": reserva["reservaId"],
            "ventaId": reserva["ventaId"],
            "estado": reserva["estado"],
            "segmentos": [{"tipoServicio": s["tipoServicio"], "proveedor": s["proveedor"],
                           "localizador": s["localizador"]} for s in reserva["segmentos"]],
            "fechaConfirmacion": reserva["fechaConfirmacion"],
        }
