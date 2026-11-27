"""Router de Facturación."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.errores import ErrorNegocio
from repository.factura_repository import factura_repository
from repository.venta_repository import venta_repository
from service.factura_service import ConsultarFacturaService

router = APIRouter(prefix="/api/v1", tags=["Facturación"])


def obtener_consultar_factura_service() -> ConsultarFacturaService:
    return ConsultarFacturaService(venta_repository, factura_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.get(
    "/ventas/{ventaId}/factura",
    status_code=200,
    summary="HU-017 Consultar mi factura",
    description="Devuelve la factura de una orden pagada en su totalidad del cliente autenticado (RN-53), emitida a "
                "nombre del cliente titular (RN-57) y con un CUFE simulado porque la integración con la DIAN no está "
                "disponible (RN-51). La factura se genera automáticamente cuando un pago aprobado deja el saldo en "
                "cero, con HU-013 o con HU-014, y se puede consultar en la misma sesión; no se elimina (RN-56). Si la "
                "orden aún no está pagada responde 409. Solo para el rol cliente.",
    responses={
        200: _ejemplo("Factura consultada", {"success": True, "data": {
            "facturaId": "FAC-00006", "numeroFactura": "OCC-2026-00006", "cufe": "SIM-8f3a2c91d7e4",
            "ventaId": "VEN-00010", "documentoCliente": "1098765432", "nombreCliente": "María Fernanda Rojas Díaz",
            "valorTotal": 8081600, "fechaEmision": "2026-11-02T10:00:05-05:00", "estado": "emitida"},
            "message": "Factura consultada exitosamente"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La orden es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Orden no encontrada", {"success": False, "data": None, "message": "La orden de venta no existe"}),
        409: _ejemplo("La orden aún no está pagada en su totalidad", {"success": False, "data": None,
                      "message": "La factura se genera cuando la orden esté pagada en su totalidad"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible consultar la factura"}),
    },
)
def consultar_mi_factura(
    ventaId: str,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ConsultarFacturaService = Depends(obtener_consultar_factura_service),
):
    try:
        factura = servicio.consultar(usuario.get("clienteId"), ventaId)
        return respuesta(data=factura, message="Factura consultada exitosamente")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible consultar la factura", 500)
