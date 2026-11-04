# Refinamiento final del backlog – Web Service One Click Caribe

Este documento consolida el refinamiento completo del proyecto: alcance, actores, historias de usuario, endpoints, reglas de negocio, criterios transversales y datos iniciales. Las historias, endpoints, APIs y reglas de negocio aquí descritas reemplazan las versiones anteriores como resultado del refinamiento completo del modelo de negocio.

## 1. Alcance

El sistema expone como Web Services el ciclo de vida completo de la venta de viajes de One Click Caribe a través de un portal web: el cliente se registra, inicia sesión, consulta el catálogo, solicita y recibe su cotización de forma automática, confirma la compra, paga en línea y consulta su reserva y su factura. La confirmación de los pagos, la reserva y la factura ocurren de forma automática. La intervención humana se limita a la gestión de proveedores y a la atención posventa.

## 2. Actores

| Actor | Rol en el sistema | Historias |
| --- | --- | --- |
| Cliente | Opera de forma autónoma todo el ciclo de vida desde el portal | HU-001, HU-002, HU-003, HU-004, HU-007, HU-008, HU-009, HU-010, HU-011, HU-012, HU-013, HU-014, HU-015, HU-016, HU-017, HU-018 |
| Administradora | Registra los proveedores y gestiona su estado | HU-005, HU-006 |
| Asesor comercial | Atiende las consultas posventa que requieren apoyo humano | HU-019 |

La pasarela de pagos es un sistema externo: notifica el resultado de las transacciones mediante un webhook (HU-014), cuyo beneficiario es el cliente.

## 3. Historias de usuario y endpoints

| HU | Historia | Actor | Método | Endpoint | Módulo | Acceso | Prioridad | Sprint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HU-001 | Registrarme en el portal | Cliente | POST | /api/v1/clientes | MOD-01 | Pública | Alta | Sprint 1 |
| HU-002 | Iniciar sesión en el portal | Cliente | POST | /api/v1/auth/login | MOD-01 | Pública | Alta | Sprint 1 |
| HU-003 | Consultar mi perfil | Cliente | GET | /api/v1/clientes/me | MOD-01 | Token, rol cliente | Media | Sprint 1 |
| HU-004 | Actualizar mis datos de contacto | Cliente | PATCH | /api/v1/clientes/me | MOD-01 | Token, rol cliente | Baja | Sprint 1 |
| HU-005 | Registrar un proveedor con su comisión pactada | Administradora | POST | /api/v1/proveedores | MOD-02 | Token, rol administradora | Media | Sprint 2 |
| HU-006 | Desactivar o reactivar un proveedor | Administradora | PATCH | /api/v1/proveedores/{proveedorId}/estado | MOD-02 | Token, rol administradora | Media | Sprint 2 |
| HU-007 | Consultar servicios disponibles por destino | Cliente | GET | /api/v1/catalogo/servicios | MOD-02 | Pública | Media | Sprint 2 |
| HU-008 | Solicitar cotización y recibirla automáticamente | Cliente | POST | /api/v1/cotizaciones | MOD-03 | Token, rol cliente | Alta | Sprint 2 |
| HU-009 | Consultar mi cotización | Cliente | GET | /api/v1/cotizaciones/{cotizacionId} | MOD-03 | Token, rol cliente | Media | Sprint 2 |
| HU-010 | Responder a mi cotización | Cliente | POST | /api/v1/cotizaciones/{cotizacionId}/respuesta | MOD-03 | Token, rol cliente | Alta | Sprint 2 |
| HU-011 | Confirmar mi compra y generar la orden de venta | Cliente | POST | /api/v1/ventas | MOD-04 | Token, rol cliente | Alta | Sprint 3 |
| HU-012 | Consultar el estado de mi compra | Cliente | GET | /api/v1/ventas/{ventaId} | MOD-04 | Token, rol cliente | Media | Sprint 3 |
| HU-013 | Pagar mi compra en línea | Cliente | POST | /api/v1/pagos | MOD-05 | Token, rol cliente | Alta | Sprint 3 |
| HU-014 | Confirmar automáticamente mi pago por PSE | Cliente | POST | /api/v1/pagos/notificaciones | MOD-05 | Firma de la pasarela | Alta | Sprint 3 |
| HU-015 | Consultar mis pagos y mi saldo | Cliente | GET | /api/v1/ventas/{ventaId}/pagos | MOD-05 | Token, rol cliente | Media | Sprint 3 |
| HU-016 | Consultar mi reserva confirmada | Cliente | GET | /api/v1/ventas/{ventaId}/reserva | MOD-07 | Token, rol cliente | Media | Sprint 4 |
| HU-017 | Consultar mi factura | Cliente | GET | /api/v1/ventas/{ventaId}/factura | MOD-06 | Token, rol cliente | Media | Sprint 4 |
| HU-018 | Registrar una consulta posventa | Cliente | POST | /api/v1/posventa/consultas | MOD-08 | Token, rol cliente | Media | Sprint 4 |
| HU-019 | Responder y cerrar una consulta posventa | Asesor comercial | PATCH | /api/v1/posventa/consultas/{consultaId} | MOD-08 | Token, rol asesor | Media | Sprint 4 |

