# Diseño N.E.X.U.S.: estado implementado y objetivo

`Design.pen` se conserva como referencia visual. No se editó: su formato no forma parte del flujo de código verificable y `DESIGN.md` delimita cualquier pantalla aspiracional.

## Implementado en Angular

- Aplicación Angular 20 con componentes standalone, rutas protegidas, guardas por rol/permiso e interceptor JWT.
- Pantallas: login, inicio, alta de estudiante, expediente, gestión de roles, cuentas institucionales, auditoría y comité.
- Expediente `StudentOverviewComponent` con layout 70/30, resumen de estudiante/comité/semestres/acuerdos y formularios integrados de semestre, tutoría y carga de evidencia.
- `AcademicCommitteeCardComponent`, formulario de tutoría y carga local de evidencia hasta 15 MiB.
- Copia sensible a `grammatical_gender`, etiquetas de roles y paginación compartida.
- Componente global de sesión expirada junto al `router-outlet`.

No existe un componente `AppShell`, `PillBadge`, timeline, drawer de acuerdos, formulario de avance de tesis ni reporte dossier con esos nombres. No deben citarse como implementados.

## Planificado

- Timeline longitudinal (HU-23), dashboard analítico (HU-24), alertas dedicadas (HU-25/26).
- Alta/comparación de avance de tesis (HU-15/16).
- CRUD de producción académica y estancia (HU-17..20).
- Evidencia DOI/URL (HU-22).
- Reporte integral y exportación PDF/XLSX (HU-27/28).
- Un shell reutilizable, drawers y badges sólo se crearán si reducen duplicación real; no son requisito existente.

## Tokens visuales de referencia

| Uso | Valor |
|---|---|
| Primario | `#6365EF` |
| Primario hover | `#4E50DC` |
| Énfasis | `#2C1867` |
| Fondo aplicación | `#F5F7FB` |
| Tarjeta | `#FFFFFF` |
| Borde | `#E4E7EC` |
| Texto principal | `#101828` |
| Pendiente | `#57949D` |
| En proceso | `#B57136` |
| Concluido | `#437E5C` |
| Vencido | `#A14D98` |

Tipografía objetivo: Inter con fallback sans-serif; escala base de 8 px, foco visible y contraste suficiente. En móvil, el layout debe reducirse a una columna sin ocultar acciones o estados. `VENCIDO` es una presentación derivada por fecha para acuerdos no concluidos, aunque el modelo conserve el choice histórico.