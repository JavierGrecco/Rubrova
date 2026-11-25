# Política de ramas e integración

**Vigencia:** 25 de noviembre de 2026  
**Rama canónica:** `main`

## Objetivo

Mantener una única línea de desarrollo fácil de revisar, probar, ejecutar localmente y recuperar. Ninguna funcionalidad se considera integrada hasta que sus cambios estén en `main`.

## Reglas operativas

1. **`main` es la fuente de verdad.** Debe contener el último estado integrado y validado. El código funcional se desarrolla en una rama y entra por PR; sólo se permiten commits directos excepcionales para documentación de gobernanza y mantenimiento administrativo del repositorio, sin alterar código de aplicación.
2. **Máximo dos ramas de trabajo activas en simultáneo.** Preferentemente una sola rama de funcionalidad. La segunda se reserva para una corrección urgente e independiente; no se crean ramas auxiliares por cada commit o ajuste.
3. **Cada rama nace del `main` actualizado.** Antes de crearla se sincroniza `main`; no se apilan ramas de funcionalidades dependientes ni se abren PR encadenados.
4. **Un PR por unidad coherente de trabajo.** Debe indicar objetivo, alcance, riesgos, pruebas ejecutadas, resultado y limitaciones conocidas. Los cambios deben apuntar directamente a `main`.
5. **Integración por hitos, no por cada commit.** Se acumulan cambios relacionados en la rama activa, se ejecutan las validaciones correspondientes y se integra el hito completo cuando la evidencia es suficiente.
6. **Preferir squash merge.** Cada hito queda representado por un commit legible en `main`, sin arrastrar una secuencia de commits de prueba, correcciones intermedias o merges de ramas.
7. **Eliminar la rama de trabajo después de integrar.** No mantener ramas históricas como lugares alternativos de desarrollo. Antes de eliminar una rama, comprobar que su contenido útil está en `main` o preservado en otro PR activo.
8. **No fusionar ramas obsoletas en bloque.** Comparar su contenido real con `main`; los commits divergentes no implican necesariamente trabajo pendiente. Recuperar selectivamente cualquier cambio que todavía aporte valor y no esté integrado.
9. **No declarar aceptación por pruebas parciales.** Separar pruebas estáticas, unitarias, compilación, arranque, API autenticada y smoke funcional. Un resultado verde de una capa no sustituye las demás.

## Convención de nombres

- `work/<area>-<objetivo>`: rama principal de la siguiente funcionalidad.
- `fix/<area>-<problema>`: única rama secundaria, sólo para una corrección urgente e independiente.

Los nombres deben ser cortos, estables y representar un objetivo, no un experimento temporal.

## Puerta de aceptación

La validación se adapta al alcance, pero para cambios del runtime MyCompany la aceptación debe incluir:

- validaciones estáticas y pruebas de contrato;
- suites Python y pruebas de regresión afectadas;
- compilación del servidor, cliente GWT y lógica MyCompany desde las fuentes fijadas;
- smoke de arranque y disponibilidad del cliente;
- llamada autenticada a la API cuando se modifica su contrato;
- ejecución en Linux y Apple Silicon, además de Windows cuando la extensión o el despliegue lo afecten;
- evidencia de conciliación contra una base local real antes de declarar validada la exportación productiva.

Las fixtures sintéticas sirven para regresión, no reemplazan la conciliación con datos reales.

## Aplicación al estado actual

- Los PR #5, #6 y #7 ya integraron el planificador, el adaptador inicial y la consolidación de compromisos por línea en `main`.
- Las ramas antiguas de esos trabajos deben tratarse como históricas: no volver a fusionarlas sin una diferencia concreta y útil.
- El PR #8 es la única integración funcional pendiente. Se acepta sólo después de completar la compilación, el arranque, la API autenticada y los smokes requeridos.
- Una vez aceptado el PR #8, se debe limpiar el conjunto de ramas históricas y continuar con una sola rama de trabajo activa (dos sólo cuando exista un hotfix independiente).

## Limpieza de las ramas históricas actuales

La comparación de archivos contra `main` confirmó que las siguientes ramas contienen versiones anteriores o contenido ya integrado. No deben volver a usarse para desarrollo:

- `diagnostic/docker-client-connectivity`
- `feature/mycompany-readonly-replenishment-adapter`
- `feature/order-line-replenishment-contract`
- `feature/projected-stock-replenishment-planner`
- `feature/stockout-aware-demand-planning`
- `fix/demo-pos-smoke-register-name`
- `test/complete-ci-regression-coverage`

La rama `feat/mycompany-readonly-replenishment-api` se conserva mientras el PR #8 siga abierto. Las otras siete ramas ya se verificaron como históricas y se pueden eliminar ahora, dejando sólo `main` y la rama del PR #8:

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

Después de fusionar y verificar el PR #8, retirar también su rama de trabajo:

```bash
git push origin --delete feat/mycompany-readonly-replenishment-api
git fetch origin --prune
git branch -r
```

Ejecutar cada borrado sólo después de comprobar el estado indicado. No crear ramas nuevas para revivir estos trabajos: toda continuación parte del `main` actualizado.

```bash
git switch main
git fetch origin --prune
git pull --ff-only origin main
git push origin --delete \
  diagnostic/docker-client-connectivity \
  feat/mycompany-readonly-replenishment-api \
  feature/mycompany-readonly-replenishment-adapter \
  feature/order-line-replenishment-contract \
  feature/projected-stock-replenishment-planner \
  feature/stockout-aware-demand-planning \
  fix/demo-pos-smoke-register-name \
  test/complete-ci-regression-coverage
git fetch origin --prune
git branch -r
```


## Rutina de inicio y cierre de cada hito

**Inicio:** actualizar `main`, revisar el estado limpio del árbol, crear una rama de trabajo desde `main` y definir criterios de aceptación.

**Durante:** mantener el alcance concentrado, ejecutar pruebas focalizadas y evitar abrir ramas paralelas para correcciones menores.

**Cierre:** ejecutar el conjunto de validaciones del hito, revisar el diff completo, integrar mediante PR a `main`, verificar el commit resultante y eliminar la rama de trabajo. Si la aceptación falla, la rama sigue siendo la única rama activa hasta resolverlo.
