"""Router de Cotizaciones."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.cotizacion import CotizacionCreate
from domain.errores import ErrorNegocio
from repository.cliente_repository import cliente_repository
from repository.cotizacion_repository import cotizacion_repository
from repository.proveedor_repository import proveedor_repository
from repository.tarifa_repository import tarifa_repository
from service.cotizacion_service import GenerarCotizacionService

router = APIRouter(prefix="/api/v1", tags=["Cotizaciones"])


def obtener_generar_cotizacion_service() -> GenerarCotizacionService:
    return GenerarCotizacionService(cotizacion_repository, cliente_repository, proveedor_repository, tarifa_repository)


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
