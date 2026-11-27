## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya pagué mi orden en su totalidad,
Para tener los localizadores de cada servicio de mi viaje,
Que el sistema me muestre la reserva confirmada de mi orden con el localizador de cada servicio.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId}/reserva de `reservas.api` con el método GET.
- La capa API valida el token de acceso del cliente y delega el caso de uso a `ConsultarReservaService`.
- El servicio verifica que la orden exista, que pertenezca al cliente del token y que esté pagada (RN-45).
- El repositorio en memoria devuelve la reserva confirmada automáticamente cuando un pago aprobado dejó el saldo en cero (HU-013 o HU-014), con un localizador por servicio (RN-61, RN-62).
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [x] La reserva solo existe para órdenes pagadas en su totalidad (RN-61); si la orden aún no está pagada, responde 409 con el mensaje "La reserva se confirma cuando la orden esté pagada en su totalidad".
- [x] Cada servicio tiene su tipo, la razón social del proveedor y un localizador único (RN-62).
- [x] La reserva confirmada al pagar una orden con HU-013 o HU-014 se puede consultar en la misma sesión.
- [x] Si la orden no existe, se responde 404 con el mensaje "La orden de venta no existe".
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo consulta las reservas de sus propias órdenes; si la orden pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (reserva precargada RES-00008 de la orden VEN-00010):

```json
{
  "success": true,
  "data": {
    "reservaId": "RES-00008",
    "ventaId": "VEN-00010",
    "estado": "confirmada",
    "segmentos": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "localizador": "AV7KQ2"
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "localizador": "PT-558201"
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "localizador": "PT-558202"
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "localizador": "AS1-90321"
      }
    ],
    "fechaConfirmacion": "2026-11-02T10:00:05-05:00"
  },
  "message": "Reserva consultada exitosamente"
}
```

- [x] Si la orden aún no está pagada, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La reserva se confirma cuando la orden esté pagada en su totalidad"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar mi reserva confirmada

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/ventas/{ventaId}/reserva`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "reservaId": "RES-00008",
    "ventaId": "VEN-00010",
    "estado": "confirmada",
    "segmentos": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "localizador": "AV7KQ2"
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "localizador": "PT-558201"
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "localizador": "PT-558202"
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "localizador": "AS1-90321"
      }
    ],
    "fechaConfirmacion": "2026-11-02T10:00:05-05:00"
  },
  "message": "Reserva consultada exitosamente"
}

````

- [x] Si la reserva se confirma en la misma sesión al pagar la orden VEN-00014 con HU-013, el backend retorna (fechaConfirmacion corresponde a la fecha y hora del pago que dejó el saldo en cero; RES-00009 es el primer identificador libre y cada localizador lleva las tres primeras letras del proveedor, el número de la reserva y la posición del servicio):

```json
{
  "success": true,
  "data": {
    "reservaId": "RES-00009",
    "ventaId": "VEN-00014",
    "estado": "confirmada",
    "segmentos": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "localizador": "AVI-00009-1"
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "localizador": "PRI-00009-2"
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "localizador": "PRI-00009-3"
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "localizador": "ASS-00009-4"
      }
    ],
    "fechaConfirmacion": "2026-11-11T10:45:00-05:00"
  },
  "message": "Reserva consultada exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y su orden precargada VEN-00010 está pagada, con la reserva RES-00008 confirmada.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00010/reserva con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.segmentos contiene un localizador por servicio
  - Campo message contiene el texto: "Reserva consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden precargada VEN-00013 tiene saldo pendiente.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00013/reserva.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La reserva se confirma cuando la orden esté pagada en su totalidad"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "reservaId" (texto)
    - "ventaId" (texto)
    - "estado" (texto)
    - "segmentos" (lista), donde cada servicio tiene:
      - "tipoServicio" (texto)
      - "proveedor" (texto)
      - "localizador" (texto)
    - "fechaConfirmacion" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El repositorio no contiene la orden VEN-09999.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-09999/reserva.
- **Resultado esperado:**

  - Código HTTP 404 Not Found
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La orden de venta no existe"

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible consultar la reserva"

## ✅ Definición de Hecho

# Historia: Consultar mi reserva confirmada

## 📦 Alcance Funcional

- [x] El endpoint devuelve la reserva confirmada con sus localizadores.
- [x] No se muestra reserva para órdenes con saldo pendiente.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el estado de pago de la orden y los localizadores.
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
