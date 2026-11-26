## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y revisé la cotización que recibí,
Para decidir si sigo adelante con la compra o la descarto, sin depender de un asesor,
Que el sistema me permita aceptar o rechazar mi cotización mientras esté vigente.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/cotizaciones/{cotizacionId}/respuesta de `cotizaciones.api` con el método POST.
- La capa API valida el token de acceso del cliente y el formato del JSON, y delega el caso de uso a `ResponderCotizacionService`.
- El servicio verifica que la cotización pertenezca al cliente del token, y el dominio valida que esté emitida y vigente (RN-26, RN-28); si ya pasó vigenteHasta, se informa como vencida.
- Si el cliente rechaza, el motivo es obligatorio (RN-30).
- Se reciben o consultan los campos:
- cotizacionId / Identificador de la cotización (parámetro de ruta)
- respuesta / `aceptada` o `rechazada`
- motivo / Motivo del rechazo (obligatorio si rechaza)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON los campos respuesta y motivo.
- [x] Solo se responde una cotización en estado `emitida`; si ya fue aceptada o rechazada, se responde 400 con el mensaje "La cotización ya fue respondida".
- [x] Una cotización vencida, también cuando ya pasó vigenteHasta (RN-28), no puede responderse; se responde 400 con el mensaje "La cotización está vencida y no puede responderse".
- [x] Si la respuesta es `rechazada`, el motivo es obligatorio (RN-30); sin motivo se responde 400 con el mensaje "El motivo del rechazo es obligatorio".
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo responde sus propias cotizaciones; si la cotización pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Los errores de formato del JSON se responden con código 400 y la estructura success, data y message. Mensajes exactos: sin respuesta, "La respuesta es obligatoria"; respuesta distinta de aceptada o rechazada, "La respuesta debe ser aceptada o rechazada".
- [x] Si la cotización no existe, se responde 404 con el mensaje "La cotización no existe".
- [x] Después de responder, la consulta de la cotización (HU-009) muestra el nuevo estado: `aceptada` o `rechazada`.


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaRespuesta corresponde a la fecha y hora en que el cliente responde la cotización):

```json
{
  "success": true,
  "data": {
    "cotizacionId": "COT-00047",
    "respuesta": "aceptada",
    "motivo": null,
    "estado": "aceptada",
    "fechaRespuesta": "2026-11-11T10:20:00-05:00"
  },
  "message": "Respuesta registrada exitosamente"
}
```

- [x] Si la cotización está vencida, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La cotización está vencida y no puede responderse"
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
  "success": true,
  "data": {
    "cotizacionId": "COT-00047",
    "respuesta": "aceptada",
    "motivo": null,
    "estado": "aceptada",
    "fechaRespuesta": "2026-11-11T10:20:00-05:00"
  },
  "message": "Respuesta registrada exitosamente"
}

````

- [x] Si la cotización está vencida, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La cotización está vencida y no puede responderse"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y generó con HU-008 la cotización COT-00047, emitida y vigente.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones/COT-00047/respuesta con respuesta "aceptada".
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.cotizacionId = "COT-00047" y data.estado = "aceptada"
  - Campo message contiene el texto: "Respuesta registrada exitosamente"

### ✅ Caso 2:

- **Precondición:** La cotización precargada COT-00046 de la cliente CLI-00188 está emitida y vigente.
- **Acción:** Ejecutar el endpoint POST /api/v1/cotizaciones/COT-00046/respuesta con respuesta "rechazada" y motivo "Presupuesto fuera de mi alcance".
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "rechazada" y data.motivo contiene el motivo enviado
  - Campo message contiene el texto: "Respuesta registrada exitosamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "cotizacionId" (texto)
    - "respuesta" (texto)
    - "motivo" (texto, o null si la cotización se acepta)
    - "estado" (texto)
    - "fechaRespuesta" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** La cotización COT-00031 está vencida, o el cliente rechaza sin motivo.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - El estado de la cotización no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La cotización está vencida y no puede responderse" o "El motivo del rechazo es obligatorio", según el caso

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

- [x] El endpoint registra la aceptación o el rechazo de la cotización.
- [x] No se responde una cotización vencida ni se acepta un rechazo sin motivo.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la vigencia, el estado y el motivo de rechazo.
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
