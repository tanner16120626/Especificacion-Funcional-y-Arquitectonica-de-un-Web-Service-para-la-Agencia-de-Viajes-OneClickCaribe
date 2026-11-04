## 📖 Historia de Usuario

Dado que soy asesor comercial de One Click Caribe y un cliente registró una consulta posventa,
Para resolver la duda del cliente y dejar constancia de la atención,
Que el sistema me permita registrar la respuesta a la consulta y cerrarla cuando quede resuelta.

## 🔁 Flujo Esperado

- El asesor comercial diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/posventa/consultas/{consultaId} de `posventa.api` con el método PATCH.
- La capa API valida el formato del JSON y delega el caso de uso a `ResponderConsultaService`.
- El dominio valida que la consulta no esté cerrada y que la respuesta esté informada.
- Si el asesor indica cerrar, la consulta pasa a `cerrada`; si no, queda `en_atencion`. La respuesta no modifica la venta (RN-81).
- Se reciben o consultan los campos:
- consultaId / Identificador de la consulta (parámetro de ruta)
- respuesta / Respuesta del asesor
- asesor / Nombre del asesor que responde
- cerrar / `true` para cerrar la consulta


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint PATCH que recibe en el cuerpo JSON respuesta, asesor y cerrar.
- [ ] Solo se responde una consulta en estado `abierta` o `en_atencion`.
- [ ] La respuesta y el asesor son obligatorios.
- [ ] La respuesta no modifica la orden de venta (RN-81).
- [ ] El endpoint exige un token con rol `asesor`; un token de otro rol responde 403 y la ausencia de token, 401.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Consulta cerrada exitosamente",
  "data": {
    "consultaId": "CON-00021",
    "estado": "cerrada",
    "respuesta": "Su tarifa incluye una maleta de 23 kg y un equipaje de mano.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-06T09:10:00-05:00"
  },
  "success": true
}
```

- [ ] Si el asesor responde sin cerrar, el backend retorna:

```json
{
  "message": "Respuesta registrada exitosamente",
  "data": {
    "consultaId": "CON-00022",
    "estado": "en_atencion",
    "respuesta": "Estamos validando su solicitud con la aerolínea.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-06T09:15:00-05:00"
  },
  "success": true
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Responder y cerrar una consulta posventa

- **Método HTTP:** `PATCH`
- **Ruta:** `/api/v1/posventa/consultas/{consultaId}`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "message": "Consulta cerrada exitosamente",
  "data": {
    "consultaId": "CON-00021",
    "estado": "cerrada",
    "respuesta": "Su tarifa incluye una maleta de 23 kg y un equipaje de mano.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-06T09:10:00-05:00"
  },
  "success": true
}

````

- [ ] Si el asesor responde sin cerrar, el backend retorna:

```json
{
  "message": "Respuesta registrada exitosamente",
  "data": {
    "consultaId": "CON-00022",
    "estado": "en_atencion",
    "respuesta": "Estamos validando su solicitud con la aerolínea.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-06T09:15:00-05:00"
  },
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La consulta CON-00021 está abierta.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/posventa/consultas/CON-00021 con respuesta, asesor y cerrar = true.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "cerrada"
  - Campo message contiene el texto: "Consulta cerrada exitosamente"

### ✅ Caso 2:

- **Precondición:** La consulta CON-00022 está abierta.
- **Acción:** Ejecutar el endpoint con respuesta, asesor y cerrar = false.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.estado = "en_atencion"
  - Campo message contiene el texto: "Respuesta registrada exitosamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "consultaId" (texto)
  - "estado" (texto)
  - "respuesta" (texto)
  - "asesor" (texto)
  - "fechaRespuesta" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

### ❌ Caso 4: 

- **Precondición:** La consulta CON-00019 ya está cerrada, o se envía sin respuesta.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - La consulta no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La consulta ya está cerrada" o "La respuesta es obligatoria", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible responder la consulta"

## ✅ Definición de Hecho

# Historia: Responder y cerrar una consulta posventa

## 📦 Alcance Funcional

- [ ] El endpoint registra la respuesta del asesor y cierra la consulta cuando corresponde.
- [ ] No se responde una consulta ya cerrada.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el estado de la consulta y los campos obligatorios.
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
