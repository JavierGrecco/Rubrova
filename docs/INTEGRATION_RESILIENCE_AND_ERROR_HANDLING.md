# Resiliencia de integraciones y tratamiento de errores

**Política obligatoria:** un proveedor externo puede fallar, demorarse, responder mal o desaparecer sin arrastrar al POS/ERP local. Cada integración debe tener límites de tiempo, manejo explícito de errores, aislamiento, trazabilidad y recuperación. No se considera terminada una integración que sólo funciona cuando todo está disponible.

## 1. Qué significa que la aplicación no falle

No es realista prometer que ningún error imaginable ocurrirá. Sí debemos exigir que los fallos previsibles y los inesperados queden contenidos en el límite donde se producen:

- Una respuesta lenta o ausente termina dentro de un plazo definido.
- Una excepción externa no llega sin control a la interfaz ni derriba el proceso de Rubrova.
- El usuario recibe un mensaje breve, entendible y con una acción siguiente.
- El detalle técnico queda registrado para diagnóstico, con correlación, pero sin secretos ni datos sensibles.
- El estado de la operación queda persistido: pendiente, confirmado, rechazado, incierto o requiere intervención.
- No se repite automáticamente una operación que podría producir un cobro, pedido, factura, envío o movimiento duplicado.
- Una integración caída no bloquea otras áreas ni las operaciones locales que no dependen de ella.
- Al recuperarse el proveedor, el trabajo pendiente se reanuda de manera controlada y conciliable.

Los límites de fallo se establecen por proveedor, cuenta, operación y módulo. No se usa un único manejador gigante que oculte errores ni se deja que cada módulo invente criterios incompatibles.

## 2. Política de tiempos de espera

lsFusion 6.2 dispone de timeoutHttp() para configurar en milisegundos el tiempo de espera de llamadas HTTP. El motor usa ese límite para conexión y respuesta. TRY/CATCH permite capturar el error resultante. El valor predeterminado upstream del motor era de 30 minutos, demasiado alto para una aplicación operativa. Rubrova lo reemplaza en el punto central de ejecución: 10 segundos por defecto y un máximo absoluto de 60 segundos incluso si un módulo intenta solicitar más. Si la propiedad recibe un valor menor que 1 ms se limita a 1 ms. Esto incluye los `EXTERNAL HTTP` heredados. Además, los adaptadores propios deben establecer un timeout explícito antes de cada solicitud mediante rubrovaSetIntegrationTimeout(), que rechaza valores menores a 1 ms o mayores a 30.000 ms. El límite global es una red de seguridad, no reemplaza el manejo de errores de cada operación.

| Contexto | Timeout por intento | Tiempo total máximo | Tratamiento |
|---|---:|---:|---|
| Consulta remota que espera una persona | 3–5 s | 6–8 s | Un intento; como máximo otro si es lectura segura y queda dentro del presupuesto |
| Acción remota no crítica iniciada desde una pantalla | 3–5 s | 8 s | Preferir encolar y mostrar estado; no mantener la pantalla esperando |
| Sincronización en segundo plano | 8–10 s | 30 s por ciclo | Hasta 3 intentos seguros con espera acotada |
| Descarga/importación grande | 10–20 s por bloque | Límite configurable | Paginación, bloques, checkpoint y reanudación |
| Operación crítica de pago/fiscal/alta externa | Según contrato del proveedor, con límite estricto | Presupuesto por operación | No repetir ciegamente; usar idempotencia y consulta de estado |

Ninguna pantalla queda esperando un timeout ilimitado. El motor impone 10 s por defecto / 60 s como máximo por llamada. Si una operación es larga, se ejecuta como tarea durable y el usuario puede seguir trabajando; no se amplía el timeout a minutos u horas.

