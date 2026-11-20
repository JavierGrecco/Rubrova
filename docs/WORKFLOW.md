# Forma de trabajo

## Regla de ramas

El repositorio tiene una sola rama viva: `main`.

- No crear ramas de funcionalidades.
- No crear ramas de corrección, experimento o release.
- No mantener ramas paralelas.
- No dejar cambios pendientes en otra rama.
- Todo trabajo integrado y vigente queda en `main`.

El trabajo se prepara sobre una copia actualizada de `main`. Se revisa el cambio, se ejecutan validaciones, se comprueba que no se pierda trabajo existente y luego se registra mediante commits pequeños en `main`.

Esta regla es deliberada y tiene prioridad para este proyecto sobre flujos convencionales basados en múltiples ramas. No se usa force-push para reescribir la historia.

## Antes de modificar

1. Leer README y documento del módulo afectado.
2. Revisar el estado actual de `main`.
3. Comprobar si ya existe una solución o decisión equivalente.
4. Identificar impactos en datos, permisos, auditoría, integraciones y pruebas.
5. Definir cómo se comprobará el resultado.

## Durante el trabajo

Mantener cambios pequeños y enfocados; no mezclar grandes refactorizaciones con cambios funcionales sin motivo; usar términos claros del negocio; evitar abstracciones sin uso real; justificar dependencias por mantenimiento, licencia y seguridad; no guardar secretos ni datos reales; actualizar documentación cuando cambie el comportamiento.

## Antes de integrar en main

- Ejecutar formato, lint, análisis estático y pruebas afectadas.
- Ejecutar pruebas completas si cambia una regla transversal.
- Revisar diff, archivos generados y migraciones.
- Verificar permisos, efectos en inventario/dinero y auditoría.
- Revisar compatibilidad entre versiones de servicios y rollback de aplicación y datos por separado.
- Confirmar claridad de estados y mensajes.

## Commits

Prefijos preferidos: `docs:`, `feat:`, `fix:`, `refactor:`, `test:`, `build:`, `security:`.

Cada commit representa un cambio entendible. Evitar mensajes vagos.

## Revisiones y errores

La revisión se realiza sobre el diff de `main` antes de integrar. Para corregir algo ya integrado, crear commit correctivo o revertir con un commit; no reescribir historia compartida.

## Versiones y rollback

- Cada servicio libera un artefacto inmutable con versión, commit, digest, dependencias, SBOM y versión de esquema.
- Los tags de release identifican puntos de código aprobados; no sustituyen el backup de datos.
- Para revertir código ya integrado en main, preferir un commit correctivo o git revert. git revert registra el cambio inverso y conserva la historia compartida.
- No usar git reset --hard ni force-push para borrar historia compartida de main. reset sólo se considera para trabajo local aún no publicado y con conocimiento de los cambios que se descartan.
- El rollback de datos se realiza desde el catálogo de backups/PITR, restaurando primero a un entorno separado y conciliando las operaciones posteriores. Nunca se confunde git revert con restaurar una base.
- Un despliegue de servicio debe permitir volver a la versión estable anterior sin actualizar los otros servicios, siempre que los contratos y migraciones se hayan mantenido compatibles.
- Las migraciones destructivas se retrasan hasta cerrar la ventana de compatibilidad; se prefiere expand-contract y corrección forward antes que SQL inverso improvisado.

La diferencia entre rollback de código, recuperación de datos y compensación de efectos externos está especificada en [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md).

## Documentación y comunicación

Cada módulo explica responsabilidad, límites, entradas, salidas y pruebas. El roadmap refleja lo implementado, no lo deseado. Los ejemplos usan datos sintéticos.

Cada entrega comunica qué cambió, por qué, pruebas y resultados, qué no se verificó y siguiente paso. No se declara una función completa por tener código escrito.


## Reutilización de código abierto

No se copia ni agrega una dependencia solo porque el repositorio sea público o tenga una etiqueta de licencia en su portada.

Antes de integrar código externo:

1. Identificar el repositorio original, versión o commit y archivos que se pretende usar.
2. Leer la licencia efectiva, avisos, excepciones y licencias de dependencias transitivas.
3. Confirmar que el uso previsto —incluida modificación y distribución local— está permitido.
4. Revisar mantenimiento, seguridad, pruebas, compatibilidad y dependencias.
5. Explicar qué responsabilidad resuelve y cómo se reemplaza si deja de mantenerse.
6. Registrar origen, cambios y avisos en el inventario de terceros.
7. Agregar la prueba que demuestre que el componente cumple nuestros contratos.

Se prefieren dependencias y extensiones antes que modificar el núcleo de un proyecto externo. No se incorpora código GPL/AGPL al núcleo ni material Enterprise/comercial sin una decisión expresa y revisión legal. Tampoco se eliminan atribuciones exigidas por la licencia.

Ver [Estrategia de reutilización de código abierto](OPEN_SOURCE_STRATEGY.md) y [Calidad y pruebas](QUALITY_AND_TESTING.md).
