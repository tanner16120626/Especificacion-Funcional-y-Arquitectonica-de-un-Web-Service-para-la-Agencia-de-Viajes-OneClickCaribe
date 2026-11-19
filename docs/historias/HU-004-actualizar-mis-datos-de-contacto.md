## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y cambié de teléfono o de correo,
Para que la agencia me contacte por el medio correcto y mis datos estén actualizados, como es mi derecho,
Que el sistema me permita actualizar mi teléfono y mi correo desde el portal.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/clientes/me de `clientes.api` con el método PATCH.
- La capa API valida el token de acceso del encabezado Authorization y el formato del JSON, y delega el caso de uso a `ActualizarContactoService`.
- El servicio identifica al cliente por su token de acceso.
- El dominio valida el formato del correo y que quede al menos un dato de contacto (RN-04).
- Solo se actualizan teléfono y correo; documento, nombre y nacionalidad no se modifican desde el portal.
- Se reciben o consultan los campos:
- telefono / Nuevo teléfono de contacto
- correo / Nuevo correo electrónico


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint PATCH en /api/v1/clientes/me que recibe en el cuerpo JSON telefono y/o correo.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] Solo se modifican los campos enviados; documento, nombre, nacionalidad y tipoCliente no se modifican.
- [x] Debe quedar al menos un dato de contacto informado (RN-04) y el correo no puede pertenecer a otro cliente.
- [x] Se garantiza el derecho del titular a actualizar sus datos (Ley 1581 de 2012).
- [x] Los errores de formato del JSON se responden con código 400 y la estructura success, data y message. Mensajes exactos: sin telefono ni correo, "Debe enviar el teléfono o el correo a actualizar"; telefono enviado como número, "El campo 'telefono' debe ser un texto".
- [x] Solo las cuentas con rol cliente actualizan sus datos de contacto; las demás cuentas reciben 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Si el cliente del token no se encuentra en el repositorio, se responde 404 con el mensaje "El cliente no se encuentra registrado".
- [x] Si se actualiza el correo, el inicio de sesión (HU-002) se realiza con el correo nuevo.
- [x] El correo no puede quedar vacío porque es el usuario de acceso; si se envía vacío se responde 400 con el mensaje "El correo no puede quedar vacío porque es su usuario de acceso".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaActualizacion corresponde a la fecha y hora de la actualización):

```json
{
  "success": true,
  "data": {
    "clienteId": "CLI-00188",
    "telefono": "+573109876543",
    "correo": "mfrojas@correo.com",
    "fechaActualizacion": "2026-11-11T10:15:00-05:00"
  },
  "message": "Datos de contacto actualizados exitosamente"
}
```

- [x] Si el correo ya pertenece a otro cliente, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "El correo ya está registrado por otro cliente"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Actualizar mis datos de contacto

- **Método HTTP:** `PATCH`
- **Ruta:** `/api/v1/clientes/me`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "clienteId": "CLI-00188",
    "telefono": "+573109876543",
    "correo": "mfrojas@correo.com",
    "fechaActualizacion": "2026-11-11T10:15:00-05:00"
  },
  "message": "Datos de contacto actualizados exitosamente"
}

````

- [x] Si el correo ya pertenece a otro cliente, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "El correo ya está registrado por otro cliente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 (registrado con HU-001) inició sesión con HU-002 y tiene un token vigente.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/clientes/me con el teléfono +573109876543.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.telefono contiene el nuevo teléfono y el correo no cambia
  - Campo message contiene el texto: "Datos de contacto actualizados exitosamente"

### ✅ Caso 2:

- **Precondición:** El correo nuevo, lagomez@correo.com, ya está registrado por el cliente CLI-00190.
- **Acción:** Ejecutar el endpoint con ese correo.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - Los datos no cambian
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "El correo ya está registrado por otro cliente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "clienteId" (texto)
    - "telefono" (texto, o null si se dejó vacío)
    - "correo" (texto)
    - "fechaActualizacion" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El cliente envía un correo con formato inválido, o deja vacíos teléfono y correo.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - Los datos no cambian
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "El correo no tiene un formato válido" o "Debe conservar al menos un dato de contacto", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible actualizar los datos de contacto"

## ✅ Definición de Hecho

# Historia: Actualizar mis datos de contacto

## 📦 Alcance Funcional

- [x] El endpoint actualiza el teléfono y el correo del cliente autenticado.
- [x] No se modifican datos de identidad ni se permite un correo de otro cliente.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar los campos modificables, el formato del correo y la duplicidad.
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
