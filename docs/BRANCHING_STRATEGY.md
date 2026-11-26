# Política de ramas e integración

**Revisión:** 26 de noviembre de 2026  
**Rama canónica:** `main`  
**Límite operativo:** una rama persistente (`main`) y como máximo una rama temporal activa para revisión.

## Objetivo

Mantener una línea principal fácil de revisar, probar, ejecutar localmente y recuperar. Ningún cambio de aplicación se considera integrado hasta que esté en `main`.

## Reglas

1. **`main` es la única fuente de verdad.** Las ramas temporales sólo existen para una revisión aislada y no sustituyen el estado de la aplicación.
2. **Una sola rama temporal activa.** Debe nacer del SHA actual de `main`, tener un alcance único y cerrarse al terminar.
3. **No apilar PR ni ramas de la misma funcionalidad.** Si un test falla, corregir el mismo PR salvo que se pruebe que la línea de trabajo ya no es recuperable.
4. **Integrar con evidencia del SHA exacto.** Revisar diff, preflight, Windows, compilación y smoke de runtime afectado.
5. **Después del merge, verificar `main` y eliminar la rama temporal.** No confiar en que GitHub lo haga automáticamente: la configuración actual `delete_branch_on_merge=false`.
6. **No revivir ramas antiguas.** Recuperar selectivamente sólo contenido que falte y compararlo con `main`.
7. **No confundir compilación verde con aceptación funcional.** Login, API autenticada, POS, ledgers, persistencia y backups son comprobaciones distintas.
8. **Mantener recuperación.** Los cambios de runtime/esquema requieren backup y evidencia de restore antes de considerarse listos.

## Convención de nombres

- `work/<area>-<objetivo>`: una funcionalidad o prueba aislada.
- `fix/<area>-<problema>`: un hotfix independiente y urgente; no abrirlo si puede corregirse en el PR activo.

## Puerta de aceptación

Para cambios del runtime o de MyCompany:

- validaciones estáticas y pruebas de contrato;
- suites Python y regresiones relacionadas;
- compilación del servidor, cliente GWT y lógica MyCompany desde fuentes fijadas;
- arranque, RMI, API y login autenticado;
- smoke nativo macOS ARM64 y Linux; Windows cuando el despliegue lo afecte;
- backup/restore y persistencia después del reinicio;
- evidencia con datos locales reales antes de declarar aceptación productiva.

Las fixtures sintéticas son regresión automatizada, no sustituyen una prueba con datos reales ni la homologación de pagos externos.

## Estado del repositorio — 26 de noviembre de 2026

Última consulta a GitHub:

- Ramas remotas: **2** — `main` y `work/stocktake-barcode-runtime-acceptance`.
- Pull requests abiertos: **1** — PR [#14](https://github.com/JavierGrecco/Rubrova/pull/14), en borrador.
- `main`: `04249dc983c3af066a386f1e1b022da2d9587ec0`.
- Rama del PR #14: `92786b7258378b063bed9ce3a5b71fdf3d2b505a`, sincronizada con `main` (`ahead 12 / behind 0` al último diff).
- PR #13 está cerrado como reemplazado; PR #15 está integrado.
- El run [45906455407](https://github.com/JavierGrecco/Rubrova/actions/runs/45906455407) de `main` terminó correctamente, incluido el smoke nativo macOS ARM64.
- El run [45907277530](https://github.com/JavierGrecco/Rubrova/actions/runs/45907277530) del PR #14 terminó rojo sólo por una expectativa incorrecta: tras venta de 1 y devolución completa de 1, el stock final persistido es 10, no 9. Los casos barcode cero/NULL/positivo pasaron. Se corrige la expectativa y se exige un run nuevo.

### Protección de la rama principal

La lista de ramas informa `protected=false` para `main`. La consulta del endpoint detallado de protección no está disponible para la conexión actual. No se afirma que existan reglas obligatorias de revisión o checks hasta verificarlas. La administración de GitHub debe activar protección, impedir force-push y exigir checks.

### Borrado automático de ramas

La API de repositorio informa `delete_branch_on_merge=false`. Esa opción no puede cambiarse desde las acciones habilitadas en esta conexión. Hasta activarla desde Settings, la rutina de cierre debe borrar manualmente la rama fuente y verificar después que sólo quede `main`.

## Rutina por hito

**Inicio:** actualizar `main`, confirmar árbol limpio, crear una rama temporal desde el SHA actual y definir la aceptación.

**Desarrollo:** mantener un único PR, ejecutar pruebas focalizadas y corregir sobre la misma rama.

**Cierre:** repetir validaciones completas, integrar por squash, verificar el SHA de `main`, borrar la rama fuente y refrescar este inventario. Si falla la aceptación, no abrir una segunda rama para el mismo trabajo.
