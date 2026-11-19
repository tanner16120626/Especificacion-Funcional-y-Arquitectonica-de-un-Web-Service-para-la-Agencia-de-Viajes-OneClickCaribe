"""Router de clientes."""
from fastapi import APIRouter, Depends

from api.dependencias import requiere_rol
from api.respuesta import respuesta, respuesta_error
from domain.cliente import ClienteCreate
from domain.errores import ErrorNegocio
from repository.cliente_repository import cliente_repository
from service.cliente_service import ClienteService, ConsultarClienteService

router = APIRouter(prefix="/api/v1", tags=["Clientes"])


def obtener_cliente_service() -> ClienteService:
    return ClienteService(cliente_repository)


def obtener_consultar_cliente_service() -> ConsultarClienteService:
    return ConsultarClienteService(cliente_repository)


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


@router.get(
    "/clientes/me",
    status_code=200,
    summary="HU-003 Consultar mi perfil",
    description="Devuelve los datos registrados del cliente autenticado, sin la contraseña. El cliente se identifica "
                "con el token de acceso del encabezado Authorization: Bearer, nunca con la URL. Solo para el rol cliente.",
    responses={
        200: _ejemplo("Cliente consultado", {"success": True, "data": {
            "clienteId": "CLI-00188", "documento": "1098765432", "nombre": "María Fernanda Rojas Díaz",
            "telefono": "+573001234567", "correo": "mfrojas@correo.com", "nacionalidad": "CO", "tipoCliente": "pareja",
            "fechaRegistro": "2026-11-11T10:15:00-05:00"}, "message": "Cliente consultado exitosamente"}),
        401: _ejemplo("Token vencido, inválido o ausente", {"success": False, "data": None, "message": "La sesión expiró. Inicie sesión nuevamente"}),
        403: _ejemplo("La cuenta no tiene rol cliente", {"success": False, "data": None, "message": "No tiene permisos para realizar esta acción"}),
        404: _ejemplo("Cliente no encontrado", {"success": False, "data": None, "message": "El cliente no se encuentra registrado"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible consultar el cliente"}),
    },
)
def consultar_mi_perfil(
    usuario: dict = Depends(requiere_rol("cliente")),
    servicio: ConsultarClienteService = Depends(obtener_consultar_cliente_service),
):
    try:
        cliente = servicio.consultar(usuario.get("clienteId"))
        return respuesta(data=cliente, message="Cliente consultado exitosamente")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible consultar el cliente", 500)
