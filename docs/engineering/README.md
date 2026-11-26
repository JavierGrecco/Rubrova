# Base de conocimiento de ingeniería de Rubrova

**Estado:** norma de trabajo del repositorio  
**Ámbito:** arquitectura, módulos, APIs, eventos, integraciones, datos, pruebas y operación.

## Propósito

Rubrova debe conservar el conocimiento que genera su desarrollo. Una solución no queda completa cuando el test pasa: también debe quedar explicado qué contrato protege, qué regla de negocio respeta, qué hipótesis se descartó, qué versión condiciona la implementación y qué evidencia permite mantenerla sin repetir la investigación.

Esta documentación es parte del producto técnico. Se versiona en Git, se revisa en los pull requests y evoluciona junto con el código.

## Documentos

- [Auditoría de reutilización de la base incorporada](BASE_REUSE_AUDIT.md): catálogo de capacidades ya implementadas, APIs nativas, contratos, riesgos heredados y matriz de reutilización antes de desarrollar equivalentes.
- [Guía de integración lsFusion 6.2 + MyCompany 6.2](LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md): arquitectura real del runtime integrado, reglas de extensión, transacciones, comunicación externa y circuitos POS/venta/devolución/pago/caja/inventario.
- [Contratos de integración](CONTRACTS.md): reglas normativas de intercambio, propiedad de datos, seguridad, formatos, versiones y compatibilidad.
- [Mapa de dominios y relaciones](DOMAIN_RELATIONSHIPS.md): propiedad de datos, relaciones observadas, claves y dependencias entre módulos.
- [Registro de decisiones](DECISION_LOG.md): decisiones técnicas/arquitectónicas con contexto, alternativas, fundamento, consecuencias y estado.
- [Registro de iteraciones](ITERATION_LOG.md): investigaciones cronológicas con síntoma, evidencia, diagnóstico, cambio y validación.
- [Plantilla de registro](RECORD_TEMPLATE.md): estructura para nuevas decisiones e iteraciones.

## Cómo clasificar lo que sabemos

Todo registro debe distinguir explícitamente:

| Clasificación | Significado | Cómo escribirlo |
|---|---|---|
| **Hecho observado** | Lo que un log, test, fuente o ejecución demuestra | Adjuntar ruta, commit, run, versión y fragmento relevante |
| **Interpretación** | Explicación razonable de los hechos | Explicar el razonamiento y qué evidencia la sostiene |
| **Hipótesis** | Posible causa todavía no demostrada | Marcarla como pendiente; no convertirla en regla |
| **Decisión** | Regla que el proyecto adopta | Registrar responsable/alcance, motivo y consecuencias |
| **Pendiente** | Dato o prueba que falta | Indicar el criterio concreto de cierre |

Una compilación correcta no demuestra que el servidor pueda cargar la lógica. Un HTTP 200 no demuestra que el cuerpo cumpla el contrato. Un job en verde con continue-on-error no demuestra que el escenario funcional haya sido aceptado.

## Reglas para cada cambio

Cada pull request que altere lógica, datos, una integración o una API debe responder:

1. ¿Qué contrato o regla de negocio cambia?
2. ¿Quién produce el dato y quién es su propietario?
3. ¿Qué módulos, procesos y consumidores dependen de él?
4. ¿Es compatible hacia atrás? ¿Cómo se versiona y migra?
5. ¿Qué ocurre con NULL, campos ausentes, listas vacías, duplicados, reintentos y datos parciales?
6. ¿Qué sucede ante timeout, caída, reinicio, concurrencia o respuesta tardía?
7. ¿Qué pruebas demuestran el comportamiento y qué entorno/versión se ejecutó?
8. ¿Cómo se diagnostica, revierte y recupera el cambio?

Si no se modifica un contrato, el PR debe indicarlo. Si se descubre una regla, aunque no haya cambio de código, se registra.

## Regla de documentación continua

