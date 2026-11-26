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

Última consulta a GitHub después de fusionar PR #14 y del commit automático de fuentes:

- Ramas remotas: **2** — `main` y `work/stocktake-barcode-runtime-acceptance`.
- Pull requests abiertos: **0**.
- `main` incluye la integración funcional de stocktake `c38fad581f669bd7e1a2795123cc8ecca242e010` y la incorporación de fuentes `7d9e5bb80e866df87b51baad852c1e6256270dd1`.
- La rama `work/stocktake-barcode-runtime-acceptance` permanece en el remoto en el HEAD `12f29a47e7b89f6f162c85a7e3684e24f9fe793b`, pero PR #14 ya está fusionado. No es trabajo activo: debe borrarse.
- El run #462 terminó correctamente en su SHA. El run #463 valida el commit funcional `c38fad5`; prevalidación y Windows pasaron, build pendiente al corte.
- El run #24 incorporó la corrección a `vendor/mycompany/.../AdjustmentList.lsf`; la validación de árboles, licencias y rutas pasó, la compilación estaba en curso.
- PR #13 está cerrado como reemplazado; PR #15 y PR #14 están integrados.
- Las ramas antiguas de devoluciones y guardas ya no aparecen en el listado remoto y no deben recrearse.

### Protección de la rama principal

La lista de ramas informa `protected=false` para `main`. La consulta del endpoint detallado de protección no está disponible para la conexión actual. No se afirma que existan reglas obligatorias de revisión o checks hasta verificarlas. La administración de GitHub debe activar protección, impedir force-push y exigir checks.

### Borrado automático de ramas

La API del repositorio informa `delete_branch_on_merge=false`. La rama fuente del PR #14 no se eliminó automáticamente. La conexión actual no ofrece una acción para borrar referencias Git ni modificar ajustes administrativos.

Después de confirmar que `main` contiene el merge, borrar desde una terminal local la rama remota fusionada:

```bash
git push origin --delete work/stocktake-barcode-runtime-acceptance
git fetch origin --prune
git branch -r
```

El resultado esperado del último comando es que sólo aparezca `origin/main`. Desde GitHub Settings → General → Pull Requests se puede activar “Automatically delete head branches” para que los próximos merges no dejen ramas huérfanas.

## Rutina por hito

**Inicio:** actualizar `main`, confirmar árbol limpio, crear una rama temporal desde el SHA actual y definir la aceptación.

**Desarrollo:** mantener un único PR, ejecutar pruebas focalizadas y corregir sobre la misma rama.

**Cierre:** repetir validaciones completas, integrar por squash, verificar el SHA de `main`, borrar la rama fuente y refrescar este inventario. Si falla la aceptación, no abrir una segunda rama para el mismo trabajo.
