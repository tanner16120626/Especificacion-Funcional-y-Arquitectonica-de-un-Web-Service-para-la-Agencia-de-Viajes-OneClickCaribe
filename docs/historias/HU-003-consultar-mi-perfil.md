## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya me registré en el sistema,
Para verificar que mis datos de contacto y nacionalidad son correctos antes de solicitar una cotización,
Que el sistema me muestre mis datos personales registrados, identificándome con mi token de acceso.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/clientes/me de `clientes.api` con el método GET.
- La capa API valida el formato del JSON y delega el caso de uso a `ConsultarClienteService`.
- El servicio obtiene el clienteId del token de acceso, no de la URL, de modo que nadie puede consultar los datos de otro cliente.
- El repositorio en memoria devuelve los datos registrados del cliente, sin la contraseña.
- Se reciben o consultan los campos:
- Authorization / Token de acceso del cliente (encabezado)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint GET en /api/v1/clientes/me que identifica al cliente por su token de acceso.
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] Se devuelven los datos registrados del cliente; la contraseña nunca se incluye.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Cliente consultado exitosamente",
  "data": {
    "clienteId": "CLI-00188",
    "documento": "1098765432",
    "nombre": "María Fernanda Rojas Díaz",
    "telefono": "+573001234567",
    "correo": "mfrojas@correo.com",
    "nacionalidad": "CO",
    "tipoCliente": "pareja",
    "fechaRegistro": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}
```

- [ ] Si el token está vencido, el backend retorna:

```json
{
  "message": "La sesión expiró. Inicie sesión nuevamente",
  "data": null,
  "success": false
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar mi perfil

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/clientes/me`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "message": "Cliente consultado exitosamente",
  "data": {
    "clienteId": "CLI-00188",
    "documento": "1098765432",
    "nombre": "María Fernanda Rojas Díaz",
    "telefono": "+573001234567",
    "correo": "mfrojas@correo.com",
    "nacionalidad": "CO",
    "tipoCliente": "pareja",
    "fechaRegistro": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}

````

- [ ] Si el token está vencido, el backend retorna:

```json
{
  "message": "La sesión expiró. Inicie sesión nuevamente",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 inició sesión y tiene un token vigente.
- **Acción:** Ejecutar el endpoint GET /api/v1/clientes/me con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data contiene los datos del cliente CLI-00188, sin contraseña
  - Campo message contiene el texto: "Cliente consultado exitosamente"

### ✅ Caso 2:

- **Precondición:** El token del cliente superó su vigencia.
- **Acción:** Ejecutar el endpoint GET /api/v1/clientes/me con el token vencido.
- **Resultado esperado:**

  - Código HTTP 401 Unauthorized
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La sesión expiró. Inicie sesión nuevamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "clienteId" (texto)
  - "documento" (texto)
  - "nombre" (texto)
  - "telefono" (texto)
  - "correo" (texto)
  - "nacionalidad" (texto)
  - "tipoCliente" (texto)
  - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

### ❌ Caso 4: 

- **Precondición:** La solicitud no incluye token, o el token fue alterado.
- **Acción:** Ejecutar el endpoint GET /api/v1/clientes/me sin token y con un token modificado.
- **Resultado esperado:**

  - Código HTTP 401 Unauthorized
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "Token de acceso inválido o ausente"

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible consultar el cliente"

## ✅ Definición de Hecho

# Historia: Consultar mi perfil

## 📦 Alcance Funcional

- [ ] El endpoint devuelve los datos del cliente autenticado.
- [ ] Ningún cliente puede consultar los datos de otro.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la identificación por token, el token vencido y el token inválido.
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