## 4. Criterios transversales

- **Respuesta uniforme:** toda respuesta usa la estructura `success`, `data` y `message`, incluidos los errores de formato del JSON, que se responden con 400.
- **Códigos HTTP:** 201 al crear, 200 al consultar o modificar, 400 por datos inválidos, 401 sin autenticación válida, 402 si la entidad financiera rechaza un pago, 403 sin permiso sobre el recurso, 404 si no existe, 409 por conflicto de estado o duplicidad, 500 por error interno y 503 si la pasarela de pagos no está disponible.
- **Métodos REST:** POST para crear, GET para consultar y PATCH para modificar parcialmente. No se usa DELETE: el negocio no elimina registros, cambia su estado.
- **Autenticación y autorización:** inicio de sesión con token JWT firmado con `SECRET_KEY` y vigencia `ACCESS_TOKEN_EXPIRE_MINUTES` (archivo .env). Cada endpoint valida el rol; el cliente solo accede a sus propios recursos y su identificador se toma del token, nunca del cuerpo de la solicitud.
- **Protección de datos personales (Ley 1581 de 2012):** autorización expresa del tratamiento de datos al registrarse, con fecha y versión de la política; minimización de los datos solicitados; protección reforzada de los datos de menores; derecho a actualizar los datos de contacto (HU-004); contraseñas cifradas y nunca devueltas.
- **Pagos seguros:** el sistema no recibe ni guarda números de tarjeta, solo el token de la pasarela; cada intento de pago usa una clave de idempotencia y las notificaciones de la pasarela se validan por firma y no se aplican dos veces.
- **Arquitectura:** capas api, services, domain, repositories y core, con repositorio en memoria y datos iniciales por módulo, de modo que cada historia se prueba de forma independiente.

## 5. Reglas de negocio

Se mantienen las reglas del modelo de negocio aplicadas en cada historia: persona natural y duplicidad del documento (RN-01, RN-04, RN-05); precio por pasajero, edades, acomodación y servicios (RN-06, RN-07, RN-09, RN-10); proveedores activos, tarifa vigente y disponibilidad (RN-13, RN-18, RN-20); tarifa neta más 12 %, con el tiquete aéreo al valor neto, y tarifa de menor (RN-22, RN-23); vigencia de la cotización hasta el cierre del día, vencimiento y motivo de rechazo (RN-26, RN-28, RN-30); orden de venta solo desde una cotización aceptada, con código propio, fecha límite del saldo y precios inmodificables (RN-31 a RN-35); pago asociado a una orden y orden pagada con saldo cero (RN-44, RN-45); liquidación neta a proveedores (RN-48, RN-49); factura del titular, simulada ante la DIAN y no eliminable (RN-51, RN-53, RN-56, RN-57); reserva con localizador por servicio tras el pago (RN-61, RN-62); y posventa vinculada a la orden, sin modificar la venta y sin vencimiento (RN-81 a RN-85).

Por el refinamiento completo del modelo de negocio se actualizan tres reglas:

| Regla | Antes | Después del refinamiento |
| --- | --- | --- |
| RN-29 | La cotización la emite el asesor | La cotización se calcula y emite automáticamente al recibir la solicitud del cliente |
| RN-41 | Solo efectivo o transferencia | Pago en línea por PSE, tarjeta de crédito o tarjeta de débito a través de la pasarela de pagos |
| RN-42 | El pago se verifica manualmente | El pago se confirma automáticamente con la respuesta o la notificación de la pasarela |

## 6. Trazabilidad

