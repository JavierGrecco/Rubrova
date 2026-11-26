# Política de ramas e integración

**Revisión:** 26 de noviembre de 2026  
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

## Estado del repositorio — 26 de noviembre de 2026

La rama canónica `main` quedó en `ac758d01` después de integrar el backup lógico PostgreSQL y la prueba nativa de restauración. En ese punto el repositorio tenía una sola rama y cero PR abiertos.

El único trabajo funcional en curso es `work/retail-return-quantity-guard`, creado desde ese SHA. Su objetivo es activar el límite de devolución acumulada en el tipo de comprobante minorista mediante `RubrovaRetailControls`, sin editar el código upstream de CreditNote. Esta rama está en preparación y todavía debe superar los gates antes de integrarse.

No deben revivirse ramas de los antiguos PR #8/#10 ni ramas históricas de reposición. Su trabajo útil ya está integrado en `main`. Antes de cerrar este hito, se debe crear un solo PR corto hacia `main`, comprobar el diff y esperar la evidencia de preflight, compilación y smoke nativo.

## Rutina por hito

**Inicio:** actualizar `main`, comprobar árbol limpio, crear una sola rama desde `main` y definir la aceptación.

**Desarrollo:** mantener el alcance concentrado y ejecutar pruebas focalizadas. Corregir sobre la misma rama mientras el PR siga siendo el único trabajo activo.

**Cierre:** revisar el diff, ejecutar validaciones completas, integrar por squash, verificar el resultado en `main` y eliminar la rama. Si falla la aceptación, no se abre otra rama para el mismo trabajo.
