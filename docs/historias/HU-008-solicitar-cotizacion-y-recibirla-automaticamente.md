## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya sé a dónde quiero viajar, en qué fechas y con quién,
Para recibir de inmediato el precio de mi viaje sin esperar a que un asesor lo calcule,
Que el sistema reciba mi solicitud en JSON y me responda automáticamente con la cotización calculada por pasajero.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/cotizaciones de `cotizaciones.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `GenerarCotizacionService`.
- El servicio identifica al cliente por su token de acceso; el cuerpo de la solicitud no incluye clienteId.
- El dominio valida que fechaInicio sea posterior a hoy y fechaFin posterior a fechaInicio, la edad de cada pasajero (RN-07), que haya al menos un servicio (RN-10) y la acomodación si hay hospedaje (RN-09).
- El servicio consulta en el catálogo la tarifa vigente de cada servicio y verifica la disponibilidad (RN-18, RN-20).
- El dominio calcula el precio de venta: tarifa neta más 12 %, excepto el tiquete aéreo, que va al valor neto (RN-22); usa la tarifa de menor según la edad (RN-23) y totaliza por pasajero (RN-06).
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

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON destino, fechaInicio, fechaFin, pasajeros, servicios y tipoAcomodacion; el cliente se identifica por su token, nunca por un clienteId enviado en el cuerpo.
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] fechaInicio debe ser posterior a la fecha actual y fechaFin posterior a fechaInicio.
- [ ] Se valida que cada pasajero tenga edad (RN-07), que haya al menos un servicio (RN-10) y que tipoAcomodacion esté informado si se pide hospedaje (RN-09).
- [ ] De los pasajeros solo se piden nombre y edad; el cliente titular autoriza su tratamiento como representante, con protección reforzada para los menores de edad (Ley 1581 de 2012).
- [ ] El precio de venta de cada servicio es la tarifa neta más 12 %, excepto el tiquete aéreo, que se vende al valor neto (RN-22).
- [ ] Se aplica la tarifa de menor a pasajeros menores de 18 años (RN-23) y el valor se presenta por pasajero (RN-06).
- [ ] La cotización se emite con vigencia hasta las 23:59:59 del día de emisión (RN-26).
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Cotización generada exitosamente",
  "data": {
    "cotizacionId": "COT-00045",
    "clienteId": "CLI-00188",
    "destino": "Cancún",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "cantidadPasajeros": 2,
    "detalle": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca",
        "tarifaNeta": 1980000,
        "porcentajeComision": 0,
        "precioVentaPorPasajero": 1980000
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel",
        "tarifaNeta": 1450000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 1624000
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel",
        "tarifaNeta": 210000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 235200
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1",
        "tarifaNeta": 180000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 201600
      }
    ],
    "valorPorPasajero": 4040800,
    "totalCotizacion": 8081600,
    "fechaEmision": "2026-11-05T10:15:00-05:00",
    "vigenteHasta": "2026-11-05T23:59:59-05:00",
    "estado": "emitida"
  },
  "success": true
}
```

- [ ] Si un servicio no tiene cupo en las fechas, el backend retorna:

```json
{
  "message": "Uno de los servicios no tiene disponibilidad para las fechas solicitadas",
  "data": null,
  "success": false
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
  "message": "Cotización generada exitosamente",
  "data": {
    "cotizacionId": "COT-00045",
    "clienteId": "CLI-00188",
    "destino": "Cancún",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "cantidadPasajeros": 2,
    "detalle": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca",
        "tarifaNeta": 1980000,
        "porcentajeComision": 0,
        "precioVentaPorPasajero": 1980000
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel",
        "tarifaNeta": 1450000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 1624000
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel",
        "tarifaNeta": 210000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 235200
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1",
        "tarifaNeta": 180000,
        "porcentajeComision": 12,
        "precioVentaPorPasajero": 201600
      }
    ],
    "valorPorPasajero": 4040800,
    "totalCotizacion": 8081600,
    "fechaEmision": "2026-11-05T10:15:00-05:00",
    "vigenteHasta": "2026-11-05T23:59:59-05:00",
    "estado": "emitida"
  },
  "success": true
}

````

- [ ] Si un servicio no tiene cupo en las fechas, el backend retorna:

```json
{
  "message": "Uno de los servicios no tiene disponibilidad para las fechas solicitadas",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 tiene un token vigente y el catálogo tiene cupo en Cancún del 2026-12-10 al 2026-12-15.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones con 2 adultos y los servicios tiquete_aereo, hospedaje, traslado y asistencia_medica, acomodación doble.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
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

  - "cotizacionId" (texto)
  - "clienteId" (texto)
  - "destino" (texto)
  - "fechaInicio" (fecha ISO 8601)
  - "fechaFin" (fecha ISO 8601)
  - "cantidadPasajeros" (número)
  - "detalle" (lista)
  - "valorPorPasajero" (número)
  - "totalCotizacion" (número)
  - "fechaEmision" (fecha ISO 8601)
  - "vigenteHasta" (fecha ISO 8601)
  - "estado" (texto)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint genera la cotización automáticamente con el precio calculado por pasajero.
- [ ] El cálculo aplica el 12 % sobre la tarifa neta, excepto en el tiquete aéreo.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el cálculo del precio, la tarifa de menor y la vigencia.
- [ ] Se cubrieron los casos de error y de excepción.
- [ ] Las pruebas funcionales están documentadas y pasadas.

## 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe:

  - Propósito del endpoint
  - Campos de entrada y salida
  - Ejemplo de respuesta exitosa
  - Ejemplo de error

## 🔐 Manejo de Errores

- [ ] Se devuelve código HTTP 500 cuando falla el acceso al repositorio de datos.
- [ ] El campo `message` en el JSON incluye un texto amigable y claro para el usuario técnico o frontend.
