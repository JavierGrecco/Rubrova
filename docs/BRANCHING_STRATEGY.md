# Política de ramas e integración

**Revisión:** 25 de noviembre de 2026  
**Rama canónica:** `main`  
**Límite operativo:** una rama de funcionalidad activa; una segunda sólo para una corrección urgente e independiente.

## Objetivo

Mantener una línea principal fácil de revisar, probar, ejecutar localmente y recuperar. Ningún cambio de aplicación se considera integrado hasta que esté en `main`.

## Reglas

1. **`main` es la fuente de verdad.** No se desarrolla directamente sobre ella. Los cambios funcionales entran mediante pull request.
2. **Máximo dos ramas de trabajo activas.** La norma es una sola rama de funcionalidad. La segunda se reserva para un hotfix independiente; no se crean ramas auxiliares por cada corrección o commit.
3. **Las ramas nacen de `main` actualizado.** No se apilan funcionalidades dependientes ni se abren PR encadenados.
4. **Un PR por hito coherente.** Debe explicar objetivo, alcance, riesgos, evidencia, limitaciones y criterio de aceptación. Siempre apunta directamente a `main`.
5. **Integrar por hitos.** Agrupar cambios relacionados, ejecutar las validaciones del alcance y revisar el diff completo antes del merge.
6. **Preferir squash merge.** Cada hito queda como un commit claro en `main`, sin arrastrar commits intermedios de prueba.
7. **Eliminar la rama después del merge.** Antes de borrarla, verificar que todo el contenido útil está integrado.
8. **No revivir ramas históricas por su historial.** Comparar archivos contra `main` y recuperar selectivamente sólo cambios útiles que falten.
9. **No confundir CI verde con aceptación funcional.** Distinguir pruebas estáticas, unitarias, compilación, arranque, login, API autenticada, smoke POS y conciliación con datos reales.

## Convención de nombres

- `work/<area>-<objetivo>`: rama principal para una nueva funcionalidad.
- `fix/<area>-<problema>`: segunda rama opcional para un hotfix urgente e independiente.

Los nombres describen un objetivo estable, no un experimento temporal.

## Puerta de aceptación

Para cambios del runtime o de MyCompany, la puerta mínima contempla:

- validaciones estáticas y pruebas de contrato;
- suites Python y regresiones relacionadas;
- compilación del servidor, cliente GWT y lógica MyCompany desde fuentes fijadas;
- arranque, RMI, disponibilidad del cliente y login;
- API autenticada cuando se modifica su contrato;
- smokes de runtime nativo macOS ARM64 y Linux; Windows cuando la extensión o el despliegue lo afecten;
- evidencia de conciliación contra una base local real antes de declarar aceptada una exportación productiva.

Las fixtures sintéticas son regresión automatizada, no sustituyen datos reales.

## Estado del repositorio — 25 de noviembre de 2026

Hay **9 ramas remotas**: `main`, una rama activa del PR #8 y siete ramas históricas. La comparación de contenido confirmó que estas siete últimas no deben volver a utilizarse para desarrollo; sus resultados útiles ya están incorporados en `main` o fueron superados por versiones posteriores:

- `diagnostic/docker-client-connectivity`
- `feature/mycompany-readonly-replenishment-adapter`
- `feature/order-line-replenishment-contract`
- `feature/projected-stock-replenishment-planner`
- `feature/stockout-aware-demand-planning`
- `fix/demo-pos-smoke-register-name`
- `test/complete-ci-regression-coverage`

La única rama funcional activa debe seguir siendo `feat/mycompany-readonly-replenishment-api` hasta que se acepte o descarte el PR #8. El PR todavía no está integrado: la compilación pasó y el login funciona en los smokes nativos, pero la API de exportación tiene pendiente resolver un HTTP 500 de lsFusion.

### Limpieza de las siete ramas históricas

Una vez sincronizado el clon local con `main`, se pueden eliminar las siete ramas históricas remotas sin tocar la rama activa del PR #8:

```bash
git switch main
git fetch origin --prune
git pull --ff-only origin main

git push origin --delete \
  diagnostic/docker-client-connectivity \
  feature/mycompany-readonly-replenishment-adapter \
  feature/order-line-replenishment-contract \
  feature/projected-stock-replenishment-planner \
  feature/stockout-aware-demand-planning \
  fix/demo-pos-smoke-register-name \
  test/complete-ci-regression-coverage

git fetch origin --prune
git branch -r
```

Después de integrar y verificar el PR #8, eliminar también su rama:

```bash
git push origin --delete feat/mycompany-readonly-replenishment-api
git fetch origin --prune
git branch -r
```

La limpieza de las ramas históricas es administrativa: no se vuelven a fusionar ni se pierden cambios ya integrados. No se deben borrar las ramas hasta comprobar que el PR #8 se encuentra preservado y que el clon local está sincronizado.

## Rutina por hito

**Inicio:** actualizar `main`, comprobar árbol limpio, crear una sola rama desde `main` y definir la aceptación.

**Desarrollo:** mantener el alcance concentrado y ejecutar pruebas focalizadas. Corregir sobre la misma rama mientras el PR siga siendo el único trabajo activo.

**Cierre:** revisar el diff, ejecutar validaciones completas, integrar por squash, verificar el resultado en `main` y eliminar la rama. Si falla la aceptación, no se abre otra rama para el mismo trabajo.
