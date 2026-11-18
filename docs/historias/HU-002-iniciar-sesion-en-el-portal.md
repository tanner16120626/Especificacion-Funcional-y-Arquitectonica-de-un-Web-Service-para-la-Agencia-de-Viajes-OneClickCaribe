## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya estoy registrado en el portal,
Para acceder de forma segura a mis cotizaciones, compras y datos personales, y que nadie más pueda verlos,
Que el sistema valide mi correo y mi contraseña y me entregue un token de acceso con vigencia limitada.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/auth/login de `clientes.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `IniciarSesionService`.
- El repositorio en memoria busca la cuenta por correo y el servicio compara la contraseña con su versión cifrada.
- Si las credenciales son correctas, se genera un token JWT firmado con SECRET_KEY y con la vigencia definida en ACCESS_TOKEN_EXPIRE_MINUTES.
- El token incluye el identificador y el rol de la cuenta (`cliente`, `administradora` o `asesor`); con él se controla el acceso a los demás endpoints.
- Se reciben o consultan los campos:
- correo / Correo registrado
- contrasena / Contraseña


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON correo y contrasena.
- [x] Si las credenciales son correctas se devuelve un token de acceso firmado, su tipo (`bearer`), su vigencia en minutos y el rol de la cuenta.
- [x] Si el correo no existe o la contraseña no coincide se responde 401 con el mismo mensaje, sin indicar cuál de los dos falló.
- [x] La vigencia del token se toma de ACCESS_TOKEN_EXPIRE_MINUTES y la firma de SECRET_KEY, definidos en el archivo .env.
- [x] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message. Mensajes exactos: sin correo, "El campo 'correo' es obligatorio"; contrasena enviada como número, "El campo 'contrasena' debe ser un texto".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (el valor de accessToken se genera en cada inicio de sesión):

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tipoToken": "bearer",
    "expiraEnMinutos": 30,
    "rol": "cliente",
    "clienteId": "CLI-00188"
  },
  "message": "Inicio de sesión exitoso"
}
```

- [x] Si las credenciales no son válidas, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "Correo o contraseña incorrectos"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Iniciar sesión en el portal

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/auth/login`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tipoToken": "bearer",
    "expiraEnMinutos": 30,
    "rol": "cliente",
    "clienteId": "CLI-00188"
  },
  "message": "Inicio de sesión exitoso"
}

````

- [x] Si las credenciales no son válidas, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "Correo o contraseña incorrectos"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El cliente CLI-00188 está registrado con el correo mfrojas@correo.com (registrado previamente con HU-001).
- **Acción:** Ejecutar el endpoint POST /api/v1/auth/login con ese correo y su contraseña.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.accessToken contiene el token y data.expiraEnMinutos = 30
  - Campo message contiene el texto: "Inicio de sesión exitoso"

### ✅ Caso 2:

- **Precondición:** La administradora tiene una cuenta con rol administradora.
- **Acción:** Ejecutar el endpoint con sus credenciales.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.rol = "administradora"
  - Campo data.clienteId = null, porque la cuenta no corresponde a un cliente

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "accessToken" (texto)
    - "tipoToken" (texto)
    - "expiraEnMinutos" (número)
    - "rol" (texto)
    - "clienteId" (texto, o null en cuentas que no son de cliente)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** Se envía una contraseña incorrecta, o un correo no registrado.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 401 Unauthorized
  - No se genera token
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "Correo o contraseña incorrectos" en ambos casos

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible iniciar sesión"

## ✅ Definición de Hecho

# Historia: Iniciar sesión en el portal

## 📦 Alcance Funcional

- [x] El endpoint autentica al usuario y entrega un token firmado con vigencia limitada.
- [x] Las credenciales inválidas se rechazan sin revelar qué dato falló.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la validación de credenciales, la firma y la vigencia del token.
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
