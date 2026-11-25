"""Router de Pagos."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.errores import ErrorNegocio
from domain.pago import PagoCreate
from repository.cliente_repository import cliente_repository
from repository.cotizacion_repository import cotizacion_repository
from repository.factura_repository import factura_repository
from repository.liquidacion_repository import liquidacion_repository
from repository.pago_repository import pago_repository
from repository.reserva_repository import reserva_repository
from repository.tarifa_repository import tarifa_repository
from repository.venta_repository import venta_repository
from service.pago_service import AutomatizarOrdenPagadaService, ProcesarPagoService
from service.pasarela_service import pasarela_pagos

router = APIRouter(prefix="/api/v1", tags=["Pagos"])

MENSAJES_PAGO = {
    "aprobado": (201, "Pago aprobado exitosamente"),
    "pendiente": (201, "Pago en proceso. Complete la operación en su banco"),
    "repetido": (200, "El pago ya fue procesado con esta clave de idempotencia"),
}


def obtener_procesar_pago_service() -> ProcesarPagoService:
    automatizacion = AutomatizarOrdenPagadaService(liquidacion_repository, reserva_repository, factura_repository,
                                                   cotizacion_repository, tarifa_repository, cliente_repository)
    return ProcesarPagoService(venta_repository, pago_repository, reserva_repository, factura_repository,
                               pasarela_pagos, automatizacion)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


_PAGO_APROBADO = {
    "pagoId": "PAG-00021", "ventaId": "VEN-00012", "transaccionId": "TRX-5580002", "medioPago": "tarjeta_credito",
    "monto": 5000000, "estado": "aprobado", "saldoPendiente": 3081600, "estadoOrden": "pago_parcial",
    "reservaConfirmada": False, "facturaGenerada": False, "fechaPago": "2026-11-11T10:15:00-05:00"}


@router.post(
    "/pagos",
    status_code=201,
    summary="HU-013 Pagar mi compra en línea",
    description="Procesa el pago total o un abono de una orden de venta del cliente autenticado con la pasarela de "
                "pagos simulada. Medios: pse, tarjeta_credito o tarjeta_debito; la tarjeta llega como token de la "
                "pasarela (prefijo tok_) y nunca su número. La orden debe tener saldo (RN-44) y el monto no supera el "
                "saldo disponible (saldo pendiente menos los PSE pendientes). Una claveIdempotencia repetida devuelve "
                "el pago original sin cobrar de nuevo. Pasarela simulada: tarjeta con tok_aprobado (o cualquier otro "
                "token tok_) se aprueba; tok_rechazado responde 402; tok_no_disponible responde 503. PSE con un banco "
                "banco_ (por ejemplo banco_bancolombia) queda pendiente hasta HU-014; banco_no_disponible responde 503. "
                "Con saldo cero la orden queda pagada (RN-45), se liquida a los proveedores al valor neto (RN-48, "
                "RN-49), se confirma la reserva (RN-61, RN-62) y se genera la factura (RN-53, RN-57). Si queda saldo, "
                "la orden pasa a pago_parcial. Solo para el rol cliente.",
    responses={
        200: _ejemplo("claveIdempotencia repetida: se devuelve el pago original sin un nuevo cobro",
                      {"success": True, "data": _PAGO_APROBADO,
                       "message": "El pago ya fue procesado con esta clave de idempotencia"}),
        201: _ejemplo("Pago aprobado (tarjeta). Por PSE el message es \"Pago en proceso. Complete la operación en "
                      "su banco\", el estado es pendiente y data incluye urlPago",
                      {"success": True, "data": _PAGO_APROBADO, "message": "Pago aprobado exitosamente"}),
        400: _ejemplo("Datos inválidos o monto mayor que el saldo",
                      {"success": False, "data": None, "message": "El monto supera el saldo pendiente"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        402: _ejemplo("La pasarela rechazó la transacción; el pago queda registrado como rechazado y el saldo no cambia",
                      {"success": False, "data": {
                          "pagoId": "PAG-00023", "ventaId": "VEN-00014", "transaccionId": "TRX-5580004",
                          "medioPago": "tarjeta_debito", "monto": 8081600, "estado": "rechazado",
                          "saldoPendiente": 8081600, "estadoOrden": "pendiente_pago", "reservaConfirmada": False,
                          "facturaGenerada": False, "fechaPago": "2026-11-11T10:40:00-05:00"},
                       "message": "La transacción fue rechazada por la entidad financiera"}),
        403: _ejemplo("La orden es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Orden no encontrada", {"success": False, "data": None, "message": "La orden de venta no existe"}),
        409: _ejemplo("Orden ya pagada. Si la claveIdempotencia se usó con otra orden, monto o medio, el message es "
                      "\"La clave de idempotencia ya se usó en otro intento de pago\"",
                      {"success": False, "data": None, "message": "La orden ya está pagada y no tiene saldo pendiente"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible procesar el pago"}),
        503: _ejemplo("La pasarela no responde; no se registra el cobro",
                      {"success": False, "data": None, "message": "La pasarela de pagos no está disponible. Intente más tarde"}),
    },
)
def pagar_mi_compra_en_linea(
    datos: PagoCreate,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ProcesarPagoService = Depends(obtener_procesar_pago_service),
):
    try:
        resultado, pago = servicio.procesar(usuario.get("clienteId"), datos)
        codigo, mensaje = MENSAJES_PAGO[resultado]
        return respuesta(data=pago, message=mensaje, status_code=codigo)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible procesar el pago", 500)
