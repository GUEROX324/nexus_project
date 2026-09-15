# Equipo 1 — núcleo y tutorías

Corte real en `Development`. Toda integración usa JWT Bearer y exclusivamente `/api/v1/`.

| HU | Sprint | Estado | Rama | Entrega / dependencia |
|---|---:|---|---|---|
| HU-01 Autenticarse | 1 | IMPLEMENTADO | `HU-01-autenticarse` | Login, refresh, logout y sesión; base de HU-02. |
| HU-03 Registrar estudiante | 1 | IMPLEMENTADO | `HU-03-registrar-estudiante` | Alta atómica y padrón; depende HU-01/02. |
| HU-05 Gestionar semestres | 1 | IMPLEMENTADO | `HU-05-gestionar-semestres` | 1..6; sólo `PROGRAM_COORDINATOR`, no `ACADEMIC_ADMIN` ni `SYSTEM_ADMIN`; depende HU-03. |
| HU-07 Registrar tutoría | 2 | IMPLEMENTADO | `HU-07-registrar-sesion-tutoria` | CRUD relacional; depende HU-03/04/05. |
| HU-08 Modalidad/participantes | 2 | IMPLEMENTADO | `HU-08-registrar-asistencia-participantes` | Presencial, virtual o híbrida; participantes asociados. |
| HU-10 Próxima reunión | 2 | IMPLEMENTADO | `HU-10-programar-proxima-reunion` | Fecha posterior y notas. |
| HU-17 Publicación | 4 | PARCIAL | por crear desde `Development` | Modelo/lectura resumen; falta CRUD/UI; depende HU-21. |
| HU-18 Evento académico | 4 | PARCIAL | por crear desde `Development` | Modelo/lectura resumen; falta CRUD/UI; depende HU-21. |
| HU-28 Exportar | 5 | PLANIFICADO | por crear desde `Development` | Depende HU-27; no hay endpoints PDF/XLSX. |

## Reglas de trabajo

Ramas `HU-XX-descripcion` cortas nacen de `Development`, se integran por PR y revisión; `main` recibe releases validados. Una HU requiere código integrado, pruebas, autorización relacional, persistencia y documentación. Cambios de API/modelo se coordinan con los otros equipos.