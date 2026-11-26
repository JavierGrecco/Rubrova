# Registro de decisiones técnicas

Este registro conserva el contexto y el motivo de las decisiones. Es acumulativo: una decisión posterior puede reemplazar a otra, pero no debe borrar la historia anterior.

Estados permitidos: **Propuesta**, **Aceptada**, **Reemplazada**, **Rechazada**. Una decisión aceptada en CI no implica por sí misma aceptación productiva.

## ADR-0001 — Respetar la versión de lenguaje fijada por la plataforma

- **Estado:** Aceptada.
- **Ámbito:** módulos lsFusion de Rubrova.
- **Contexto:** el runtime del proyecto está fijado a MyCompany 6.2 / lsFusion 6.2. La documentación de la plataforma cambia entre versiones; una forma válida en 7.x no necesariamente pertenece a la gramática 6.2.
- **Evidencia:** el run [45730502272](https://github.com/JavierGrecco/Rubrova/actions/runs/45730502272), commit `b189e2c7d526d5b9eebcf39590d845016ed8f742`, mostró al inicializar el servidor Linux y macOS: `RubrovaReplenishmentExport:11:12 mismatched input 'JSON' expecting ';'` al usar `RETURN JSON FROM`. El parser v6 define `RETURN` como una instrucción sin expresión. Los endpoints de CI existentes usan `EXPORT JSON FROM`.
- **Decisión:** todo módulo se escribe y revisa contra la documentación de la versión bloqueada en `platform/mycompany-6.2.lock.json`. Una actualización de plataforma requiere una prueba explícita de sintaxis y comportamiento; no copiar fragmentos de la documentación latest sin adaptación.
- **Consecuencia:** los cuatro endpoints de reposición vuelven a `EXPORT JSON FROM`. La regresión estática fija el contrato v6.
- **Referencias:** [lsFusion 6.x Access from an external system](https://docs.lsfusion.org/v6/Access_from_an_external_system/), [RETURN operator](https://docs.lsfusion.org/v6/RETURN_operator/), [EXPORT operator](https://docs.lsfusion.org/v6/EXPORT_operator/).
- **Límite:** queda pendiente validar en runtime el cuerpo HTTP y la regla de colecciones vacías bajo este patrón v6.

## ADR-0002 — No inferir una colección vacía por la ausencia de una propiedad JSON

- **Estado:** Aceptada como regla del adaptador; pendiente de aceptación nativa.
- **Ámbito:** exportaciones jerárquicas de MyCompany hacia Rubrova.
- **Contexto:** las pruebas nativas previas respondieron HTTP 200 y JSON parseable, pero el inspector no encontró `outgoingCommitments` como lista. El access log registró cuerpos de 12 bytes para sondas de compromisos en Linux y macOS. La prueba fallaba después del transporte.
- **Decisión:** las tres colecciones deben ir acompañadas de conteos independientes calculados con los mismos filtros. Sólo se normaliza una colección ausente a `[]` cuando el contador nativo vale cero; si el contador es positivo, falta la propiedad o la longitud no coincide, se rechaza.
- **Consecuencia:** se añaden `inventoryCount`, `outgoingCommitmentsCount` y `receiptsCount`; el adaptador y el inspector verifican ambos valores.
- **Riesgo pendiente:** falta confirmar que el conteo y el `JSON FROM` de lsFusion 6.2 recorren exactamente el mismo conjunto de filas con datos reales.

## ADR-0003 — La compilación no sustituye la carga del modelo en runtime

- **Estado:** Aceptada.
- **Ámbito:** CI de MyCompany/lsFusion y pruebas de módulos.
- **Contexto:** el build de artefactos del run [45730502272](https://github.com/JavierGrecco/Rubrova/actions/runs/45730502272) terminó correctamente, pero ambos servidores nativos fallaron al cargar el módulo por sintaxis inválida.
- **Decisión:** la aceptación requiere ejecutar el servidor recién construido, esperar la carga de módulos y ejecutar una acción autenticada de contrato. Los tests estáticos y la compilación son gates previos, no evidencia final de runtime.
- **Consecuencia:** el smoke nativo es obligatorio para afirmar que un módulo lsFusion puede ejecutarse. Un job marcado `continue-on-error` queda clasificado como diagnóstico y no como aceptación.

## ADR-0004 — Usar una clave compuesta de negocio para serializar líneas de venta

- **Estado:** Aceptada para el contrato de exportación; su estabilidad con distintas series/compañías requiere prueba de instalación real.
- **Ámbito:** identidad de compromisos de salida en la exportación nativa.
- **Contexto:** el agregado de negocio que se consolida es `Sales.OrderLine`, pero la capa de exportación no debe asumir que toda clase tenga un `id()` utilizable. La lógica actual serializa cada línea con el número comercial de la orden y el índice de la línea.
- **Decisión:** dentro de MyCompany se agrupa y suma por el objeto `Sales.OrderLine`; hacia JSON se expone `sourceLineId = Sales.number(Order) + Sales.index(OrderLine)`. Esta es una clave de intercambio, no una sustitución del agregado interno ni una promesa de clave primaria universal.
- **Consecuencia:** el adaptador rechaza claves compuestas duplicadas; la documentación de proyección debe describir la misma identidad. La versión de `main` consultada todavía contiene una redacción anterior que menciona `Sales.OrderLine.id`; esa diferencia se debe reconciliar al actualizar la rama contra `main`, sin reintroducir un ID que el contrato actual no usa.
- **Evidencia:** `RubrovaReplenishmentExport.lsf`, `scripts/replenishment/adapt_mycompany_native_export.py`, `docs/PROJECTED_STOCK_AND_REPLENISHMENT.md` de esta rama. Las pruebas estáticas prohíben el uso de `Sales.id(...)` y `Purchase.id(...)`.
- **Pendiente:** verificar unicidad de número de orden + índice dentro de las series, compañías y particiones del MyCompany real que se soporten. Si el ámbito de unicidad necesita compañía/serie, ampliar el contrato con una versión explícita.


## ADR-0005 — Prevalidación local común y CI escalonada

- **Estado:** Aceptada como estrategia de trabajo; pendiente de la primera ejecución del nuevo workflow.
- **Ámbito:** validación de plataforma, reposición y runtime local.
- **Contexto:** se observaron ejecuciones CI de más de 30 minutos. En [45637101959](https://github.com/JavierGrecco/Rubrova/actions/runs/45637101959), el build tomó 401 segundos, el smoke macOS 417 segundos y el diagnóstico Docker/Linux 1.005 segundos. El diagnóstico Docker es no bloqueante y no es el runtime de desarrollo prioritario.
- **Decisión:** mantener una sola rutina `scripts/platform/local-preflight.sh` con capas `--platform` y `--replenishment`, invocada tanto por el desarrollador como por los workflows. Mantener en cada PR la compilación desde fuentes propias y el smoke nativo macOS ARM64. Pasar Linux nativo y Docker/Linux a `workflow_dispatch`; siguen disponibles para investigar compatibilidad, pero no frenan cada cambio. Cancelar workflows anteriores cuando llega un nuevo commit al mismo PR.
- **Consecuencia:** el ciclo normal evita Docker/Linux, pero sigue exigiendo build completo y prueba autenticada en Apple Silicon. Se elimina la divergencia entre los comandos locales y los rápidos de CI.
- **Límite:** preflight verde no prueba parser/carga de lsFusion, consulta SQL generada, autenticación HTTP, persistencia ni flujo POS. No habilita merge por sí solo ni equivale a aceptación productiva.
- **Reversión:** volver a activar los jobs Linux/Docker en cada PR si una regresión demuestra que el runtime o artefacto que cubren no puede detectarse con el build, el smoke macOS y los tests rápidos.

## ADR-0008 — Serializar la inicialización RMI por usuario

- **Estado:** Aceptada.
- **Ámbito:** runtime lsFusion 6.2, conexiones remotas del cliente web y cualquier cliente que cree varias conexiones para el mismo usuario.
- **Hecho observado:** el smoke [45741635022](https://github.com/JavierGrecco/Rubrova/actions/runs/45741635022) registró dos transacciones PostgreSQL que intentaron actualizar simultáneamente `Authentication_customUser.clientLanguage_CustomUser` para el usuario `admin` (`key0=786`). PostgreSQL informó `could not serialize access due to concurrent update`. El servidor sí llegó a iniciar y el usuario se autenticó; el smoke terminó fallando por otra aserción (`effectiveReserved=0`), por lo que estos conflictos eran un problema real adicional y no la causa directa de aquel exit code.
- **Causa:** cada nueva conexión RMI ejecuta `RemoteConnection.initConnectionContext()` y `saveUserContext()`, que persiste `clientLanguage`, `clientCountry`, zona horaria y formatos en la misma fila `CustomUser`. El cliente web puede abrir el navegador de navegación y conexiones de formularios casi simultáneamente. En PostgreSQL con transacciones serializables, dos sesiones del mismo usuario pueden competir al inicializar `clientLanguage`.
- **Decisión:** agrupar 64 bloqueos ligeros por hash de login. `initConnectionContext()` valida/obtiene el login del token y adquiere su bloqueo antes de abrir `ExecSession`; así la segunda conexión del mismo usuario toma su snapshot transaccional después de que la primera haya terminado. Usuarios distintos continúan inicializando en paralelo salvo colisión de stripe.
- **Alternativas descartadas:** ignorar el log; rebajar el aislamiento de PostgreSQL; quitar la persistencia de idioma; o presembrar `clientLanguage` sólo en el usuario de CI. Ninguna corrige el problema general sin cambiar semántica o esconder el conflicto.
- **Consecuencia:** las escrituras de contexto de un mismo usuario se ordenan al crear conexiones, sin serializar peticiones normales ni conexiones de otros usuarios.
- **Regresión:** la prueba estática exige adquirir el bloqueo antes de `getExecSession()`. El smoke nativo busca el `SQLConflictException` específico en los logs del runtime y falla si reaparece.
- **Límite:** la protección cubre inicialización de `RemoteConnection` dentro de un mismo proceso de servidor. No reemplaza la gestión de conflictos de negocio ni resuelve escrituras concurrentes ajenas al contexto del usuario.

## ADR-0009 — Extender contratos abstractos y preservar los ledgers nativos

- **Estado:** Aceptada como regla de diseño para extensiones LSF; las implementaciones deben validar sus escenarios de runtime.
- **Ámbito:** módulos Rubrova integrados en MyCompany 6.2.
- **Contexto:** la investigación de CreditNote, CreditNoteContract, CreditNoteReceipt e InvoiceShipment confirmó que MyCompany expone puntos explícitos como fill ABSTRACT LIST (...), mientras que acciones como CreditNote.create(Bill, Invoice) son concretas. Extender una acción concreta con ACTION+ no es el contrato disponible. Los flujos POS ya conectan factura, pago, despacho/recepción y ledgers.
- **Decisión:** antes de implementar un caso de uso se localiza el dueño del dato, se reconstruye el flujo y se prefiere un punto abstracto declarado. Las extensiones agregan sólo reglas/datos Rubrova. Los hechos financieros y físicos continúan en los objetos y ledgers nativos; no se crean balances paralelos.
- **Reglas derivadas:** (1) propiedad abstracta se amplía con la forma de extensión de propiedades (+ = +=); acción abstracta con el hook compatible (ACTION+ / +); no asumir que el operador sirve para ambos; (2) una acción concreta no se transforma en hook por pertenecer a un módulo requerido; (3) UI invoca el caso de uso, pero constraints y reglas transaccionales viven en el modelo/acción; (4) HTTP se reserva para fronteras externas, no módulos de la misma instancia.
- **Consecuencia:** cada cambio registra firma del hook, punto de llamada, selección/multiplicidad, momento transaccional, entidades tocadas y ledger resultante. Se añaden pruebas estáticas y runtime por caso de uso.
- **Evidencia:** guía docs/engineering/LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md; fuentes 6.2 CreditNote.lsf, InvoiceShipment.lsf, ShipmentInv.lsf, ReceiptInv.lsf, Payment.lsf; PR #13, commit correctivo 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53.
- **Límites:** el mapa cubre en profundidad POS, devoluciones, pagos, caja e inventario; no afirma que Compras, mayorista, ARCA, fabricación o seguridad estén completamente inventariados.
