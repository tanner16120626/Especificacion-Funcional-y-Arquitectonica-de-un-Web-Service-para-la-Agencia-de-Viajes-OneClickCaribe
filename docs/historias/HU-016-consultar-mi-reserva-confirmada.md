## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya pagué mi orden en su totalidad,
Para tener los localizadores de cada servicio de mi viaje,
Que el sistema me muestre la reserva confirmada de mi orden con el localizador de cada servicio.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId}/reserva de `reservas.api` con el método GET.
- La capa API valida el formato del JSON y delega el caso de uso a `ConsultarReservaService`.
- El servicio verifica que la orden exista y esté pagada (RN-45).
- El repositorio en memoria devuelve la reserva confirmada automáticamente cuando un pago aprobado dejó el saldo en cero, con un localizador por servicio (RN-61, RN-62).
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [ ] La reserva solo existe para órdenes pagadas en su totalidad (RN-61).
- [ ] Cada servicio tiene un localizador único (RN-62).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Reserva consultada exitosamente",
  "data": {
    "reservaId": "RES-00008",
    "ventaId": "VEN-00010",
    "estado": "confirmada",
    "segmentos": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca",
        "localizador": "AV7KQ2"
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel",
        "localizador": "PT-558201"
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel",
        "localizador": "PT-558202"
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1",
        "localizador": "AS1-90321"
      }
    ],
    "fechaConfirmacion": "2026-11-05T11:30:00-05:00"
  },
  "success": true
}
```

- [ ] Si la orden aún no está pagada, el backend retorna:

```json
{
  "message": "La reserva se confirma cuando la orden esté pagada en su totalidad",
  "data": null,
  "success": false
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
  "message": "Reserva consultada exitosamente",
  "data": {
    "reservaId": "RES-00008",
    "ventaId": "VEN-00010",
    "estado": "confirmada",
    "segmentos": [
      {
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca",
        "localizador": "AV7KQ2"
      },
      {
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel",
        "localizador": "PT-558201"
      },
      {
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel",
        "localizador": "PT-558202"
      },
      {
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1",
        "localizador": "AS1-90321"
      }
    ],
    "fechaConfirmacion": "2026-11-05T11:30:00-05:00"
  },
  "success": true
}

````

- [ ] Si la orden aún no está pagada, el backend retorna:

```json
{
  "message": "La reserva se confirma cuando la orden esté pagada en su totalidad",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La orden VEN-00010 está pagada y su reserva fue confirmada.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00010/reserva.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.segmentos contiene un localizador por servicio
  - Campo message contiene el texto: "Reserva consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden VEN-00012 tiene saldo pendiente.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00012/reserva.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La reserva se confirma cuando la orden esté pagada en su totalidad"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "reservaId" (texto)
  - "ventaId" (texto)
  - "estado" (texto)
  - "segmentos" (lista)
  - "fechaConfirmacion" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint devuelve la reserva confirmada con sus localizadores.
- [ ] No se muestra reserva para órdenes con saldo pendiente.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el estado de pago de la orden y los localizadores.
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