Los adaptadores GET ya pueden utilizar rubrovaHttpGet(provider, operation, correlation, url, timeoutMs): inicializa el resultado, valida el límite, ejecuta EXTERNAL HTTP GET dentro de TRY/CATCH y registra tanto una respuesta HTTP no exitosa como un fallo de red/timeout. Devuelve rubrovaHttpSucceeded(), rubrovaHttpResponse(), rubrovaHttpFailureCategory() y rubrovaHttpFailureMessage() sin lanzar la excepción externa al llamador. No hace reintentos automáticos. Para otros métodos y parsing, el adaptador debe rodear cada paso con TRY/CATCH y registrar los fallos de contrato por separado. El helper registra la incidencia en una sesión independiente; si la base de incidencias no responde, intenta un log local de emergencia. El detalle registrado por la ruta común es deliberadamente saneado: no persiste la URL completa, el cuerpo ni la excepción cruda porque podrían contener secretos.

El tiempo total incluye conexión, respuesta, reintentos y pausas. No alcanza con fijar un timeout por intento y permitir una cantidad ilimitada de reintentos.

### Camino de HTTP ejecutado por el navegador

Las llamadas `EXTERNAL HTTP CLIENT` atraviesan una ruta distinta: el servidor convierte `HttpClientAction` en `GHttpClientAction` y el navegador realiza la petición con `XMLHttpRequest`. El timeout se propaga ahora junto a la acción, el cliente GWT aplica el mismo máximo de 60 segundos y un temporizador aborta la petición si no termina. El callback se completa una sola vez tanto en timeout como en respuesta/error de red; la respuesta sin HTTP se devuelve con estado 0 y cuerpo ausente (`null`) para que la capa lsFusion la convierta en excepción capturable por `TRY/CATCH` sin intentar interpretar bytes inexistentes.

La ruta usa `XMLHttpRequest` y no `RequestBuilder` porque el cliente actual necesita conservar respuestas binarias (`arraybuffer`). GWT documenta un timeout nativo en `RequestBuilder`, pero su API de alto nivel no reemplaza sin más este contrato binario. La prueba estática confirma la propagación y la compilación GWT del módulo web-client debe aprobarse en el build del fork antes de considerar esta corrección validada en runtime.

## 3. Cuándo reintentar

Los reintentos son limitados, medidos y dependen de la semántica de la operación.

| Resultado | Acción |
|---|---|
| Timeout, DNS, conexión rechazada o conexión interrumpida | Reintentar sólo lectura segura o escritura protegida por idempotencia |
| HTTP 408, 425 | Error remoto transitorio; reintento diferido y acotado. Respetar Retry-After cuando corresponda |
| HTTP 429 | Límite del proveedor; respetar Retry-After y reducir concurrencia |
| HTTP 500, 502, 503, 504 | Considerar transitorio; reintentar sólo si repetir no duplica efectos |
| HTTP 400 / 422 | Error de validación o contrato; no reintentar sin corregir datos |
| HTTP 401 / 403 | Detener; renovar credenciales una vez si el flujo lo permite o pedir reconexión |
| HTTP 404 | Resolver según contrato; no reintentar en bucle |
| HTTP 409 | Conciliar versión/estado y resolver conflicto; no repetir a ciegas |
| JSON inválido o campos obligatorios ausentes | Capturar, poner en cuarentena, registrar versión de contrato y no aplicar parcialmente |
| Certificado TLS inválido o hostname no coincidente | Fallar cerrado; nunca desactivar verificación SSL para hacerlo funcionar |
| Error persistente de negocio | Marcar rechazado o acción requerida |

Para operaciones reintentables se aplica backoff exponencial limitado con jitter. Se respeta Retry-After, sea segundos o fecha HTTP. Se establece un número máximo de intentos y una fecha de próximo intento.

**No todos los POST son reintentables.** Una operación de creación, cobro, emisión o despacho puede haberse completado aunque se haya perdido la respuesta. Sólo se reintenta si el proveedor soporta una clave idempotente estable o si primero se consulta el estado usando una referencia externa. La misma clave y el mismo contenido deben producir el mismo resultado; la misma clave con contenido diferente debe generar conflicto.

## 4. Circuit breaker y aislamiento

Cada proveedor/cuenta dispone de un circuito independiente:

- **Cerrado:** solicitudes permitidas; se miden errores y latencia.
- **Abierto:** después del umbral configurado de fallos transitorios, se dejan de enviar solicitudes y se devuelve un resultado degradado inmediatamente.
- **Semia-bierto:** tras el intervalo de espera, se permite una única prueba; según el resultado se cierra o vuelve a abrir.

