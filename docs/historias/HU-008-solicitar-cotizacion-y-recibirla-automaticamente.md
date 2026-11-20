## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya sé a dónde quiero viajar, en qué fechas y con quién,
Para recibir de inmediato el precio de mi viaje sin esperar a que un asesor lo calcule,
Que el sistema reciba mi solicitud en JSON y me responda automáticamente con la cotización calculada por pasajero.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/cotizaciones de `cotizaciones.api` con el método POST.
- La capa API valida el token de acceso del cliente y el formato del JSON, y delega el caso de uso a `GenerarCotizacionService`.
- El servicio identifica al cliente por su token de acceso; el cuerpo de la solicitud no incluye clienteId.
- El dominio valida que fechaInicio sea posterior a hoy y fechaFin posterior a fechaInicio, la edad de cada pasajero (RN-07), que haya al menos un servicio (RN-10) y la acomodación si hay hospedaje (RN-09).
- El servicio consulta en el catálogo la tarifa vigente de cada servicio y verifica la disponibilidad (RN-18, RN-20).
- El dominio calcula el precio de venta: tarifa neta más el porcentaje de comisión pactado con el proveedor (HU-005); las aerolíneas tienen comisión 0, porque el tiquete aéreo se vende al valor neto (RN-22); usa la tarifa de menor según la edad (RN-23) y presenta el valor de cada pasajero (RN-06).
- La cotización queda emitida con vigencia hasta las 23:59:59 del mismo día (RN-26).
- Se reciben o consultan los campos:
- destino / Ciudad de destino
- fechaInicio / Fecha de inicio del viaje
- fechaFin / Fecha de fin del viaje
- pasajeros / Lista de pasajeros con nombre y edad
- servicios / Servicios solicitados (`tiquete_aereo`, `hospedaje`, `traslado`, `asistencia_medica`)
- tipoAcomodacion / Tipo de acomodación (obligatorio si hay hospedaje)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON destino, fechaInicio, fechaFin, pasajeros, servicios y tipoAcomodacion; el cliente se identifica por su token, nunca por un clienteId enviado en el cuerpo.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente"; las cuentas que no son de cliente reciben 403 con "No tiene permisos para realizar esta acción".
- [x] fechaInicio debe ser posterior a la fecha actual y fechaFin posterior a fechaInicio.
- [x] Se valida que cada pasajero tenga edad (RN-07), que haya al menos un servicio (RN-10) y que tipoAcomodacion esté informado si se pide hospedaje (RN-09).
- [x] De los pasajeros solo se piden nombre y edad; el cliente titular autoriza su tratamiento como representante, con protección reforzada para los menores de edad (Ley 1581 de 2012).
- [x] El precio de venta de cada servicio es la tarifa neta más el porcentaje de comisión pactado con su proveedor; las aerolíneas tienen comisión 0, porque el tiquete aéreo se vende al valor neto (RN-22).
- [x] Se aplica la tarifa de menor a pasajeros menores de 18 años (RN-23) y el valor se presenta por pasajero (RN-06).
- [x] La cotización se emite con vigencia hasta las 23:59:59 del día de emisión (RN-26).
- [x] Los errores de formato del JSON se responden con código 400 y la estructura success, data y message. Mensajes exactos: "El destino es obligatorio"; "La fecha de inicio debe ser posterior a hoy"; "La fecha de fin debe ser posterior a la fecha de inicio"; "Debe registrar al menos un pasajero"; "El nombre de cada pasajero es obligatorio"; "La edad de cada pasajero es obligatoria"; "La edad de cada pasajero debe estar entre 0 y 120"; "Debe solicitar al menos un servicio"; "Los servicios deben ser tiquete_aereo, hospedaje, traslado o asistencia_medica"; "El tipo de acomodación es obligatorio cuando se solicita hospedaje".
- [x] Solo se cotizan servicios de proveedores activos (RN-13); si un servicio solicitado no se ofrece o no tiene cupo en las fechas, se responde 409 con el mensaje "Uno de los servicios no tiene disponibilidad para las fechas solicitadas".
- [x] Si el destino no tiene servicios de proveedores activos, se responde 404 con el mensaje "No hay servicios disponibles para el destino".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaEmision corresponde a la fecha y hora de la solicitud y vigenteHasta, a las 23:59:59 de ese mismo día) (valorPorPasajero corresponde al valor de un pasajero adulto, o al de un menor si no viaja ningún adulto; el valor de cada pasajero se detalla en pasajeros):

