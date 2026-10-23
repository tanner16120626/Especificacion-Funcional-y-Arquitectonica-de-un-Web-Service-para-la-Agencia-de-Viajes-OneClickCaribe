# Especificación Funcional y Arquitectónica de un Web Service para la Agencia de Viajes One Click Caribe

Proyecto académico de la asignatura **Web Services** (Unidades Tecnológicas de Santander, docente Edward Villamizar).
Autor: **Tanner José Cedeño Miranda**.

## Enlaces

- Repositorio: https://github.com/tanner16120626/Especificacion-Funcional-y-Arquitectonica-de-un-Web-Service-para-la-Agencia-de-Viajes-OneClickCaribe
- Tablero GitHub Projects ("Columnas"): https://github.com/users/tanner16120626/projects/1

## Propósito

Centralizar la información operativa de One Click Caribe, automatizar el cálculo de cotizaciones y pagos, y estandarizar la comunicación entre los componentes del sistema mediante Web Services.

## Organización del backlog

| Elemento | Representación en GitHub |
|---|---|
| Épica (módulo MOD-01 a MOD-08) | Etiqueta `MOD-XX` |
| Historia de usuario (HU-001 a HU-052) | Issue `[HU-XXX]` con la plantilla del docente |
| Trazabilidad FUN / PRO / RN | Campo `Trazabilidad` del Project |
| Prioridad | Campo `Prioridad` (Alta, Media, Baja) |
| Planificación | Campos `Corte` y `Sprint` |

## Estados del tablero

| Columna | Significado |
|---|---|
| To do | Historia registrada en el backlog, pendiente de refinamiento |
| In progress | Historia en refinamiento |
| Gestión Integración | Historia documentada completa y lista para desarrollo |
| Testing | Historia implementada en pruebas (tercer corte) |
| Done | Historia implementada que cumple la Definición de Hecho (tercer corte) |

## Convenciones de los servicios

- Toda respuesta JSON contiene `success`, `data` y `message`.
- Rutas con prefijo `/api/v1`.
- Nombres de campos en camelCase y fechas en ISO 8601.

## Estructura del repositorio

- `.github/ISSUE_TEMPLATE/historia-de-usuario.md`: plantilla del docente para crear historias desde *New issue*.
- `docs/plantilla/`: copia literal de la plantilla del docente.
- `docs/historias/`: especificación de cada historia documentada (una por commit).