- Los contratos describen el comportamiento que los módulos deben cumplir; no se escriben como una narración de una ejecución.
- El registro de decisiones conserva el porqué. No se reescriben decisiones históricas para que parezcan correctas a posteriori; se marcan como reemplazadas y se agrega una nueva.
- El registro de iteraciones conserva el orden real de los descubrimientos, incluidos los intentos fallidos y las hipótesis descartadas.
- Una corrección sólo se registra como validada cuando la prueba pertinente se ejecutó sobre el commit identificado.
- Las referencias a CI deben incluir URL del run y SHA probado; los artefactos deben identificarse por nombre y digest cuando sean relevantes.
- No copiar secretos, tokens, contraseñas, datos personales ni dumps productivos en los documentos o logs.
- Si se descubre que una conclusión anterior era incorrecta, se corrige de forma visible y se documenta qué evidencia cambió la interpretación.

## Comunicación entre módulos y equipos

La comunicación debe ser explícita, versionada y observable. En Rubrova hay que distinguir entre módulos LSF de una misma instancia integrada y servicios/procesos externos:

- **Módulos LSF internos:** se conectan mediante dependencias REQUIRE, clases, propiedades, acciones, eventos, constraints y puntos abstractos de extensión. Consumen el contrato lógico público del módulo dueño. No se llama por HTTP a un módulo que ya participa de la misma instancia.
- **Servicios externos o procesos independientes:** se comunican mediante APIs/eventos/archivos versionados; definen autenticación, permisos, esquema, timeout, idempotencia, correlación, errores y compatibilidad.
- El productor es dueño del significado, formato, unidad y ciclo de vida del dato que publica.
- Consultas y comandos se distinguen. Una consulta no debe producir efectos de negocio.
- Los eventos notifican hechos ya ocurridos; no sustituyen a una respuesta síncrona cuando el consumidor necesita confirmar un comando.
- Los efectos externos deben ser idempotentes o llevar una clave de idempotencia estable.
- Los mensajes deben conservar identificador de correlación y referencias a la operación de origen.
- Los reintentos requieren timeout finito, política explícita y protección contra duplicados.
- En el runtime integrado no se escriben tablas físicas por SQL para eludir el modelo lógico y sus reglas. Para servicios independientes no se comparten tablas ni se realizan escrituras cruzadas.
- Los errores deben permitir distinguir rechazo funcional, falta de autenticación/autorización, timeout, indisponibilidad, conflicto y fallo de validación.
- Los cambios incompatibles requieren versión nueva o migración coordinada; nunca se cambia silenciosamente el significado de un campo.

Para detalles del contrato de módulo lsFusion, sus extensiones y los circuitos nativos MyCompany 6.2, seguir la [guía de integración](LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md).

## Calidad de la evidencia

Los niveles de evidencia son distintos y no se sustituyen entre sí:

1. análisis estático;
2. tests unitarios;
3. tests de contrato;
4. compilación de todas las fuentes;
5. carga real de módulos y arranque del servidor;
6. pruebas HTTP autenticadas;
7. integración contra una base real/sintética controlada;
8. pruebas de extremo a extremo;
9. pruebas en equipos físicos y con periféricos reales;
10. operación prolongada, backup y restauración.

Cada afirmación de aceptación debe nombrar el nivel alcanzado y las limitaciones restantes.

## Incorporación de conocimiento

Al cerrar una investigación:

1. agregar el resultado cronológico en ITERATION_LOG.md;
2. crear o actualizar una decisión en DECISION_LOG.md cuando cambie una regla;
3. actualizar CONTRACTS.md si cambia el acuerdo entre componentes;
4. modificar tests para proteger el nuevo aprendizaje cuando sea automatizable;
5. vincular la documentación desde el PR y actualizarla en el mismo cambio.

No esperar al final del proyecto: documentar en la misma iteración en que aparece el conocimiento.

## Prevalidación local repetible

Ejecutar desde la raíz:

~~~bash
bash scripts/platform/local-preflight.sh
~~~

Para aislar una capa:

~~~bash
bash scripts/platform/local-preflight.sh --platform
bash scripts/platform/local-preflight.sh --replenishment
~~~

El workflow de plataforma y el de reposición llaman a este mismo script, para que los comandos usados antes de publicar sean los mismos que ejecuta CI. El resultado sólo cubre análisis estático, pruebas locales y fixtures; la carga del módulo, el servidor y la API autenticada siguen siendo una puerta de runtime independiente.