```json
{
  "success": true,
  "data": {
    "cotizacionId": "COT-00047",
    "clienteId": "CLI-00188",
    "destino": "Cancún",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "cantidadPasajeros": 2,
    "pasajeros": [
      {
        "nombre": "María Fernanda Rojas Díaz",
        "edad": 32,
        "valor": 4040800
      },
      {
        "nombre": "Andrés Felipe Rojas",
        "edad": 33,
        "valor": 4040800
      }
    ],
    "detalle": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "tarifaNeta": 1980000,
        "porcentajeComision": 0,
        "precioVentaPorPasajero": 1980000
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNeta": 1450000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 1624000
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNeta": 210000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 235200
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "tarifaNeta": 180000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 201600
      }
    ],
    "valorPorPasajero": 4040800,
    "totalCotizacion": 8081600,
    "fechaEmision": "2026-11-11T10:15:00-05:00",
    "vigenteHasta": "2026-11-11T23:59:59-05:00",
    "estado": "emitida"
  },
  "message": "Cotización generada exitosamente"
}
```

- [x] Si un servicio no tiene cupo en las fechas, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "Uno de los servicios no tiene disponibilidad para las fechas solicitadas"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Solicitar cotización y recibirla automáticamente

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/cotizaciones`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "cotizacionId": "COT-00047",
    "clienteId": "CLI-00188",
    "destino": "Cancún",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "cantidadPasajeros": 2,
    "pasajeros": [
      {
        "nombre": "María Fernanda Rojas Díaz",
        "edad": 32,
        "valor": 4040800
      },
      {
        "nombre": "Andrés Felipe Rojas",
        "edad": 33,
        "valor": 4040800
      }
    ],
    "detalle": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "tarifaNeta": 1980000,
        "porcentajeComision": 0,
        "precioVentaPorPasajero": 1980000
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNeta": 1450000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 1624000
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNeta": 210000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 235200
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "tarifaNeta": 180000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 201600
      }
    ],
    "valorPorPasajero": 4040800,
    "totalCotizacion": 8081600,
    "fechaEmision": "2026-11-11T10:15:00-05:00",
    "vigenteHasta": "2026-11-11T23:59:59-05:00",
    "estado": "emitida"
  },
  "message": "Cotización generada exitosamente"
}

````

- [x] Si un servicio no tiene cupo en las fechas, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "Uno de los servicios no tiene disponibilidad para las fechas solicitadas"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 (registrado con HU-001) inició sesión con HU-002 y el catálogo tiene cupo en Cancún del 2026-12-10 al 2026-12-15.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones con 2 adultos y los servicios tiquete_aereo, hospedaje, traslado y asistencia_medica, acomodación doble.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.cotizacionId = "COT-00047" y data.estado = "emitida"
  - Campo data.valorPorPasajero = 4040800 y data.totalCotizacion = 8081600
  - Campo message contiene el texto: "Cotización generada exitosamente"

### ✅ Caso 2:

- **Precondición:** El hospedaje en Cancún no tiene cupo del 2026-12-24 al 2026-12-31.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones con esas fechas.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - No se crea la cotización
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "Uno de los servicios no tiene disponibilidad para las fechas solicitadas"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "cotizacionId" (texto)
    - "clienteId" (texto)
    - "destino" (texto)
    - "fechaInicio" (fecha ISO 8601)
    - "fechaFin" (fecha ISO 8601)
    - "cantidadPasajeros" (número)
    - "pasajeros" (lista de objetos), cada uno con los campos:
      - "nombre" (texto)
      - "edad" (número)
      - "valor" (número)
    - "detalle" (lista de objetos), cada uno con los campos:
      - "tipoServicio" (texto)
      - "proveedor" (texto)
      - "tarifaNeta" (número)
      - "porcentajeComision" (número)
      - "precioVentaPorPasajero" (número)
    - "valorPorPasajero" (número)
    - "totalCotizacion" (número)
    - "fechaEmision" (fecha ISO 8601)
    - "vigenteHasta" (fecha ISO 8601)
    - "estado" (texto)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El cliente envía una fechaInicio pasada, un pasajero sin edad o una lista de servicios vacía.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones con cada uno de esos datos inválidos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - No se crea la cotización
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La fecha de inicio debe ser posterior a hoy", "La edad de cada pasajero es obligatoria" o "Debe solicitar al menos un servicio", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible generar la cotización"

## ✅ Definición de Hecho

# Historia: Solicitar cotización y recibirla automáticamente

## 📦 Alcance Funcional

- [x] El endpoint genera la cotización automáticamente con el precio calculado por pasajero.
- [x] El cálculo aplica sobre la tarifa neta el porcentaje de comisión pactado con cada proveedor; las aerolíneas tienen comisión 0.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el cálculo del precio, la tarifa de menor y la vigencia.
- [x] Se cubrieron los casos de error y de excepción.
- [x] Las pruebas funcionales están documentadas y pasadas.

## 📄 Documentación Técnica

- [x] Endpoint documentado en Swagger / OpenAPI.
- [x] Se describe:

  - Propósito del endpoint
  - Campos de entrada y salida
  - Ejemplo de respuesta exitosa
  - Ejemplo de error

## 🔐 Manejo de Errores

- [x] Se devuelve código HTTP 500 cuando falla el acceso al repositorio de datos.
- [x] El campo `message` en el JSON incluye un texto amigable y claro para el usuario técnico o frontend.
