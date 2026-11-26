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
- **Reglas derivadas:** (1) una propiedad abstracta se extiende con la sintaxis de propiedad `+=`; una acción abstracta se extiende con el operador de acción `+` (ACTION+); no intercambiar ambos operadores; (2) una acción concreta no se transforma en hook por pertenecer a un módulo requerido; (3) UI invoca el caso de uso, pero constraints y reglas transaccionales viven en el modelo/acción; (4) HTTP se reserva para fronteras externas, no módulos de la misma instancia.
- **Consecuencia:** cada cambio registra firma del hook, punto de llamada, selección/multiplicidad, momento transaccional, entidades tocadas y ledger resultante. Se añaden pruebas estáticas y runtime por caso de uso.
- **Evidencia:** guía docs/engineering/LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md; fuentes 6.2 CreditNote.lsf, InvoiceShipment.lsf, ShipmentInv.lsf, ReceiptInv.lsf, Payment.lsf; PR #13, commit correctivo 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53.
- **Límites:** el mapa cubre en profundidad POS, devoluciones, pagos, caja e inventario; no afirma que Compras, mayorista, ARCA, fabricación o seguridad estén completamente inventariados.


## ADR-0010 — Separar pedido, movimiento físico, factura y liquidación

- **Estado:** Aceptada como regla de modelado; los módulos que la implementan se deben validar con pruebas de escenarios parciales.
- **Ámbito:** compras, ventas mayoristas, POS, stock, cuentas por cobrar/pagar e informes.
- **Contexto:** las fuentes MyCompany 6.2 muestran flujos desacoplados por documentos relacionados: Purchase.Order puede originar Receipt y Bill; Sales.Order puede originar Shipment e Invoice; los pagos se registran y concilian en el modelo común Debt/Payment. Las cantidades se enlazan por líneas originales a través de entregas parciales.
- **Decisión:** Rubrova debe tratar cuatro etapas diferentes: (1) pedido/compromiso comercial; (2) recepción o despacho físico; (3) factura/nota de crédito y deuda; (4) cobro/reintegro/pago y liquidación. El estado de una etapa no implica que las otras hayan ocurrido. Las políticas ordered/delivered se seleccionan explícitamente por tipo de documento.
- **Consecuencias:** los límites y reportes concilian cantidades ordenadas, recibidas/despachadas, facturadas y dinero pagado en dimensiones independientes. El stock físico procede del ledger de inventario; las reservas proceden del ledger de reservas; las deudas y pagos proceden del modelo financiero. Los reportes de ventas usan SalesLedger y preservan el origen del dato.
- **Advertencias:** el campo de línea PurchaseOrderBill.paid representa cantidad asociada a Bills done, no un valor monetario. El enlace SalesOrderPurchase une líneas de órdenes, pero por sí mismo no prueba compra automática ni reserva de inventario.
- **Evidencia:** guía docs/engineering/LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md, secciones 6.7–6.11; fuentes PurchaseOrderReceipt, ReceiptRes, ReceiptInv, PurchaseOrderBill, PurchaseOrderBillReceipt, BillDebt, BillPayment, SalesOrderShipment, ShipmentRes, SalesOrderInvoiceShipment, SalesOrderPurchase y SalesLedger.


## ADR-0011 — No considerar operativa una integración de terminales por tener el modelo de datos