El estado del circuito, contador de fallos y próxima prueba se persisten localmente para que un reinicio no provoque una tormenta de solicitudes. Debe haber aislamiento por proveedor y por operación: una falla de Mercado Libre no abre el circuito de Mercado Pago, ARCA ni del POS local.

La cola de trabajo tiene concurrencia limitada, límites por proveedor y prioridad. Si Mercado Libre está caído, no se consumen todos los hilos esperando respuestas. Los trabajos pendientes no se procesan en un bucle agresivo cuando vuelve la conexión.

## 5. Operaciones locales y externas

El POS/ERP local no debe ejecutar una llamada de Internet dentro de la transacción que registra la venta o afecta stock/caja. La operación local se valida y confirma primero; el evento para el proveedor queda en una Outbox durable en la misma transacción. Un trabajador independiente intenta sincronizarlo.

Estados mínimos del trabajo externo:

- PENDIENTE: creado localmente, todavía no enviado.
- EN_PROCESO: tomado por un trabajador con lease y vencimiento.
- CONFIRMADO: el proveedor devolvió evidencia suficiente y se guardó el ID externo.
- RECHAZADO: el proveedor rechazó definitivamente los datos o permisos.
- REINTENTO_PROGRAMADO: fallo transitorio, con número y fecha del próximo intento.
- INCIERTO: pudo haber surtido efecto externo pero no se conoce el resultado; requiere consulta, nunca reenvío ciego.
- REQUIERE_ATENCION: venció la política automática o precisa decisión humana.

La Outbox guarda clave idempotente, proveedor/cuenta, tipo de operación, ID local, payload versionado o referencia segura, hash del contenido, correlación, cantidad de intentos, última respuesta y próximo intento. Los secretos se resuelven al enviar; nunca se copian al payload de auditoría.

Las operaciones locales continúan disponibles cuando el proveedor no responde. La excepción son funciones cuyo resultado exige autorización remota: un cobro con tarjeta/QR no puede marcarse como pagado sin confirmación. En ese caso se bloquea o deja incierto ese medio de pago, no todo el POS; el operador puede utilizar otro medio permitido, como efectivo, sujeto a las reglas del negocio.

## 6. Ejemplo: Mercado Libre no responde

Si Mercado Libre se encuentra caído o la API excede el límite:

1. La llamada termina por timeout dentro del presupuesto.
2. El adaptador captura el error y clasifica si es red, timeout, 429, 5xx, autorización, validación o conflicto.
3. Se actualiza el estado local y el trabajo Outbox queda pendiente o reintentable.
4. Se abre el circuito cuando corresponde y no se siguen acumulando solicitudes lentas.
5. El usuario recibe un aviso, sin perder la venta ni quedar bloqueado en una pantalla.
6. El panel muestra que Mercado Libre está degradado, último intento, siguiente reintento y cantidad de elementos pendientes.
7. Cuando vuelve el servicio, la cola retoma en orden y concilia pedidos, cantidades, precios, facturación y referencias externas.
8. Si una creación pudo haber sido aceptada, se consulta antes de volver a crearla.

Mensaje normal:

> Mercado Libre no está respondiendo. La operación local quedó guardada y la sincronización está pendiente. No necesitás repetirla.

Resultado incierto:

> No pudimos confirmar la respuesta de Mercado Libre. La operación quedó pendiente de verificación para evitar duplicados.

El texto no afirma que el proveedor haya creado, cobrado o aceptado algo que aún no confirmó.

## 7. Catálogo común de fallos

Cada borde de Rubrova convierte errores técnicos en categorías estables:

