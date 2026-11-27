## 📖 Historia de Usuario

Dado que soy asesor comercial de One Click Caribe y un cliente registró una consulta posventa,
Para resolver la duda del cliente y dejar constancia de la atención,
Que el sistema me permita registrar la respuesta a la consulta y cerrarla cuando quede resuelta.

## 🔁 Flujo Esperado

- El asesor comercial diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/posventa/consultas/{consultaId} de `posventa.api` con el método PATCH.
- La capa API valida el token de acceso del asesor y el formato del JSON, y delega el caso de uso a `ResponderConsultaService`.
- El servicio verifica que la consulta exista, incluidas las registradas con HU-018 en la misma sesión.
- El dominio valida que la consulta no esté cerrada y que la respuesta esté informada.
- Si el asesor indica cerrar, la consulta pasa a `cerrada`; si no, queda `en_atencion`. La respuesta no modifica la venta (RN-81).
- Se reciben o consultan los campos:
- consultaId / Identificador de la consulta (parámetro de ruta)
- respuesta / Respuesta del asesor
- asesor / Nombre del asesor que responde
- cerrar / `true` para cerrar la consulta


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint PATCH que recibe en el cuerpo JSON respuesta, asesor y cerrar.
- [x] Solo se responde una consulta en estado `abierta` o `en_atencion`; si la consulta está cerrada, responde 400 con el mensaje "La consulta ya está cerrada".
- [x] Con cerrar = true la consulta queda `cerrada` y responde "Consulta cerrada exitosamente"; con cerrar = false queda `en_atencion` y responde "Respuesta registrada exitosamente". Se guardan la respuesta, el asesor y la fecha de la respuesta.
- [x] La respuesta y el asesor son obligatorios; si faltan o llegan vacíos, responde 400 con "La respuesta es obligatoria" o "El asesor es obligatorio", y si falta cerrar, con "El indicador cerrar es obligatorio".
- [x] Si la consulta no existe, se responde 404 con el mensaje "La consulta no existe".
- [x] La consulta registrada con HU-018 en la misma sesión se puede responder.
- [x] La respuesta no modifica la orden de venta (RN-81).
- [x] El endpoint exige un token con rol `asesor`; un token de otro rol (cliente o administradora) responde 403 con "No tiene permisos para realizar esta acción". Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message; por ejemplo, "El campo 'cerrar' debe ser verdadero o falso (true o false)" o "El campo 'respuesta' debe ser un texto".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (consulta precargada CON-00021 respondida y cerrada; fechaRespuesta corresponde a la fecha y hora en que el asesor registra la respuesta):

```json
{
  "success": true,
  "data": {
    "consultaId": "CON-00021",
    "estado": "cerrada",
    "respuesta": "Su tarifa incluye una maleta de 23 kg y un equipaje de mano.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-11T11:00:00-05:00"
  },
  "message": "Consulta cerrada exitosamente"
}
```

- [x] Si el asesor responde sin cerrar, el backend retorna (consulta precargada CON-00022):

```json
{
  "success": true,
  "data": {
    "consultaId": "CON-00022",
    "estado": "en_atencion",
    "respuesta": "Estamos validando su solicitud con la aerolínea.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-11T11:05:00-05:00"
  },
  "message": "Respuesta registrada exitosamente"
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
  "success": true,
  "data": {
    "consultaId": "CON-00021",
    "estado": "cerrada",
    "respuesta": "Su tarifa incluye una maleta de 23 kg y un equipaje de mano.",
    "asesor": "Tanner Cedeño",
    "fechaRespuesta": "2026-11-11T11:00:00-05:00"
  },
  "message": "Consulta cerrada exitosamente"
}

````

- [x] Si la consulta ya está cerrada (por ejemplo la consulta precargada CON-00019), el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La consulta ya está cerrada"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El asesor inició sesión con HU-002 (asesor@oneclickcaribe.com) y la consulta precargada CON-00021 está abierta.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/posventa/consultas/CON-00021 con su token, respuesta, asesor y cerrar = true.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "cerrada"
  - Campo message contiene el texto: "Consulta cerrada exitosamente"

### ✅ Caso 2:

- **Precondición:** La consulta precargada CON-00022 está abierta.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/posventa/consultas/CON-00022 con respuesta, asesor y cerrar = false.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.estado = "en_atencion"
  - Campo message contiene el texto: "Respuesta registrada exitosamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "consultaId" (texto)
    - "estado" (texto)
    - "respuesta" (texto)
    - "asesor" (texto)
    - "fechaRespuesta" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** La consulta precargada CON-00019 ya está cerrada, o se envía sin respuesta.
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

- [x] El endpoint registra la respuesta del asesor y cierra la consulta cuando corresponde.
- [x] No se responde una consulta ya cerrada.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el estado de la consulta y los campos obligatorios.
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