- **Estado:** Aceptada.
- **Ámbito:** terminales POS, cobros electrónicos, reintegros y liquidaciones.
- **Contexto:** RubrovaPaymentTerminals declara clases y formularios para cuentas, terminales, asignaciones, PaymentTerminalIntent, PaymentTerminalAttempt, PaymentProviderEvent, PaymentRefund y PaymentSettlement. Sin embargo, el módulo inspeccionado no implementa un comando de cobro real, HTTP POST al proveedor, receptor de webhooks ni protocolo de bridge local. El runtime install doc ya etiqueta el módulo como configuración/trazabilidad, no como cobro real. RubrovaIntegrationResilience sólo implementa rubrovaHttpGet, clasificación y registro de incidencias; no realiza reintentos automáticos.
- **Decisión:** el estado de capacidad es modelo preparado / no operativo hasta que exista adaptador de terminal/proveedor, protocolo local, idempotencia durable, confirmación de proveedor, reconciliación y prueba hardware end-to-end. Un intento/intención no es un cobro contable; sólo IncomingPayment representa el cobro en el ledger nativo después de confirmación. Un timeout posterior al envío queda desconocido y requiere conciliación.
- **Consecuencia:** los métodos de pago con terminal no deben mostrarse como integrados ni usarse en operación real hasta cumplir la matriz de pruebas; las ventas locales en efectivo no deben depender de la terminal. Se separan bruto, comisiones, impuestos y neto de liquidación.
- **Evidencia:** extensions/lsfusion/RubrovaPaymentTerminals.lsf; extensions/lsfusion/RubrovaIntegrationResilience.lsf; docs/MYCOMPANY_RUNTIME_INSTALL.md; búsqueda de acciones EXTERNAL HTTP POST en el snapshot actual sin resultados.


## ADR-0012 — Reutilizar APIs y procesos nativos antes de crear contratos paralelos

- **Estado:** Aceptada.
- **Ámbito:** integración de e-commerce, marketplaces, apps y servicios externos.
- **Contexto:** MyCompany 6.2 ya incluye ItemAPI, CategoryAPI, ItemAttributeAPI, SalesPricelistAPI, InvLedgerAPI, SalesOrderAPI y TaskAPI en los árboles de dominios principales. No todas tienen semánticas suficientes para sincronización bidireccional o reintentos.
- **Decisión:** los consumidores parten de la API o acción nativa. Se añade wrapper/adapter sólo para versionar esquema, completar validaciones, idempotencia, paginación, correlación o proyecciones que falten. No habilitar @@noauth ni evaluación arbitraria para integraciones ordinarias.
- **Consecuencia:** SalesOrderAPI.newOrders es alta por número, no upsert: ignora órdenes cuyo número ya existe; deleteOrders sólo elimina drafts. InvLedgerAPI.getInventory devuelve onHand, no available. Cada contrato debe probar duplicados, conflicto de contenido, estado y respuesta perdida.
- **Evidencia:** docs/engineering/BASE_REUSE_AUDIT.md, sección 4; fuentes ItemAPI.lsf, CategoryAPI.lsf, ItemAttributeAPI.lsf, SalesPricelistAPI.lsf, InvLedgerAPI.lsf, SalesOrderAPI.lsf y TaskAPI.lsf.


## ADR-0013 — Mantener el costo planificado separado del costo real de inventario

- **Estado:** Aceptada como regla de analítica; valoración FIFO histórica pendiente de regresión.
- **Ámbito:** compras, inventario, devoluciones, fabricación y rentabilidad.
- **Contexto:** MyCompany implementa ItemCost (planificado por fecha) y CostLedger (FIFO/AVCO/standardPrice), enlaza costos de Receipt/Shipment/Adjustment/Manufacturing con movimientos y extiende SalesLedger con costo real de ShipmentLine y ReceiptLine.
- **Decisión:** no calcular margen sólo desde ItemCost cuando existe costo real de movimiento. Conservar fuente, método, fecha, ubicación y documento de origen; reportar desde SalesLedger y ledgers nativos.
- **Riesgo:** CostLedger.lsf tiene comentados filtros temporales dateTime(inCost) <= dateTime(outCost) en dos asignaciones FIFO. No se concluye bug sin reproducir; bloquear afirmaciones sobre FIFO retroactivo hasta cubrir salidas anteriores a entradas y recálculo.
- **Evidencia:** BASE_REUSE_AUDIT.md, sección 3.6; ItemCost, CostLedger, ReceiptCost, ShipmentCost, SalesLedgerInvoiceShipment y SalesLedgerBillReceipt.


## ADR-0014 — Reutilizar stocktake nativo y separar arqueo de efectivo