| Categoría | Ejemplos | Respuesta del sistema |
|---|---|---|
| TIMEOUT | Conexión o respuesta excedió plazo | Fallido o incierto según operación; deadline cumplido |
| NETWORK_UNAVAILABLE | DNS, ruta, conexión rechazada/reset | Degradar proveedor; mantener tarea pendiente |
| RATE_LIMITED | 429, cuota excedida | Respetar Retry-After y limitar concurrencia |
| REMOTE_5XX | Servicio remoto 5xx | Backoff y circuit breaker |
| AUTHENTICATION | Token vencido, 401 | Renovación controlada o reconexión |
| AUTHORIZATION | 403, alcance insuficiente | No reintentar; requerir corrección |
| VALIDATION | 400/422, datos inválidos | Mostrar qué campo corregir |
| CONFLICT | 409, versión o estado divergente | Consultar autoridad y conciliar |
| CONTRACT_INVALID | JSON ilegible, esquema incompatible | Cuarentena; no aplicar parcialmente |
| TLS_SECURITY | Certificado/host no válido | Fallar cerrado y alertar |
| DUPLICATE | Webhook/comando repetido | Devolver resultado idempotente |
| DATABASE_TRANSIENT | Lock, deadlock, desconexión corta | Reintentar transacción local sólo si es seguro |
| DATABASE_PERMANENT | Restricción, esquema o datos inválidos | Rechazar; no repetir en bucle |
| STORAGE | Disco lleno, permisos o I/O | Proteger datos, detener escritura afectada y avisar |
| RESOURCE_EXHAUSTED | Memoria, hilos, conexiones, cola | Limitar carga; aislar módulo y alertar |
| HARDWARE_UNAVAILABLE | Impresora, lector, balanza, terminal | Informar periférico afectado; conservar operación |
| INTERNAL_UNEXPECTED | Excepción no prevista | Capturar en límite superior, registrar incidente protegido |
| PROCESS_INTERRUPTED | Cierre inesperado o reinicio | Recuperar por persistencia, leases e idempotencia |

Los errores de validación no se disfrazan como errores de red. Los problemas permanentes no se reintentan. Los errores inesperados no se suprimen: generan evidencia, alertas y una ruta de recuperación.

## 8. Mensajes y diagnóstico

El usuario recibe un mensaje con qué función está disponible o no, si sus datos quedaron guardados, si la operación está confirmada/pendiente/incierta, qué puede hacer ahora y un código de incidente para soporte.

Ejemplos:
- "No se pudo conectar con el servicio de Mercado Libre. Las ventas locales siguen funcionando."
- "La impresora no respondió. La venta quedó registrada; podés reimprimir el comprobante."
- "No se pudo confirmar el cobro. No vuelvas a cobrar todavía; estamos verificando el estado."
- "No hay espacio suficiente para guardar la copia de seguridad. Liberá espacio o elegí otro destino."

El registro técnico conserva fecha UTC, proveedor/servicio, operación, intento, status HTTP, duración, clase de excepción, código, correlación, versión de contrato y stack trace cuando corresponde. No conserva contraseñas, tokens, certificados, claves, CVV, cookies, encabezados de autorización ni payloads sensibles en crudo. Se guardan hashes, referencias y fragmentos saneados si son necesarios.

Si también falla la escritura en la base local, el manejador no debe provocar una cascada. Se usa un registro local de emergencia rotativo, limitado y protegido, más el supervisor de proceso. No se finge que la incidencia quedó persistida en la base.

## 9. Protección del propio Rubrova

El mismo criterio se aplica a fallos internos: validar entrada antes de abrir transacción; encapsular operaciones y clasificar errores; limitar consultas, importaciones, exportaciones, hilos, memoria y tamaño de payload; capturar excepciones en el borde de cada módulo/tarea y en el límite superior UI/API; no mostrar stack traces, SQL ni paths internos; no continuar una transacción parcialmente válida; registrar incidente, correlación, módulo, versión y acción.

Un fallo de impresión, sincronización o reporte no puede revertir una venta ya confirmada. Health checks y reinicio supervisado ayudan si un proceso se detiene, pero no sustituyen la recuperación de estado. Si no se puede determinar un resultado con seguridad, se conserva como INCIERTO y se concilia; nunca se inventa un resultado.

## 10. Pruebas obligatorias de fallos

Cada conector se prueba contra un servidor falso local o simulador que controle el tiempo y la respuesta. No dependemos de que Mercado Libre, ARCA o un banco estén caídos el día del test.

