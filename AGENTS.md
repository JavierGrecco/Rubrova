# Instrucciones de trabajo para agentes y asistentes

Estas reglas aplican a toda tarea sobre Rubrova. No dependas de la memoria de una conversación ni supongas que conocés el repositorio por haber trabajado antes en él: verificá siempre el estado de `main` y los documentos vigentes.

## Lectura obligatoria antes de tocar código

1. Leer `README.md`.
2. Leer `docs/platform-audit/README.md`: es la puerta obligatoria del mapeo de MyCompany 6.2 y lsFusion 6.2.
3. Identificar el nombre exacto `MODULE` que se va a tocar y buscarlo en `docs/platform-audit/MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md`. Si no aparece en la tabla manual, ejecutar `node scripts/platform/module-integration-route.mjs --module NombreExacto`.
4. Leer la primera sección indicada por el directorio/CLI, el dossier principal, la ficha del módulo y los documentos transversales que el resultado recomiende. No empezar desde el nombre del archivo ni desde una suposición.
5. Leer `docs/ENGINEERING_MASTER.md` para conocer estado, evidencia, decisiones, contratos y roadmap.
6. Leer `docs/WORKFLOW.md` y confirmar los commits fijados en `platform/source-lock.json` y la composición real desde `extensions/lsfusion/RubrovaCustom.lsf`.



### Ruta obligatoria por módulo

Cuando una tarea mencione un módulo o archivo LSF concreto, usar el directorio por nombre exacto. El comando `module-integration-route.mjs` es la forma obligatoria de resolver cualquier módulo de los snapshots, incluidos los que no tienen ficha manual todavía. Revisar tanto `REQUIRE` (dependencia de código) como consumidores directos y relaciones de negocio (documentos/ledgers); no son equivalentes. Si la salida marca un módulo fuera de `RubrovaCustom`, no asumir que está cargado o habilitado. Cuando el módulo no tenga análisis suficiente, completar la ficha con `MODULE_INTEGRATION_PASSPORT_TEMPLATE.md` antes de aprobar el cambio.

## Regla reuse-first obligatoria

Antes de proponer, diseñar o implementar una función o integración:

- Buscar si MyCompany ya ofrece la capacidad, incluso fuera del cierre actual de `RubrovaCustom`.
- Buscar si lsFusion o sus clientes, APIs, herramientas, utilidades y mecanismos de extensión ya resuelven la necesidad.
- Seguir dependencias `REQUIRE`, extensiones, clases, propiedades, acciones, formularios, restricciones, eventos, permisos, APIs y recursos implicados.
- Revisar los flujos de extremo a extremo y sus documentos, estados, ledgers, reportes y efectos laterales.
- Revisar módulos regionales cuando puedan contener una integración o comportamiento reutilizable, sin asumir que cumplen requisitos argentinos.
- Elegir y registrar una decisión explícita: reutilizar, extender, adaptar, construir módulo propio, parchear upstream o incorporar una dependencia. Explicar la evidencia y el motivo.

**No inventes una carencia a partir de una búsqueda superficial.** Un módulo inventariado no equivale a una función comprendida; una función documentada no equivale a una función probada; un módulo en `REQUIRE` no equivale a una pantalla habilitada.

## Qué actualizar al terminar

En el mismo cambio:

- Actualizar el dossier de dominio con fuentes, módulos/rutas, relaciones, decisión y límites.
- Actualizar `docs/platform-audit/README.md` si cambia la cobertura o aparece/desaparece un dossier.
- Actualizar el estado, decisión, contrato, evidencia y roadmap en `docs/ENGINEERING_MASTER.md`.
- Agregar o ajustar pruebas que protejan la conclusión.
- Declarar qué no se revisó o probó.

Si una tarea no afecta las plataformas base, indicar por qué el gate de mapeo no aplica. Nunca afirmar que el mapeo completo está terminado mientras el índice marque pendientes.

## Precisión y seguridad

Distinguir fuente, documentación, build, composición, carga, comportamiento de runtime, conciliación y aceptación. No inferir permisos o seguridad por la existencia de una API o pantalla. No copiar secretos, datos personales ni dumps comerciales. Respetar licencias, atribuciones, snapshots y parches upstream.

## Fuente de verdad

`docs/ENGINEERING_MASTER.md` conserva estado, decisiones, contratos, evidencia y roadmap. `docs/platform-audit/README.md` navega los dossiers de mapeo. Los dossiers aportan detalle de fuente. Si se contradicen, informar y corregir la inconsistencia; no elegir silenciosamente la versión más conveniente.
