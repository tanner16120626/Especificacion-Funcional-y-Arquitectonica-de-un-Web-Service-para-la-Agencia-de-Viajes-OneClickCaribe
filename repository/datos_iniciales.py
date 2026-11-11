"""Datos iniciales del repositorio en memoria (base de datos temporal).

Cada repositorio carga desde aquí sus registros al iniciar la aplicación. Los datos
se reinician cada vez que el servidor se reinicia. Las fechas de las cotizaciones
vigentes se calculan al iniciar, para que siempre estén dentro de su vigencia.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone

ZONA_COLOMBIA = timezone(timedelta(hours=-5))
_AHORA = datetime.now(ZONA_COLOMBIA).replace(microsecond=0)
_FIN_DEL_DIA = _AHORA.replace(hour=23, minute=59, second=59)
_HOY = _AHORA.isoformat()

# Cuentas de acceso. Contraseñas de prueba: Cliente2026*, Luis2026*, Admin2026*, Asesor2026*
CUENTAS = [
    {"cuentaId": "CTA-001", "correo": "mfrojas@correo.com", "rol": "cliente", "clienteId": "CLI-00188",
     "contrasenaCifrada": "pbkdf2_sha256$100000$2abbe3f95ba57bbc96e680efb97f59de$429b84a90bb047ba4e6ffa37f7fb97cb95ec548af1a9c23b651419f9b1109649"},
    {"cuentaId": "CTA-002", "correo": "lagomez@correo.com", "rol": "cliente", "clienteId": "CLI-00190",
     "contrasenaCifrada": "pbkdf2_sha256$100000$c10e92ab53dc0ef802bff793607804eb$0277b8c8bbe034b33503716a3c34b1f4f55967036c93b7ca9bb57e46e5054dde"},
    {"cuentaId": "CTA-003", "correo": "admin@oneclickcaribe.com", "rol": "administradora", "clienteId": None,
     "contrasenaCifrada": "pbkdf2_sha256$100000$b70cf0f340fcebfecf6781e252854cc1$1aaeb7cd6ad4b54ea3225cdd2fc0b65c28d53fb340d42947c3f070e2a55d5634"},
    {"cuentaId": "CTA-004", "correo": "asesor@oneclickcaribe.com", "rol": "asesor", "clienteId": None,
     "contrasenaCifrada": "pbkdf2_sha256$100000$6f8664f51172affdb831729b1bbe447e$cd3103952d8806efee2c49a2e4e22f55fc926183e6f3c23298306cfa902a449f"},
]

CLIENTES = [
    {"clienteId": "CLI-00188", "documento": "1098765432", "nombre": "María Fernanda Rojas Díaz",
     "telefono": "+573001234567", "correo": "mfrojas@correo.com", "nacionalidad": "CO", "tipoCliente": "pareja",
     "autorizacionDatos": {"aceptada": True, "versionPolitica": "1.0", "fechaAutorizacion": "2026-11-01T09:00:00-05:00"},
     "fechaRegistro": "2026-11-01T09:00:00-05:00"},
    {"clienteId": "CLI-00190", "documento": "1095123456", "nombre": "Luis Andrés Gómez Pérez",
     "telefono": "+573157654321", "correo": "lagomez@correo.com", "nacionalidad": "CO", "tipoCliente": "individual",
     "autorizacionDatos": {"aceptada": True, "versionPolitica": "1.0", "fechaAutorizacion": "2026-11-02T10:30:00-05:00"},
     "fechaRegistro": "2026-11-02T10:30:00-05:00"},
]

PROVEEDORES = [
    {"proveedorId": "PRV-0003", "nit": "890100577-6", "razonSocial": "Avianca S.A.", "tipoProveedor": "aerolinea",
     "porcentajeComision": 0, "servicios": ["tiquete_aereo"], "destinos": ["Cancún", "Ciudad de México"], "estado": "activo"},
    {"proveedorId": "PRV-0021", "nit": "900555111-2", "razonSocial": "PriceTravel Colombia S.A.S.", "tipoProveedor": "mayorista",
     "porcentajeComision": 12, "servicios": ["hospedaje", "traslado"], "destinos": ["Cancún"], "estado": "activo"},
    {"proveedorId": "PRV-0022", "nit": "900777333-1", "razonSocial": "HotelDo S.A.S.", "tipoProveedor": "mayorista",
     "porcentajeComision": 12, "servicios": ["hospedaje"], "destinos": ["Ciudad de México"], "estado": "activo"},
    {"proveedorId": "PRV-0031", "nit": "900888444-5", "razonSocial": "Assist1 Colombia S.A.S.", "tipoProveedor": "aseguradora",
     "porcentajeComision": 12, "servicios": ["asistencia_medica"], "destinos": ["Cancún", "Ciudad de México"], "estado": "activo"},
    {"proveedorId": "PRV-0040", "nit": "900999555-8", "razonSocial": "Viajes del Sol S.A.S.", "tipoProveedor": "mayorista",
     "porcentajeComision": 12, "servicios": ["hospedaje"], "destinos": ["Cancún"], "estado": "inactivo"},
]

# Tarifas netas por adulto y por menor (COP). La consulta en tiempo real al proveedor se simula con estos datos.
TARIFAS = [
    {"servicioId": "SRV-001", "proveedorId": "PRV-0003", "tipoServicio": "tiquete_aereo", "destino": "Cancún",
     "tarifaNetaAdulto": 1980000, "tarifaNetaMenor": 1782000, "sinCupo": []},
    {"servicioId": "SRV-002", "proveedorId": "PRV-0021", "tipoServicio": "hospedaje", "destino": "Cancún",
     "tarifaNetaAdulto": 1450000, "tarifaNetaMenor": 725000, "sinCupo": [{"desde": "2026-12-24", "hasta": "2026-12-31"}]},
    {"servicioId": "SRV-003", "proveedorId": "PRV-0021", "tipoServicio": "traslado", "destino": "Cancún",
     "tarifaNetaAdulto": 210000, "tarifaNetaMenor": 105000, "sinCupo": []},
    {"servicioId": "SRV-004", "proveedorId": "PRV-0031", "tipoServicio": "asistencia_medica", "destino": "Cancún",
     "tarifaNetaAdulto": 180000, "tarifaNetaMenor": 180000, "sinCupo": []},
    {"servicioId": "SRV-005", "proveedorId": "PRV-0040", "tipoServicio": "hospedaje", "destino": "Cancún",
     "tarifaNetaAdulto": 1300000, "tarifaNetaMenor": 650000, "sinCupo": []},
]

_DETALLE_CANCUN = [
    {"tipoServicio": "tiquete_aereo", "proveedorId": "PRV-0003", "proveedor": "Avianca S.A.", "tarifaNeta": 1980000, "porcentajeComision": 0, "precioVentaPorPasajero": 1980000},
    {"tipoServicio": "hospedaje", "proveedorId": "PRV-0021", "proveedor": "PriceTravel Colombia S.A.S.", "tarifaNeta": 1450000, "porcentajeComision": 12, "precioVentaPorPasajero": 1624000},
    {"tipoServicio": "traslado", "proveedorId": "PRV-0021", "proveedor": "PriceTravel Colombia S.A.S.", "tarifaNeta": 210000, "porcentajeComision": 12, "precioVentaPorPasajero": 235200},
    {"tipoServicio": "asistencia_medica", "proveedorId": "PRV-0031", "proveedor": "Assist1 Colombia S.A.S.", "tarifaNeta": 180000, "porcentajeComision": 12, "precioVentaPorPasajero": 201600},
]
_PASAJEROS = [{"nombre": "María Fernanda Rojas Díaz", "edad": 32}, {"nombre": "Andrés Felipe Rojas", "edad": 33}]


def _cotizacion(cotizacion_id, estado, emision, vigencia):
    return {"cotizacionId": cotizacion_id, "clienteId": "CLI-00188", "destino": "Cancún",
            "fechaInicio": "2026-12-10", "fechaFin": "2026-12-15", "pasajeros": deepcopy(_PASAJEROS),
            "tipoAcomodacion": "doble", "detalle": deepcopy(_DETALLE_CANCUN), "cantidadPasajeros": 2,
            "valorPorPasajero": 4040800, "totalCotizacion": 8081600, "comisionTotal": 441600,
            "fechaEmision": emision, "vigenteHasta": vigencia, "estado": estado,
            "respuesta": "aceptada" if estado == "aceptada" else None, "motivo": None}


COTIZACIONES = [
    _cotizacion("COT-00040", "aceptada", "2026-11-02T09:00:00-05:00", "2026-11-02T23:59:59-05:00"),
    _cotizacion("COT-00044", "aceptada", "2026-11-04T10:00:00-05:00", "2026-11-04T23:59:59-05:00"),
    _cotizacion("COT-00045", "aceptada", _HOY, _FIN_DEL_DIA.isoformat()),
    _cotizacion("COT-00046", "emitida", _HOY, _FIN_DEL_DIA.isoformat()),
    {**_cotizacion("COT-00031", "vencida", "2026-10-21T09:40:00-05:00", "2026-10-21T23:59:59-05:00"),
     "destino": "Cartagena", "detalle": [], "valorPorPasajero": 1575000, "totalCotizacion": 3150000, "comisionTotal": 0},
]


def _venta(venta_id, cotizacion_id, modalidad, fecha_limite, total_aprobado, estado, total=8081600, segmentos=True):
    return {"ventaId": venta_id, "cotizacionId": cotizacion_id, "clienteId": "CLI-00188", "valorTotal": total,
            "modalidadPago": modalidad, "fechaLimiteSaldo": fecha_limite, "totalAprobado": total_aprobado,
            "saldoPendiente": total - total_aprobado, "estado": estado,
            "segmentos": deepcopy(_DETALLE_CANCUN) if segmentos else [], "fechaCreacion": "2026-11-04T11:05:00-05:00"}


VENTAS = [
    _venta("VEN-00010", "COT-00040", "total", None, 8081600, "pagada"),
    _venta("VEN-00012", "COT-00044", "parcial", "2026-11-30", 0, "pendiente_pago"),
    _venta("VEN-00013", "COT-00031", "total", None, 0, "pendiente_pago", total=3150000, segmentos=False),
]

PAGOS = [
    {"pagoId": "PAG-00020", "ventaId": "VEN-00010", "transaccionId": "TRX-5580001", "medioPago": "tarjeta_credito",
     "monto": 8081600, "estado": "aprobado", "claveIdempotencia": "seed-ven-00010", "fechaPago": "2026-11-02T10:00:00-05:00"},
]

LIQUIDACIONES = [
    {"ventaId": "VEN-00010", "proveedorId": "PRV-0003", "valorCobradoCliente": 3960000, "comisionRetenida": 0, "montoPagado": 3960000},
    {"ventaId": "VEN-00010", "proveedorId": "PRV-0021", "valorCobradoCliente": 3718400, "comisionRetenida": 398400, "montoPagado": 3320000},
    {"ventaId": "VEN-00010", "proveedorId": "PRV-0031", "valorCobradoCliente": 403200, "comisionRetenida": 43200, "montoPagado": 360000},
]

RESERVAS = [
    {"reservaId": "RES-00008", "ventaId": "VEN-00010", "estado": "confirmada", "fechaConfirmacion": "2026-11-02T10:00:05-05:00",
     "segmentos": [
         {"tipoServicio": "tiquete_aereo", "proveedor": "Avianca S.A.", "localizador": "AV7KQ2"},
         {"tipoServicio": "hospedaje", "proveedor": "PriceTravel Colombia S.A.S.", "localizador": "PT-558201"},
         {"tipoServicio": "traslado", "proveedor": "PriceTravel Colombia S.A.S.", "localizador": "PT-558202"},
         {"tipoServicio": "asistencia_medica", "proveedor": "Assist1 Colombia S.A.S.", "localizador": "AS1-90321"}]},
]

FACTURAS = [
    {"facturaId": "FAC-00006", "numeroFactura": "OCC-2026-00006", "cufe": "SIM-8f3a2c91d7e4", "ventaId": "VEN-00010",
     "documentoCliente": "1098765432", "nombreCliente": "María Fernanda Rojas Díaz", "valorTotal": 8081600,
     "fechaEmision": "2026-11-02T10:00:05-05:00", "estado": "emitida"},
]

CONSULTAS_POSVENTA = [
    {"consultaId": "CON-00019", "ventaId": "VEN-00010", "categoria": "documentos", "descripcion": "¿Necesito visa para México?",
     "estado": "cerrada", "respuesta": "Con pasaporte colombiano vigente no requiere visa para turismo.", "asesor": "Asesor One Click Caribe",
     "fechaRegistro": "2026-11-03T08:00:00-05:00", "fechaRespuesta": "2026-11-03T09:00:00-05:00"},
    {"consultaId": "CON-00021", "ventaId": "VEN-00010", "categoria": "equipaje", "descripcion": "¿Cuántas maletas puedo llevar en el vuelo?",
     "estado": "abierta", "respuesta": None, "asesor": None, "fechaRegistro": "2026-11-06T08:45:00-05:00", "fechaRespuesta": None},
    {"consultaId": "CON-00022", "ventaId": "VEN-00010", "categoria": "check_in", "descripcion": "¿Cuándo puedo hacer el check-in del vuelo?",
     "estado": "abierta", "respuesta": None, "asesor": None, "fechaRegistro": "2026-11-06T09:00:00-05:00", "fechaRespuesta": None},
]


def copia(datos):
    """Devuelve una copia independiente, para que cada repositorio tenga sus propios datos."""
    return deepcopy(datos)
