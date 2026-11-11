## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y cambié de teléfono o de correo,
Para que la agencia me contacte por el medio correcto y mis datos estén actualizados, como es mi derecho,
Que el sistema me permita actualizar mi teléfono y mi correo desde el portal.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/clientes/me de `clientes.api` con el método PATCH.
- La capa API valida el formato del JSON y delega el caso de uso a `ActualizarContactoService`.
- El servicio identifica al cliente por su token de acceso.
- El dominio valida el formato de los datos y que quede al menos un dato de contacto (RN-04).
- Solo se actualizan teléfono y correo; documento, nombre y nacionalidad no se modifican desde el portal.
- Se reciben o consultan los campos:
- telefono / Nuevo teléfono de contacto
- correo / Nuevo correo electrónico


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint PATCH en /api/v1/clientes/me que recibe en el cuerpo JSON telefono y/o correo.
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] Solo se modifican los campos enviados; documento, nombre, nacionalidad y tipoCliente no se modifican.
- [ ] Debe quedar al menos un dato de contacto informado (RN-04) y el correo no puede pertenecer a otro cliente.
- [ ] Se garantiza el derecho del titular a actualizar sus datos (Ley 1581 de 2012).
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Datos de contacto actualizados exitosamente",
  "data": {
    "clienteId": "CLI-00188",
    "telefono": "+573109876543",
    "correo": "mfrojas@correo.com",
    "fechaActualizacion": "2026-11-07T10:00:00-05:00"
  },
  "success": true
}
```

- [ ] Si el correo ya pertenece a otro cliente, el backend retorna:

```json
{
  "message": "El correo ya está registrado por otro cliente",
  "data": null,
  "success": false
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
  "message": "Datos de contacto actualizados exitosamente",
  "data": {
    "clienteId": "CLI-00188",
    "telefono": "+573109876543",
    "correo": "mfrojas@correo.com",
    "fechaActualizacion": "2026-11-07T10:00:00-05:00"
  },
  "success": true
}

````

- [ ] Si el correo ya pertenece a otro cliente, el backend retorna:

```json
{
  "message": "El correo ya está registrado por otro cliente",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 tiene un token vigente.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/clientes/me con un nuevo teléfono.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.telefono contiene el nuevo teléfono y el correo no cambia
  - Campo message contiene el texto: "Datos de contacto actualizados exitosamente"

### ✅ Caso 2:

- **Precondición:** El correo nuevo ya está registrado por el cliente CLI-00190.
- **Acción:** Ejecutar el endpoint con ese correo.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - Los datos no cambian
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "El correo ya está registrado por otro cliente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "clienteId" (texto)
  - "telefono" (texto)
  - "correo" (texto)
  - "fechaActualizacion" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint actualiza el teléfono y el correo del cliente autenticado.
- [ ] No se modifican datos de identidad ni se permite un correo de otro cliente.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar los campos modificables, el formato del correo y la duplicidad.
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
