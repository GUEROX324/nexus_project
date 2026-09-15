# Contrato de API REST v1

Estado verificado contra `Backend/nexus/nexus/urls.py`, `views.py` y `serializers.py` en la rama `Development`.

## Convenciones

- Único prefijo operativo: `/api/v1/`; barra final obligatoria.
- JSON en `snake_case`; carga de evidencia mediante `multipart/form-data`.
- Autenticación JWT de SimpleJWT: `Authorization: Bearer <access_token>`.
- Access token: 15 minutos. Refresh token: 7 días, con rotación y blacklist.
- Las colecciones paginadas usan `{count,next,previous,results}`, 10 elementos por defecto y `page_size` hasta 100.
- Estados: **IMPLEMENTADO** existe y está conectado; **PARCIAL** cubre parte de la HU; **PLANIFICADO** no tiene endpoint y se documenta sin inventar ruta.

## Endpoints reales

| Estado | Sprint / HU | Método y ruta | Alcance real |
|---|---|---|---|
| IMPLEMENTADO | S1 HU-01 | `POST /api/v1/auth/login/` | Devuelve `access`, `refresh` y usuario. |
| IMPLEMENTADO | S1 HU-01 | `POST /api/v1/auth/token/refresh/` | Rota refresh según configuración. |
| IMPLEMENTADO | S1 HU-01 | `POST /api/v1/auth/logout/` | Requiere refresh y lo añade a blacklist. |
| IMPLEMENTADO | S1 HU-01/02 | `GET /api/v1/auth/me/` | Usuario, rol, permisos, `student_id` y `grammatical_gender`. |
| IMPLEMENTADO | S1 HU-02 | `GET /api/v1/auth/users/` | Lista paginada para asignación de roles/comité. |
| IMPLEMENTADO | S1 HU-02 | `PATCH /api/v1/auth/users/{user_id}/role/` | Asignación auditada; no promueve a `SYSTEM_ADMIN`. |
| IMPLEMENTADO | S1 HU-02 | `POST /api/v1/admin/users/` | Crea cuenta institucional y auditoría. |
| IMPLEMENTADO | S1 HU-02/04 | `GET /api/v1/admin/audit/` | Bitácora administrativa paginada. |
| IMPLEMENTADO | S1 HU-03/06 | `GET /api/v1/students/` | Padrón filtrado por rol y relación. |
| IMPLEMENTADO | S1 HU-03 | `POST /api/v1/students/` | Crea usuario estudiante y expediente atómicamente. |
| IMPLEMENTADO | S1 HU-06 | `GET /api/v1/students/{id}/` | Expediente consolidado. |
| IMPLEMENTADO | S1 HU-06 | `GET /api/v1/students/{id}/overview/` | Mismo contrato consolidado con control relacional explícito. |
| IMPLEMENTADO | S1 HU-04 | `GET/POST /api/v1/committees/` | Lista o crea comité con `memberships`. |
| IMPLEMENTADO | S1 HU-04 | `DELETE /api/v1/committee-memberships/{assignment_id}/` | Elimina una membresía. |
| IMPLEMENTADO | S1 HU-04 | `GET /api/v1/admin/students/` | Padrón auxiliar para gestión de comité. |
| IMPLEMENTADO | S1 HU-05 | `GET/POST /api/v1/students/{student_id}/semesters/` | Consulta/alta; sólo `PROGRAM_COORDINATOR` administra. |
| IMPLEMENTADO | S1 HU-05 | `PATCH /api/v1/students/{student_id}/semesters/{semester_id}/` | Modifica y activa un semestre. |
| IMPLEMENTADO | S2 HU-07/10 | `GET/POST /api/v1/tutoring-sessions/` | Lista/crea tutorías; el router ofrece además retrieve, PUT, PATCH y DELETE. |
| IMPLEMENTADO | S2 HU-07 | `POST /api/v1/tutoring/` | Alias v1 de creación conservado por compatibilidad. |
| IMPLEMENTADO | S2 HU-08 | `GET/POST /api/v1/tutoring-sessions/{id}/participants/` | Participantes vinculados al expediente. |
| IMPLEMENTADO | S2 HU-09 | `GET/POST /api/v1/tutoring-sessions/{id}/observations/` | Observaciones con autor autenticado. |
| IMPLEMENTADO | S2 HU-11/12 | `GET/POST /api/v1/tutoring-sessions/{id}/agreements/` | Acuerdos de una tutoría y responsable relacionado. |
| IMPLEMENTADO | S2 HU-14 | `GET /api/v1/agreements/` | Filtros efectivos: `student`, `responsable`, `estado`, `vencido=true`. |
| IMPLEMENTADO | S2 HU-14 | `GET /api/v1/agreements/{id}/` | Detalle. |
| IMPLEMENTADO | S2 HU-13 | `PATCH /api/v1/agreements/{id}/status/` | Sólo responsable; `PENDIENTE → EN_PROCESO → CONCLUIDO`. |
| IMPLEMENTADO | S2 HU-13 | `GET /api/v1/agreements/{id}/audit-log/` | Historial de transiciones. |
| IMPLEMENTADO | S3 HU-21 | `GET/POST /api/v1/evidence/` | Archivo local, máximo 15 MiB, extensión/firma/MIME verificados. |
| PARCIAL | S1 HU-06 / S4 HU-24 | `GET /api/v1/academic/overview/` | Padrón activo consolidado; no es dashboard analítico. |
| PLANIFICADO | S3+ HU-15–20, HU-22–28 | — | Hay modelos para tesis y producción académica, pero no endpoints públicos; URL/DOI, timeline, alertas, dashboard, reportes y exportaciones no están implementados. |

## Autorización vigente

- `PROGRAM_COORDINATOR`: lectura académica global, alta de estudiantes, gestión de semestres y comité.
- `TUTOR` y `COMMITTEE_MEMBER`: expedientes asignados y tutorías relacionadas.
- `STUDENT`: expediente propio.
- `ACADEMIC_ADMIN`: cuentas/roles y lectura global; no gestiona semestres ni comités.
- `SYSTEM_ADMIN`: cuentas/roles y auditoría; el expediente académico está bloqueado.

Los errores de validación siguen el formato nativo de DRF por campo; autenticación, permisos y no encontrado usan `detail` cuando la vista lo define.