| ID | Falla inyectada | Resultado exigido |
|---|---|---|
| ER01 | Conexión bloqueada/puerto sin listener | Termina dentro del plazo; POS continúa |
| ER02 | DNS inválido | Error clasificado, sin caída general |
| ER03 | Conexión aceptada pero no responde | Timeout aplicado; sin espera indefinida |
| ER04 | Respuesta lenta antes/después del límite | Cumplir deadline total |
| ER05 | Reset después de enviar el cuerpo | Lectura segura reintentable; escritura incierta |
| ER06 | 429 con Retry-After en segundos | Pausar y programar; no bombardear |
| ER07 | 429 con Retry-After como fecha HTTP | Interpretar fecha y respetar límite |
| ER08 | 500/502/503/504 | Backoff limitado y circuit breaker |
| ER09 | 400/401/403/404/409/422 | Clasificación correcta; no retry indiscriminado |
| ER10 | TLS inválido/certificado vencido/hostname erróneo | Fallar cerrado; no desactivar validación |
| ER11 | JSON roto, campos ausentes o tipos inesperados | Cuarentena; no aplicar mitad del payload |
| ER12 | Mismo webhook/comando repetido y concurrente | Un único efecto local |
| ER13 | Timeout después de que el proveedor procesó el POST | Consultar por clave; jamás crear/cobrar otra vez |
| ER14 | Proveedor cae y vuelve | Circuito abre/cierra; backlog se drena con límite |
| ER15 | Caída de Mercado Libre durante sincronización | Caja y catálogo local siguen utilizables |
| ER16 | Token vencido durante tarea | Renovación controlada; si falla, pedir reconexión |
| ER17 | Base desconectada/lock/deadlock | Rollback seguro; retry sólo transacción idempotente |
| ER18 | Disco lleno al persistir/log/backup | No informar éxito; aviso y recuperación |
| ER19 | Cola saturada y trabajador detenido | Backpressure; POS no consume todos los hilos |
| ER20 | Impresora/lector/balanza desconectados | Mensaje específico y continuidad del resto |
| ER21 | Excepción inesperada dentro de una tarea | Incidente correlacionado; tarea recuperable |
| ER22 | Matar trabajador después de ejecutar proveedor y antes de guardar resultado | Reconciliar por clave; no duplicar |
| ER23 | Reiniciar servidor con tareas pendientes | Recuperar desde Outbox y leases |
| ER24 | Falla el propio manejador al registrar en DB | Fallback local limitado; no recursión ni cascada |

Se agrega una puerta de aceptación por proveedor: una integración no se habilita en producción hasta que aprueba ER01–ER24 aplicables, flujos de negocio propios y recuperación sin duplicados.

## 11. Criterio de terminado

No se acepta "manejo de errores" por tener un TRY/CATCH superficial. Deben existir timeout por intento y deadline total, clasificación, política de retry, circuit breaker, idempotencia, Outbox durable para procesos diferidos, estado visible, logging saneado, alertas, límites de concurrencia y pruebas de fallo. La política es común; cada adaptador declara sus particularidades y no puede relajar los mínimos.

La aceptación final requiere demostrar que la caída de un proveedor no rompe el funcionamiento local y que ninguna operación con resultado incierto se duplica.

## Prueba ejecutable de timeout y recuperación

El smoke test efímero incorpora un proveedor HTTP simulado en la propia máquina de CI. El módulo de Rubrova ejecuta un GET con límite de 1 segundo contra un endpoint que demora 5 segundos, captura el resultado sin propagar la excepción a la API, registra una incidencia local y luego vuelve a consultar un endpoint saludable. La prueba verifica también que la incidencia quede persistida. No usa credenciales ni un servicio real y no crea ventas ni pagos. Esta prueba inicial cubre el patrón GET; los métodos de escritura, los circuit breakers y la Outbox requieren sus propias pruebas de idempotencia y recuperación.


## Preparación de precios en la prueba de POS

El fixture de CI no se limita a mostrar el precio del catálogo: asigna ARS al tipo de precio minorista en un módulo temporal separado (`RubrovaCISalesFixture`). La aceptación visual registra el DOM del renglón y los importes del recibo para diferenciar el precio de búsqueda del precio efectivamente calculado en la factura. Este módulo existe sólo dentro del stack descartable de CI.