- **Estado:** Aceptada.
- **Ámbito:** stock, caja y auditoría física.
- **Contexto:** MyCompany tiene Adjustment/AdjustmentList, estados de conteo, cantidad teórica, cantidad real, hojas y barcode; la validación genera InvAdjustment en el ledger. Session/POS registra pagos, depósitos y retiros, pero no se encontró conteo físico de billetes/monedas en el modelo POS central inspeccionado.
- **Decisión:** stocktake Rubrova extenderá Adjustment para conteo ciego/reconteo/autorización. El arqueo físico de efectivo será una capacidad separada ligada a Session/Pos que compare saldo esperado y contado con motivo, operador y autorización; nunca sobrescribe Payment.balance.
- **Evidencia:** BASE_REUSE_AUDIT.md, sección 3.4; Adjustment.lsf, AdjustmentInProgress.lsf, AdjustmentDone.lsf, AdjustmentList.lsf, Session.lsf y PosDashboardCash.lsf.


## ADR-0015 — Complementar backup nativo con paquete verificado y recuperación probada

- **Estado:** Aceptada; riesgo en restore selectivo upstream pendiente de regresión.
- **Ámbito:** operación local y recuperación.
- **Contexto:** lsFusion trae backup completo/parcial, retención, scheduler y restauración selectiva; Rubrova tiene paquete PostgreSQL con manifiesto/SHA-256 y restauración a base nueva.
- **Decisión:** mantener ambos como complementarios hasta demostrar equivalencia: nativo aporta selección lógica; Rubrova aporta paquete, integridad y recuperación completa. Toda restauración crítica debe validar resultado y limpiar temporales ante error.
- **Hallazgo:** PostgreDataAdapter.customRestoreDB devuelve el nombre de la DB temporal desde el catch de IOException de pg_restore y no hace dropDB en ese catch. Debe probarse el fallo y evitar tratar el retorno no nulo como éxito.
- **Evidencia:** BASE_REUSE_AUDIT.md, sección 5.3; Backup.lsf; BackupAction.java; PostgreDataAdapter.java; native-postgres-backup.py.


## ADR-0016 — Activar integraciones regionales sólo con adaptación local y seguridad

- **Estado:** Aceptada.
- **Ámbito:** ARCA, terminales, WhatsApp, e-commerce, WMS y telecomunicaciones.
- **Contexto:** el snapshot incluye raíces optativas RU/PL/BG con ATOL, Wazzup, EnterpriseData, KSeF, WMS, CRPT y telefonía; MyCompany.lsf no las requiere y el árbol no incluye raíz Argentina/ARCA.
- **Decisión:** no añadir raíces regionales al topModule argentino indiscriminadamente. Reutilizar patrones sólo después de definir contrato legal/proveedor local, autenticación, secreto, idempotencia, replay, timeout y reconciliación.
- **Riesgo concreto:** WazzupWebhook usa @@noauth y registra el body completo; el handler revisado no evidencia verificación de firma. No copiar esa política a endpoints Rubrova.
- **Evidencia:** BASE_REUSE_AUDIT.md, secciones 2.2 y 6; MyCompanyRu.lsf, MyCompanyPl.lsf, CashRegisterAtol.lsf y WazzupWebhook.lsf.


## ADR-0017 — Transportar el resultado de un APPLY rechazado sin perderlo al cerrar la sesión

- **Estado:** Aceptada para fixtures, APIs y diagnósticos transaccionales.
- **Ámbito:** pruebas de constraints, rechazo funcional y persistencia de evidencias.
- **Contexto:** en run 45872444450, MyCompany rechazó la sobredevolución de 0,7 unidades sobre un remanente de 0,6, pero la fixture escribió el indicador durable dentro de la misma NEWSESSION cuyo APPLY fue cancelado. Al cerrarse esa sesión, la marca no llegó al API; la respuesta contenía overReturnRejected = NULL aunque el servidor había registrado el mensaje de constraint.
- **Decisión:** usar DATA LOCAL NESTED para transportar la marca de cancelación hacia la sesión padre. Fuera de la sesión fallida, persistir una evidencia durable mediante un APPLY independiente y exitoso cuando el contrato de prueba requiera observarla después del reinicio.
- **Consecuencia:** una prueba nunca debe sustituir una constraint real por una asignación de bandera optimista ni escribir la evidencia en la transacción que se espera cancelar.
- **Evidencia:** fuente v6 Session management/APPLY/NEWSESSION; docs/engineering/LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md, sección 4.2; PR #13.
