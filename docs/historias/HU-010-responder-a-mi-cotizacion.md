## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y revisé la cotización que recibí,
Para decidir si sigo adelante con la compra o la descarto, sin depender de un asesor,
Que el sistema me permita aceptar o rechazar mi cotización mientras esté vigente.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/cotizaciones/{cotizacionId}/respuesta de `cotizaciones.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `ResponderCotizacionService`.
- El dominio valida que la cotización esté emitida y vigente (RN-26, RN-28).
- Si el cliente rechaza, el motivo es obligatorio (RN-30).
- Se reciben o consultan los campos:
- cotizacionId / Identificador de la cotización (parámetro de ruta)
- respuesta / `aceptada` o `rechazada`
- motivo / Motivo del rechazo (obligatorio si rechaza)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON los campos respuesta y motivo.
- [ ] Solo se responde una cotización en estado `emitida`.
- [ ] Una cotización vencida no puede aceptarse (RN-28).
- [ ] Si la respuesta es `rechazada`, el motivo es obligatorio (RN-30).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Respuesta registrada exitosamente",
  "data": {
    "cotizacionId": "COT-00045",
    "respuesta": "aceptada",
    "motivo": null,
    "estado": "aceptada",
    "fechaRespuesta": "2026-11-05T11:02:00-05:00"
  },
  "success": true
}
```

- [ ] Si la cotización está vencida, el backend retorna:

```json
{
  "message": "La cotización está vencida y no puede aceptarse",
  "data": null,
  "success": false
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Responder a mi cotización

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/cotizaciones/{cotizacionId}/respuesta`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "message": "Respuesta registrada exitosamente",
  "data": {
    "cotizacionId": "COT-00045",
    "respuesta": "aceptada",
    "motivo": null,
    "estado": "aceptada",
    "fechaRespuesta": "2026-11-05T11:02:00-05:00"
  },
  "success": true
}

````

- [ ] Si la cotización está vencida, el backend retorna:

```json
{
  "message": "La cotización está vencida y no puede aceptarse",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cotización COT-00045 está emitida y vigente.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones/COT-00045/respuesta con respuesta "aceptada".
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "aceptada"
  - Campo message contiene el texto: "Respuesta registrada exitosamente"

### ✅ Caso 2:

- **Precondición:** La cotización COT-00046 está emitida y vigente.
- **Acción:** Ejecutar el endpoint con respuesta "rechazada" y motivo "Presupuesto fuera de mi alcance".
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "rechazada" y data.motivo contiene el motivo enviado

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "cotizacionId" (texto)
  - "respuesta" (texto)
  - "motivo" (texto)
  - "estado" (texto)
  - "fechaRespuesta" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

### ❌ Caso 4: 

- **Precondición:** La cotización COT-00031 está vencida, o el cliente rechaza sin motivo.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - El estado de la cotización no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La cotización está vencida y no puede aceptarse" o "El motivo del rechazo es obligatorio", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible registrar la respuesta"

## ✅ Definición de Hecho

# Historia: Responder a mi cotización

## 📦 Alcance Funcional

- [ ] El endpoint registra la aceptación o el rechazo de la cotización.
- [ ] No se acepta una cotización vencida ni un rechazo sin motivo.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la vigencia, el estado y el motivo de rechazo.
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
