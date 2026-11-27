"""Router de Reservas."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.errores import ErrorNegocio
from repository.reserva_repository import reserva_repository
from repository.venta_repository import venta_repository
from service.reserva_service import ConsultarReservaService

router = APIRouter(prefix="/api/v1", tags=["Reservas"])


def obtener_consultar_reserva_service() -> ConsultarReservaService:
    return ConsultarReservaService(venta_repository, reserva_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.get(
    "/ventas/{ventaId}/reserva",
    status_code=200,
    summary="HU-016 Consultar mi reserva confirmada",
    description="Devuelve la reserva confirmada de una orden pagada en su totalidad del cliente autenticado (RN-45, "
                "RN-61), con el tipo de servicio, la razón social del proveedor y un localizador único por servicio "
                "(RN-62). La reserva se confirma automáticamente cuando un pago aprobado deja el saldo en cero, con "
                "HU-013 o con HU-014, y se puede consultar en la misma sesión. Si la orden aún no está pagada responde "
                "409. Solo para el rol cliente.",
    responses={
        200: _ejemplo("Reserva consultada", {"success": True, "data": {
            "reservaId": "RES-00008", "ventaId": "VEN-00010", "estado": "confirmada", "segmentos": [
                {"tipoServicio": "tiquete_aereo", "proveedor": "Avianca S.A.", "localizador": "AV7KQ2"},
                {"tipoServicio": "hospedaje", "proveedor": "PriceTravel Colombia S.A.S.", "localizador": "PT-558201"},
                {"tipoServicio": "traslado", "proveedor": "PriceTravel Colombia S.A.S.", "localizador": "PT-558202"},
                {"tipoServicio": "asistencia_medica", "proveedor": "Assist1 Colombia S.A.S.", "localizador": "AS1-90321"}],
            "fechaConfirmacion": "2026-11-02T10:00:05-05:00"}, "message": "Reserva consultada exitosamente"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La orden es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Orden no encontrada", {"success": False, "data": None, "message": "La orden de venta no existe"}),
        409: _ejemplo("La orden aún no está pagada en su totalidad", {"success": False, "data": None,
                      "message": "La reserva se confirma cuando la orden esté pagada en su totalidad"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible consultar la reserva"}),
    },
)
def consultar_mi_reserva_confirmada(
    ventaId: str,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ConsultarReservaService = Depends(obtener_consultar_reserva_service),
):
    try:
        reserva = servicio.consultar(usuario.get("clienteId"), ventaId)
        return respuesta(data=reserva, message="Reserva consultada exitosamente")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible consultar la reserva", 500)
