# Política de ramas e integración

**Revisión:** 26 de noviembre de 2026  
**Rama canónica:** `main`  
**Límite operativo:** `main` como única línea persistente; ramas temporales sólo para cambios aislados y con cierre inmediato.

## Objetivo

Mantener una línea principal fácil de revisar, probar, ejecutar localmente y recuperar. Ningún cambio de aplicación se considera integrado hasta que esté en `main`.

## Reglas

1. **`main` es la única fuente de verdad y la rama persistente.** No mantener ramas de desarrollo abiertas cuando el hito ya está integrado.
2. **Ramas temporales sólo por necesidad de revisión aislada.** Deben nacer del SHA actual de `main`, tener alcance único y cerrarse al terminar.
3. **No apilar funcionalidades ni PR encadenados.** Cada cambio se valida contra la revisión exacta que se pretende integrar.
4. **Integrar pronto y de forma coherente.** Revisar el diff, ejecutar preflight, build y smoke afectados; actualizar `main` sólo con evidencia.
5. **Eliminar referencias temporales al integrar.** Cerrar PR y borrar la rama en el mismo hito; no acumular ramas históricas.
6. **No revivir ramas por su historial.** Recuperar selectivamente sólo contenido que falte y comprobarlo contra `main`.
7. **No confundir CI verde con aceptación funcional.** Separar unitarias, compilación, arranque, login, API autenticada, smoke POS y conciliación de datos.
8. **Mantener una vía de recuperación.** Los cambios de runtime/esquema deben tener backup antes de migraciones y evidencia de restore.

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

La consulta actual a GitHub confirma:

- Ramas remotas visibles: **1**, únicamente `main`.
- Pull requests abiertos: **0**.
- SHA actual: `ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a`.
- El workflow [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó correctamente.

No hay ramas feature pendientes de integrar. No se deben ejecutar los comandos históricos de borrado que aparecían en versiones anteriores de esta guía: ya no describen el estado actual.

### Protección de la rama principal

La API de GitHub informa `protected: false` para `main`. Tener una única rama no impide por sí solo un push directo ni obliga a que pasen los checks. La protección de rama/ruleset debe activarse desde GitHub Settings por alguien con permisos administrativos. La política recomendada es exigir los workflows aplicables, impedir force-push y exigir revisión cuando haya más colaboradores. No se declara esa protección activa hasta verificarla.

## Rutina por hito

**Inicio:** actualizar `main`, comprobar árbol limpio, crear una sola rama desde `main` y definir la aceptación.

**Desarrollo:** mantener el alcance concentrado y ejecutar pruebas focalizadas. Corregir sobre la misma rama mientras el PR siga siendo el único trabajo activo.

**Cierre:** revisar el diff, ejecutar validaciones completas, integrar por squash, verificar el resultado en `main` y eliminar la rama. Si falla la aceptación, no se abre otra rama para el mismo trabajo.
