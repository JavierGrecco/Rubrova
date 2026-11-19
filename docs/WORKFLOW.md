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
- Revisar compatibilidad y rollback de migración.
- Confirmar claridad de estados y mensajes.

## Commits

Prefijos preferidos: `docs:`, `feat:`, `fix:`, `refactor:`, `test:`, `build:`, `security:`.

Cada commit representa un cambio entendible. Evitar mensajes vagos.

## Revisiones y errores

La revisión se realiza sobre el diff de `main` antes de integrar. Para corregir algo ya integrado, crear commit correctivo o revertir con un commit; no reescribir historia compartida.

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
