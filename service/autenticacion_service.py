"""Servicio de autenticación: valida las credenciales y entrega el token de acceso."""
from domain.autenticacion import CredencialesInvalidasError, LoginRequest
from repository.cliente_repository import ClienteRepository
from service.seguridad_service import crear_token, minutos_vigencia, verificar_contrasena

MENSAJE_CREDENCIALES_INVALIDAS = "Correo o contraseña incorrectos"


class IniciarSesionService:
    """Caso de uso del inicio de sesión."""

    def __init__(self, repositorio: ClienteRepository):
        self._repositorio = repositorio

    def iniciar_sesion(self, datos: LoginRequest) -> dict:
        """HU-002: valida correo y contraseña y devuelve un token firmado con vigencia limitada."""
        cuenta = self._repositorio.buscar_cuenta_por_correo(datos.correo)
        if cuenta is None or not verificar_contrasena(datos.contrasena, cuenta["contrasenaCifrada"]):
            raise CredencialesInvalidasError(MENSAJE_CREDENCIALES_INVALIDAS)
        token = crear_token({"sub": cuenta["cuentaId"], "rol": cuenta["rol"], "clienteId": cuenta["clienteId"]})
        return {
            "accessToken": token,
            "tipoToken": "bearer",
            "expiraEnMinutos": minutos_vigencia(),
            "rol": cuenta["rol"],
            "clienteId": cuenta["clienteId"],
        }
