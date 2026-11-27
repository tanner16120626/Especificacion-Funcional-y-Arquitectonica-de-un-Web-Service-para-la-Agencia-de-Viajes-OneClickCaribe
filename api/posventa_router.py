"""Router de Posventa."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.consulta import ConsultaCreate, RespuestaConsultaUpdate
from domain.errores import ErrorNegocio
from repository.consulta_repository import consulta_repository
from repository.venta_repository import venta_repository
from service.posventa_service import RegistrarConsultaService, ResponderConsultaService

router = APIRouter(prefix="/api/v1", tags=["Posventa"])


def obtener_registrar_consulta_service() -> RegistrarConsultaService:
    return RegistrarConsultaService(venta_repository, consulta_repository)


def obtener_responder_consulta_service() -> ResponderConsultaService:
    return ResponderConsultaService(consulta_repository)


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


@router.patch(
    "/posventa/consultas/{consultaId}",
    status_code=200,
    summary="HU-019 Responder y cerrar una consulta posventa",
    description="Registra la respuesta del asesor a una consulta posventa abierta o en atención, con el nombre del "
                "asesor y la fecha de la respuesta. Con cerrar = true la consulta queda cerrada; con cerrar = false "
                "queda en_atencion y se puede responder de nuevo. Una consulta cerrada no se responde. También se "
                "responden las consultas registradas con HU-018 en la misma sesión. La respuesta no modifica la "
                "venta (RN-81). Solo para el rol asesor.",
    responses={
        200: _ejemplo("Consulta cerrada (cerrar = true). Con cerrar = false el estado es en_atencion y el message es "
                      "\"Respuesta registrada exitosamente\"",
                      {"success": True, "data": {
                          "consultaId": "CON-00021", "estado": "cerrada",
                          "respuesta": "Su tarifa incluye una maleta de 23 kg y un equipaje de mano.",
                          "asesor": "Tanner Cedeño", "fechaRespuesta": "2026-11-11T11:00:00-05:00"},
                       "message": "Consulta cerrada exitosamente"}),
        400: _ejemplo("Consulta cerrada o datos inválidos. Otros mensajes: \"La respuesta es obligatoria\", \"El "
                      "asesor es obligatorio\", \"El indicador cerrar es obligatorio\" o \"El campo 'cerrar' debe ser "
                      "verdadero o falso (true o false)\"",
                      {"success": False, "data": None, "message": "La consulta ya está cerrada"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cuenta no tiene rol asesor",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Consulta no encontrada", {"success": False, "data": None, "message": "La consulta no existe"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible responder la consulta"}),
    },
)
def responder_consulta_posventa(
    consultaId: str,
    datos: RespuestaConsultaUpdate,
    usuario: dict = Depends(requiere_rol("asesor")),
    servicio: ResponderConsultaService = Depends(obtener_responder_consulta_service),
):
    try:
        consulta = servicio.responder(consultaId, datos)
        mensaje = "Consulta cerrada exitosamente" if consulta["estado"] == "cerrada" else "Respuesta registrada exitosamente"
        return respuesta(data=consulta, message=mensaje)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible responder la consulta", 500)
