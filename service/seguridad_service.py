"""Servicio de seguridad: cifrado de contraseñas y tokens de acceso.

Usa únicamente la biblioteca estándar de Python. El token sigue el formato JWT
(HS256), firmado con SECRET_KEY y con la vigencia de ACCESS_TOKEN_EXPIRE_MINUTES,
ambos definidos en el archivo .env. Esta capa no depende de FastAPI.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

ITERACIONES = 100_000


class TokenInvalidoError(ValueError):
    """El token no existe, está mal formado o su firma no coincide."""


class TokenVencidoError(ValueError):
    """El token superó su vigencia."""


def _clave_secreta() -> bytes:
    return os.getenv("SECRET_KEY", "cambia-este-valor-en-produccion").encode("utf-8")


def minutos_vigencia() -> int:
    """Vigencia configurada del token, en minutos."""
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def _b64url(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode("ascii")


def _b64url_decodificar(texto: str) -> bytes:
    relleno = "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode(texto + relleno)


def cifrar_contrasena(contrasena: str) -> str:
    """Devuelve la contraseña cifrada con PBKDF2-SHA256 y una sal aleatoria."""
    sal = secrets.token_hex(16)
    resumen = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal.encode("utf-8"), ITERACIONES)
    return f"pbkdf2_sha256${ITERACIONES}${sal}${resumen.hex()}"


def verificar_contrasena(contrasena: str, cifrada: str) -> bool:
    """Compara una contraseña en texto plano con su versión cifrada."""
    try:
        _, iteraciones, sal, resumen = cifrada.split("$")
    except ValueError:
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal.encode("utf-8"), int(iteraciones))
    return hmac.compare_digest(calculado.hex(), resumen)


def crear_token(datos: dict) -> str:
    """Crea un token firmado que incluye los datos recibidos y su vencimiento."""
    encabezado = {"alg": "HS256", "typ": "JWT"}
    ahora = int(time.time())
    carga = {**datos, "iat": ahora, "exp": ahora + minutos_vigencia() * 60}
    partes = [
        _b64url(json.dumps(encabezado, separators=(",", ":")).encode("utf-8")),
        _b64url(json.dumps(carga, separators=(",", ":")).encode("utf-8")),
    ]
    firma = hmac.new(_clave_secreta(), ".".join(partes).encode("ascii"), hashlib.sha256).digest()
    return ".".join(partes + [_b64url(firma)])


def verificar_token(token: str) -> dict:
    """Valida la firma y la vigencia del token y devuelve sus datos."""
    try:
        encabezado, carga, firma = token.split(".")
        esperada = hmac.new(_clave_secreta(), f"{encabezado}.{carga}".encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(esperada), firma):
            raise TokenInvalidoError("Firma inválida")
        datos = json.loads(_b64url_decodificar(carga))
    except TokenInvalidoError:
        raise
    except Exception as error:
        raise TokenInvalidoError("Token mal formado") from error
    if int(datos.get("exp", 0)) < int(time.time()):
        raise TokenVencidoError("Token vencido")
    return datos
