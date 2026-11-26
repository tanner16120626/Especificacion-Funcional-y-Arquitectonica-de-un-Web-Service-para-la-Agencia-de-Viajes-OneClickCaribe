## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya recibí una cotización,
Para revisar con calma el detalle del precio y saber hasta cuándo puedo aceptarla,
Que el sistema me permita consultar mi cotización con su detalle, su vigencia y su estado actual.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/cotizaciones/{cotizacionId} de `cotizaciones.api` con el método GET.
- La capa API valida el token de acceso del cliente y delega el caso de uso a `ConsultarCotizacionService`.
- El repositorio en memoria busca la cotización por su identificador y el servicio verifica que pertenezca al cliente del token.
- El dominio informa el estado `vencida` si la cotización está emitida y ya pasó su vigencia (RN-28); el servicio registra ese estado en el repositorio.
- Se reciben o consultan los campos:
- cotizacionId / Identificador de la cotización (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET que recibe el cotizacionId como parámetro de ruta.
- [x] Se devuelve el detalle completo de la cotización, con su vigencia y su estado.
- [x] Si la cotización está emitida y la fecha y hora actual supera vigenteHasta, el estado se informa como `vencida` (RN-28) y el mensaje es "La cotización está vencida".
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo accede a sus propias cotizaciones; si la cotización pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Si la cotización no existe, se responde 404 con el mensaje "La cotización no existe".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaEmision y vigenteHasta corresponden a la fecha de la consulta, porque la cotización COT-00046 se precarga con la fecha del día en que se inicia el servicio):

```json
{
  "success": true,
  "data": {
    "cotizacionId": "COT-00046",
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
  "message": "Cotización consultada exitosamente"
}
```

- [x] Si la cotización ya venció, el backend retorna el estado actualizado:

```json
{
  "success": true,
  "data": {
    "cotizacionId": "COT-00031",
    "clienteId": "CLI-00188",
    "destino": "Cartagena",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "cantidadPasajeros": 2,
    "pasajeros": [
      {
        "nombre": "María Fernanda Rojas Díaz",
        "edad": 32,
        "valor": 1575000
      },
      {
        "nombre": "Andrés Felipe Rojas",
        "edad": 33,
        "valor": 1575000
      }
    ],
    "detalle": [],
    "valorPorPasajero": 1575000,
    "totalCotizacion": 3150000,
    "fechaEmision": "2026-10-21T09:40:00-05:00",
    "vigenteHasta": "2026-10-21T23:59:59-05:00",
    "estado": "vencida"
  },
  "message": "La cotización está vencida"
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
  "success": true,
  "data": {
    "cotizacionId": "COT-00046",
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
  "message": "Cotización consultada exitosamente"
}

````

- [x] Si la cotización ya venció, el backend retorna el estado actualizado:

```json
{
  "success": true,
  "data": {
    "cotizacionId": "COT-00031",
    "clienteId": "CLI-00188",
    "destino": "Cartagena",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "cantidadPasajeros": 2,
    "pasajeros": [
      {
        "nombre": "María Fernanda Rojas Díaz",
        "edad": 32,
        "valor": 1575000
      },
      {
        "nombre": "Andrés Felipe Rojas",
        "edad": 33,
        "valor": 1575000
      }
    ],
    "detalle": [],
    "valorPorPasajero": 1575000,
    "totalCotizacion": 3150000,
    "fechaEmision": "2026-10-21T09:40:00-05:00",
    "vigenteHasta": "2026-10-21T23:59:59-05:00",
    "estado": "vencida"
  },
  "message": "La cotización está vencida"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y el repositorio contiene su cotización COT-00046, emitida y vigente.
- **Acción:** Ejecutar el endpoint GET /api/v1/cotizaciones/COT-00046 con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.cotizacionId = "COT-00046" y data.estado = "emitida"
  - Campo message contiene el texto: "Cotización consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** El repositorio contiene la cotización COT-00031 de la cliente CLI-00188, emitida el 2026-10-21 y con vigencia hasta las 23:59:59 de ese día.
- **Acción:** Ejecutar el endpoint GET /api/v1/cotizaciones/COT-00031 con el token de la cliente.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "vencida"
  - Campo message contiene el texto: "La cotización está vencida"

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

- [x] El endpoint devuelve la cotización con su detalle y estado.
- [x] El estado refleja la vencida cuando pasó su vigencia.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la consulta por identificador y el cálculo de vencimiento.
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
