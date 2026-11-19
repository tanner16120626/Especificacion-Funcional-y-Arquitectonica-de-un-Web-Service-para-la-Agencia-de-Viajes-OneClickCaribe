## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya me registré en el sistema,
Para verificar que mis datos de contacto y nacionalidad son correctos antes de solicitar una cotización,
Que el sistema me muestre mis datos personales registrados, identificándome con mi token de acceso.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/clientes/me de `clientes.api` con el método GET.
- La capa API valida el token de acceso del encabezado Authorization y delega el caso de uso a `ConsultarClienteService`.
- El servicio obtiene el clienteId del token de acceso, no de la URL, de modo que nadie puede consultar los datos de otro cliente.
- El repositorio en memoria devuelve los datos registrados del cliente, sin la contraseña.
- Se reciben o consultan los campos:
- Authorization / Token de acceso del cliente (encabezado)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET en /api/v1/clientes/me que identifica al cliente por su token de acceso.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] Se devuelven los datos registrados del cliente; la contraseña nunca se incluye.
- [x] Solo las cuentas con rol cliente consultan su perfil; las demás cuentas reciben 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Si el cliente del token no se encuentra en el repositorio, se responde 404 con el mensaje "El cliente no se encuentra registrado".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaRegistro corresponde a la fecha y hora en que el cliente se registró):

```json
{
  "success": true,
  "data": {
    "clienteId": "CLI-00188",
    "documento": "1098765432",
    "nombre": "María Fernanda Rojas Díaz",
    "telefono": "+573001234567",
    "correo": "mfrojas@correo.com",
    "nacionalidad": "CO",
    "tipoCliente": "pareja",
    "fechaRegistro": "2026-11-11T10:15:00-05:00"
  },
  "message": "Cliente consultado exitosamente"
}
```

- [x] Si el token está vencido, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La sesión expiró. Inicie sesión nuevamente"
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
  "success": true,
  "data": {
    "clienteId": "CLI-00188",
    "documento": "1098765432",
    "nombre": "María Fernanda Rojas Díaz",
    "telefono": "+573001234567",
    "correo": "mfrojas@correo.com",
    "nacionalidad": "CO",
    "tipoCliente": "pareja",
    "fechaRegistro": "2026-11-11T10:15:00-05:00"
  },
  "message": "Cliente consultado exitosamente"
}

````

- [x] Si el token está vencido, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La sesión expiró. Inicie sesión nuevamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 (registrado con HU-001) inició sesión con HU-002 y tiene un token vigente.
- **Acción:** Ejecutar el endpoint GET /api/v1/clientes/me con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data contiene los datos del cliente CLI-00188, sin contraseña
  - Campo message contiene el texto: "Cliente consultado exitosamente"

### ✅ Caso 2:

- **Precondición:** El token del cliente superó su vigencia (para la prueba, ACCESS_TOKEN_EXPIRE_MINUTES se configura en 1 en el archivo .env).
- **Acción:** Ejecutar el endpoint GET /api/v1/clientes/me con el token vencido.
- **Resultado esperado:**

  - Código HTTP 401 Unauthorized
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La sesión expiró. Inicie sesión nuevamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "clienteId" (texto)
    - "documento" (texto)
    - "nombre" (texto)
    - "telefono" (texto)
    - "correo" (texto)
    - "nacionalidad" (texto)
    - "tipoCliente" (texto)
    - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)

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

- [x] El endpoint devuelve los datos del cliente autenticado.
- [x] Ningún cliente puede consultar los datos de otro.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la identificación por token, el token vencido y el token inválido.
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
