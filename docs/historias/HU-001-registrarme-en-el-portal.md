## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y quiero solicitar un viaje sin depender de una llamada o un mensaje,
Para quedar registrado una sola vez y que mis cotizaciones, compras y consultas queden asociadas a mí,
Que el sistema me permita registrarme con mis datos personales, una contraseña y mi autorización para el tratamiento de datos.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/clientes de `clientes.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso al método `registrar` de `ClienteService`.
- El dominio valida que el cliente sea persona natural (RN-01) y que la nacionalidad y al menos un dato de contacto estén informados (RN-04).
- Se exige la autorización expresa del tratamiento de datos personales (Ley 1581 de 2012); sin ella, el registro se rechaza.
- El servicio verifica en el repositorio en memoria que el documento no esté registrado (RN-05), cifra la contraseña y guarda el cliente y su cuenta de acceso.
- Se reciben o consultan los campos:
- documento / Documento de identidad
- nombre / Nombre completo
- telefono / Teléfono de contacto
- correo / Correo electrónico
- nacionalidad / Nacionalidad (código ISO de 2 letras)
- tipoCliente / Tipo de cliente (`individual`, `pareja` o `grupo_familiar`)
- contrasena / Contraseña de acceso al portal (mínimo 8 caracteres)
- aceptaTratamientoDatos / Autorización del tratamiento de datos personales (`true`)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON documento, nombre, telefono, correo, nacionalidad, tipoCliente, contrasena y aceptaTratamientoDatos.
- [x] Se valida que documento, nombre, nacionalidad y tipoCliente estén informados, y que exista al menos uno entre telefono y correo (RN-04).
- [x] Se valida que la nacionalidad sea un código ISO de 2 letras.
- [x] Se valida que tipoCliente sea `individual`, `pareja` o `grupo_familiar`; el valor `corporativo` se rechaza (RN-01).
- [x] aceptaTratamientoDatos debe ser `true`; se registran la fecha de la autorización y la versión de la política de tratamiento de datos (Ley 1581 de 2012).
- [x] La contraseña tiene mínimo 8 caracteres, se almacena cifrada (hash) y nunca se devuelve en ninguna respuesta.
- [x] Se valida que el documento no tenga un registro previo (RN-05).
- [x] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (los campos fechaAutorizacion y fechaRegistro toman la fecha y hora en que se realiza el registro):

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
    "autorizacionDatos": {
      "aceptada": true,
      "versionPolitica": "1.0",
      "fechaAutorizacion": "2026-11-11T10:15:00-05:00"
    },
    "fechaRegistro": "2026-11-11T10:15:00-05:00"
  },
  "message": "Cliente registrado exitosamente"
}
```

- [x] Si el cliente ya existe, el backend retorna:

```json
{
  "success": false,
  "data": {
    "clienteId": "CLI-00188",
    "documento": "1098765432"
  },
  "message": "El cliente ya se encuentra registrado"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Registrarme en el portal

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/clientes`

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
    "autorizacionDatos": {
      "aceptada": true,
      "versionPolitica": "1.0",
      "fechaAutorizacion": "2026-11-11T10:15:00-05:00"
    },
    "fechaRegistro": "2026-11-11T10:15:00-05:00"
  },
  "message": "Cliente registrado exitosamente"
}

````

- [x] Si el cliente ya existe, el backend retorna:

```json
{
  "success": false,
  "data": {
    "clienteId": "CLI-00188",
    "documento": "1098765432"
  },
  "message": "El cliente ya se encuentra registrado"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El repositorio no contiene un cliente con el documento 1098765432.
- **Acción:** Ejecutar el endpoint POST /api/v1/clientes con los datos del cliente, una contraseña de 8 o más caracteres y aceptaTratamientoDatos = true.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.clienteId contiene el identificador asignado y la respuesta no incluye la contraseña
  - Campo message contiene el texto: "Cliente registrado exitosamente"

### ✅ Caso 2:

- **Precondición:** El repositorio ya contiene un cliente con el documento 1098765432.
- **Acción:** Ejecutar el endpoint POST /api/v1/clientes con el mismo documento.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - No se crea un nuevo registro
  - Campo success = false
  - Campo data.clienteId contiene el identificador del cliente existente
  - Campo message contiene el texto: "El cliente ya se encuentra registrado"

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
    - "autorizacionDatos" (objeto: "aceptada" booleano, "versionPolitica" texto, "fechaAutorizacion" fecha ISO 8601)
    - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El cliente envía datos que no cumplen las reglas del registro.
- **Acción:** Ejecutar el endpoint POST /api/v1/clientes con cada uno de los datos inválidos de la tabla.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - No se crea el registro
  - Campo success = false y campo data = null
  - Campo message contiene el texto correspondiente a cada caso:

| Dato inválido | Texto del campo message |
|---|---|
| aceptaTratamientoDatos = false | "Debe autorizar el tratamiento de sus datos personales" |
| Sin nacionalidad | "La nacionalidad del cliente es obligatoria" |
| tipoCliente = "corporativo" | "Solo se registran clientes persona natural" |
| Sin telefono ni correo | "Debe informar al menos un dato de contacto: teléfono o correo" |
| contrasena con menos de 8 caracteres | "La contraseña debe tener mínimo 8 caracteres" |
| documento enviado como número | "El campo 'documento' debe ser un texto" |
| Sin documento | "El documento es obligatorio" |
| Sin nombre | "El nombre es obligatorio" |
| Sin tipoCliente | "El tipo de cliente es obligatorio" |
| tipoCliente = "empresa" | "El tipo de cliente debe ser individual, pareja o grupo_familiar" |
| nacionalidad = "COL" | "La nacionalidad debe ser un código ISO de 2 letras" |

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible registrar el cliente"

## ✅ Definición de Hecho

# Historia: Registrarme en el portal

## 📦 Alcance Funcional

- [x] El endpoint registra al cliente con su autorización de tratamiento de datos.
- [x] La contraseña se guarda cifrada y la validación de duplicidad impide dos registros con el mismo documento.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la autorización de datos, la contraseña, la persona natural, la nacionalidad y la duplicidad del documento.
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
