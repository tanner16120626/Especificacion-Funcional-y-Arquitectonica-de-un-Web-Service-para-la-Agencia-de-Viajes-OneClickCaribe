"""Servicio de clientes: orquesta el registro aplicando las reglas del dominio."""
from datetime import datetime, timedelta, timezone

from domain.cliente import VERSION_POLITICA_DATOS, Cliente, ClienteCreate, ClienteResponse
from domain.errores import ConflictoError
from repository.cliente_repository import ClienteRepository
from service.seguridad_service import cifrar_contrasena

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


class ClienteService:
    """Casos de uso del cliente."""

    def __init__(self, repositorio: ClienteRepository):
        self._repositorio = repositorio

    def registrar(self, datos: ClienteCreate) -> dict:
        """HU-001: registra al cliente con su contraseña cifrada y su autorización de datos."""
        Cliente.validar_registro(datos)
        documento = datos.documento.strip()
        existente = self._repositorio.buscar_por_documento(documento)
        if existente:
            raise ConflictoError(
                "El cliente ya se encuentra registrado",
                {"clienteId": existente["clienteId"], "documento": existente["documento"]},
            )
        ahora = datetime.now(ZONA_COLOMBIA).replace(microsecond=0).isoformat()
        cliente = {
            "clienteId": self._repositorio.siguiente_cliente_id(),
            "documento": documento,
            "nombre": datos.nombre.strip(),
            "telefono": datos.telefono.strip() if datos.telefono else None,
            "correo": datos.correo.strip().lower() if datos.correo else None,
            "nacionalidad": datos.nacionalidad.strip().upper(),
            "tipoCliente": datos.tipoCliente.strip().lower(),
            "autorizacionDatos": {
                "aceptada": True,
                "versionPolitica": VERSION_POLITICA_DATOS,
                "fechaAutorizacion": ahora,
            },
            "fechaRegistro": ahora,
        }
        cuenta = {
            "cuentaId": self._repositorio.siguiente_cuenta_id(),
            "correo": cliente["correo"],
            "rol": "cliente",
            "clienteId": cliente["clienteId"],
            "contrasenaCifrada": cifrar_contrasena(datos.contrasena),
        }
        self._repositorio.guardar(cliente, cuenta)
        return ClienteResponse(**cliente).model_dump()
