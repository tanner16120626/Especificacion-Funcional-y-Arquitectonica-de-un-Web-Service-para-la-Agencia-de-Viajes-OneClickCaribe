"""Router de Proveedores y catálogo."""
from datetime import date

from fastapi import APIRouter, Depends, Query

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.errores import ErrorNegocio
from domain.proveedor import CambioEstadoProveedor, ProveedorCreate
from repository.proveedor_repository import proveedor_repository
from repository.tarifa_repository import tarifa_repository
from service.catalogo_service import ConsultarCatalogoService
from service.proveedor_service import CambiarEstadoProveedorService, RegistrarProveedorService

router = APIRouter(prefix="/api/v1", tags=["Proveedores y catálogo"])


def obtener_registrar_proveedor_service() -> RegistrarProveedorService:
    return RegistrarProveedorService(proveedor_repository)


def obtener_cambiar_estado_proveedor_service() -> CambiarEstadoProveedorService:
    return CambiarEstadoProveedorService(proveedor_repository)


def obtener_consultar_catalogo_service() -> ConsultarCatalogoService:
    return ConsultarCatalogoService(tarifa_repository, proveedor_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.post(
    "/proveedores",
    status_code=201,
    summary="HU-005 Registrar un proveedor con su comisión pactada",
    description="Registra un proveedor activo (RN-13) con su NIT, razón social, tipo, comisión pactada, servicios y "
                "destinos. La comisión debe estar entre 0 y 100 y las aerolíneas se registran con comisión 0 (RN-22). "
                "El NIT no puede estar registrado. Solo para el rol administradora.",
    responses={
        201: _ejemplo("Proveedor registrado", {"success": True, "data": {
            "proveedorId": "PRV-0041", "nit": "900123456-7", "razonSocial": "Caribe Travel Mayorista S.A.S.",
            "tipoProveedor": "mayorista", "porcentajeComision": 12, "servicios": ["hospedaje", "traslado"],
            "destinos": ["Cancún", "Ciudad de México"], "estado": "activo",
            "fechaRegistro": "2026-11-11T10:15:00-05:00"}, "message": "Proveedor registrado exitosamente"}),
        400: _ejemplo("Datos inválidos", {"success": False, "data": None, "message": "Las aerolíneas se registran con comisión 0"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cuenta no tiene rol administradora", {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        409: _ejemplo("NIT ya registrado", {"success": False, "data": {"proveedorId": "PRV-0041", "nit": "900123456-7"},
                                            "message": "El proveedor ya se encuentra registrado"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible registrar el proveedor"}),
    },
)
def registrar_proveedor(
    datos: ProveedorCreate,
    usuario: dict = Depends(requiere_rol("administradora")),
    servicio: RegistrarProveedorService = Depends(obtener_registrar_proveedor_service),
):
    try:
        proveedor = servicio.registrar(datos)
        return respuesta(data=proveedor, message="Proveedor registrado exitosamente", status_code=201)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible registrar el proveedor", 500)


@router.patch(
    "/proveedores/{proveedorId}/estado",
    status_code=200,
    summary="HU-006 Desactivar o reactivar un proveedor",
    description="Cambia el estado del proveedor entre activo e inactivo, indicando el motivo; el proveedor nunca se "
                "elimina. El estado queda registrado para que el catálogo y las cotizaciones excluyan a los inactivos "
                "(RN-13). Solo para el rol administradora.",
    responses={
        200: _ejemplo("Proveedor desactivado. Si queda activo, el mensaje es \"Proveedor reactivado exitosamente\"",
                      {"success": True, "data": {
                          "proveedorId": "PRV-0021", "razonSocial": "PriceTravel Colombia S.A.S.", "estado": "inactivo",
                          "motivo": "Fin del convenio comercial", "fechaCambioEstado": "2026-11-11T10:15:00-05:00"},
                       "message": "Proveedor desactivado exitosamente"}),
        400: _ejemplo("Datos inválidos", {"success": False, "data": None, "message": "El proveedor ya se encuentra en ese estado"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "Token de acceso inválido o ausente"}),
        403: _ejemplo("La cuenta no tiene rol administradora", {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Proveedor no encontrado", {"success": False, "data": None, "message": "El proveedor no se encuentra registrado"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible cambiar el estado del proveedor"}),
    },
)
def cambiar_estado_proveedor(
    proveedorId: str,
    datos: CambioEstadoProveedor,
    usuario: dict = Depends(requiere_rol("administradora")),
    servicio: CambiarEstadoProveedorService = Depends(obtener_cambiar_estado_proveedor_service),
):
    try:
        proveedor = servicio.cambiar_estado(proveedorId, datos)
        mensaje = "Proveedor desactivado exitosamente" if proveedor["estado"] == "inactivo" else "Proveedor reactivado exitosamente"
        return respuesta(data=proveedor, message=mensaje)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible cambiar el estado del proveedor", 500)


@router.get(
    "/catalogo/servicios",
    status_code=200,
    summary="HU-007 Consultar servicios disponibles por destino",
    description="Devuelve los servicios del destino de proveedores activos (RN-13), con su tarifa neta y su "
                "disponibilidad en las fechas (RN-20). Es público: no requiere token. Las fechas usan el formato "
                "AAAA-MM-DD y la fecha de fin no puede ser anterior a la de inicio.",
    responses={
        200: _ejemplo("Servicios consultados", {"success": True, "data": {
            "destino": "Cancún", "fechaInicio": "2026-12-10", "fechaFin": "2026-12-15", "servicios": [
                {"servicioId": "SRV-001", "tipoServicio": "tiquete_aereo", "proveedor": "Avianca S.A.",
                 "tarifaNetaAdulto": 1980000, "tarifaNetaMenor": 1782000, "disponible": True},
                {"servicioId": "SRV-002", "tipoServicio": "hospedaje", "proveedor": "PriceTravel Colombia S.A.S.",
                 "tarifaNetaAdulto": 1450000, "tarifaNetaMenor": 725000, "disponible": True},
                {"servicioId": "SRV-003", "tipoServicio": "traslado", "proveedor": "PriceTravel Colombia S.A.S.",
                 "tarifaNetaAdulto": 210000, "tarifaNetaMenor": 105000, "disponible": True},
                {"servicioId": "SRV-004", "tipoServicio": "asistencia_medica", "proveedor": "Assist1 Colombia S.A.S.",
                 "tarifaNetaAdulto": 180000, "tarifaNetaMenor": 180000, "disponible": True}],
            "fechaHoraConsulta": "2026-11-11T10:15:00-05:00"}, "message": "Servicios consultados exitosamente"}),
        400: _ejemplo("Parámetros inválidos", {"success": False, "data": None, "message": "La fecha de fin no puede ser anterior a la fecha de inicio"}),
        404: _ejemplo("Sin servicios para el destino", {"success": False, "data": None, "message": "No hay servicios disponibles para el destino"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible consultar los servicios"}),
    },
)
def consultar_servicios_por_destino(
    destino: str = Query(..., description="Ciudad de destino"),
    fechaInicio: date = Query(..., description="Fecha de inicio del viaje (AAAA-MM-DD)"),
    fechaFin: date = Query(..., description="Fecha de fin del viaje (AAAA-MM-DD)"),
    servicio: ConsultarCatalogoService = Depends(obtener_consultar_catalogo_service),
):
    try:
        catalogo = servicio.consultar(destino, fechaInicio, fechaFin)
        return respuesta(data=catalogo, message="Servicios consultados exitosamente")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible consultar los servicios", 500)
