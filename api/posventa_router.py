"""Router de Posventa."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.consulta import ConsultaCreate
from domain.errores import ErrorNegocio
from repository.consulta_repository import consulta_repository
from repository.venta_repository import venta_repository
from service.posventa_service import RegistrarConsultaService

router = APIRouter(prefix="/api/v1", tags=["Posventa"])


def obtener_registrar_consulta_service() -> RegistrarConsultaService:
    return RegistrarConsultaService(venta_repository, consulta_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.post(
    "/posventa/consultas",
    status_code=201,
    summary="HU-018 Registrar una consulta posventa",
    description="Registra una consulta posventa del cliente autenticado vinculada a una de sus órdenes (RN-83). "
                "Categorías: equipaje, documentos, itinerario, check_in, servicios_adicionales u otro; la "
                "descripción es obligatoria. La consulta queda abierta y sin fecha de vencimiento (RN-85), a la "
                "espera de la respuesta del asesor (HU-019), y no modifica la venta (RN-81). Solo para el rol cliente.",
    responses={
        201: _ejemplo("Consulta registrada", {"success": True, "data": {
            "consultaId": "CON-00023", "ventaId": "VEN-00010", "categoria": "equipaje",
            "descripcion": "¿Puedo llevar una maleta adicional de 23 kg en el vuelo de regreso?", "estado": "abierta",
            "fechaRegistro": "2026-11-11T10:50:00-05:00"}, "message": "Consulta registrada exitosamente"}),
        400: _ejemplo("Datos inválidos. Otros mensajes: \"El identificador de la orden es obligatorio\", \"La "
                      "categoría es obligatoria\", \"La descripción es obligatoria\" o \"El campo 'descripcion' debe "
                      "ser un texto\"",
                      {"success": False, "data": None, "message": "La categoría de la consulta no es válida"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La orden es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Orden no encontrada", {"success": False, "data": None, "message": "La orden de venta no existe"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible registrar la consulta"}),
    },
)
def registrar_consulta_posventa(
    datos: ConsultaCreate,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: RegistrarConsultaService = Depends(obtener_registrar_consulta_service),
):
    try:
        consulta = servicio.registrar(usuario.get("clienteId"), datos)
        return respuesta(data=consulta, message="Consulta registrada exitosamente", status_code=201)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible registrar la consulta", 500)
