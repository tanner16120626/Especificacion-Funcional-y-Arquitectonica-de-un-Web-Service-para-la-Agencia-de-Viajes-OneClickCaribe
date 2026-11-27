"""Dominio de pagos: esquema del pago en línea y reglas de su procesamiento."""
import hmac
from datetime import datetime
from hashlib import sha256
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict

from domain.cotizacion import Cotizacion
from domain.errores import ConflictoError, ErrorNegocio, FirmaInvalidaError

MEDIOS_PAGO = ("pse", "tarjeta_credito", "tarjeta_debito")
PREFIJO_TOKEN_TARJETA = "tok_"
PREFIJO_BANCO_PSE = "banco_"
URL_PAGO_PSE = "https://pasarela.simulada/pse/"
ESTADOS_NOTIFICACION = ("aprobado", "rechazado")


class PagoCreate(BaseModel):
    """Solicitud del cliente para pagar su orden de venta, total o por abonos."""

    ventaId: Optional[str] = None
    monto: Optional[int] = None
    medioPago: Optional[str] = None
    datosPago: Optional[str] = None
    claveIdempotencia: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "ventaId": "VEN-00012",
        "monto": 5000000,
        "medioPago": "tarjeta_credito",
        "datosPago": "tok_aprobado",
        "claveIdempotencia": "pago-ven-00012-abono-1",
    }})


class NotificacionPagoCreate(BaseModel):
    """Notificación (webhook) que envía la pasarela cuando el banco resuelve una transacción PSE."""

    transaccionId: Optional[str] = None
    estado: Optional[str] = None
    monto: Optional[int] = None
    firma: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "transaccionId": "TRX-5580003",
        "estado": "aprobado",
        "monto": 3081600,
        "firma": "3668aafc2d5651e7c08112dbc15ee40f049f718c2d716bd236fe711e4129780f",
    }})


def _vacio(valor: Optional[str]) -> bool:
    return valor is None or not str(valor).strip()


