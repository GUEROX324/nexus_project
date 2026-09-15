# Equipo 3 — expediente y seguimiento longitudinal

Corte real en `Development`. Toda integración usa JWT Bearer y exclusivamente `/api/v1/`.

| HU | Sprint | Estado | Rama | Entrega / dependencia |
|---|---:|---|---|---|
| HU-06 Expediente | 1 | IMPLEMENTADO | `HU-06-consultar-expediente-resumen-estudiante` | Vista consolidada y UI 70/30; depende HU-03/04/05. |
| HU-14 Acuerdos abiertos/vencidos | 2 | IMPLEMENTADO | `HU-14-consultar-acuerdos-pendientes-vencidos` | Lista y filtros por estudiante, responsable, estado y vencido derivado; depende HU-11..13. |
| HU-19 Estancia | 4 | PARCIAL | por crear desde `Development` | Modelo/lectura resumen; falta CRUD/UI. |
| HU-20 Otro producto | 4 | PARCIAL | por crear desde `Development` | Modelo únicamente. |
| HU-23 Timeline | 3 | PLANIFICADO | por crear desde `Development` | Depende HU-07/13/15/21; no existe endpoint. |
| HU-24 Dashboard coordinador | 4 | PARCIAL | por crear desde `Development` | Hay padrón académico global, no dashboard analítico. |
| HU-25 Alertas de acuerdos | 3 | PARCIAL | por crear desde `Development` | Consulta `vencido=true`; falta interfaz/motor de alertas. |
| HU-27 Reporte integral | 5 | PLANIFICADO | por crear desde `Development` | Depende HU-23/24; no existe endpoint. |

La autorización combina rol y relación: estudiante propio, tutor/miembro asignado, coordinador global. `SYSTEM_ADMIN` no consulta expedientes. Sólo `PROGRAM_COORDINATOR` gestiona semestres; no `ACADEMIC_ADMIN` ni `SYSTEM_ADMIN`. Ramas HU nacen de `Development` y se integran por PR/revisión.