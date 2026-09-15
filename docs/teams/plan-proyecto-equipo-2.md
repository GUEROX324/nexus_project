# Equipo 2 — permisos, acuerdos, tesis y evidencias

Corte real en `Development`. Toda integración usa JWT Bearer y exclusivamente `/api/v1/`.

| HU | Sprint | Estado | Rama | Entrega / dependencia |
|---|---:|---|---|---|
| HU-02 Control de acceso | 1 | IMPLEMENTADO | `HU-02-controlar-acceso-por-rol` | RBAC + relación; cuentas, roles y auditoría; depende HU-01. |
| HU-04 Comité | 1 | IMPLEMENTADO | `HU-04-asignar-comite-academico` | Comité con memberships `ASESOR/COASESOR/COMMITTEE_MEMBER`; depende HU-03. |
| HU-09 Observaciones | 2 | IMPLEMENTADO | `HU-09-registrar-observaciones-minutas` | Múltiples observaciones con autor; depende HU-07. |
| HU-11 Crear acuerdos | 2 | IMPLEMENTADO | `HU-11-registrar-acuerdos-compromisos` | Desde tutoría; depende HU-07. |
| HU-12 Responsable/fecha | 2 | IMPLEMENTADO | `HU-12-asignar-responsable-fecha-limite` | Responsable relacionado y fecha válida; depende HU-11. |
| HU-13 Estado | 2 | IMPLEMENTADO | `HU-13-gestionar-estados-acuerdos` | Sólo responsable: pendiente→en proceso→concluido; auditoría; vencido derivado. |
| HU-15 Avance de tesis | 3 | PARCIAL | por crear desde `Development` | Modelo y lectura resumen; falta API de escritura/UI. |
| HU-16 Comparar avance | 4 | PLANIFICADO | por crear desde `Development` | Depende HU-15. |
| HU-21 Cargar evidencia | 3 | IMPLEMENTADO | `HU-21-cargar-evidencia` | Archivo local hasta 15 MiB con validación de firma/MIME; depende HU-03/05. |
| HU-22 DOI/URL | 3 | PARCIAL | por crear desde `Development` | Campo/modelo existen, API actual no expone enlace. |
| HU-26 Alertas seguimiento | 5 | PLANIFICADO | por crear desde `Development` | Depende HU-07/10/21. |

Sólo `PROGRAM_COORDINATOR` gestiona semestres; `ACADEMIC_ADMIN` y `SYSTEM_ADMIN` no tienen `semesters.manage`. Ramas HU nacen de `Development`, pasan PR/revisión y coordinan cualquier cambio de contrato o migración.