| HU | Trazabilidad (módulo · endpoint · reglas) |
| --- | --- |
| HU-001 | MOD-01 · POST /api/v1/clientes · RN-01, RN-04, RN-05 · Ley 1581 |
| HU-002 | MOD-01 · POST /api/v1/auth/login · Seguridad |
| HU-003 | MOD-01 · GET /api/v1/clientes/me · Seguridad |
| HU-004 | MOD-01 · PATCH /api/v1/clientes/me · RN-04 · Ley 1581 |
| HU-005 | MOD-02 · POST /api/v1/proveedores · RN-13, RN-22 |
| HU-006 | MOD-02 · PATCH /api/v1/proveedores/{proveedorId}/estado · RN-13, RN-34 |
| HU-007 | MOD-02 · GET /api/v1/catalogo/servicios · RN-13, RN-18, RN-20 |
| HU-008 | MOD-03 · POST /api/v1/cotizaciones · RN-06, RN-07, RN-09, RN-10, RN-18, RN-20, RN-22, RN-23, RN-26 · Ley 1581 |
| HU-009 | MOD-03 · GET /api/v1/cotizaciones/{cotizacionId} · RN-28 |
| HU-010 | MOD-03 · POST /api/v1/cotizaciones/{cotizacionId}/respuesta · RN-26, RN-28, RN-30 |
| HU-011 | MOD-04 · POST /api/v1/ventas · RN-31, RN-32, RN-33, RN-34 |
| HU-012 | MOD-04 · GET /api/v1/ventas/{ventaId} · RN-45 |
| HU-013 | MOD-05 · POST /api/v1/pagos · RN-44, RN-45, RN-48, RN-49, RN-53, RN-57, RN-61, RN-62 |
| HU-014 | MOD-05 · POST /api/v1/pagos/notificaciones · RN-45, RN-48, RN-49, RN-53, RN-57, RN-61, RN-62 |
| HU-015 | MOD-05 · GET /api/v1/ventas/{ventaId}/pagos · RN-45 |
| HU-016 | MOD-07 · GET /api/v1/ventas/{ventaId}/reserva · RN-45, RN-61, RN-62 |
| HU-017 | MOD-06 · GET /api/v1/ventas/{ventaId}/factura · RN-51, RN-53, RN-56, RN-57 |
| HU-018 | MOD-08 · POST /api/v1/posventa/consultas · RN-81, RN-83, RN-85 |
| HU-019 | MOD-08 · PATCH /api/v1/posventa/consultas/{consultaId} · RN-81 |

## 7. Datos iniciales del repositorio en memoria

| Repositorio | Datos iniciales |
| --- | --- |
| Cuentas | Cliente CLI-00188 (mfrojas@correo.com), cliente CLI-00190, una cuenta con rol administradora y una cuenta con rol asesor; contraseñas cifradas. |
| Clientes | CLI-00188, María Fernanda Rojas Díaz, documento 1098765432, CO, pareja, con autorización de datos; CLI-00190, sin cotizaciones. |
| Proveedores | PRV-0003 Avianca, aerolínea, 0 %; PRV-0021 PriceTravel, mayorista, 12 %; PRV-0022 HotelDo, mayorista, 12 %; PRV-0031 Assist1, aseguradora, 12 %; PRV-0040, inactivo. |
| Catálogo y tarifas (Cancún) | Tiquete aéreo 1.980.000 (menor 1.782.000); hospedaje 1.450.000 (menor 725.000); traslado 210.000 (menor 105.000); asistencia médica 180.000; sin cupo de hospedaje del 2026-12-24 al 2026-12-31. |
| Cotizaciones | COT-00045 aceptada (8.081.600 para 2 adultos); COT-00046 emitida; COT-00031 vencida. |
| Ventas | VEN-00012 de COT-00045, pago parcial, saldo 8.081.600; VEN-00010 pagada, con reserva RES-00008 y factura FAC-00006; VEN-00013 sin pagos, 3.150.000. |
| Posventa | CON-00021 y CON-00022 abiertas; CON-00019 cerrada. |

Cada prueba prepara su precondición a partir de estos datos, de modo que las historias se prueban de forma independiente.

## 8. Fuera del alcance

Cancelaciones, modificaciones y cambios de servicios (flujos alternos); reportes de rentabilidad; reembolsos; cálculo de IVA en la factura; e integraciones reales con la DIAN, la pasarela de pagos y los sistemas de reserva de los proveedores, que se simulan en el repositorio en memoria.

## 9. Flujo de trabajo en el tablero

| Columna | Condición |
| --- | --- |
| To do | Historia refinada, sin código |
| In progress | Rama feature/HU-XXX creada desde development, con desarrollo en curso |
| Gestión Integración | Rama fusionada en development e integrada con los demás módulos |
| Testing | Fusionada en testing, con los 5 casos de prueba ejecutados y capturas de request y response |
| Done | Criterios de aceptación y Definición de Hecho cumplidos, con el JSON de la issue igual a la respuesta real |
