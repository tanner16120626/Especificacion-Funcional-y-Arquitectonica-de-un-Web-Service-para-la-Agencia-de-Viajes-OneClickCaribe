"""Router de Proveedores y catálogo."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.errores import ErrorNegocio
from domain.proveedor import ProveedorCreate
from repository.proveedor_repository import proveedor_repository
from service.proveedor_service import RegistrarProveedorService

router = APIRouter(prefix="/api/v1", tags=["Proveedores y catálogo"])


def obtener_registrar_proveedor_service() -> RegistrarProveedorService:
    return RegistrarProveedorService(proveedor_repository)


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
