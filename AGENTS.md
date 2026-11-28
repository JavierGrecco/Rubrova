# Instrucciones de trabajo para agentes y asistentes

Estas reglas aplican a toda tarea sobre Rubrova. No dependas de la memoria de una conversación ni supongas que conocés el repositorio por haber trabajado antes en él: verificá siempre el estado de `main` y los documentos vigentes.

## Lectura obligatoria antes de tocar código

1. Leer `README.md`.
2. Leer `docs/platform-audit/README.md`: es la puerta obligatoria del mapeo de MyCompany 6.2 y lsFusion 6.2.
3. Leer `docs/ENGINEERING_MASTER.md` para conocer estado, evidencia, decisiones, contratos y roadmap.
4. Leer `docs/WORKFLOW.md` y el dossier de cada dominio afectado.
5. Confirmar los commits fijados en `platform/source-lock.json` y la composición real desde `extensions/lsfusion/RubrovaCustom.lsf`.

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
