"""Router de Ventas."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.errores import ErrorNegocio
from domain.venta import OrdenVentaCreate
from repository.cotizacion_repository import cotizacion_repository
from repository.factura_repository import factura_repository
from repository.reserva_repository import reserva_repository
from repository.venta_repository import venta_repository
from service.venta_service import ConsultarOrdenService, GenerarOrdenVentaService

router = APIRouter(prefix="/api/v1", tags=["Ventas"])


def obtener_generar_orden_venta_service() -> GenerarOrdenVentaService:
    return GenerarOrdenVentaService(venta_repository, cotizacion_repository)


def obtener_consultar_orden_service() -> ConsultarOrdenService:
    return ConsultarOrdenService(venta_repository, reserva_repository, factura_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.post(
    "/ventas",
    status_code=201,
    summary="HU-011 Confirmar mi compra y generar la orden de venta",
    description="Genera la orden de venta de una cotización aceptada y vigente del cliente autenticado (RN-31), con un "
                "ventaId propio vinculado a la cotización (RN-32) y los precios de la cotización, que ya no se "
                "modifican (RN-34). La modalidad de pago es total o parcial; si es parcial, fechaLimiteSaldo es "
                "obligatoria y anterior a la fecha de inicio del viaje (RN-33). Una cotización solo tiene una orden. "
                "Solo para el rol cliente.",
    responses={
        201: _ejemplo("Orden de venta generada", {"success": True, "data": {
            "ventaId": "VEN-00014", "cotizacionId": "COT-00045", "clienteId": "CLI-00188", "valorTotal": 8081600,
            "modalidadPago": "parcial", "fechaLimiteSaldo": "2026-11-30", "totalPagado": 0, "saldoPendiente": 8081600,
            "estado": "pendiente_pago", "fechaCreacion": "2026-11-11T10:25:00-05:00"},
            "message": "Orden de venta generada exitosamente"}),
        400: _ejemplo("Datos inválidos o cotización no aceptada",
                      {"success": False, "data": None, "message": "Solo se genera la orden de una cotización aceptada"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cotización es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Cotización no encontrada", {"success": False, "data": None, "message": "La cotización no existe"}),
        409: _ejemplo("La cotización ya tiene una orden", {"success": False, "data": {
            "ventaId": "VEN-00014", "cotizacionId": "COT-00045"}, "message": "La cotización ya tiene una orden de venta"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible generar la orden de venta"}),
    },
)
def generar_orden_venta(
    datos: OrdenVentaCreate,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: GenerarOrdenVentaService = Depends(obtener_generar_orden_venta_service),
):
    try:
        venta = servicio.generar(usuario.get("clienteId"), datos)
        return respuesta(data=venta, message="Orden de venta generada exitosamente", status_code=201)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible generar la orden de venta", 500)


@router.get(
    "/ventas/{ventaId}",
    status_code=200,
    summary="HU-012 Consultar el estado de mi compra",
    description="Devuelve el estado de la orden de venta del cliente autenticado: valor total, total pagado (solo "
                "pagos aprobados por la pasarela, RN-45), saldo pendiente, estado (pendiente_pago, pago_parcial o "
                "pagada) y si la reserva está confirmada y la factura generada. El cliente solo consulta sus propias "
                "órdenes. Solo para el rol cliente.",
    responses={
        200: _ejemplo("Orden consultada", {"success": True, "data": {
            "ventaId": "VEN-00010", "clienteId": "CLI-00188", "valorTotal": 8081600, "totalPagado": 8081600,
            "saldoPendiente": 0, "estado": "pagada", "reservaConfirmada": True, "facturaGenerada": True},
            "message": "Orden consultada exitosamente"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La orden es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Orden no encontrada", {"success": False, "data": None, "message": "La orden de venta no existe"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible consultar la orden"}),
    },
)
def consultar_estado_de_mi_compra(
    ventaId: str,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ConsultarOrdenService = Depends(obtener_consultar_orden_service),
):
    try:
        orden = servicio.consultar(usuario.get("clienteId"), ventaId)
        return respuesta(data=orden, message="Orden consultada exitosamente")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible consultar la orden", 500)
