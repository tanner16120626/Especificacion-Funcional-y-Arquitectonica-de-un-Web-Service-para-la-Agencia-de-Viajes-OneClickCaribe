"""Router de Autenticación."""
from fastapi import APIRouter, Depends

from api.respuesta import respuesta, respuesta_error
from domain.autenticacion import LoginRequest
from domain.errores import ErrorNegocio
from repository.cliente_repository import cliente_repository
from service.autenticacion_service import IniciarSesionService

router = APIRouter(prefix="/api/v1", tags=["Autenticación"])


def obtener_iniciar_sesion_service() -> IniciarSesionService:
    return IniciarSesionService(cliente_repository)


def _ejemplo(descripcion: str, contenido: dict) -> dict:
    return {"description": descripcion, "content": {"application/json": {"example": contenido}}}


@router.post(
    "/auth/login",
    status_code=200,
    summary="HU-002 Iniciar sesión en el portal",
    description="Valida el correo y la contraseña de la cuenta y entrega un token de acceso firmado con SECRET_KEY "
                "y con la vigencia de ACCESS_TOKEN_EXPIRE_MINUTES. Si el correo no existe o la contraseña no "
                "coincide, responde 401 con el mismo mensaje.",
    responses={
        200: _ejemplo("Inicio de sesión exitoso", {"success": True, "data": {
            "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "tipoToken": "bearer", "expiraEnMinutos": 30,
            "rol": "cliente", "clienteId": "CLI-00188"}, "message": "Inicio de sesión exitoso"}),
        400: _ejemplo("Datos inválidos", {"success": False, "data": None, "message": "El campo 'correo' es obligatorio"}),
        401: _ejemplo("Credenciales inválidas", {"success": False, "data": None, "message": "Correo o contraseña incorrectos"}),
        500: _ejemplo("Error del repositorio", {"success": False, "data": None, "message": "No fue posible iniciar sesión"}),
    },
)
def iniciar_sesion(datos: LoginRequest, servicio: IniciarSesionService = Depends(obtener_iniciar_sesion_service)):
    try:
        sesion = servicio.iniciar_sesion(datos)
        return respuesta(data=sesion, message="Inicio de sesión exitoso")
    except ErrorNegocio as error:
        return respuesta_error(error.mensaje, error.status_code, error.data)
    except Exception:
        return respuesta_error("No fue posible iniciar sesión", 500)