class Pago:
    """Reglas de negocio del pago en línea."""

    @staticmethod
    def validar_solicitud(datos: PagoCreate) -> None:
        """Valida los campos del pago; la tarjeta llega como token y nunca como su número."""
        if _vacio(datos.ventaId):
            raise ErrorNegocio("El identificador de la orden es obligatorio")
        if datos.monto is None:
            raise ErrorNegocio("El monto es obligatorio")
        if datos.monto <= 0:
            raise ErrorNegocio("El monto debe ser mayor que cero")
        if _vacio(datos.medioPago):
            raise ErrorNegocio("El medio de pago es obligatorio")
        medio = datos.medioPago.strip().lower()
        if medio not in MEDIOS_PAGO:
            raise ErrorNegocio("El medio de pago debe ser pse, tarjeta_credito o tarjeta_debito")
        if _vacio(datos.datosPago):
            raise ErrorNegocio("Los datos de pago son obligatorios")
        valor = datos.datosPago.strip().lower()
        if medio == "pse" and not valor.startswith(PREFIJO_BANCO_PSE):
            raise ErrorNegocio("Para pagos por PSE, los datos de pago deben indicar el banco con el prefijo banco_")
        if medio != "pse" and not valor.startswith(PREFIJO_TOKEN_TARJETA):
            raise ErrorNegocio("Los datos de la tarjeta deben ser el token de la pasarela con el prefijo tok_; "
                               "no envíe el número de la tarjeta")
        if _vacio(datos.claveIdempotencia):
            raise ErrorNegocio("La clave de idempotencia es obligatoria")

    @staticmethod
    def firma_notificacion(clave: str, transaccion_id: str, estado: str, monto: int) -> str:
        """Firma HMAC-SHA256 en hexadecimal de la cadena "transaccionId|estado|monto"."""
        mensaje = f"{transaccion_id}|{estado}|{monto}".encode("utf-8")
        return hmac.new(clave.encode("utf-8"), mensaje, sha256).hexdigest()

    @staticmethod
    def validar_notificacion(datos: "NotificacionPagoCreate", clave: str) -> None:
        """Valida los campos y la firma de la notificación enviada por la pasarela."""
        if _vacio(datos.transaccionId):
            raise ErrorNegocio("El identificador de la transacción es obligatorio")
        if _vacio(datos.estado):
            raise ErrorNegocio("El estado es obligatorio")
        if datos.monto is None:
            raise ErrorNegocio("El monto es obligatorio")
        if _vacio(datos.firma):
            raise FirmaInvalidaError("La firma de la notificación es obligatoria")
        esperada = Pago.firma_notificacion(clave, datos.transaccionId, datos.estado, datos.monto)
        if not hmac.compare_digest(esperada, datos.firma.strip().lower()):
            raise FirmaInvalidaError("La firma de la notificación no es válida")
        if datos.estado.strip().lower() not in ESTADOS_NOTIFICACION:
            raise ErrorNegocio("El estado debe ser aprobado o rechazado")

    @staticmethod
    def validar_monto_notificado(pago: dict, monto: int) -> None:
        """El monto notificado debe coincidir con el de la transacción registrada."""
        if pago["monto"] != monto:
            raise ErrorNegocio("El monto no coincide con la transacción")

    @staticmethod
    def presentar_notificacion(pago: dict, venta: dict, reserva: Optional[dict], factura: Optional[dict]) -> dict:
        """Resultado de la notificación: el pago y el estado de su orden."""
        return {
            "pagoId": pago["pagoId"],
            "transaccionId": pago["transaccionId"],
            "estadoPago": pago["estado"],
            "saldoPendiente": venta["saldoPendiente"],
            "estadoOrden": venta["estado"],
            "reservaConfirmada": reserva is not None and reserva["estado"] == "confirmada",
            "facturaGenerada": factura is not None,
        }

    @staticmethod
    def presentar_pagos(venta: dict, pagos: List[dict]) -> dict:
        """Pagos de la orden en orden de fecha; el saldo descuenta solo los pagos aprobados (RN-45)."""
        total_aprobado = sum(p["monto"] for p in pagos if p["estado"] == "aprobado")
        ordenados = sorted(pagos, key=lambda p: datetime.fromisoformat(p["fechaPago"]))
        return {
            "ventaId": venta["ventaId"],
            "valorTotal": venta["valorTotal"],
            "totalAprobado": total_aprobado,
            "saldoPendiente": venta["valorTotal"] - total_aprobado,
            "pagos": [{"pagoId": p["pagoId"], "fechaPago": p["fechaPago"], "medioPago": p["medioPago"],
                       "monto": p["monto"], "estado": p["estado"]} for p in ordenados],
        }

    @staticmethod
    def es_mismo_intento(pago: dict, venta_id: str, monto: int, medio: str) -> bool:
        """Una claveIdempotencia repetida solo es válida para el mismo intento de pago."""
        return pago["ventaId"] == venta_id and pago["monto"] == monto and pago["medioPago"] == medio

    @staticmethod
    def validar_monto(venta: dict, monto: int, pendiente_pse: int) -> None:
        """RN-44: el pago se asocia a una orden con saldo y no supera el saldo disponible.

        El saldo disponible descuenta los pagos PSE pendientes, para no pagar dos veces el mismo dinero.
        """
        if venta["saldoPendiente"] <= 0:
            raise ConflictoError("La orden ya está pagada y no tiene saldo pendiente")
        if monto > venta["saldoPendiente"]:
            raise ErrorNegocio("El monto supera el saldo pendiente")
        if monto > venta["saldoPendiente"] - pendiente_pse:
            raise ErrorNegocio("El monto supera el saldo disponible, porque hay un pago PSE pendiente de confirmación")

    @staticmethod
    def aplicar_aprobado(venta: dict, monto: int) -> Tuple[int, int, str]:
        """RN-45: recalcula el total aprobado y el saldo; con saldo cero la orden queda pagada."""
        total_aprobado = venta["totalAprobado"] + monto
        saldo = venta["valorTotal"] - total_aprobado
        return total_aprobado, saldo, "pagada" if saldo == 0 else "pago_parcial"

    @staticmethod
    def liquidar(venta: dict, pasajeros: List[dict], tarifas_menor: Dict[Tuple[str, str], int]) -> List[dict]:
        """RN-48, RN-49: liquida a cada proveedor el valor neto y retiene la comisión de la agencia."""
        liquidaciones: Dict[str, dict] = {}
        for segmento in venta["segmentos"]:
            clave = (segmento["proveedorId"], segmento["tipoServicio"])
            for pasajero in pasajeros:
                neto = (tarifas_menor.get(clave, segmento["tarifaNeta"])
                        if Cotizacion.es_menor(pasajero["edad"]) else segmento["tarifaNeta"])
                cobrado = Cotizacion.precio_venta(neto, segmento["porcentajeComision"])
                fila = liquidaciones.setdefault(segmento["proveedorId"], {
                    "ventaId": venta["ventaId"], "proveedorId": segmento["proveedorId"],
                    "valorCobradoCliente": 0, "comisionRetenida": 0, "montoPagado": 0})
                fila["valorCobradoCliente"] += cobrado
                fila["comisionRetenida"] += cobrado - neto
                fila["montoPagado"] += neto
        return list(liquidaciones.values())

    @staticmethod
    def localizador(proveedor: str, numero_reserva: int, posicion: int) -> str:
        """RN-62: localizador único por servicio, con las tres primeras letras del proveedor."""
        return f"{proveedor[:3].upper()}-{numero_reserva:05d}-{posicion}"

    @staticmethod
    def cufe_simulado(factura_id: str, venta_id: str, fecha_emision: str) -> str:
        """RN-51: la integración con la DIAN no está disponible; el CUFE se simula."""
        return "SIM-" + sha256(f"{factura_id}|{venta_id}|{fecha_emision}".encode("utf-8")).hexdigest()[:12]

    @staticmethod
    def presentar(pago: dict, venta: dict, reserva: Optional[dict], factura: Optional[dict]) -> dict:
        """Resultado del pago que devuelve la API; el PSE pendiente incluye la dirección para completarlo."""
        if pago["medioPago"] == "pse" and pago["estado"] == "pendiente":
            return {
                "pagoId": pago["pagoId"],
                "ventaId": pago["ventaId"],
                "transaccionId": pago["transaccionId"],
                "medioPago": pago["medioPago"],
                "monto": pago["monto"],
                "estado": pago["estado"],
                "urlPago": URL_PAGO_PSE + pago["transaccionId"],
                "saldoPendiente": venta["saldoPendiente"],
            }
        return {
            "pagoId": pago["pagoId"],
            "ventaId": pago["ventaId"],
            "transaccionId": pago["transaccionId"],
            "medioPago": pago["medioPago"],
            "monto": pago["monto"],
            "estado": pago["estado"],
            "saldoPendiente": venta["saldoPendiente"],
            "estadoOrden": venta["estado"],
            "reservaConfirmada": reserva is not None and reserva["estado"] == "confirmada",
            "facturaGenerada": factura is not None,
            "fechaPago": pago["fechaPago"],
        }
