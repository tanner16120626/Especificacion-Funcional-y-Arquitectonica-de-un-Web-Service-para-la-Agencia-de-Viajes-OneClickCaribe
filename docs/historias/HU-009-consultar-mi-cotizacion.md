## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya recibí una cotización,
Para revisar con calma el detalle del precio y saber hasta cuándo puedo aceptarla,
Que el sistema me permita consultar mi cotización con su detalle, su vigencia y su estado actual.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/cotizaciones/{cotizacionId} de `cotizaciones.api` con el método GET.
- La capa API valida el formato del JSON y delega el caso de uso a `ConsultarCotizacionService`.
- El repositorio en memoria busca la cotización por su identificador.
- El dominio actualiza el estado a `vencida` si ya pasó su vigencia (RN-28).
- Se reciben o consultan los campos:
- cotizacionId / Identificador de la cotización (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint GET que recibe el cotizacionId como parámetro de ruta.
- [ ] Se devuelve el detalle completo de la cotización, con su vigencia y su estado.
- [ ] Si la fecha y hora actual supera vigenteHasta, el estado se informa como `vencida` (RN-28).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Cotización consultada exitosamente",
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

- [ ] Si la cotización ya venció, el backend retorna el estado actualizado:

```json
{
  "message": "La cotización está vencida",
  "data": {
    "cotizacionId": "COT-00031",
    "vigenteHasta": "2026-10-21T23:59:59-05:00",
    "estado": "vencida"
  },
  "success": true
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar mi cotización

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/cotizaciones/{cotizacionId}`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "message": "Cotización consultada exitosamente",
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

- [ ] Si la cotización ya venció, el backend retorna el estado actualizado:

```json
{
  "message": "La cotización está vencida",
  "data": {
    "cotizacionId": "COT-00031",
    "vigenteHasta": "2026-10-21T23:59:59-05:00",
    "estado": "vencida"
  },
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El repositorio contiene la cotización COT-00045 vigente.
- **Acción:** Ejecutar el endpoint GET /api/v1/cotizaciones/COT-00045.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "emitida"
  - Campo message contiene el texto: "Cotización consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** El repositorio contiene la cotización COT-00031, emitida el 2026-10-21.
- **Acción:** Ejecutar el endpoint GET /api/v1/cotizaciones/COT-00031.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "vencida"
  - Campo message contiene el texto: "La cotización está vencida"

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

- **Precondición:** El repositorio no contiene la cotización COT-09999.
- **Acción:** Ejecutar el endpoint GET /api/v1/cotizaciones/COT-09999.
- **Resultado esperado:**

  - Código HTTP 404 Not Found
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La cotización no existe"

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible consultar la cotización"

## ✅ Definición de Hecho

# Historia: Consultar mi cotización

## 📦 Alcance Funcional

- [ ] El endpoint devuelve la cotización con su detalle y estado.
- [ ] El estado refleja la vencida cuando pasó su vigencia.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la consulta por identificador y el cálculo de vencimiento.
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
