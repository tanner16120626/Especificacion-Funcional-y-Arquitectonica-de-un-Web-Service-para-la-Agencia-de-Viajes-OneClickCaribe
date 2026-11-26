"""Dominio de ventas: esquema de la orden de venta y reglas de su generación."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio

MODALIDADES_PAGO = ("total", "parcial")


class OrdenVentaCreate(BaseModel):
    """Solicitud del cliente para confirmar su compra a partir de una cotización aceptada."""

    cotizacionId: Optional[str] = None
    modalidadPago: Optional[str] = None
    fechaLimiteSaldo: Optional[date] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "cotizacionId": "COT-00045",
        "modalidadPago": "parcial",
        "fechaLimiteSaldo": "2026-11-30",
    }})


def _vacio(valor: Optional[str]) -> bool:
    return valor is None or not str(valor).strip()


class Venta:
    """Reglas de negocio de la orden de venta."""

    @staticmethod
    def validar_solicitud(datos: OrdenVentaCreate) -> None:
        """Valida la cotización, la modalidad de pago y la fecha límite si el pago es parcial (RN-33)."""
        if _vacio(datos.cotizacionId):
            raise ErrorNegocio("El identificador de la cotización es obligatorio")
        if _vacio(datos.modalidadPago):
            raise ErrorNegocio("La modalidad de pago es obligatoria")
        if datos.modalidadPago.strip().lower() not in MODALIDADES_PAGO:
            raise ErrorNegocio("La modalidad de pago debe ser total o parcial")
        if datos.modalidadPago.strip().lower() == "parcial" and datos.fechaLimiteSaldo is None:
            raise ErrorNegocio("La fecha límite del saldo es obligatoria")

    @staticmethod
    def validar_cotizacion(cotizacion: dict, ahora: datetime) -> None:
        """RN-31: solo se genera la orden de una cotización aceptada y vigente."""
        if cotizacion["estado"] != "aceptada":
            raise ErrorNegocio("Solo se genera la orden de una cotización aceptada")
        if ahora > datetime.fromisoformat(cotizacion["vigenteHasta"]):
            raise ErrorNegocio("La cotización está vencida y no puede generar una orden de venta")

    @staticmethod
    def validar_fecha_limite(fecha_limite: Optional[date], fecha_inicio_viaje: date) -> None:
        """RN-33: la fecha límite del saldo debe ser anterior a la fecha de inicio del viaje."""
        if fecha_limite is not None and fecha_limite >= fecha_inicio_viaje:
            raise ErrorNegocio("La fecha límite del saldo debe ser anterior a la fecha de inicio del viaje")

    @staticmethod
    def presentar_estado(venta: dict, reserva: Optional[dict], factura: Optional[dict]) -> dict:
        """Estado completo de la compra; totalPagado solo incluye pagos aprobados por la pasarela (RN-45)."""
        return {
            "ventaId": venta["ventaId"],
            "clienteId": venta["clienteId"],
            "valorTotal": venta["valorTotal"],
            "totalPagado": venta["totalAprobado"],
            "saldoPendiente": venta["saldoPendiente"],
            "estado": venta["estado"],
            "reservaConfirmada": reserva is not None and reserva["estado"] == "confirmada",
            "facturaGenerada": factura is not None,
        }

    @staticmethod
    def presentar(venta: dict) -> dict:
        """Datos de la orden que devuelve la API; totalPagado es el total de pagos aprobados."""
        return {
            "ventaId": venta["ventaId"],
            "cotizacionId": venta["cotizacionId"],
            "clienteId": venta["clienteId"],
            "valorTotal": venta["valorTotal"],
            "modalidadPago": venta["modalidadPago"],
            "fechaLimiteSaldo": venta["fechaLimiteSaldo"],
            "totalPagado": venta["totalAprobado"],
            "saldoPendiente": venta["saldoPendiente"],
            "estado": venta["estado"],
            "fechaCreacion": venta["fechaCreacion"],
        }
