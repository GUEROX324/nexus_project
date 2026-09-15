# Especificación del esquema de datos vigente

Fuente de verdad: modelos y migraciones de la única aplicación Django `nexus`. Las tablas de dominio usan el prefijo `nexus_`; no existen aplicaciones operativas separadas `identity`, `students`, `agreements`, etc.

## Tablas de dominio

| Tabla | Modelo | Campos y reglas relevantes |
|---|---|---|
| `nexus_customuser` | `CustomUser` | Email único; nombres de 150; `role` de 30; `grammatical_gender` de 20 (`MASCULINE`, `FEMININE`, `NEUTRAL`, `UNSPECIFIED`); flags y timestamps. Incluye M2M Django de grupos/permisos. |
| `nexus_student` | `Student` | Usuario 1:1 opcional `SET_NULL`; `matricula varchar(20)` única, indexada y además única sin distinguir mayúsculas/minúsculas; nombre, programa, ingreso, cohorte, activo y timestamps. |
| `nexus_semester` | `Semester` | Estudiante `CASCADE`; número 1..6; fechas con `fecha_fin >= fecha_inicio`; único `(student, numero)`; sólo uno activo se asegura en la capa API, no por constraint DB. |
| `nexus_academiccommittee` | `AcademicCommittee` | Un comité por estudiante mediante OneToOne `CASCADE`. |
| `nexus_committeemembership` | `CommitteeMembership` | Comité y usuario `CASCADE`; rol efectivo `ASESOR`, `COASESOR` o `COMMITTEE_MEMBER`; único `(committee,user,role)` y máximo un `COASESOR` por comité. La API exige cuenta `TUTOR` para asesor/coasesor y `COMMITTEE_MEMBER` para miembro. No hay regla aprobada de asesor único. |
| `nexus_adminauditlog` | `AdminAuditLog` | Acción, actor `PROTECT`, usuario/membresía objetivo `SET_NULL`, JSON y fecha. |
| `nexus_tutoringsession` | `TutoringSession` | Estudiante y semestre `CASCADE`; fecha, modalidad `PRESENCIAL/VIRTUAL/HIBRIDA`, resumen, próxima reunión, creador `SET_NULL`, timestamps. |
| `nexus_tutoringparticipant` | `TutoringParticipant` | Sesión/usuario `CASCADE`; rol `ESTUDIANTE/ASESOR_PRINCIPAL/COASESOR/MIEMBRO_COMITE`; asistencia y notas; único `(session,user)`. |
| `nexus_tutoringobservation` | `TutoringObservation` | Sesión/autor `CASCADE`, tema, observación y timestamps. |
| `nexus_agreement` | `Agreement` | Sesión opcional `SET_NULL`; estudiante `CASCADE`; responsable `CASCADE`; límite, estado persistido (`PENDIENTE`, `EN_PROCESO`, `CONCLUIDO`, `VENCIDO`), conclusión, creador `SET_NULL`, timestamps. `is_vencido` es derivado: no concluido y fecha límite anterior a hoy; la API no persiste automáticamente `VENCIDO`. |
| `nexus_agreementauditlog` | `AgreementAuditLog` | Acuerdo `CASCADE`, usuario `SET_NULL`, estados, comentario y fecha. |
| `nexus_thesisprogress` | `ThesisProgress` | Estudiante/semestre `CASCADE`; avance 0..100; `componentes_json` libre, observaciones, registrador `SET_NULL`, fechas. |
| `nexus_evidence` | `Evidence` | Estudiante `CASCADE`, semestre opcional `SET_NULL`; tipo `ARCHIVO_LOCAL/ENLACE_DOI`; actividad `TUTORIA/ACUERDO/TESIS/OTRO`; archivo, `enlace_url`, MIME, bytes, fechas y creador. La API actual sólo acepta archivo local y valida máximo **15 MiB** (`15 * 1024 * 1024`), extensiones PDF/PNG/JPG/JPEG/DOCX/ZIP, firma y MIME. |
| `nexus_publication` | `Publication` | Base académica: estudiante, semestre/evidencia opcionales; título, autores, tipo/estado como texto sin `choices`, editorial, fecha y DOI. |
| `nexus_academicevent` | `AcademicEvent` | Base académica; tipo, evento, ponencia, fecha, sede y modalidad son campos de texto sin `choices` ORM. |
| `nexus_researchstay` | `ResearchStay` | Base académica; institución, país, fechas (`fin >= inicio`), responsable, objetivos y resultados. |
| `nexus_otherproduct` | `OtherProduct` | Base académica; tipo, título, descripción y fecha. |

`AcademicOutputBase` es abstracto y no crea tabla. Además existen tablas estándar de Django (`auth_*`, `django_*`) y de blacklist de SimpleJWT.

## Decisiones de integridad

- Las eliminaciones siguen exactamente `CASCADE`, `SET_NULL` y `PROTECT` indicados; no se promete conservación adicional.
- Los catálogos sólo son cerrados cuando el modelo declara `TextChoices` o una restricción explícita. Los campos de producción académica permanecen abiertos.
- Las asociaciones polimórficas de evidencia (`actividad_tipo`, `actividad_id`) no son claves foráneas y su integridad depende de la API.
- SQLite es la base configurada actualmente; cualquier afirmación de PostgreSQL, latencia o volumen queda fuera del estado implementado.