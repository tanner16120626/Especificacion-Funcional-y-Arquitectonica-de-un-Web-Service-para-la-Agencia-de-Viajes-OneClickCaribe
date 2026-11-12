"""Router de clientes."""
from fastapi import APIRouter, Depends

from api.respuesta import respuesta, respuesta_error
from domain.cliente import ClienteCreate
from domain.errores import ErrorNegocio
from repository.cliente_repository import cliente_repository
from service.cliente_service import ClienteService

router = APIRouter(prefix="/api/v1", tags=["Clientes"])


def obtener_cliente_service() -> ClienteService:
    return ClienteService(cliente_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.post(
    "/clientes",
    status_code=201,
    summary="HU-001 Registrarme en el portal",
    description="Registra al cliente con sus datos personales, una contraseña cifrada y su autorización "
                "para el tratamiento de datos (Ley 1581 de 2012). Aplica RN-01, RN-04 y RN-05.",
    responses={
        201: _ejemplo("Cliente registrado", {"success": True, "data": {
            "clienteId": "CLI-00188", "documento": "1098765432", "nombre": "María Fernanda Rojas Díaz",
            "telefono": "+573001234567", "correo": "mfrojas@correo.com", "nacionalidad": "CO", "tipoCliente": "pareja",
            "autorizacionDatos": {"aceptada": True, "versionPolitica": "1.0", "fechaAutorizacion": "2026-11-11T10:15:00-05:00"},
            "fechaRegistro": "2026-11-11T10:15:00-05:00"}, "message": "Cliente registrado exitosamente"}),
        400: _ejemplo("Datos inválidos", {"success": False, "data": None, "message": "Debe autorizar el tratamiento de sus datos personales"}),
        409: _ejemplo("Documento ya registrado", {"success": False, "data": {"clienteId": "CLI-00188", "documento": "1098765432"},
                                                  "message": "El cliente ya se encuentra registrado"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible registrar el cliente"}),
    },
)
def registrar_cliente(datos: ClienteCreate, servicio: ClienteService = Depends(obtener_cliente_service)):
    try:
        cliente = servicio.registrar(datos)
        return respuesta(data=cliente, message="Cliente registrado exitosamente", status_code=201)
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible registrar el cliente", 500)
