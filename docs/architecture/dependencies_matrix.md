# Matriz de dependencias e integración

Corte: rama `Development`. Dominios como identidad, estudiantes, tutorías o acuerdos son agrupaciones **conceptuales** dentro de la única aplicación Django `nexus`, no paquetes desplegables independientes.

| HU | Sprint | Equipo | Estado | Rama de trabajo | Dependencias | Dominio / entrega vigente |
|---|---:|---:|---|---|---|---|
| HU-01 | 1 | 1 | IMPLEMENTADO | `HU-01-autenticarse` | — | JWT login/refresh/logout/me. |
| HU-02 | 1 | 2 | IMPLEMENTADO | `HU-02-controlar-acceso-por-rol` | HU-01 | RBAC, roles, cuentas y auditoría. |
| HU-03 | 1 | 1 | IMPLEMENTADO | `HU-03-registrar-estudiante` | HU-01,02 | Alta y padrón de estudiantes. |
| HU-04 | 1 | 2 | IMPLEMENTADO | `HU-04-asignar-comite-academico` | HU-03 | Comité y memberships. |
| HU-05 | 1 | 1 | IMPLEMENTADO | `HU-05-gestionar-semestres` | HU-03 | Semestres 1..6; sólo coordinador gestiona. |
| HU-06 | 1 | 3 | IMPLEMENTADO | `HU-06-consultar-expediente-resumen-estudiante` | HU-03,04,05 | Expediente consolidado backend/frontend. |
| HU-07 | 2 | 1 | IMPLEMENTADO | `HU-07-registrar-sesion-tutoria` | HU-03,04,05 | CRUD de tutorías relacionadas. |
| HU-08 | 2 | 1 | IMPLEMENTADO | `HU-08-registrar-asistencia-participantes` | HU-04,07 | Modalidad y participantes. |
| HU-09 | 2 | 2 | IMPLEMENTADO | `HU-09-registrar-observaciones-minutas` | HU-07 | Observaciones con autor. |
| HU-10 | 2 | 1 | IMPLEMENTADO | `HU-10-programar-proxima-reunion` | HU-07 | Fecha/notas futuras. |
| HU-11 | 2 | 2 | IMPLEMENTADO | `HU-11-registrar-acuerdos-compromisos` | HU-07 | Acuerdos creados desde tutoría. |
| HU-12 | 2 | 2 | IMPLEMENTADO | `HU-12-asignar-responsable-fecha-limite` | HU-11 | Responsable relacionado y fecha válida. |
| HU-13 | 2 | 2 | IMPLEMENTADO | `HU-13-gestionar-estados-acuerdos` | HU-11,12 | Transiciones y bitácora. |
| HU-14 | 2 | 3 | IMPLEMENTADO | `HU-14-consultar-acuerdos-pendientes-vencidos` | HU-11..13 | Consulta/filtros; vencido derivado. |
| HU-15 | 3 | 2 | PARCIAL | por crear desde `Development` | HU-03,05 | Modelo y lectura en overview; falta API de alta/histórico y UI. |
| HU-16 | 4 | 2 | PLANIFICADO | por crear desde `Development` | HU-15 | Comparación por semestre. |
| HU-17 | 4 | 1 | PARCIAL | por crear desde `Development` | HU-03,05,21 | Modelo y lectura resumida; falta CRUD/UI. |
| HU-18 | 4 | 1 | PARCIAL | por crear desde `Development` | HU-03,05,21 | Modelo y lectura resumida; falta CRUD/UI. |
| HU-19 | 4 | 3 | PARCIAL | por crear desde `Development` | HU-03,05,21 | Modelo y lectura resumida; falta CRUD/UI. |
| HU-20 | 4 | 3 | PARCIAL | por crear desde `Development` | HU-03,05,21 | Modelo únicamente. |
| HU-21 | 3 | 2 | IMPLEMENTADO | `HU-21-cargar-evidencia` | HU-03,05 | Archivo local de hasta 15 MiB y UI de carga. |
| HU-22 | 3 | 2 | PARCIAL | por crear desde `Development` | HU-03,05 | Modelo admite enlace; serializador/API actual no lo expone. |
| HU-23 | 3 | 3 | PLANIFICADO | por crear desde `Development` | HU-07,13,15,21 | Timeline. |
| HU-24 | 4 | 3 | PARCIAL | por crear desde `Development` | HU-06,14,23 | Overview global no equivale al dashboard previsto. |
| HU-25 | 3 | 3 | PARCIAL | por crear desde `Development` | HU-12,13,14 | Filtro de vencidos; faltan alertas visuales dedicadas. |
| HU-26 | 5 | 2 | PLANIFICADO | por crear desde `Development` | HU-07,10,21 | Alertas de seguimiento incompleto. |
| HU-27 | 5 | 3 | PLANIFICADO | por crear desde `Development` | HU-23,24 | Reporte integral. |
| HU-28 | 5 | 1 | PLANIFICADO | por crear desde `Development` | HU-27 | Exportación PDF/XLSX. |

## Reglas compartidas migradas

- Un repositorio, una API `/api/v1/`, una base y una rama de integración `Development`.
- Ramas HU cortas con nombre `HU-XX-descripcion`, nacidas de `Development`; integración por PR/revisión. `main` queda para releases validados.
- Autorización por rol y relación con el expediente; no basta el rol para datos académicos sensibles.
- Cambios de modelo, contrato API o dependencias se comunican entre equipos y se acompañan de migración/pruebas/documentación.
- Una HU sólo se considera terminada cuando está integrada, probada, persistente, autorizada y demostrable; mockup o código aislado no cuentan.
- Alcance: una web responsiva; alertas internas antes que mensajería externa; sin firma electrónica; sin microservicios.