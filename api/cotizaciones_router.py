"""Router de Cotizaciones."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.cotizacion import CotizacionCreate, RespuestaCotizacion
from domain.errores import ErrorNegocio
from repository.cliente_repository import cliente_repository
from repository.cotizacion_repository import cotizacion_repository
from repository.proveedor_repository import proveedor_repository
from repository.tarifa_repository import tarifa_repository
from service.cotizacion_service import ConsultarCotizacionService, GenerarCotizacionService, ResponderCotizacionService

router = APIRouter(prefix="/api/v1", tags=["Cotizaciones"])


def obtener_generar_cotizacion_service() -> GenerarCotizacionService:
    return GenerarCotizacionService(cotizacion_repository, cliente_repository, proveedor_repository, tarifa_repository)


def obtener_consultar_cotizacion_service() -> ConsultarCotizacionService:
    return ConsultarCotizacionService(cotizacion_repository)


def obtener_responder_cotizacion_service() -> ResponderCotizacionService:
    return ResponderCotizacionService(cotizacion_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


_DETALLE_EJEMPLO = [
    {"tipoServicio": "tiquete_aereo", "proveedor": "Avianca S.A.", "tarifaNeta": 1980000, "porcentajeComision": 0,
     "precioVentaPorPasajero": 1980000},
    {"tipoServicio": "hospedaje", "proveedor": "PriceTravel Colombia S.A.S.", "tarifaNeta": 1450000,
     "porcentajeComision": 12, "precioVentaPorPasajero": 1624000},
    {"tipoServicio": "traslado", "proveedor": "PriceTravel Colombia S.A.S.", "tarifaNeta": 210000,
     "porcentajeComision": 12, "precioVentaPorPasajero": 235200},
    {"tipoServicio": "asistencia_medica", "proveedor": "Assist1 Colombia S.A.S.", "tarifaNeta": 180000,
     "porcentajeComision": 12, "precioVentaPorPasajero": 201600},
]


@router.post(
    "/cotizaciones",
    status_code=201,
    summary="HU-008 Solicitar cotización y recibirla automáticamente",
    description="Genera la cotización del cliente autenticado con la tarifa vigente de servicios de proveedores "
                "activos (RN-13, RN-18, RN-20). El precio de venta es la tarifa neta más la comisión pactada con el "
                "proveedor; las aerolíneas tienen comisión 0 (RN-22). Los menores de 18 años usan la tarifa de menor "
                "(RN-23) y el valor se presenta por pasajero (RN-06). Vigente hasta las 23:59:59 del día (RN-26). "
                "valorPorPasajero es el valor de un pasajero adulto, o el de un menor si no viaja ningún adulto. "
                "Solo para el rol cliente.",
    responses={
        201: _ejemplo("Cotización generada", {"success": True, "data": {
            "cotizacionId": "COT-00047", "clienteId": "CLI-00188", "destino": "Cancún", "fechaInicio": "2026-12-10",
            "fechaFin": "2026-12-15", "cantidadPasajeros": 2,
            "pasajeros": [{"nombre": "María Fernanda Rojas Díaz", "edad": 32, "valor": 4040800},
                          {"nombre": "Andrés Felipe Rojas", "edad": 33, "valor": 4040800}],
            "detalle": _DETALLE_EJEMPLO, "valorPorPasajero": 4040800, "totalCotizacion": 8081600,
            "fechaEmision": "2026-11-11T10:15:00-05:00", "vigenteHasta": "2026-11-11T23:59:59-05:00",
            "estado": "emitida"}, "message": "Cotización generada exitosamente"}),
        400: _ejemplo("Datos inválidos", {"success": False, "data": None, "message": "La fecha de inicio debe ser posterior a hoy"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cuenta no tiene rol cliente", {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Destino sin servicios", {"success": False, "data": None, "message": "No hay servicios disponibles para el destino"}),
        409: _ejemplo("Servicio sin disponibilidad", {"success": False, "data": None,
                                                      "message": "Uno de los servicios no tiene disponibilidad para las fechas solicitadas"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible generar la cotización"}),
    },
)
def solicitar_cotizacion(
    datos: CotizacionCreate,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: GenerarCotizacionService = Depends(obtener_generar_cotizacion_service),
):
    try:
        cotizacion = servicio.generar(usuario.get("clienteId"), datos)
        return respuesta(data=cotizacion, message="Cotización generada exitosamente", status_code=201)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible generar la cotización", 500)


@router.get(
    "/cotizaciones/{cotizacionId}",
    status_code=200,
    summary="HU-009 Consultar mi cotización",
    description="Devuelve la cotización del cliente autenticado con su detalle, su vigencia y su estado actual. Si la "
                "cotización está emitida y ya pasó vigenteHasta, se informa como vencida (RN-28) y el mensaje es "
                "\"La cotización está vencida\". El cliente solo consulta sus propias cotizaciones. Solo para el rol cliente.",
    responses={
        200: _ejemplo("Cotización consultada. Si está vencida, el mensaje es \"La cotización está vencida\"",
                      {"success": True, "data": {
                          "cotizacionId": "COT-00046", "clienteId": "CLI-00188", "destino": "Cancún",
                          "fechaInicio": "2026-12-10", "fechaFin": "2026-12-15", "cantidadPasajeros": 2,
                          "pasajeros": [{"nombre": "María Fernanda Rojas Díaz", "edad": 32, "valor": 4040800},
                                        {"nombre": "Andrés Felipe Rojas", "edad": 33, "valor": 4040800}],
                          "detalle": _DETALLE_EJEMPLO, "valorPorPasajero": 4040800, "totalCotizacion": 8081600,
                          "fechaEmision": "2026-11-11T10:15:00-05:00", "vigenteHasta": "2026-11-11T23:59:59-05:00",
                          "estado": "emitida"}, "message": "Cotización consultada exitosamente"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cotización es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Cotización no encontrada", {"success": False, "data": None, "message": "La cotización no existe"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible consultar la cotización"}),
    },
)
def consultar_mi_cotizacion(
    cotizacionId: str,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ConsultarCotizacionService = Depends(obtener_consultar_cotizacion_service),
):
    try:
        cotizacion = servicio.consultar(usuario.get("clienteId"), cotizacionId)
        mensaje = "La cotización está vencida" if cotizacion["estado"] == "vencida" else "Cotización consultada exitosamente"
        return respuesta(data=cotizacion, message=mensaje)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible consultar la cotización", 500)


@router.post(
    "/cotizaciones/{cotizacionId}/respuesta",
    status_code=200,
    summary="HU-010 Responder a mi cotización",
    description="Registra la aceptación o el rechazo de la cotización del cliente autenticado. Solo se responde una "
                "cotización emitida y vigente (RN-26, RN-28); si ya pasó vigenteHasta se informa como vencida. Si el "
                "cliente la rechaza, el motivo es obligatorio (RN-30). El cliente solo responde sus propias "
                "cotizaciones. Solo para el rol cliente.",
    responses={
        200: _ejemplo("Respuesta registrada", {"success": True, "data": {
            "cotizacionId": "COT-00047", "respuesta": "aceptada", "motivo": None, "estado": "aceptada",
            "fechaRespuesta": "2026-11-11T10:20:00-05:00"}, "message": "Respuesta registrada exitosamente"}),
        400: _ejemplo("Datos inválidos, cotización vencida o ya respondida",
                      {"success": False, "data": None, "message": "La cotización está vencida y no puede responderse"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cotización es de otro cliente o la cuenta no tiene rol cliente",
                      {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Cotización no encontrada", {"success": False, "data": None, "message": "La cotización no existe"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible registrar la respuesta"}),
    },
)
def responder_mi_cotizacion(
    cotizacionId: str,
    datos: RespuestaCotizacion,
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ResponderCotizacionService = Depends(obtener_responder_cotizacion_service),
):
    try:
        respuesta_cotizacion = servicio.responder(usuario.get("clienteId"), cotizacionId, datos)
        return respuesta(data=respuesta_cotizacion, message="Respuesta registrada exitosamente")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible registrar la respuesta", 500)
