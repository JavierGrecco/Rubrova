# Manual técnico canónico de Rubrova
## Arquitectura, reutilización, contratos, evidencia y roadmap

**Fuente única de verdad técnica.** Este manual centraliza el conocimiento para mantener y evolucionar Rubrova POS+ERP: qué incorporamos, qué reutilizamos, cómo se conectan los módulos, quién es dueño de cada dato, qué contratos protegen los procesos, qué se ha probado y qué falta demostrar.

**Corte de estado:** 27 de noviembre de 2026  
**Base de main antes de consolidar este manual:** [84121794b9570a4418970272349331bed4cc1711](https://github.com/JavierGrecco/Rubrova/commit/84121794b9570a4418970272349331bed4cc1711)  
**Commit que consolidó los anexos:** [1c3bf7a8235f4128eea2b5f0b0c4b34f8822b67b](https://github.com/JavierGrecco/Rubrova/commit/1c3bf7a8235f4128eea2b5f0b0c4b34f8822b67b)  
**Corrección posterior de enlaces internos:** [57118291eaedffe3aa85a90bcc167cd5fee4d69f](https://github.com/JavierGrecco/Rubrova/commit/57118291eaedffe3aa85a90bcc167cd5fee4d69f)  
**Última revisión de código funcional:** [d9791ff1c7894346d31ea5e0d240077940ba788c](https://github.com/JavierGrecco/Rubrova/commit/d9791ff1c7894346d31ea5e0d240077940ba788c)  
**Fuentes fijadas:** lsFusion 6.2, commit dd4dbe5bf9b136e73e18fe25d741253929324350; MyCompany 6.2, commit d21ca6978717b98b6300d90267f9767db7414008.

> **Precedencia:** las secciones 1–11 representan el estado vigente. Los anexos preservan íntegramente las investigaciones, contratos, decisiones y planes anteriores, pero son históricos. Si un anexo contradice las secciones vigentes, prevalece el estado actual y la discrepancia debe corregirse aquí; no se crea otro documento competidor.

---

<a id="cómo-usar-y-mantener-este-manual"></a>

## 1. Cómo usar y mantener este manual

### 1.1 Fuente única

Las conclusiones técnicas sobre MyCompany, lsFusion, módulos, contratos, propiedad de datos, integraciones, decisiones, pruebas y roadmap viven aquí. No crear archivos separados para nuevas auditorías, mapas de relaciones, contratos, registros de decisiones o avances de investigación.

Se mantienen en el repositorio los documentos de producto que definen requisitos funcionales específicos (POS, fiscalidad, mayorista, servicios, datos analíticos, etc.). Pueden detallar necesidades del negocio, pero no mantener contratos técnicos diferentes de los aquí definidos.

Los archivos ROADMAP.md, PROJECT_STATUS.md, MASTER_IMPLEMENTATION_PLAN.md y QUALITY_AND_TESTING.md se retiraron como documentos independientes. Su contenido histórico está preservado en los anexos H–K; el estado actual y el roadmap vigente sólo se actualizan en las secciones 2 y 9 de este manual.

### 1.2 Clasificación del conocimiento

| Clasificación | Significado | Cómo se comunica |
|---|---|---|
| Hecho de fuente | La revisión fijada contiene el código descrito | «La fuente declara/calcula…»; no implica que funcione en runtime |
| Hecho de test | Un test identificado ejecutó y observó ese resultado | Indicar SHA, run/job, plataforma, versión y escenario |
| Interpretación | Explicación consistente con fuentes y observaciones | Exponer el razonamiento |
| Hipótesis | Posible causa aún no reproducida | Mantenerla abierta; no tratarla como causa raíz |
| Decisión | Regla adoptada por Rubrova | Registrar motivo, alcance y consecuencias |
| Pendiente | Falta una prueba o información | Definir criterio de cierre verificable |

No son equivalentes: archivo incorporado, módulo incluido en REQUIRE, módulo inicializado, acción ejecutada, transacción confirmada, respuesta HTTP válida, flujo conciliado E2E, prueba en equipo físico y operación productiva.

Un HTTP 200 con cuerpo vacío o mal formado es un fallo de contrato. Una compilación no demuestra carga de módulos. Un job verde con una prueba omitida o no bloqueante no es aceptación. Una fixture sintética no demuestra que los datos de una tienda real estén conciliados.

### 1.3 Regla de actualización obligatoria

Cada investigación o cambio que produzca conocimiento actualiza este mismo archivo en el mismo cambio de código/documentación:

1. Estado y nivel de evidencia.
2. Contrato: productor, consumidor, tipos, unidad, moneda, estado, null/zero/empty, clave e invariantes.
3. Relaciones y ledgers afectados.
4. Decisión, si cambió una regla.
5. Registro cronológico: pregunta, fuentes, revisión, hechos, hipótesis, resultado y pendientes.
6. Roadmap y criterio de salida.
7. Tests automatizados que protejan el aprendizaje.

Toda afirmación de aceptación debe identificar SHA, URL de run, job, plataforma/arquitectura, runtime, fixture o datos utilizados y qué quedó sin probar. No copiar credenciales, tokens, PII ni dumps comerciales al manual.

### 1.4 Procedimiento para incorporar a un desarrollador nuevo

Antes de tocar código:
1. Leer las secciones 2–11 de este manual.
2. Revisar los locks y la composición activa de módulos.
3. Localizar aquí el contrato y el propietario del dato que se va a cambiar.
4. Seguir la fuente desde acción/pantalla hasta documento, líneas, estados, pagos, ledgers y reportes.
5. Confirmar que el comportamiento se puede extender con un hook nativo y no crear un equivalente.
6. Leer evidencia y riesgos del flujo; ejecutar primero la prueba más pequeña que discrimine las hipótesis.

Al cerrar el trabajo, actualizar este manual. No depender de conversaciones, memoria de una persona ni ramas históricas para comprender por qué se tomó una decisión.

---

<a id="estado-actual-de-main"></a>

## 2. Estado actual de main

### 2.1 Identidad de la revisión

- La auditoría de fuentes y contratos conserva como referencia `d9791ff1c7894346d31ea5e0d240077940ba788c`; describe el código de MyCompany/lsFusion examinado y no implica que cada capacidad esté aceptada en runtime.
- El PR #15 integró las devoluciones parciales por squash en `main`, commit `04249dc983c3af066a386f1e1b022da2d9587ec0`.
- El PR #14 integró el conteo nativo por barcode por squash en `main`, commit `c38fad581f669bd7e1a2795123cc8ecca242e010`, desde el HEAD validado `12f29a47e7b89f6f162c85a7e3684e24f9fe793b`.
- El workflow de incorporación de fuentes fijadas creó después el commit `7d9e5bb80e866df87b51baad852c1e6256270dd1`; incorporó en el árbol vendorizado la corrección de `AdjustmentList.lsf` ya probada por #462 y está compilando ese snapshot.
- Los resultados históricos permanecen en los reportes numerados. Las secciones 2–10 describen el estado operativo actual y distinguen validación pre-merge de validación del SHA integrado.

### 2.2 Evidencia de aceptación vigente

| Área | Evidencia | Resultado exacto |
|---|---|---|
| Prevalidación, Windows y compilación del conteo por barcode | [Run #462](https://github.com/JavierGrecco/Rubrova/actions/runs/45909363575), SHA `12f29a4` | Éxito: prevalidación compartida, validación PowerShell, compilación completa de lsFusion + MyCompany 6.2, cliente GWT y artefactos de runtime |
| Runtime nativo macOS ARM64 del PR #14 | Run #462, job `140215704940` | Éxito: servidor y RMI nativos, PostgreSQL ARM64, UI autenticada y ejecución funcional sobre MyCompany 6.2 |
| Conteo por barcode | Run #462 | Cero preservado en hoja y AdjustmentLine; NULL elimina la fila de lista y deja la línea principal sin cantidad; positivo 2 reconciliado en ambas líneas; el conteo pendiente no modifica `onHand=10` |
| Persistencia del conteo | Run #462 | Tras reiniciar el servidor permanecen la hoja, ambas líneas y cantidad 2; `onHand=10` sigue intacto |
| Devoluciones parciales y caja | Runs [#458](https://github.com/JavierGrecco/Rubrova/actions/runs/45906455407) y #462 | 0,4 + 0,6 unidades; rechazo de 0,7; dos reintegros en efectivo por ARS 1.250; stock reingresado; caja neta cero; persistencia tras reinicio |
| Backup PostgreSQL | Run #458 | Backup, verificación y restauración en una DB aislada pasaron dentro del smoke nativo |
| Exportación de reposición | Run #458 y fixtures | API autenticada de sólo lectura sobre datos sintéticos; falta conciliar con una base comercial real |
| Post-merge del commit funcional | [Run #463](https://github.com/JavierGrecco/Rubrova/actions/runs/45911383909), SHA `c38fad5` | Prevalidación y Windows pasaron; build seguía en curso al corte. Este run no incluye el commit de fuentes posterior `7d9e5bb` |
| Incorporación de fuentes completas | [Run #24](https://github.com/JavierGrecco/Rubrova/actions/runs/45911383784), commit generado `7d9e5bb` | Árboles, licencias y rutas Maven pasaron; corrección aplicada a `AdjustmentList.lsf`; compilación de fuentes incorporadas en curso |
| Offline macOS | `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested` | Pendiente; runtime local no equivale a aceptación offline |
| Egreso de red | `RUBROVA_NATIVE_EGRESS_BLOCKED=false` | La prueba no bloqueó egress; no afirmar aislamiento de red |
| Linux/Docker | Jobs omitidos en #458 y #462 | No aprobado por omisión |
| Windows | Validación de sintaxis PowerShell | No equivale a instalación ni smoke funcional nativo |
| Producción | Sin homologación integral con datos reales | No autorizado |

El run #462 terminó correctamente sobre el HEAD del PR #14 y aportó evidencia funcional completa del conteo por barcode. El cambio se integró después en `main` mediante `c38fad5`. El workflow #24 incorporó la misma corrección a la fuente vendorizada y está compilándola; el run #463 valida el commit `c38fad5`, anterior al commit de fuente `7d9e5bb`. No declarar el snapshot más reciente como plenamente validado hasta que termine la compilación #24 y se complete la verificación nativa correspondiente.

### 2.3 Devoluciones parciales: integradas y probadas en `main`

PR [#15](https://github.com/JavierGrecco/Rubrova/pull/15) fue integrado por squash en `main`, commit [04249dc](https://github.com/JavierGrecco/Rubrova/commit/04249dc983c3af066a386f1e1b022da2d9587ec0). PR #13 quedó cerrado como reemplazado; su historial de fallos se conserva como evidencia histórica.

- `RubrovaRetailReturns` está incluido en `RubrovaCustom` y en `platform/mycompany-6.2.lock.json`.
- La extensión reutiliza `CreditNote.fill(BillLine, InvoiceLine)` para completar sólo la cantidad no devuelta. Mantiene la protección de `checkReturnedQuantity` de MyCompany y reutiliza documentos, pagos, recibos y ledgers nativos.
- El fixture ejecuta los eventos locales después de crear la nota de crédito y después de ajustar la cantidad, antes de calcular y asignar el importe del reintegro.
- [Run #458](https://github.com/JavierGrecco/Rubrova/actions/runs/45906455407), SHA `04249dc`, pasó en `main`: prevalidación, Windows, compilación, smoke nativo macOS ARM64, cierre, backup/restore PostgreSQL, reinicio y demo.
- El escenario verificó venta de ARS 1.250, devolución 0,4, rechazo de 0,7 cuando quedaban 0,6, segunda devolución de 0,6, dos notas y dos reintegros en efectivo por ARS 1.250, stock físico final 10, caja neta cero y persistencia tras reinicio.
- El run #462 volvió a ejecutar la conciliación de devoluciones mientras probaba stocktake y confirmó cierre de turno, caja conciliada y persistencia.
- Linux x86_64 y Docker/Linux se omitieron. La fixture es de efectivo sintético; pagos mixtos, reintegros tarjeta/QR, conciliación de adquirentes y terminales reales siguen pendientes.

No trasladar esta aceptación a medios de pago o entornos no cubiertos por el escenario.

### 2.4 Estado de ramas

Inventario remoto consultado después del run #491, el 27 de noviembre de 2026:

- `main` permanece en `a994c271e5bdf2fce73a525d1083ac22c99a4e56`; no recibió ninguno de los cambios de reintegros acumulados.
- Ramas remotas visibles: **2** — `main` y `work/pos-refund-cumulative-method-guard`.
- La rama temporal corresponde al PR [#16](https://github.com/JavierGrecco/Rubrova/pull/16), abierto y en borrador. El run #495 comprobó el HEAD `ca5ff7e77e9d11d0e444f88c02654ee89c0482fc`; la corrección de aislamiento de cuentas de REP-035 continúa en esta misma rama. El PR no está integrado y no debe mezclarse con `main` hasta superar la aceptación funcional completa.
- Pull requests abiertos: **1** — PR #16. Los trabajos de ramas anteriores se consolidaron/cerraron y no deben recrearse.
- La rama de trabajo actual es la única rama temporal permitida. No abrir ramas adicionales para correcciones sucesivas; corregir aquí, validar por etapas y consolidar una sola vez al cumplir los criterios de salida.

La política continúa siendo una sola rama persistente (`main`) y como máximo una rama temporal para revisión. Después de integrar PR #16, eliminar su rama temporal y comprobar que sólo quede `main`.

### 2.5 Reintegros acumulados por medio de pago: guard implementado en rama de trabajo, pendiente de aceptación

La inspección de fuentes nativas identificó que el formulario de MyCompany sólo compara cada reintegro con el importe original del método. La solución en revisión amplía el control sin crear pagos ni ledgers paralelos:

- `PosDashboardReturnPayment.lsf` calcula `invoicePaid(Bill, PaymentMethod)` sin filtrar explícitamente cobros cancelados. El parche Rubrova calcula el cobro original por método sumando `paid(IncomingPayment, Invoice)` sólo para ingresos activos, y cambia `invalidAmount` para comparar el importe actual con `rubrovaRefundRemaining`, que descuenta egresos activos anteriores enlazados a la misma factura. Se usa la porción aplicada al documento, no el `amount` completo de un cobro que pudiera repartirse entre facturas.
- `SessionPayment.lsf` conserva `paymentMethod(Bill, OutgoingPayment)` y su resumen `paid(Bill, PaymentMethod)`; el guard suma el importe contable normalizado `amount[Debt](OutgoingPayment)` de cada egreso activo, comparable con los cobros aplicados a la factura y válido cuando la moneda origen del pago difiere de la moneda funcional. La macro `defineDocLineRelation` de `utils/Doc.lsf` permite seguir las notas hasta la factura original.
- `OutgoingPaymentCanceled.lsf` define la actividad del egreso como listo o hecho y no cancelado. **El cupo se calcula por egresos activos, no por notas activas.** Cancelar una nota no cancela por sí mismo su pago, así que el dinero que ya salió sigue consumiendo cupo. El cupo sólo se libera cuando el egreso nativo correspondiente también deja de estar activo.
- La regla global `rubrovaRefundedByMethod` suma los pagos de salida activos relacionados con cada factura original y método, y rechaza el exceso dentro del `APPLY`. La pantalla muestra el importe original, el remanente y el límite del valor ingresado.
- El parche de preparación cambia el `APPLY` del diálogo POS nativo a `APPLY SERIALIZABLE`. La documentación de lsFusion 6.x admite ese nivel de aislamiento para una aplicación concreta. La restricción global sigue siendo la regla de integridad; el aislamiento serializable hace que dos confirmaciones que compiten por el mismo cupo no puedan confirmar ambas sobre la misma lectura anterior.

**Estado de aceptación (runs #486–#488):** en #486, la prevalidación, Windows y compilación pasaron, pero macOS ARM64 se detuvo por un caption antiguo `invoicePaid(b,pm)` en `RubrovaPOSLocalization`. La corrección quedó en `c865d88`: localización, dependencia, lock y clave española pasaron a usar `rubrovaOriginalPaidForReturn` y `rubrovaRefundRemaining`. El #487 pasó Windows y registró 35/36 pruebas por una expectativa estática obsoleta; se alineó al código vigente en `fd111a1`. El #488 aprobó 36/36 pruebas de extensión, 34/34 pruebas adicionales, Windows y compilación completa. Su smoke ARM64 cargó el módulo del guard, la pantalla de reintegros y la localización; se detuvo al inicializar `RubrovaCISalesFixture:189:26` por `Retail.session` ambiguo entre las variantes de Invoice, Bill y pagos. No se alcanzaron las APIs E2E, las operaciones concurrentes ni la persistencia. La siguiente revisión tipa explícitamente el `Bill` en los dos agregados de egresos de la fixture y agrega regresiones estáticas.

**Evidencia del run #489 (PR head `a7f63b2`; checkout de integración `bf4dbde98e17a0cad2be09ba886b166e86494ee9`):** la prevalidación aprobó 36/36 pruebas, Windows pasó y la compilación completa lsFusion/MyCompany terminó correctamente. El smoke macOS ARM64 detuvo la inicialización antes de ejecutar las APIs E2E. La causa exacta fue `RubrovaCISalesFixture:443:51 use NULL instead of FALSE`: la fixture intentaba asignar `FALSE` a un `DATA BOOLEAN` persistente. El log de lsFusion ya contenía la ubicación, pero el mensaje principal del smoke sólo decía que el supervisor había terminado; durante la limpieza aparecía además un mensaje secundario de cierre que ocultaba el código de salida original. No se alcanzaron login, reintegros, concurrencia, conciliación ni persistencia.

**Cobertura de runtime añadida a la rama:**

1. Factura original de ARS 1.250: efectivo ARS 500 y tarjeta ARS 750.
2. Primera nota: 0,4 unidades, efectivo ARS 200 y tarjeta ARS 300.
3. Rechazar una segunda devolución de 0,6 unidades que solicita ARS 600 de tarjeta: cada devolución está por debajo de ARS 750, pero el acumulado sería ARS 900.
4. Dos confirmaciones concurrentes de tarjeta por ARS 300: una debe confirmar y la otra rechazarse, porque el cupo antes de la carrera es ARS 450.
5. Completar el remanente con efectivo y tarjeta; los totales confirmados deben cerrar en ARS 500 y ARS 750 respectivamente.
6. Cancelar sólo la nota original no debe liberar cupo mientras sus dos egresos permanezcan activos. Cancelar después los egresos nativos debe liberar exactamente esos importes, permitiendo una nueva devolución dentro del remanente.
7. Conciliar cantidad devuelta, notas activas, estado de egresos, caja/medios y persistencia después del reinicio.

**Resultado más reciente (#495, 27 de noviembre de 2026; [workflow](https://github.com/JavierGrecco/Rubrova/actions/runs/45939652935), HEAD `ca5ff7e`):** preflight 37/37 Node y 34/34 validaciones adicionales, Windows y compilación completa pasaron. El smoke macOS ARM64 volvió a iniciar el servidor y la UI autenticada. El escenario de reintegros mixtos superó exceso acumulado, carrera concurrente, cancelación sólo de la nota (sin liberar cupo), cancelación de los dos egresos (liberando el cupo), conciliación completa y saldos finales: efectivo ARS 1.000, banco ARS 1.000, tres notas/ARS 1.250, cantidad 1 y stock 10. Sin embargo, al continuar con el smoke POS general, el cierre del turno encontró `cashBalance=1000` cuando esperaba cero, aunque ventas y devoluciones del turno conciliaban en ARS 1.250 cada una. **Causa confirmada en fuentes:** `RubrovaCIRetailFixture.lsf` asignaba las mismas `CashAccount` y `BankAccount` a `rubrova-ci` y `rubrova-ci-refund`; MyCompany calcula `Retail.cashBalance(Pos)` desde la cuenta asociada al medio efectivo. El movimiento inicial de ARS 1.000 del escenario de reintegros se reflejó así en el cajón del turno general. No es un fallo del guard ni de la devolución; es contaminación entre fixtures por compartir cuentas. El run terminó antes de reiniciar y comprobar persistencia. La siguiente revisión crea cuentas central, efectivo y banco independientes para la caja de reintegros, y agrega una regresión estática que prohíbe volver a compartirlas. Aún no hay aceptación E2E final.

No extender esta aceptación a terminales reales, adquirentes, pagos mixtos productivos ni QR externo: esta fixture es local y sintética.

## 3. Qué incorporamos: versiones, alcance y composición

### 3.1 Versiones y procedencia

| Componente | Versión | Commit fijado | Licencia | Carpeta |
|---|---|---|---|---|
| lsFusion | 6.2 | dd4dbe5bf9b136e73e18fe25d741253929324350 | LGPL-3.0 | vendor/platform |
| MyCompany | 6.2 | d21ca6978717b98b6300d90267f9767db7414008 | Apache-2.0 | vendor/mycompany |

Los locks registran 1.335 archivos MyCompany, incluidos 800 módulos LSF, y 4.887 archivos lsFusion, incluidos 3.330 Java sources. Es inventario de snapshots, no prueba individual de cada módulo/fuente. El runtime smoke ha cargado 722 módulos en una composición; no se deben presentar como probados todos los 800 módulos por ese hecho.

build/rubrova/pom.xml compila desde el código versionado en Rubrova. El reactor lsFusion contiene build, api, desktop-client, server y web-client.

### 3.2 Composición funcional principal

MyCompany.lsf incluye servicios transversales y dominios: Eval, ProcessMonitor, Backup, Chat, Documentation, MasterDataP, Inventory, Invoicing, InvoicingInventory, Purchase, Sales, Retail, Manufacturing, ProjectManagement, HumanResources, CRM, Fleet, BillReceiptCost y BillReceiptCostService.

RubrovaCustom.lsf en main requiere:
- MyCompany
- RubrovaPOSLocalization
- RubrovaIntegrationResilience
- RubrovaPaymentTerminals
- RubrovaReplenishmentExport

RubrovaRetailReturns está cargado desde RubrovaCustom y extiende el hook nativo CreditNote.fill. Los módulos regionales RU/PL/BG están en el snapshot pero no se cargan automáticamente en el core argentino.

### 3.3 Regla reuse-first

Antes de construir un módulo, clase, ledger o API:
1. Encontrar el propietario nativo.
2. Seguir el circuito desde la UI/acción al documento y líneas.
3. Seguir estados, constraints, pagos, movimientos físicos/financieros, costos y reportes.
4. Identificar el punto de extensión correcto.
5. Reutilizar el comportamiento nativo, agregar únicamente lo que falta.
6. Probar el circuito completo.
7. Sólo justificar una entidad propia si posee un concepto, dueño y ciclo de vida diferentes.

No crear ledgers paralelos de stock, caja, cuentas por cobrar/pagar, facturación, devoluciones ni costos.

---

## 4. Cómo interactúan los módulos y cómo se extienden

### 4.1 Módulos LSF dentro de la misma instancia

Los módulos de MyCompany/lsFusion no son microservicios separados. Se cargan en una instancia lógica y cooperan mediante REQUIRE, CLASS, propiedades, acciones, eventos, constraints y extensiones abstractas. No deben comunicarse por HTTP entre sí cuando ya participan de la misma instancia.

HTTP/API, webhooks, archivos y procesos independientes se reservan para dispositivos, integraciones externas o consumidores fuera del runtime.

### 4.2 Contratos de módulo

- MODULE identifica la unidad lógica.
- REQUIRE declara dependencia y orden de inicialización; no crea un servicio remoto.
- CLASS identifica el tipo de agregado/objeto.
- DATA crea una propiedad almacenada; DATA LOCAL es temporal y su duración depende de la sesión.
- Propiedades calculadas expresan relaciones/cálculos; no duplicar sus resultados en la UI.
- ABSTRACT define un contrato extensible.
- Acción abstracta se extiende con + / ACTION+ y una firma compatible.
- Propiedad abstracta se extiende con +=.
- Acción concreta no se convierte automáticamente en hook por pertenecer a un módulo requerido.
- EXTEND FORM cambia la interfaz, no sustituye las reglas server-side.
- CONSTRAINT protege invariantes y puede cancelar APPLY.

Para cada hook documentar firma, parámetros, tipo de acción (LIST/MULTI/CASE), selección, multiplicidad, orden, condición, sesión/transacción y efectos en documentos/ledgers.

### 4.3 APPLY, CANCEL, NEWSESSION y NESTEDSESSION

- APPLY valida restricciones y trata de confirmar los cambios del ciclo de sesión.
- Si una constraint cancela APPLY, se revierten los cambios persistentes de esa transacción.
- CANCEL no equivale a anular un documento ya contabilizado; elimina cambios no confirmados del contexto correspondiente.
- NEWSESSION abre un nuevo ciclo; las propiedades locales normales pueden reiniciarse.
- NESTEDSESSION permite trabajar con cambios/locales anidados que pueden volver al contexto padre.
- DATA LOCAL NESTED es útil para pasar una marca transitoria al padre luego de un APPLY cancelado dentro de NEWSESSION.

**Lección de PR #13:** no guardar la evidencia durable del rechazo dentro de la misma transacción que esperamos que se revierta. Detectar canceled(), transportar el resultado al padre con LOCAL NESTED y persistir la evidencia en una transacción limpia posterior si hace falta consultarla después.

**Efectos externos:** las acciones dentro de una transacción pueden repetirse por conflictos/reintentos. No colocar cobros externos, emisión fiscal irreversible, impresión no repetible o publicación de webhook dentro de un APPLY susceptible de retry. Guardar intención/idempotency key, ejecutar el efecto externo fuera de ese bloque y reconciliar su resultado.

---

## 5. Contratos de datos y flujos de negocio

### 5.1 Catálogo, producto y socio

**Propietario:** MyCompany MasterData. El catálogo nativo contiene Item/Product/Service, categorías jerárquicas, variantes, SKU, barcode, atributos, UOM, imágenes, Partner, clientes/proveedores, contactos, empresas, empleados, ubicaciones, moneda y tipos de cambio.

Un ID de un marketplace o integración es una referencia externa, no una identidad duplicada. Extender objetos nativos; no crear otra tabla de productos/clientes/proveedores salvo que represente un concepto realmente distinto.

### 5.2 Venta, pago y sesión POS

**Propietarios:** Retail + Invoicing.

Flujo:
1. Pos es una caja lógica.
2. Session es el turno de esa caja; openedSession/openSession evitan dos sesiones abiertas simultáneamente para el mismo POS.
3. Una venta crea Invoice e InvoiceLine.
4. El cobro genera IncomingPayment asociado a la factura y PaymentMethod.
5. SessionPayment agrega los ingresos por medio y descuenta los egresos asociados a devoluciones.
6. Los movimientos de depósito/retiro son hechos financieros separados.
7. El cierre de sesión no equivale a arqueo físico.

Efectivo recibido, vuelto y pago neto son magnitudes diferentes. Los pagos mixtos se conservan separados por medio. No modificar el pago original para representar el arqueo o una diferencia.

### 5.3 Devolución, reintegro y reingreso físico

**Propietarios nativos:** CreditNote/Bill, OutgoingPayment, BillReceipt/Receipt e Inventory ledgers.

Flujo:
1. La nota de crédito es Bill y mantiene relación con Invoice.
2. BillLine conserva relación con InvoiceLine.
3. CreditNote.returned(InvoiceLine) suma cantidades de devoluciones de Bills activos.
4. checkReturnedQuantity en InvoiceType protege la cantidad acumulada y puede cancelar APPLY.
5. OutgoingPayment registra el reintegro, vinculado al Bill y PaymentMethod.
6. La recepción física es otro documento. BillReceipt puede crear Receipt automáticamente según autoCreateReceipt.
7. ReceiptInvLedger materializa la cantidad efectivamente recibida en el inventario físico.

No confundir nota de crédito (compensación comercial/fiscal), reintegro (salida de dinero) y recepción física (entrada de mercadería).

**Tipos:** CreditNoteReceiptInitial asigna receiptType='return' tanto a creditnote como a retailreturn, pero activa autoCreateReceipt sólo para retailreturn. Por tanto no asumir que toda nota de crédito repone stock.

**Reintegro por medio:** PosDashboardReturnPayment valida cada documento de reintegro comparando amount(pm) con invoicePaid(b,pm). No demuestra que varios reintegros acumulados nunca superen lo pagado originalmente por método. Probar el acumulado por medio en forma independiente.

**Anomalía a investigar:** el bloque de cancelación de PosDashboardReturnPayment elimina IncomingPayment, mientras que el bloque de confirmación crea OutgoingPayment. No parchear upstream hasta demostrar si la cancelación de sesión revierte automáticamente el egreso o deja residuos.

### 5.4 Inventario físico, reservas y disponible

**Propietarios:** Inventory.InvLedger y Inventory.ResLedger.

InvLedger:
- inQuantity suma movimientos activos, aceptados, cuya ubicación destino y producto coinciden;
- outQuantity suma movimientos activos con ubicación origen coincidente;
- onHand = inQuantity − outQuantity;
- onHandB/prevOnHandB dan magnitudes históricas.

ResLedger:
- expected representa reservas entrantes negativas como magnitud positiva;
- reserved agrega reservas positivas;
- planned suma reservas firmadas que no tienen skipAvailable;
- available = onHand − planned.

No confundir onHand físico, available, reserved bruto, expected entrada esperada y planned reserva neta. Una transferencia no aceptada sigue excluida de la existencia del destino. increaseAvailableStock determina si determinadas recepciones esperadas afectan el disponible.

### 5.5 Stocktake/ajuste de mercadería

**Dueño nativo:** Adjustment, AdjustmentLine, AdjustmentList, AdjustmentListLine, InvAdjustment y luego InvLedger.

Circuito:
1. Crear Adjustment para ubicación/tipo/categoría.
2. Cargar theoreticalQuantity usando prevOnHandB(location, product, dateTime(adjustment)).
3. Marcar inProgress con markAsToDo.
4. Cargar realQuantity directamente o por hojas separadas.
5. difference = realQuantity − theoreticalQuantity.
6. Validar; InvAdjustment transforma la diferencia en movimiento de Inventory.InvLedger.

No desarrollar otro motor de stocktake. Extender el existente con conteo ciego, zona/operador, reconteo, tolerancias, aprobación, evidencia y auditoría.

**Semántica comprobada por fuente y documentación del lenguaje:**

1. `AdjustmentListSearch.setRealQuantity(a,p,loc,q)` recibe una cantidad `NUMERIC[16,3]` y usa `IF q THEN` en las ramas de actualización/creación; el `ELSE` elimina la línea. En lsFusion, una condición se cumple cuando su valor no es `NULL`, no cuando el número es distinto de cero. Por eso `q=0` es un valor presente y entra en la rama de guardar; el borrado corresponde a `q=NULL`. Ver la documentación v6 de [IF ... THEN](https://docs.lsfusion.org/v6/IF_..._THEN_action_operator/) y [operadores de selección](https://docs.lsfusion.org/v6/Selection_CASE_IF_MULTI_OVERRIDE_EXCLUSIVE/).
2. `AdjustmentList.listRealQuantity` agrega las filas de las hojas por (Adjustment, Product, Location). Una fila existente cuya cantidad sea cero mantiene una fila para ese agregado; una colección sin filas puede, en cambio, producir un agregado `NULL`. `Adjustment` crea/actualiza la línea principal desde ese agregado; `AdjustmentDone` calcula `difference = realQuantity - theoreticalQuantity` y genera `InvAdjustment` cuando corresponde.
3. `Adjustment.fill` filtra con `level(...) AND onHand(location, product)`. Esa condición de lsFusion prueba que `onHand` no sea `NULL`; no es un filtro `onHand > 0`. Un saldo numérico cero no se excluye por ser cero. Los productos cuyo `onHand` resulte `NULL` sí pueden quedar fuera del autollenado; probar especialmente productos sin movimientos y decidir cómo incorporarlos a un conteo amplio.
4. **Corrección de auditoría:** la hipótesis anterior de que `IF q THEN` trataba `0` como falso era incorrecta y se retira. No se debe parchear `AdjustmentListSearch` con `IS NOT NULL` ni crear lógica paralela. El fuente vendorizado se restauró byte por byte al original fijado; queda pendiente una prueba de runtime de `q=0`, `q=NULL`, agregado en hojas y `Fill` para convertir la semántica documentada en evidencia de instalación.

**Pruebas imprescindibles:** capturar por barcode cero en una hoja sin línea y con línea existente; probar `NULL` como borrado; verificar que una fila cero se conserva y propaga a la línea principal y `difference=-teórico`; probar el efecto de validación/InvLedger en una ubicación aislada; probar `onHand=0` no nulo frente a `onHand=NULL`/sin movimientos; además varias hojas, dos ubicaciones, cambios de stock tras la fecha teórica, reconteo, cancelación, doble validación, permisos, lotes, costo y persistencia.

### 5.6 Compras, recepciones y costo de inventario

PurchaseOrder es el compromiso de compra. Receipt es la recepción, ReceiptResLedger puede representar entrada esperada y ReceiptInvLedger representa cantidad física efectivamente completada. Bill es factura proveedor y BillReceipt enlaza factura con recepción y costo.

Cantidades pedidas, reservadas, esperadas, aceptadas, recibidas y facturadas son hechos distintos. Conservar los vínculos a las líneas originales; no usar cantidad pedida como si fuera recibida.

### 5.7 Costos, valoración y margen

Separar siempre:
- ItemCost: costo planificado/histórico por producto/fecha.
- CostLedger: costo real de movimientos físicos; métodos standardPrice, AVCO y FIFO.
- SalesLedger: hechos comerciales para ingresos, impuestos, costo y markup/margen.

Reutilizar ReceiptCost, ShipmentCost, AdjustmentCost, BillReceiptCost, BillReceiptCostService y ManufacturingOrderCost. El costo de flete/servicio puede distribuirse por importe, costo planificado, precio de venta, peso, volumen o cantidad.

SalesLedgerInvoiceShipment aporta costo de ShipmentLine; SalesLedgerBillReceipt aporta el costo real de ReceiptLine para devoluciones. No usar sólo costo planificado cuando exista costo real vinculado.

**Riesgo FIFO prioritario:** CostLedger.calculateCost() ordena los movimientos de salida marcados para recalcular por fecha y producto. Para cada salida busca capas InCostLedger de igual ubicación/producto y reparte cantidades no costeadas, pero en las dos ramas de asignación FIFO aparece comentado dateTime(il) <= dateTime(ol). Por lo tanto, al recalcular un conjunto que contiene una salida anterior y una entrada posterior, la consulta de capas no impide estáticamente consumir esa entrada futura. Es un riesgo reproducible en principio, no un bug runtime confirmado; hay que establecer la política de inventario negativo/backdating antes de corregir.

Test FIFO: misma ubicación/producto; salida anterior a entrada; entrada anterior a salida; capas con costos distintos; inventario negativo transitorio; transferencias; backdating; recalcular desde fecha; comparar consumo por capa, amount(OutCostLedger), precio unitario y margen de SalesLedger. Definir qué debe suceder ante salida anterior a recepción antes de corregir fuente upstream.

SalesLedger.costAmount es ABSTRACT VALUE con implementación planificada y extensiones de costo real. No suponer suma o selección de valores sin probar lsFusion 6.2. Cubrir factura no despachada, parcialmente despachada, completamente despachada y devoluciones sin/con Receipt.

### 5.8 APIs nativas

| API nativa | Aporta | Límite |
|---|---|---|
| MasterData.getItems | Catálogo, barcode, categoría, UOM, país, imagen/desc opcional | Filtros y volumen por probar |
| MasterData.getCategories | Categorías y jerarquía | Identidad y vigencia por versionar |
| MasterData.getItemAttributes | Atributos por producto | Esquema dinámico/opcional |
| Sales.getPrices | Precio por tipo/lista/fecha | Moneda, impuestos, UOM y vigencia |
| Inventory.getInventory | onHand por producto/ubicación | No es available; el filtro `onHand(...)` excluye valores NULL, no saldos numéricos cero |
| Sales.newOrders | Crear pedido desde JSON | Create-only por número; si existe lo ignora, no upsert |
| Sales.deleteOrders | Borrar pedido | Sólo borrador |
| ProjectManagement.getTasks/addTasks | Consultar/crear/actualizar tareas | IDs y relaciones; idempotencia externa no garantizada |

Empezar por API nativa; wrapper sólo cuando falte schemaVersion, idempotency key, cursor/paginación, correlación, upsert, reconciliación, permisos o proyección. No usar @@noauth ni EVAL para integraciones ordinarias.

### 5.9 Seguridad, permisos y acceso a ubicaciones

Security implementa usuarios, roles y permisos de navegación, formularios, propiedades y acciones. LocationEmployee.hasAccess usa jerarquía de ubicaciones.

**Regla importante observada:** si el empleado no tiene ninguna fila explícita de hasAccess, countLocationAccess=0 y las expresiones conceden acceso a todas las ubicaciones. defineDocLocationAccess sólo se aplica a documentos donde el macro está invocado; no es autorización universal de filas ni protege automáticamente todas las APIs.

Probar usuarios sin filas, permisos de padre/hijo, denegaciones, varias compañías, cada documento y cada API desde el servidor. Ocultar botones no protege datos.

Eval es un intérprete privilegiado; no exponer a usuarios o integraciones ordinarias.

### 5.10 Scheduler, monitor y backups nativos

Scheduler permite periodicidad, ventanas, timeout y logging; no es una cola durable. Si la PC está apagada no se ejecuta. ProcessMonitor aporta SQL, procesos, locks y stack. Backup nativo necesita scheduler activo y rutas/binaries correctos; comprobarlos por instalación.

El análisis de PostgreDataAdapter.customRestoreDB detectó riesgo: un IOException durante pg_restore puede devolver el nombre de una DB temporal como si existiera resultado. La importación selectiva posterior escribe por tabla con APPLY repetidos. Un restore parcial no debe tratarse como éxito. Falta reproducir el fallo y proteger atomicidad/limpieza.

El backup Rubrova de PostgreSQL usa manifest/checksum y restaura en DB nueva sin sobrescribir la activa. Es sólo DB: adjuntos, documentos externos, imágenes, binarios, secretos, certificados, instaladores y configuración runtime deben cubrirse aparte. La recuperación completa necesita copia off-device y prueba en PC nueva.

### 5.11 Integraciones regionales

El snapshot incluye raíces RU/PL/BG pero no una raíz ARCA argentina. ATOL, Wazzup, EnterpriseData, KSeF, CRPT, WMS y telefonía son patrones de arquitectura, no integraciones argentinas listas. WazzupWebhook usa @@noauth y registra body; no copiar ese patrón sin firma, deduplicación durable y política de PII. El driver ATOL no es un adapter fiscal argentino.

---

## 6. Contratos externos comunes

Toda API define endpoint/método, versión, autenticación/autorización, productor/propietario, claves, correlación, esquema, tipos, ausencia/NULL/cero/empty, moneda, unidad, precisión, zona horaria, fechas de ocurrencia/registro, límites, timeouts, errores, idempotencia y reconciliación.

Una respuesta HTTP 200 es sólo transporte. Validar Content-Type, cuerpo, estructura, tipos y semántica de cada campo.

Un evento representa un hecho ocurrido. Debe incluir eventId, tipo, versión, emisor, occurredAt, agregado origen y correlationId. Asumir entrega al menos una vez y deduplicar durablemente. Manejar mensajes duplicados, tardíos y fuera de orden; permitir replay/reconciliación.

Un timeout puede ocurrir después de que el proveedor aceptó el cobro. No repetir a ciegas. Persistir PaymentIntent/Attempt y la clave de idempotencia antes del llamado externo; consultar estado/reconciliar antes de reintentar.

Estado actual:
- RubrovaIntegrationResilience clasifica incidencias HTTP y tiene helper GET con timeout; no es cliente POST genérico ni cola de reintentos.
- RubrovaPaymentTerminals guarda cuentas, terminales, asignaciones, intenciones, intentos, eventos, reintegros y liquidaciones; no efectúa cobros reales ni tiene bridge/webhook completo.
- RubrovaReplenishmentExport es autenticado y de sólo lectura.
- RubrovaPOSLocalization amplía UI/captions sin sustituir lógica nativa.
- RubrovaRetailReturns sigue fuera de main.

---

## 7. Mapa de propiedad de datos

| Dato | Dueño | Consumidores | Regla |
|---|---|---|---|
| Producto, categoría, barcode, UOM | MasterData | POS, ventas, compra, BI | Identidad maestra única |
| Venta/lineas | Invoice/InvoiceLine + Retail | pago, despacho, reportes | Venta no es pago ni despacho |
| Caja/turno | Pos/Session | POS, pago, cierre | Turno no es caja física |
| Cobro | IncomingPayment | factura, SessionPayment, conciliación | Un registro por medio/operación |
| Devolución | CreditNote/Bill y líneas | reintegro, recepción, ventas | Respetar cantidad original |
| Reintegro | OutgoingPayment | Bill, PaymentMethod, caja | No reescribir cobro original |
| Stock físico | InvLedger | available, reportes, reposición | Sólo movimientos activos/aceptados |
| Reservas | ResLedger | available y reposición | Conservar signo y skipAvailable |
| Stocktake | Adjustment/InvAdjustment | InvLedger y costos | real − teórico |
| Costo físico | CostLedger | SalesLedger/valuación | Método/capa/fecha explícitos |
| Costo planificado | ItemCost | estimación/fallback | Nunca presentarlo como real |
| Margen | SalesLedger | BI/reportes | Preservar fuente de costo |
| Snapshot de reposición | Adaptador Rubrova | Planificador | Proyección derivada; no escribe al ERP |

Las claves de intercambio del export de reposición no son necesariamente PK: inventario por productId+locationId; línea de venta por número+índice; recepción por número+índice; múltiples ShipmentLine se agrupan por Sales.OrderLine. No asumir unicidad global fuera del documento/serie/compañía probados.

---

## 8. Registro de riesgos y prioridades vigentes

### P0 — primero, antes de ampliar el circuito comercial

1. **Devolución parcial:** diagnosticar cuerpo 5-byte y Content-Type; investigar Bill.amount y OutgoingPayment.amount; probar dos credit notes, rechazo real, egresos correctos, Receipt, InvLedger, neto por método, acumulado de reintegros, cancelación y reinicio.
2. **Stocktake: aceptación runtime de NULL/cero y selección Fill:** probar que q=0 se crea/actualiza, q=NULL limpia y una hoja con cantidad cero se agrega al Adjustment padre; comprobar `difference`, InvAdjustment e InvLedger en ubicación aislada. Diferenciar `onHand=0` (valor presente) de `onHand=NULL` (sin balance derivado) en el autollenado y definir cómo agregar productos sin movimientos.
3. **FIFO temporal:** reproducir salida anterior a entrada; definir semántica; sólo entonces cambiar algoritmo y test.
4. **SalesLedger costo real:** probar sin/partial/full shipment y devoluciones sin/con receipt; confirmar selección/semántica de ABSTRACT VALUE.
5. **Restore selectivo:** fallo pg_restore, fallo por tabla, import parcial y cleanup; error inequívoco, sin DB temporal huérfana ni aplicación parcial.
6. **Permisos por ubicación:** probar APIs y documentos con usuarios sin filas, scope padre/hijo/denegación y varias compañías.

### P1 — operación local

- Prueba en Mac físico Apple Silicon.
- Instalación limpia, doctor, login, venta, devolución, cierre, reinicio, backup y restore.
- Offline con egress bloqueado.
- Arqueo físico efectivo (teórico vs contado, diferencia/motivo/cajero/supervisor) separado de SessionPayment.
- Vuelto, pagos mixtos, depósitos y retiros, cancelación y persistencia.

### P2 — integración y continuidad

- Conciliar reposición con base local MyCompany real y evidencia anonimizada.
- Wrapper sólo donde falten versionado, idempotencia, cursor, permisos, correlación o reconciliación.
- Adquirente/terminal con sandbox, bridge local, firma de webhook, consulta de estado y conciliación.
- Backup portátil integral con adjuntos/documentos/configuración y recuperación en otra PC.

### P3 — fiscalidad/canales

- Adapter ARCA argentino; numeración, puntos de venta, CAE/CAEA, contingencia, reintento y conciliación.
- Marketplace/ecommerce/WhatsApp, evitar doble facturación cuando marketplace ya emitió.
- Servicios B2B, mayorista/distribución y logística avanzada sin cambiar la autoridad del POS/ERP local.

---

<a id="roadmap-técnico-único-y-definición-de-terminado"></a>

## 9. Roadmap técnico único y definición de terminado

### Hito A — conocimiento y contratos
**Consolidado en este manual.** Toda investigación futura actualiza este archivo; sus anexos preservan la historia.

### Hito B — POS transaccional seguro (prioridad activa)
Cerrar devolución parcial, reintegros por medio, conciliación de caja y stock, cancelación y persistencia. Salida: venta→cobro→devolución parcial/total→reintegro→reingreso físico→caja/stock conciliados→reinicio.

### Hito C — inventario y costos confiables
Stocktake cero, FIFO temporal, SalesLedger de costo real, permisos por ubicación. Salida: conteos, ajustes, recepciones, despachos, transferencias y valoración histórica coherentes con ledgers nativos.

### Hito D — recuperación local
Mac físico, offline, backup integral y restore en PC nueva. Salida: instalación y recuperación sin dependencia cloud, con datos, adjuntos y configuración verificables.

### Hito E — ERP administrativo y localización argentina
Compras, recepción parcial, proveedores, costo puesto, cuentas corrientes, bancos, ARCA e interoperabilidad contable. Salida: circuito comercial/contable/fiscal conciliado.

### Hito F — analítica
Captura histórica correcta desde día uno; rentabilidad/demanda por producto, rubro, marca, canal, área, sucursal, cliente y temporada. Salida: métricas trazables, hechos separados de estimaciones y pruebas fuera de muestra.

### Hito G — canales/logística
Ecommerce, Mercado Libre, WhatsApp, mayorista, distribución, servicios B2B y transportistas. Salida: pedidos reconciliados sin duplicar venta, pago, comprobante ni stock.

**Definition of done transversal:** el código está en main; contrato documentado; pruebas pertinentes pasan en el SHA integrado; se nombra plataforma/runtime; se concilian ledgers y estados; logs permiten diagnosticar; rollback/restore está definido; las limitaciones no probadas se declaran.

---

## 10. Registro de trabajo futuro

Cada nueva entrada se añade en orden cronológico aquí:
- ID y fecha.
- Pregunta/síntoma y objetivo.
- SHA de Rubrova y commits de los vendors.
- Archivos/propiedades/acciones inspeccionados.
- Propietario del dato, flujo y contrato afectados.
- Hechos de fuente y hechos de test por separado.
- Hipótesis/alternativas y cómo se discriminaron.
- Decisión/cambio realizado.
- Run/job, SHA, ambiente y resultados.
- Pendientes y criterio de cierre.
- Hito de roadmap.

No llamar “solucionado” a un error sin reproducir la solución en la prueba que fallaba.

### 2026-11-26 — REP-021 — Corrección de semántica NULL/cero en stocktake

- La hipótesis inicial de que `IF q THEN` borraba la cantidad `0` se basó en interpretar la condición como truthiness numérica. Esa interpretación era incorrecta para lsFusion: la condición se considera cumplida cuando el valor no es `NULL`; `NUMERIC 0` es un valor no nulo.
- La misma precisión aplica a `Adjustment.fill` y `InvLedgerAPI`: usar `onHand(...)` como condición comprueba presencia, no `onHand > 0`. Un valor numérico cero puede pasar; un resultado `NULL` puede quedar fuera.
- Se retiró el parche temporal de `IS NOT NULL`, se eliminó la prueba estática derivada de la hipótesis y se restauró `AdjustmentListSearch.lsf` exactamente al blob original fijado (`557ab54dc51c14a06b45d952295db58c33ca9d66`). El script de parches Rubrova ya no contiene esa transformación.
- **Estado:** fuente y semántica documental corregidas; runtime de conteo por barcode y política de `Fill` siguen pendientes. No afirmar que el circuito se validó en ejecución.


---


### 2026-11-26 — REP-022 — Aceptación runtime de captura por barcode (en validación)

- Se añade a la fixture descartable de CI un Adjustment en progreso con una AdjustmentList nativa, enlazada al mismo producto/ubicación sintéticos de POS.
- La prueba invoca el helper upstream `Inventory.setRealQuantity`, que es el utilizado por `@defineBarCodeSearch`: primero ingresa `0`, verifica que exista una fila y que `listRealQuantity` se agregue a `AdjustmentLine`; luego ingresa `NULL` y verifica que la fila se elimine; finalmente reingresa `2` y concilia ambas cantidades.
- El Adjustment queda sin validar. No crea InvAdjustment ni modifica InvLedger/onHand, por lo que no contamina la venta POS ni su conciliación.
- La misma cantidad positiva se consulta después del reinicio del runtime para verificar persistencia de la hoja y del Adjustment padre.
- **Límite explícito:** esto no acepta todavía `Adjustment.fill` para la distinción entre `onHand=0` y `onHand=NULL`, ni prueba conteo ciego, reconteo, tolerancias, permisos o doble validación. Tampoco equivale a una prueba física con lector barcode real; la ruta de backend se ejercita invocando el helper que usa la pantalla.
- **Evidencia inicial (run #454, SHA `38805f47cc3697034e73c1b7837e5dab8d26ddea`):** preflight, Windows y compilación pasaron; el smoke nativo arrancó, pero falló porque `AdjustmentListLine` tenía una fila con `0` y no existía la `AdjustmentLine` agregada (`listLineCount=1`, `adjustmentLineCount=0`). El cero quedó almacenado en la hoja, pero no se propagó al documento padre. La corrección se valida en el registro REP-024; aún no se acepta el circuito.


### 2026-11-26 — REP-023 — Cálculo de importe en devolución parcial y eventos locales

- **Hecho observado:** en el run 45876903441, el endpoint de CI para devoluciones devolvió HTTP 200 con un cuerpo de 5 bytes; el inspector falló al parsearlo como JSON. En `adjust.log` quedó el mensaje `Property Importe(Invoicing.amount[Invoicing.OutgoingPayment] ...) is not set` para el egreso `OVN/000001`. El contenido exacto de los cinco bytes no se capturó en esa ejecución.
- **Hechos de fuente:** el POS de MyCompany usa `PosDashboardReturnPayment.posPayment`: limita cada importe por medio al cobrado originalmente, registra `OutgoingPayment` por cada método, asigna `amount(p)` desde el importe ingresado para ese medio y sólo después marca la nota lista y ejecuta `APPLY`. Además, `BillPayment.registerPayment` usa `fill(OutgoingPayment, Bill)`, llama `executeLocalEvents()` y luego calcula `sourceLeft(b)` antes de completar el egreso.
- **Diferencia detectada en el fixture anterior:** tras `Invoicing.create(b, i)` y el ajuste de cantidad, el fixture creaba `OutgoingPayment` y asignaba `amount(p) <- amount(b)` sin ejecutar explícitamente los eventos locales de la nota. El hook nativo `CreditNote.fill(BillLine, InvoiceLine)` y los eventos que completan precio/impuestos dependen de ese ciclo local.
- **Hipótesis prioritaria, todavía no causa raíz confirmada:** la lectura de `amount(b)` precedía a la ejecución de eventos locales que materializan precio/impuestos de las líneas, por lo que el valor transferido a la propiedad no nula `OutgoingPayment.amount` quedaba ausente. La secuencia nativa de `BillPayment.registerPayment` respalda la necesidad de ejecutar esos eventos antes de consultar el saldo.
- **Cambio preparado desde main:** se portó el módulo `RubrovaRetailReturns` y su cableado de despliegue/lock/CI sobre la base vigente. El fixture ahora llama `executeLocalEvents()` después de crear la nota y otra vez después de cambiar la cantidad. El inspector registra Content-Type y cuerpo textual cuando el endpoint no devuelve JSON válido.
- **Criterio de aceptación:** compilación del fork, prevalidación y scripts Windows, smoke nativo macOS ARM64, dos devoluciones (0,4 y remanente 0,6), rechazo de 0,7, dos reintegros por efectivo, reingreso físico de una unidad, caja neta cero y persistencia tras reinicio. Comprobar también que ninguna devolución por medio supera lo abonado originalmente con ese medio.
- **Límite:** el fixture actual es de efectivo sintético. El circuito mixto tarjeta/efectivo y la experiencia del operador se deberán probar con el mismo contrato de distribución por medio antes de aceptar operación real.
- **Resultado:** run 45901168467, SHA e7c1fc1be1463dc726065f2ac16508943b156f53, completó correctamente prevalidación, Windows, compilación completa y smoke nativo macOS ARM64. Verificó dos devoluciones (0,4 + 0,6), rechazo de 0,7, dos reintegros en efectivo por ARS 1.250, stock 9→10, caja neta cero y persistencia tras reinicio. Linux y Docker/Linux se omitieron.
- **Integración:** PR #15 fue integrado por squash en main, commit 04249dc983c3af066a386f1e1b022da2d9587ec0.
- **Límites:** aceptado para fixture sintética de efectivo. Pagos mixtos, reintegros tarjeta/QR y terminales/adquirentes reales siguen pendientes. La ejecución posterior del SHA integrado de main se registra por separado.

### 2026-11-26 — REP-024 — Diagnóstico del cero en el agregado de hojas de conteo

- **Revisión observada:** PR #14, SHA `38805f47cc3697034e73c1b7837e5dab8d26ddea`, ejecución #454, job macOS ARM64 nativo.
- **Hecho del runtime:** al ingresar la primera cantidad `0`, la API devolvió HTTP 200 y `listLineCount=1`, pero `adjustmentLineCount=0`. El servidor nativo y la compilación del fork pasaron; el fallo se produjo en el flujo de aceptación funcional.
- **Causa identificada en la semántica del lenguaje:** `AdjustmentList.listRealQuantity` era un `GROUP SUM` directo. En lsFusion, una suma cuyo resultado es cero devuelve `NULL`. Por eso el agregado no distinguía una fila contada en cero de un grupo sin filas, y el `WHEN SETCHANGED(listRealQuantity(...))` nativo no podía materializar el padre al pasar de grupo vacío a suma cero. La documentación de lsFusion también confirma que los agregados `GROUP MAX` pueden conservar un cero no nulo y que `OVERRIDE` permite usar un valor de respaldo.
- **Decisión:** preservar el `GROUP SUM` nativo y agregar una segunda agregación que produce `0.000` sólo cuando existe al menos una línea con cantidad no nula. `OVERRIDE` usa la suma original cuando no es cero y ese respaldo cuando la suma devuelve `NULL`; si no queda ninguna línea, ambas agregaciones son `NULL`. Así el evento upstream conserva su función original, el cero llega al padre y `NULL` sigue significando grupo vacío.
- **Implementación reproducible:** `scripts/platform/apply-rubrova-source-patches.py` aplica el cambio al módulo propietario `AdjustmentList.lsf`, con ancla exacta, marcadores, detección de drift e idempotencia. No se crean clases ni ledgers paralelos.
- **Fallos intermedios:** run #455 falló sólo por una aserción estática sensible a mayúsculas (`el` frente a `El`); run #456 compiló los artefactos Java del fork, pero el runtime abortó al parsear `IS NULL` en la fixture, sintaxis que no existe en lsFusion. Para comprobar ausencia se usa `NOT propiedad(...)`, conforme a la semántica del lenguaje.
- **Cobertura:** la prueba exige fila padre/cantidad cero, borrado de la hoja con línea padre retenida y cantidad NULL, cantidad positiva 2, stock físico sin cambios mientras el Adjustment sigue pendiente y persistencia después del reinicio.
- **Estado:** corrección del agregado y sintaxis de fixture en nueva revisión de PR #14; pendiente de compilación de lógica y smoke ARM64. Ningún resultado funcional se considera aprobado todavía.

### 2026-11-26 — REP-025 — Fallo del runtime #456 y corrección de sintaxis de ausencia

- **Ejecución:** #456, SHA `0b314ed5a24036f2022c150d5594b1d0e65a0784`; prevalidación Node/Python, Windows y build Java/Maven pasaron.
- **Fallo exacto:** el servidor abortó durante el parseo de módulos con `RubrovaCISalesFixture:190:98 no viable alternative at input 'NULL'`. La causa fue usar `IS NULL`, operador de SQL que no forma parte del lenguaje lsFusion. El smoke funcional no comenzó.
- **Corrección:** la sonda ahora usa `NOT Inventory.realQuantity(...)`, que devuelve TRUE cuando la propiedad no tiene valor y distingue cero (no nulo) de ausencia. El test estático prohíbe reintroducir `IS NULL` en la fixture.
- **Estado:** nueva revisión pendiente de ejecución. El fallo de #456 no invalida el build Java completado, pero tampoco aporta evidencia del flujo de conteo.

### 2026-11-26 — REP-026 — Corrección de lectura del conteo cero en la sonda

- **Ejecución:** run 45905585216, job macOS ARM64 140202817953, SHA 689e0101c881ee640514e8ec9db5b7c4f7589687.
- **Resultado observado:** prevalidación, validación Windows y compilación pasaron. El servidor nativo inició y la API respondió HTTP 200. La sonda informó listLineCount=1, adjustmentLineCount=1, adjustmentQuantityIsZero=true y onHand=10, pero no exportó zeroQuantityPreserved; el inspector falló al exigirlo.
- **Interpretación:** la prueba consultaba una propiedad agregada de la lista, no la cantidad almacenada en la fila individual AdjustmentListLine. Esa lectura no es una prueba fiable del cero de la línea. El log confirma que el cero llegó a la línea principal del Adjustment y que el conteo pendiente no alteró onHand.
- **Corrección preparada:** resolver la AdjustmentListLine sintética por lista/producto/ubicación y leer directamente Inventory.realQuantity(AdjustmentListLine). La API positiva y la comprobación tras reinicio usan el mismo acceso por fila. Se añade una regresión estática para impedir volver a consultar el agregado equivocado.
- **Estado:** corrección preparada para revalidación sobre el main vigente. No se acepta todavía el circuito barcode.

### 2026-11-26 — REP-027 — Expectativa de inventario tras venta y devolución completa

- **Ejecución:** run 45907277530 (#459), job macOS ARM64 `140208799219`, SHA `92786b7258378b063bed9ce3a5b71fdf3d2b505a`.
- **Checks previos:** prevalidación compartida, Windows y compilación completa del fork pasaron.
- **Hechos del smoke:** los endpoints de stocktake devolvieron HTTP 200. El caso cero confirmó `listLineCount=1`, `adjustmentLineCount=1`, `zeroQuantityPreserved=true`, `adjustmentQuantityIsZero=true`, `onHand=10`. El caso NULL dejó cero filas en AdjustmentList, conservó la AdjustmentLine con cantidad NULL y mantuvo `onHand=10`. El caso positivo guardó 2 tanto en la fila de lista como en AdjustmentLine, sin alterar `onHand=10`.
- **Fallo real:** después del reinicio, la hoja y sus cantidades 2 persistieron. El único error fue que el inspector esperaba `onHand=9`, pero el endpoint devolvió 10.
- **Causa:** el flujo E2E no termina sólo con la venta de una unidad. Después de vender 1 (stock 10→9), ejecuta la devolución completa en dos partes (0,4 + 0,6), que reingresa la unidad (stock 9→10). El valor persistido correcto al final del escenario es 10, y coincide con `UI_PARTIAL_RETURNS_INVENTORY` y la sonda de reinicio del POS. No es evidencia de que el Adjustment pendiente haya alterado stock.
- **Corrección:** la sonda de persistencia espera 10 y el mensaje explica que se compara después de venta y devoluciones. La regresión estática exige ese contrato para impedir una expectativa desfasada.
- **Límite:** cero, NULL, positivo y persistencia de fila pasan en la ejecución #459; el run global quedó rojo únicamente por la expectativa de stock. El circuito no se declara aceptado hasta que un nuevo smoke completo termine verde con la expectativa corregida.

### 2026-11-26 — REP-028 — Aceptación nativa del conteo por barcode e integración en main

- **Ejecución:** run #462, ID `45909363575`; job nativo macOS ARM64 `140215704940`; HEAD probado `12f29a47e7b89f6f162c85a7e3684e24f9fe793b`.
- **Checks:** prevalidación compartida, validación Windows, compilación completa del fork lsFusion + MyCompany 6.2, cliente GWT y smoke funcional nativo finalizaron correctamente.
- **Cero:** `AdjustmentListLine` y `AdjustmentLine` permanecieron presentes; la cantidad cero se conservó y el stock físico siguió en 10.
- **NULL:** la fila de la hoja se eliminó, la línea principal del ajuste permaneció sin cantidad y el stock físico siguió en 10.
- **Positivo:** la cantidad 2 se reconcilió entre la fila de hoja y la línea principal; el stock físico siguió en 10.
- **Reinicio:** tras reiniciar servidor, hoja, líneas y cantidad 2 persistieron; el stock físico permaneció en 10.
- **Escenario POS simultáneo:** el smoke confirmó rechazo del exceso de devolución, cantidades remanentes, dos reintegros en efectivo, cierre de turno, caja conciliada y persistencia de devoluciones.
- **Resultado:** todos los marcadores obligatorios de conteo y persistencia se emitieron; el run #462 terminó `success`. El run #459, documentado en REP-027, había quedado rojo por una expectativa incorrecta de stock final (9 en vez de 10); la expectativa corregida pasó en #462.
- **Integración:** PR [#14](https://github.com/JavierGrecco/Rubrova/pull/14) se fusionó por squash en `main`, commit [c38fad5](https://github.com/JavierGrecco/Rubrova/commit/c38fad581f669bd7e1a2795123cc8ecca242e010).
- **Fuentes vendorizadas:** run [#24](https://github.com/JavierGrecco/Rubrova/actions/runs/45911383784) creó el commit `7d9e5bb80e866df87b51baad852c1e6256270dd1`, aplicando a `vendor/mycompany/.../AdjustmentList.lsf` la corrección de agregación validada; su compilación de fuentes estaba en curso al redactar este informe.
- **Verificación del merge:** run #463, ID `45911383909`, se lanzó sobre `c38fad5`; prevalidación y Windows pasaron, build pendiente al corte. No incluye el commit de fuentes `7d9e5bb`.
- **Límites:** Linux x86_64 y Docker/Linux fueron omitidos; aceptación offline no probada; egress de red no bloqueado. El Adjustment de conteo permaneció sin validar y no generó movimiento de inventario. Esto prueba semántica de captura y persistencia, no un proceso productivo completo de inventario físico.

### 2026-11-26 — REP-029 — Límite acumulado de reintegros por método de pago

- **Fuente nativa examinada:** `retail/pos/dashboard/return/PosDashboardReturnPayment.lsf`, `retail/sessions/SessionPayment.lsf`, `invoicing/invoices/creditnotes/CreditNote.lsf`, `invoicing/bills/BillCanceled.lsf` y la macro `defineDocLineRelation` de `utils/Doc.lsf`.
- **Hecho observado:** `invalidAmount(Bill, PaymentMethod)` compara el reintegro actual con `invoicePaid(Bill, PaymentMethod)`, suma original de la factura para ese medio. No resta los pagos de reintegros anteriores.
- **Relaciones disponibles:** `SessionPayment` define el método de cada `OutgoingPayment` por nota y agrega `paid(Bill, PaymentMethod)`. La relación nativa `in(Invoice, Bill)` enlaza cada nota a su factura original mediante las líneas. `active(Bill)` excluye notas no listas o canceladas.
- **Riesgo:** dos devoluciones sucesivas podrían ser cada una menor al total originalmente pagado por el medio y, aun así, excederlo al sumarlas. El smoke actual es sólo de efectivo y reembolsa exactamente ARS 1.250; no cubre una sobredevolución acumulada con tarjeta/QR ni múltiples medios.
- **Diseño por validar:** agregar la suma de egresos de notas anteriores activas ligadas a la misma factura y método, excluyendo la nota actual, restarla al monto originalmente pagado y aplicar el límite tanto en la UI nativa como en una validación de servidor que resista concurrencia y replay.
- **Estado:** diagnóstico de fuente confirmado; implementación y pruebas de runtime pendientes. No hay aceptación de reintegros mixtos, tarjetas o QR por esta inspección.
- **Criterio de aceptación:** factura sintética de efectivo ARS 500 + tarjeta ARS 750; primera nota reembolsa ARS 300 + ARS 250; segunda nota por tarjeta ARS 600 se rechaza (acumulado 850); importe válido de ARS 500 se acepta (acumulado 750); cancelar una nota libera su importe sólo si la nota deja de estar activa; dos confirmaciones concurrentes no pueden superar el límite; conciliación de los ledgers nativos y persistencia post-reinicio.

### 2026-11-26 — REP-030 — Implementación del límite acumulado de reintegros en revisión

- **Rama:** `work/pos-refund-cumulative-method-guard`, creada desde `main` `a994c271e5bdf2fce73a525d1083ac22c99a4e56`.
- **Cambio en extensión:** `RubrovaRetailReturns.lsf` agrega el agregado de egresos activos por factura/método, el cálculo del cupo remanente, y una restricción global que impide superar lo cobrado originalmente.
- **Cambio de runtime:** `apply-rubrova-source-patches.py` modifica el diálogo nativo `PosDashboardReturnPayment` para mostrar el remanente y realizar la confirmación con `APPLY SERIALIZABLE`. El parche usa anclas exactas e idempotencia; cualquier drift o aplicación parcial debe detener la compilación.
- **Dependencia del módulo POS:** el parche agrega `RubrovaRetailRefundLimits` a la declaración `REQUIRE` de `PosDashboardReturnPayment`; declarar las propiedades en el módulo superior no las hace visibles automáticamente al diálogo nativo.
- **Semántica de cancelación corregida:** la suma del cupo filtra `Invoicing.active(OutgoingPayment)`, no `active(Bill)`. Cancelar la nota no cancela automáticamente los egresos relacionados; el saldo de salida continúa consumiendo cupo hasta cancelar cada pago nativo.
- **Fixture añadida:** segundo POS sintético y turno abierto mediante los hooks nativos `beforeOpen` / `afterOpen`, con factura pagada ARS 500 en efectivo + ARS 750 en tarjeta; exceso acumulado, dos reintegros concurrentes, cancelación aislada de nota y cancelación de los dos egresos.
- **Aserciones añadidas:** prevalidación estática de la regla global, parche nativo, semántica de cancelación, llamadas concurrentes y marcadores obligatorios del smoke/reinicio.
- **Evidencia del run #481 (SHA `caf5a834`):** la prevalidación y la compilación completa de lsFusion/MyCompany terminaron correctamente; el smoke macOS ARM64 detuvo el servidor al inicializar la lógica: `PosDashboardReturnPayment:8:85 property or action 'rubrovaRefundRemaining[Invoicing.Bill,Retail.PaymentMethod]' is not found`. La causa inmediata es la falta de una dependencia explícita del módulo POS hacia el módulo que declara el guard.
- **Corrección en esta revisión:** `RubrovaRetailRefundLimits` depende de `CreditNote`, `SessionPayment`, `IncomingPaymentDebt` y `RubrovaRetailReturns`; esta última depende de `CreditNote` y `OutgoingPaymentDebt`. Se elimina el requisito del agregado `MyCompany` de ambas extensiones para evitar el ciclo `MyCompany → Retail → PosDashboardReturnPayment → RubrovaRetailRefundLimits → MyCompany`. El patcher declara ahora la dependencia directa del diálogo POS y comprueba su ancla exacta e idempotencia.
- **Evidencia del run #482 (SHA `3fe5fd5`):** Windows pasó; la prevalidación falló antes de compilar. El test de arquitectura contenía una aserción del texto `source.replace` con escape incorrecto y el test de devoluciones parciales aún esperaba las declaraciones `REQUIRE` anteriores a la refactorización. No es evidencia de un fallo en runtime ni valida todavía el nuevo grafo. Se actualizan las aserciones para comprobar el texto real y los nuevos requisitos hoja; el workflow nativo quedó omitido por dependencia del preflight.
- **Evidencia del run #483 (SHA `b91001b`):** la prevalidación encontró un falso positivo en la aserción de ausencia de `MyCompany`: la segunda línea de `RubrovaRetailReturns.lsf` contiene un comentario que menciona el agregado, aunque la declaración `REQUIRE` no lo incluye. El resto de pruebas estáticas superó sus comprobaciones; se ajusta la aserción para excluir el comentario y evaluar sólo la declaración. El build y el smoke nativo quedaron omitidos por dependencia del preflight.
- **Evidencia del run #484 (SHA `d6e39a8`):** prevalidación, validación Windows y compilación completa del fork lsFusion/MyCompany pasaron. El smoke macOS ARM64 llegó al arranque, pero el servidor se detuvo con `PosDashboardReturnPayment:38:52 property 'invoicePaid(b,pm)' is not found`. El formulario ya reemplazaba `invoicePaid` por los dos importes Rubrova, pero el bloque `DESIGN` conservaba `PROPERTY(invoicePaid(b, pm))`; se identificó la referencia de diseño obsoleta como causa inmediata.
- **Corrección en esta revisión:** el patcher reemplaza también la celda del diseño por `rubrovaOriginalPaidForReturn` y `rubrovaRefundRemaining`. El lock `platform/mycompany-6.2.lock.json` se sincroniza con las dependencias hoja reales: `RubrovaRetailReturns` requiere `CreditNote` y `OutgoingPaymentDebt`; `RubrovaRetailRefundLimits` requiere `CreditNote`, `SessionPayment`, `IncomingPaymentDebt` y `RubrovaRetailReturns`. La prevalidación exige el mapeo para impedir que el diseño quede fuera del parche.
- **Evidencia del run #485 (SHA `7b5f6b5`):** Windows pasó; la prevalidación detectó que el lock reproducible había cambiado a las dependencias hoja nuevas, pero la aserción de contrato seguía esperando `MyCompany` en ambas extensiones. El build y el runtime quedaron omitidos. Se alinearon las expectativas del lock. En la misma revisión se endurece la comprobación idempotente contra un diseño que conserve `invoicePaid`, y el texto del reemplazo visual se construye con `chr(10).join` para evitar ambigüedades de escape al generar el parche Python.
- **Evidencia del run #486 (SHA `045c022`):** prevalidación, Windows y compilación completa pasaron. El servidor nativo macOS ARM64 llegó al inicializador de lógica y falló en `RubrovaPOSLocalization:92:32` porque el caption seguía referenciando `invoicePaid(b,pm)`. La referencia pertenecía al diseño localizado del diálogo; el formulario nativo ya mostraba las nuevas propiedades Rubrova, por lo que esa referencia antigua no estaba disponible desde el módulo de localización. No llegaron a ejecutarse la fixture de reintegros, la carrera concurrente ni la prueba de persistencia.
- **Corrección aplicada después del #486:** `RubrovaPOSLocalization` pasa a requerir directamente `RubrovaRetailRefundLimits` y sus captions apuntan a `rubrovaOriginalPaidForReturn` y `rubrovaRefundRemaining`. Se incorpora la clave `rubrova.pos.refund_remaining`, se sincroniza el lock y se añade una regresión estática que prohíbe volver a referenciar `invoicePaid` desde localización.
- **Evidencia del run #487 (SHA `c865d88`):** Windows pasó. La prevalidación ejecutó 36 pruebas: 35 pasaron y una falló por una expectativa de test obsoleta en la línea 679, que todavía exigía `PROPERTY(invoicePaid(b, pm))` dentro de `RubrovaPOSLocalization`; el propio log mostró que los nuevos captions estaban presentes. Build y smoke quedaron omitidos. No fue un fallo de compilación ni runtime. La expectativa se sustituyó por comprobaciones de los dos campos Rubrova y ausencia del identificador antiguo.
- **Evidencia del run #488 (SHA `fd111a1`):** prevalidación (36 + 34 pruebas), Windows y compilación completa pasaron. El servidor nativo ARM64 llegó a inicializar `RubrovaRetailRefundLimits`, `PosDashboardReturnPayment`, `RubrovaPOSLocalization` y 721 de 723 módulos; el fallo se produjo al compilar la fixture de ventas, en la línea 189:26, por la referencia no tipada `Retail.session(b)` dentro de un agregado de egresos. lsFusion informó que coexistían las variantes de `SessionInvoice` para `Invoice`/`Bill` y las variantes de `PosDashboardCash` para pagos entrantes/salientes. El motor se detuvo antes de llamar a las APIs de prueba. No hay todavía evidencia E2E de reintegros.
- **Corrección después del #488:** los dos agregados de importes de egresos (`rubrovaCIReturnCashPaymentAmount` y `rubrovaCIMixedActivePaymentAmount`) declaran ahora `Retail.session(Invoicing.Bill b)` explícitamente. Se añaden aserciones para impedir que esos filtros vuelvan a introducir una referencia ambigua. Se conserva el uso de la relación nativa de sesión/egreso de MyCompany; no se agrega un campo ni una relación paralela.
- **Evidencia del run #489 (PR head `a7f63b2`; checkout de integración `bf4dbde`):** prevalidación 36/36, Windows y compilación completa pasaron. El smoke macOS ARM64 alcanzó la carga de `RubrovaRetailRefundLimits`, `PosDashboardReturnPayment`, `RubrovaPOSLocalization` y la fixture de ventas, pero lsFusion rechazó `RubrovaCISalesFixture:443:51` con `use NULL instead of FALSE`. El fallo ocurrió antes de login y antes de cualquier llamada E2E; no demuestra ni refuta el comportamiento del límite de reintegros.
- **Causa inmediata del #489:** `rubrovaCIMixedOverLimitRejected` es un `DATA BOOLEAN` persistente. Su reinicio estaba escrito con `FALSE`; lsFusion exigió limpiar el valor con `NULL`. En ese momento se asumió erróneamente que la regla no aplicaba a `DATA LOCAL NESTED BOOLEAN`.
- **Evidencia del run #490 (SHA `5a62862`):** preflight 37/37 pruebas Node y 34/34 pruebas adicionales, Windows y compilación completa pasaron. El smoke macOS ARM64 falló al inicializar la fixture con `RubrovaCISalesFixture:459:56 use NULL instead of FALSE`. El diagnóstico nuevo identificó el stage, la clase de fallo y el código de salida del supervisor. La ubicación correspondió a `rubrovaCIMixedOverLimitRejectedLocal() <- FALSE`, que es `DATA LOCAL NESTED BOOLEAN`: la misma regla aplica tanto a los valores booleanos persistentes como a los booleanos locales de esta fixture. No se ejecutaron login ni APIs E2E.
- **Evidencia del run #491 (HEAD `e57f2e6`, [workflow](https://github.com/JavierGrecco/Rubrova/actions/runs/45933719063)):** preflight 37/37 Node y 34/34 pruebas adicionales, validación Windows y compilación completa lsFusion 6.2 + cliente GWT + MyCompany 6.2 pasaron. El smoke nativo macOS ARM64 alcanzó PostgreSQL/RMI/Tomcat, abrió la interfaz y autenticó al usuario administrador. Se abrieron el POS y el turno, se completó una venta en efectivo de ARS 1.250 y pasó la reconciliación de inventario; también pasaron la devolución parcial con rechazo de exceso y el conteo por barcode (cero frente a NULL y agregación). El smoke se detuvo antes de probar el guard acumulado: la API de preparación devolvió `sourceInvoiceFound=0`.
- **Causa del #491 identificada en las fuentes fijadas de MyCompany 6.2:** el método de pago `card` se enlaza a `customerbank`, cuyo tipo permite `BankAccount` y rechaza `CashAccount`; el tipo `customercash` permite `CashAccount`. Las constraints de `IncomingPayment.lsf` y `OutgoingPayment.lsf` lo expresan por tipo. Las dos fixtures propias habían configurado la cuenta de tarjeta como `CashAccount`. La transacción de factura mixta se cancelaba con `For this type of payment, company cash registers are not allowed`, por lo que no existía factura al consultar la API.
- **Corrección aplicada en esta revisión:** cambiar la cuenta asociada a tarjeta a una `BankAccount` real, vinculada a un banco sintético y con número de cuenta, tanto en la fixture CI como en la demostración local. La demostración también migra la cuenta del POS ya existente, en lugar de aplicar el cambio sólo en instalaciones nuevas. Se mantiene la asociación de efectivo a `CashAccount` y se conserva el uso nativo de `companyAccount` del POS; no se elimina el vínculo financiero ni se modifica el flujo estándar de cobro. Las regresiones estáticas exigen esta correspondencia de tipos.
- **Límites de la evidencia #491:** no se ejecutaron ni aceptaron aún el exceso acumulado por método, la carrera SERIALIZABLE, la cancelación separada de nota y egresos, la liberación de cupo ni la persistencia post-reinicio del escenario mixto. La corrección de cuenta bancaria necesita un nuevo build y smoke ARM64; no se debe inferir su éxito antes del runtime.
- **Evidencia del run #492 (SHA `7d08b88`, [workflow](https://github.com/JavierGrecco/Rubrova/actions/runs/45935917035)):** preflight 37/37 Node y 34/34 pruebas adicionales, Windows y compilación completa pasaron. El smoke nativo ARM64 inició PostgreSQL/RMI/Tomcat, abrió la interfaz, autenticó al administrador y completó venta, devolución parcial en efectivo y stocktake. La fixture de medios mixtos ya encontró la factura y registró correctamente el pago original de ARS 500 en efectivo + ARS 750 en tarjeta; la primera devolución registró ARS 200 en efectivo + ARS 300 en tarjeta.
- **Fallo funcional real en #492:** el intento de devolver otros ARS 600 de tarjeta (acumulado 300 + 600 > 750) fue bloqueado por `Account / cash balance cannot be negative`, no por la restricción `El total reintegrado por medio de pago supera el importe cobrado originalmente`. El saldo bancario de prueba contenía sólo el cobro original de ARS 750; tras devolver ARS 300 quedaban ARS 450, por lo que el egreso de ARS 600 habría dejado la cuenta en -ARS 150. El mensaje de rechazo no prueba la regla acumulativa, y el smoke falló correctamente. No se ejecutaron la carrera concurrente ni la persistencia del escenario mixto.
- **Corrección preparada tras #492:** agregar movimientos nativos independientes de saldo inicial (`IncomingPayment`, tipo `initial`) por ARS 1.000 a cada cuenta sintética (efectivo y banco), sin asociarlos a la factura minorista. Esto mantiene intactos los cobros originales aplicados de ARS 500/750 y permite que las operaciones de reintegro pasen el control legítimo de saldo de cuenta para que la restricción global se evalúe de manera independiente. Los saldos de cuenta quedan expuestos en las APIs de fixture y se concilian en cada etapa y después del reinicio.
- **Endurecimiento del inspector:** la respuesta perdedora de la carrera puede exportar `NULL` como `null`, no necesariamente `false`. El inspector ahora acepta cualquier valor distinto de `true` sólo si `applyMessage` contiene la causa exacta del límite acumulado; así no convierte un error de saldo, una caída o una serialización genérica en éxito.
- **Límite:** los saldos iniciales y el contrato de mensaje de concurrencia necesitan validación nativa en una nueva ejecución. No afirmar todavía que el guard acumulativo o la carrera fueron aceptados.
- **Corrección posterior al #490:** las cuatro inicializaciones restantes de booleanos locales (`rubrovaCIMixedOverLimitRejectedLocal`, `rubrovaCIMixedRaceAAccepted`, `rubrovaCIMixedRaceBAccepted` y `rubrovaCIMixedBillCancelRejectedLocal`) pasan de `FALSE` a `NULL`. El preflight exige explícitamente esos reinicios y prohíbe cualquier asignación `<- FALSE;` en la fixture para evitar que el motor encuentre el siguiente caso de a uno.
- **Ajuste adicional del diagnóstico:** el #490 mostró que el extractor podía confundir la hora `01:44:15` del log con una ubicación `Módulo:línea:columna`, porque aceptaba que el identificador comenzara con un dígito. El patrón ahora exige que el nombre de módulo comience con una letra o guion bajo, y la regresión estática protege esta condición.
- **Estado al commit `5a62862`:** las correcciones de inicialización de los dos errores detectados y la mejora de diagnóstico están en la rama/PR; el #490 no pasó el smoke por el segundo booleano inicializado con FALSE. Esta nueva revisión amplía la corrección a todos los reinicios booleanos de la fixture y corrige la extracción de ubicación. Pendientes nueva prevalidación, compilación y smoke ARM64.
- **Estado de aceptación:** no integrar a `main` ni declarar aceptado el límite acumulado hasta ejecutar el flujo autenticado y obtener conciliación y persistencia.
- **Riesgos pendientes de runtime:** resolver cualquier siguiente error de inicialización; después ejecutar las relaciones `Invoicing.in(Invoice, Bill)`, `Retail.paymentMethod(Bill, OutgoingPayment)`, acciones nativas de cancelación, eventos automáticos de recibo, exceso acumulado por método, concurrencia real, cancelación independiente de nota/egresos, conciliación y persistencia post-reinicio. Si falla, corregir en esta misma rama y conservar la evidencia del primer error.

### 2026-11-27 — REP-031 — Cuenta de tarjeta modelada con tipo incorrecto en fixtures POS

- **Evidencia:** workflow #491, SHA `e57f2e6`, smoke nativo macOS ARM64. Servidor, login, venta cash, devolución parcial y stocktake pasaron; la preparación mixta no encontró factura después de cancelarse el APPLY.
- **Causa confirmada en MyCompany 6.2:** `PaymentMethodInitial` mapea `card` a `customerbank`. Los tipos de pago bancario aceptan `BankAccount` y prohíben `CashAccount`; los tipos de efectivo aceptan `CashAccount`. La cuenta POS asociada a tarjeta se había creado erróneamente como `CashAccount` en las fixtures CI y de demostración.
- **Decisión:** modelar la cuenta de tarjeta como `BankAccount`, con banco y número de cuenta, conservando `CashAccount` para efectivo y la asignación financiera nativa del POS. La demostración repara además una cuenta POS ya creada.
- **Protección:** el test de extensión verifica la asignación a tipos de pago, las constraints nativas, ambos fixtures y los atributos de BankAccount. Falta ejecutar nuevamente el runtime real para confirmar que la factura mixta y los pagos bancarios se crean antes de evaluar el guard acumulado.

### 2026-11-27 — REP-036 — Evitar regex doblemente escapadas en regresión de cuentas

- **Evidencia:** workflow #496, HEAD `710cc6d`, [run](https://github.com/JavierGrecco/Rubrova/actions/runs/45941019832). Windows pasó. La prevalidación falló una prueba Node de las 37; las restantes 36 pasaron. Build y smoke quedaron omitidos por la dependencia correcta del preflight.
- **Causa:** la nueva regresión escribía expresiones regulares con doble escape y esperaba barras invertidas literales alrededor de paréntesis del código LSF. El texto fuente era correcto; la expectativa de test no coincidía.
- **Corrección:** reemplazar esos patrones por `String.includes` exactos para la expresión `cashBalance` y las asignaciones de cuenta de ambas cajas, además de comprobar que el puesto de reintegros no referencia las cuentas del POS principal.
- **Alcance:** no es evidencia de un error de compilación o runtime ni invalida el diagnóstico de contaminación entre fixtures de REP-035. Se requiere repetir el preflight y después build/runtime con el nuevo commit.

### 2026-11-27 — REP-035 — Aislar las cuentas sintéticas del POS de reintegros

- **Evidencia:** workflow #495, HEAD `ca5ff7e`, [run](https://github.com/JavierGrecco/Rubrova/actions/runs/45939652935). Preflight 37/37 Node y 34/34 validaciones adicionales, Windows y compilación completa pasaron.
- **Cobertura funcional observada:** macOS ARM64 completó autenticación, fixture de venta mixta, rechazo del exceso por método, carrera concurrente (una aceptación y un rechazo por el guard), cancelación de la nota sin liberar el cupo, cancelación de los dos egresos, liberación del cupo y conciliación: 3 notas, ARS 1.250, unidad devuelta, stock 10 y saldos finales ARS 1.000/1.000.
- **Fallo posterior:** el smoke general cerró el turno POS y devolvió ventas ARS 1.250, devoluciones ARS 1.250, pero `cashBalance=1000` en lugar de cero. La aserción de caja no se relaja.
- **Causa confirmada:** la fixture de dos puestos asignaba `cashAccountCI` y `cardAccountCI` tanto a `rubrova-ci` como a `rubrova-ci-refund`. MyCompany define `cashBalance(Pos)` como el saldo de `account(Pos, cashPaymentMethod())`; por tanto, el ingreso inicial independiente del segundo escenario impactaba el cajón del primero. El comportamiento detectado es una fuga de aislamiento entre datos sintéticos, no un problema del guard acumulado.
- **Corrección en esta revisión:** crear para el POS de reintegros su propia cuenta central, su propia `CashAccount` y su propia `BankAccount`; mantener las cuentas originales exclusivamente en el POS principal. Agregar test estático de tipo y asignación para ambas cajas, y prohibir que la caja secundaria vuelva a referenciar las cuentas del POS principal.
- **Pendiente:** preflight, compilación y smoke macOS ARM64; verificar que el cierre principal vuelve a caja neta cero, y luego completar reinicio/persistencia del escenario de reintegros. No integrar a `main` hasta pasar todas esas etapas.

- **Runs #496–#497:** [#496](https://github.com/JavierGrecco/Rubrova/actions/runs/45941019832), HEAD `710cc6d`, pasó Windows pero la prevalidación se detuvo por una aserción estática que esperaba una expresión de saldo ya sustituida en MyCompany. [#497](https://github.com/JavierGrecco/Rubrova/actions/runs/45941124530), HEAD `04e5e5f`, pasó prevalidación, Windows y compilación completa (lsFusion, GWT y MyCompany); el smoke macOS ARM64 volvió a detenerse antes del login.
- **Causa raíz del run #497:** las tres cuentas exclusivas de reintegros se declararon dentro del bloque de inicialización de `cardAccountCI`. La fixture comprobaba su existencia y las asignaciones, pero el parámetro `refundCentralAccountCI` no era visible desde la inicialización hermana `refundCashRegisterCI`; lsFusion abortó en `RubrovaCIRetailFixture:73:84` con `parameter 'refundCentralAccountCI' is not found`. No se ejecutaron APIs E2E en ese run.
- **Corrección:** mover las tres cuentas al ámbito padre de `bankCI`, antes de abrir `cardAccountCI`, para que ambos registros POS las reciban desde un ámbito visible. El test estático ahora comprueba posición y ámbito de las tres declaraciones, no sólo que los nombres existan.
- **Validación pendiente:** ejecutar una sola vez el workflow completo sobre el commit corregido. El criterio inmediato es que lsFusion inicialice la fixture y el servidor llegue al login; después deben volver a pasar el cierre de caja neta cero, guard por medio, concurrencia, cancelación de nota/egresos y persistencia. No integrar a `main` antes de completar esa aceptación.

### 2026-11-27 — REP-034 — Verificar cancelación de nota con estado nativo explícito

- **Evidencia:** workflow #494, HEAD `33e69893`, [run](https://github.com/JavierGrecco/Rubrova/actions/runs/45937795996). Preflight 37/37 Node, 34/34 validaciones adicionales, Windows y compilación completa pasaron. El smoke macOS ARM64 inició el servidor y completó la venta mixta, el exceso acumulado y la carrera concurrente.
- **Resultado de runtime:** exactamente una de las dos devoluciones concurrentes se aceptó; la perdedora informó el mensaje del límite acumulado. La cancelación de la primera nota conservó dos egresos activos, los importes reintegrados de ARS 500/750, los saldos de efectivo/banco de ARS 1.000/1.000 y rechazó otro reintegro por el guard.
- **Causa del fallo del smoke:** el inspector exigía `originalBillActive is False`. MyCompany define `active(Bill)` como `ready(Bill) AND NOT canceled(Bill)`; el resultado derivado inactivo no llegó como booleano `false` explícito en el JSON exportado. La aserción confundía la omisión de ese valor derivado con una nota activa, a pesar de las restantes evidencias. La cancelación aún debe verificarse con el estado persistido explícito; no se considera completada la cobertura de cancelación/persistencia.
- **Corrección en la rama:** exportar `canceled`, `ready` y una proyección textual `active/inactive` de la nota; comprobar esos campos al cancelar sólo la nota, después de cancelar sus egresos y tras reiniciar. La prueba estática también prohíbe volver a depender de la serialización del booleano derivado.
- **Pendiente de aceptación:** nuevo preflight, build y smoke macOS ARM64 para comprobar la corrección y ejecutar cancelación de egresos, conciliación y persistencia post-reinicio. No integrar a `main` mientras esas etapas sigan sin evidencia.

### 2026-11-27 — REP-033 — Acotar regresión estática del saldo inicial

- **Evidencia:** workflow #493, SHA `48c61d2`. Windows pasó. El preflight informó 36/37 pruebas Node aprobadas y una regresión fallida por una aserción demasiado amplia; por dependencia quedaron omitidos build y smoke nativo.
- **Causa:** el test prohibía toda aparición de `Retail.paymentMethod` en el bloque de saldos iniciales. La selección de la cuenta bancaria de tarjeta necesita consultar `Retail.paymentMethod('card')`, aunque el movimiento de apertura no se asocia a factura ni pago minorista aplicado.
- **Corrección:** prohibir únicamente `Invoicing.paid` y la relación `Retail.paymentMethod(openingCash|openingCard, ...)`. La selección de la cuenta por método permanece permitida.
- **Pendiente:** repetir preflight, build y smoke ARM64 para validar el uso real del tipo nativo `initial`, los saldos de ARS 1.000 y el mensaje del guard.

- **Prevalidación del run #493 (SHA `48c61d2`, [workflow](https://github.com/JavierGrecco/Rubrova/actions/runs/45937691881)):** Windows pasó. La prevalidación ejecutó 37 pruebas Node y encontró un único fallo en el test nuevo: la aserción que debía impedir asociar el saldo inicial a una factura también prohibía la referencia al método de pago necesaria para seleccionar la cuenta bancaria. El código de la fixture no había asociado el saldo inicial a ninguna factura; fue una expectativa estática demasiado amplia. Build y runtime quedaron omitidos por la dependencia del preflight. Se acota la aserción para prohibir sólo `Retail.paymentMethod(openingCash|openingCard, ...)` e `Invoicing.paid`, manteniendo permitido seleccionar la cuenta con `Retail.paymentMethod('card')`. No es evidencia de un fallo del motor ni del guard acumulado.

### 2026-11-27 — REP-032 — Separar saldo de tesorería del límite de reintegro

- **Evidencia:** workflow #492, SHA `7d08b88`. La factura mixta y el primer reintegro se guardaron correctamente: ARS 500 efectivo + ARS 750 tarjeta; reintegro de ARS 200 efectivo + ARS 300 tarjeta.
- **Causa del rechazo enmascarado:** el pago de salida de ARS 600 por tarjeta fue rechazado por el constraint nativo de saldo de cuenta porque el saldo bancario disponible quedaba en -ARS 150. El mensaje no correspondía al límite acumulado Rubrova. La prueba detectó correctamente esa diferencia y falló.
- **Decisión de test:** mantener activo el constraint nativo de saldo negativo. Aportar ARS 1.000 de saldo inicial independiente mediante pagos nativos `IncomingPayment` de tipo `initial` en las cuentas sintéticas de efectivo y banco. No asociarlos a la factura de venta; el cobro aplicado a esa factura sigue siendo exactamente ARS 500/750.
- **Conciliación adicional:** verificar saldo de cada cuenta en la preparación (ARS 1.300/1.450 después del primer reintegro), al completar el total (ARS 1.000/1.000), después de cancelar sólo la nota, después de cancelar los egresos y tras el reinicio.
- **Concurrencia:** un resultado `accepted=null` es un rechazo válido sólo cuando `applyMessage` informa explícitamente la restricción de límite acumulado. Un mensaje de saldo negativo o un error genérico no pasa.
- **Pendiente:** compilar y repetir el smoke ARM64. El guard aún no tiene aceptación E2E.

## 11. Anexos históricos preservados

Los anexos siguientes contienen el texto completo de las auditorías, contratos, relaciones, decisiones, iteraciones y hojas de trabajo anteriores. Los estados y referencias de sus cabeceras son históricos. Las secciones vigentes 1–10 prevalecen y se actualizan cuando exista evidencia nueva.



<a id="a-reuse-first"></a>

## Anexo A — Auditoría reuse-first de MyCompany y lsFusion

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Estado:** auditoría de fuentes y contratos; lo observado en código se distingue de lo que aún requiere prueba de runtime.  
**Revisión Rubrova:** 475ca9224520d296b23990071b1c79f00d6dced9.  
**Plataforma fijada:** lsFusion 6.2, commit dd4dbe5bf9b136e73e18fe25d741253929324350.  
**ERP/POS fijado:** MyCompany 6.2, commit d21ca6978717b98b6300d90267f9767db7414008.

> La regla para el producto es aprovechar primero el comportamiento nativo completo. No crear un documento, ledger, API o proceso Rubrova equivalente hasta haber seguido su implementación base desde la pantalla/acción hasta el documento, los estados, los pagos, los ledgers y los informes.

## 1. Resultado ejecutivo

El inventario fijado por el repositorio declara 1.335 archivos MyCompany, incluidos 800 módulos LSF, y 4.887 archivos de lsFusion, incluidos 3.330 fuentes Java. Los metadatos exactos están en platform/source-lock.json y platform/mycompany-6.2.lock.json. Son snapshots completos, versionados dentro de Rubrova.

La composición principal MyCompany.lsf requiere:
- servicios de plataforma: Eval, ProcessMonitor, Backup, Chat y Documentation;
- datos maestros: MasterDataP;
- Inventory, Invoicing, InvoicingInventory, Purchase, Sales y Retail;
- Manufacturing, ProjectManagement, HumanResources, CRM y Fleet;
- BillReceiptCost y BillReceiptCostService.

La base incorporada es sustancialmente más amplia que lo que Rubrova había comenzado a utilizar. Esta auditoría encontró capacidades adicionales que ya podemos aprovechar:

1. Stocktake de mercadería con teórico, conteo real, hojas separadas, búsqueda por barcode y contabilización de diferencias en el ledger.
2. Transferencias, aceptación, picking por ubicación, put-away, lotes/series y mermas.
3. Costeo FIFO, AVCO/promedio y precio estándar; valoración histórica; costo real de recepciones, despachos, ajustes y fabricación; asignación de fletes/servicios.
4. APIs nativas de catálogo, categorías, atributos, precios, inventario, pedidos y tareas.
5. Autenticación, roles/permisos, acceso por depósito, backups, scheduler, monitor de procesos y visor de documentación.
6. CRM a pedido, órdenes de compra vinculadas a ventas, fabricación a compras, calendario de deudas y caja.
7. Adaptadores regionales opcionales que contienen patrones útiles, pero no están activos ni listos para Argentina.

La conclusión no es cargar todo sin criterio. Es consumir la lógica base, mantener sus ledgers como autoridad, y sumar en Rubrova las diferencias que realmente necesitemos.

## 2. Qué está incorporado y qué está activo

### 2.1 Composición principal

MyCompany.lsf carga la mayoría de los dominios de ERP/POS y los módulos transversales señalados arriba. Que un dominio esté incluido no garantiza que toda función esté activada: dependen de tipos de documento, default data, parámetros, permisos y configuración de compañía.

El código bajo vendor/mycompany/src/main/lsfusion/region/ también está incorporado al snapshot, pero no forma parte de MyCompany.lsf. En el árbol revisado hay raíces regionales BG, PL y RU; no hay raíz Argentina/ARCA.

### 2.2 Integraciones regionales

| Raíz opcional | Ejemplos de capacidad | Decisión para Rubrova |
|---|---|---|
| MyCompanyRu | driver fiscal ATOL, Wazzup, EnterpriseData, CRPT, DaData, FusionWMS, telefonía | no activar indiscriminadamente; adaptar proveedor, seguridad y país |
| MyCompanyPl | KSeF, certificados/tokens, consulta y envío de facturas, REGON | no activar en Argentina |
| BG | telefonía Zadarma y módulos asociados | estudiar el patrón, no la configuración |

MyCompanyRu.lsf y MyCompanyPl.lsf declaran explícitamente las dependencias regionales. No deben agregarse a RubrovaCustom sólo porque sus fuentes estén presentes.

El modelo genérico Tax/TaxGroup/TaxItem permite calcular impuestos y precios con/sin impuestos. No hay una raíz Argentina/ARCA en el snapshot revisado. La facturación fiscal argentina requiere un adaptador propio con CAE/CAEA, comprobantes, puntos de venta, contingencia, reintentos y reconciliación.

## 3. Capacidades nativas que Rubrova debe reutilizar

### 3.1 Datos maestros

MyCompany ya tiene:
- Item/Product/Service, categorías jerárquicas, variantes, atributos, UOM, imágenes y códigos de barra;
- Partner, Individual, LegalEntity, clientes/proveedores, contactos, bancos, historial, etiquetas y atributos;
- Employee, Company, Department, Location, Currency, Country y ExchangeRate;
- ItemCost con costo planificado por fecha.

Rutas principales: masterdata/items/, masterdata/partners/, masterdata/partners/employees/, masterdata/company/, masterdata/locations/ y masterdata/currency/.

**Regla:** no crear clases paralelas de producto, cliente, proveedor, sucursal o marca cuando corresponda extender el objeto nativo. Una integración no debe fabricar una segunda identidad del mismo artículo.

### 3.2 POS, turnos, pagos y caja

MyCompany implementa:
- Pos como caja lógica y Session como turno;
- openedSession(Pos) y openSession para evitar dos turnos abiertos en una caja;
- beforeOpen/afterOpen y beforeClose/afterClose como puntos abstractos;
- factura minorista, líneas, búsqueda, barcode, touch, descuentos y totalización;
- pagos divididos por PaymentMethod, creando IncomingPayment por cada medio;
- devolución Bill y egresos OutgoingPayment por medio;
- depósito y retiro de efectivo como movimientos financieros separados;
- saldos teóricos por cuenta y netos del turno por medio.

Fuentes: retail/pos/, retail/sessions/Session.lsf, SessionInvoice.lsf, SessionPayment.lsf, PosDashboardPayment.lsf y PosDashboardCash.lsf.

Los medios iniciales son efectivo y tarjeta. QR, transferencia y otros métodos se configuran con PaymentMethod, tipos financieros y cuentas; no justifican crear otro ledger.

**Distinción crítica:** Session/POS conserva pagos, depósitos, retiros y saldo teórico. En el modelo POS central inspeccionado no encontré conteo físico de billetes/monedas. El arqueo de efectivo es una capacidad Rubrova pendiente, distinta del stocktake de mercadería descrito abajo. No ajustar el saldo financiero sobrescribiendo Payment.

### 3.3 Compras, ventas, facturas y deuda

MyCompany ya soporta:
- pedidos de compra/venta confirmados;
- recepciones y despachos parciales;
- reservas antes del movimiento físico;
- políticas de facturación por cantidad pedida o por cantidad recibida/despachada;
- Bills/Invoices, notas de crédito, cobros, pagos y conciliación de deuda;
- descuentos por producto, atributos, tags de socio y ubicación;
- listas de precios y precios históricos;
- impuestos genéricos y tax-inclusive price.

Los documentos mantienen relaciones a sus líneas originales. Pedido, recepción/despacho, factura/nota de crédito y pago son etapas diferentes; sus estados y cantidades no son intercambiables.

Módulos representativos: PurchaseOrderReceipt, PurchaseOrderBill, PurchaseOrderBillReceipt, SalesOrderShipment, SalesOrderInvoice, SalesOrderInvoiceShipment, BillDebt, BillPayment, InvoiceDebt, SessionPayment y Payment.

### 3.4 Inventario físico: el stocktake ya existe

Esta fue una omisión importante de la investigación anterior. MyCompany ya implementa un circuito de conteo físico con diferencias contabilizadas en el ledger.

Fuentes:
- inventory/adjustments/Adjustment.lsf
- AdjustmentInProgress.lsf
- AdjustmentDone.lsf
- AdjustmentCreate.lsf
- inventory/adjustments/lists/AdjustmentList.lsf
- AdjustmentListSearch.lsf
- AdjustmentCost.lsf

Flujo observado:
1. Se crea Adjustment para ubicación, tipo y opcionalmente categoría.
2. Fill crea las líneas de productos/ubicaciones elegibles y calcula theoreticalQuantity desde prevOnHandB(location, product, dateTime(ajuste)); es teórico histórico a la fecha del conteo.
3. En borrador, realQuantity se inicia con theoreticalQuantity si no se usa la agregación de hojas.
4. Mark as ToDo pasa el ajuste a inProgress; el operador carga cantidades reales y puede filtrar mismatch, surplus y missing.
5. Con useList se crean AdjustmentList separadas; se agregan cantidades por producto/ubicación al ajuste padre. AdjustmentListSearch incorpora captura por barcode.
6. Validate marca done y genera InvAdjustment con realQuantity menos theoreticalQuantity.
7. InvAdjustment se incorpora al InvLedger; AdjustmentCost contempla su costo.

**Uso Rubrova:** extender el proceso nativo con conteo ciego, asignación por zona/operador, reconteo, tolerancias, autorización de diferencias, evidencias y auditoría si hacen falta. No crear una segunda tabla de stock ni otro motor de diferencias.

**Pruebas pendientes:** producto omitido, conteo cero, líneas duplicadas en hojas, producto en varias ubicaciones, cambio de stock entre fecha teórica y conteo, reconteo, cancelación, doble validación, permisos y costo de ajuste. Verificar Fill para productos con onHand cero y el mecanismo para agregar artículos no incluidos automáticamente.

### 3.5 Operación logística, lotes y mermas

MyCompany también incluye:
- TransferBulkCreate y TransferMobile;
- ShipmentAcceptance con confirmación de recepción por depósito;
- LocationProduct para ubicar productos;
- ShipmentPicking por ubicación y PickingTaskMobile;
- ReceiptPutAway para distribuir mercadería recibida en ubicaciones hijas;
- Scrap/ScrapInv para registrar merma y salida física;
- Lot, ReceiptLot, ShipmentLot, AdjustmentLot, ScrapLot, InvoiceLot, CreditNoteLot y POS lotes/series.

Los módulos de lotes manejan barcode, asignación de cantidad por lote y validación de que la suma de lotes coincida con la cantidad de línea. La cantidad física sigue contabilizándose a través de sus ledgers, no mediante un stock Rubrova duplicado.

### 3.6 Costos y rentabilidad

Hay tres conceptos diferentes:

1. ItemCost: costo planificado/histórico del producto por fecha.
2. CostLedger: costo real de movimientos de inventario, con métodos standardPrice, avco y fifo, heredados/configurados por categoría/producto.
3. SalesLedger: hechos comerciales de facturas y devoluciones con cantidad, importe, impuestos, costo y margen.

Módulos:
- inventory/ledgers/cost/CostProduct.lsf
- masterdata/items/ItemCost.lsf
- inventory/ledgers/cost/CostLedger.lsf
- inventory/receipts/ReceiptCost.lsf
- inventory/shipments/ShipmentCost.lsf
- inventory/adjustments/AdjustmentCost.lsf
- invoicing/inventory/receipts/BillReceiptCost.lsf
- BillReceiptCostService.lsf
- manufacturing/orders/ManufacturingOrderCost.lsf
- sales/ledgers/SalesLedger.lsf
- SalesLedgerInvoiceShipment.lsf
- SalesLedgerBillReceipt.lsf

BillReceiptCost y BillReceiptCostService asignan costo de la factura de proveedor y gastos de servicios a las recepciones. ManufacturingOrderCost separa materiales, extra, mano de obra y servicios. SalesLedgerInvoiceShipment añade costos reales de ShipmentLine a las facturas vinculadas; SalesLedgerBillReceipt añade costos reales de ReceiptLine a las devoluciones vinculadas.

**Regla para los márgenes:** usar el ledger comercial y preservar si el costo viene de ItemCost planificado o del movimiento real. Probar facturas con/sin ShipmentLine, devoluciones con/sin ReceiptLine, descuentos, costos de servicio, moneda y ajustes retroactivos.

**Riesgo FIFO que requiere regresión:** CostLedger.lsf tiene comentados filtros temporales dateTime(InCostLedger) <= dateTime(OutCostLedger) en dos bloques de asignación FIFO. No concluyo que sea un bug; sí significa que no debemos afirmar que el costo FIFO histórico está validado hasta probar una salida fechada antes de una entrada, varias capas y recálculo desde fecha.

### 3.7 Fabricación y compras por demanda

BOM, operaciones, centros de trabajo, ManufacturingOrder, WorkOrder y costos ya están implementados. Consumos y productos terminados alimentan InvLedger; reservas de materiales y producción planificada afectan ResLedger/available según la opción increaseAvailableStock. PurchaseOrderManufacturingAuto calcula demanda de materiales por consumos/periodos y MyCompany 6.2 permite crear pedidos de compra desde órdenes de fabricación seleccionadas.

No reconstruir BOM, cálculo de consumo, reservas de fabricación o costo de producción como servicios Rubrova paralelos.

### 3.8 CRM, proyectos, RR. HH. y flota

- CRM: leads, actividades/llamadas, campaña/medio/fuente, artículos y acción de creación de Sales.Order desde un Lead.
- Proyectos: Project/Task, asignación, equipos, kanban, horas, timesheets, asistencia, turnos y relaciones a ventas, compras, facturas, fabricación y logística.
- HR: empleados, postulaciones, asistencia, nómina/payslips, tipos y numeración, tarifas históricas.
- Fleet: vehículos, conductores, contratos, mantenimiento y servicios.

Estos dominios ya existen. Sólo debemos activarlos y extenderlos cuando haya un caso de uso real.

### 3.9 Cuentas, deuda, bancos y calendario

Además de IncomingPayment/OutgoingPayment, MyCompany trae:
- Payment/Account y saldos históricos;
- IncomingDebt/OutgoingDebt, matching y saldos pendientes;
- importación/exportación bancaria;
- PaymentCalendar para proyectar cambios de deuda y saldo esperado;
- Tax/TaxGroup/TaxItem y cálculos genéricos;
- documentos aduaneros y otros flujos financieros.

El saldo proyectado no equivale a extracto bancario conciliado ni a efectivo contado.

## 4. APIs existentes que no debemos ignorar

Los módulos siguientes están en los árboles de dominio requeridos y aportan acciones marcadas @@api:

| API nativa | Función | Límite observado |
|---|---|---|
| MasterData.getItems | catálogo, barcode, categoría, UOM, país; imagen/descripción opcional | probar filtros, volumen y esquema |
| MasterData.getCategories | jerarquía de categorías | versionado y claves |
| MasterData.getItemAttributes | valores de atributos por artículo | atributos opcionales/dinámicos |
| Sales.getPrices | precio por tipo/lista y fecha | moneda, impuestos y vigencia |
| Inventory.getInventory | onHand por producto/ubicación | no devuelve available/reservas; condiciona por presencia de onHand, no por saldo positivo |
| Sales.newOrders | importar pedidos y líneas desde JSON | sólo alta; número existente hace que se ignore la fila |
| Sales.deleteOrders | borrar pedidos por número | sólo estado draft; no cancela confirmados |
| ProjectManagement.getTasks/addTasks | consultar/importar tareas | mapear relaciones, IDs y asignados |

### SalesOrderAPI: contrato observado

newOrders importa JSON, crea Sales.Order si el número no existe y copia cabecera y líneas; luego aplica el cambio y eleva applyMessage si la transacción no se pudo confirmar. No es un upsert: un número ya existente no actualiza sus líneas/campos. No hay idempotencyKey ni schemaVersion explícitos en la implementación inspeccionada. deleteOrders borra sólo drafts por número. El ejemplo de exportación está comentado.

**Decisión:** comenzar por API nativa. Si la integración necesita upsert, eventos, idempotencia remota, paginación, versión, correlación, permisos o reconciliación, agregar un wrapper/adapter versionado sobre el dueño nativo. No exponer la API suponiendo que es un contrato bidireccional completo.

## 5. Plataforma: seguridad, scheduler, monitor y backup

### 5.1 Seguridad y permisos

Authentication y Security implementan usuarios, roles múltiples, rol principal y permisos permit/forbid/default por navegación, grupos, propiedades y acciones. MyCompany LocationEmployee agrega acceso a ubicaciones por empleado; macros documentales insertan filtros y constraints en documentos según el depósito.

Reutilizar esos mecanismos. Rubrova sí debe agregar auditoría de negocio y matriz de permisos por función sensible, pero no otro login ni una autorización basada solamente en ocultar botones.

### 5.2 Scheduler y operación

Scheduler permite periodicidad, fecha/hora, días, orden de acciones, timeout, ignoreExceptions y logs. Se activa desde onStarted; las tareas deben existir y estar activas. ProcessMonitor aporta diagnóstico de procesos, stack y SQL. Documentation brinda visor Markdown; Eval es el intérprete administrativo y no debe exponerse a integraciones.

Que exista una tarea configurada no garantiza que corra cuando la PC está apagada.

### 5.3 Backup nativo vs backup Rubrova

Backup.lsf aporta backup completo/parcial, exclusión de datos, logs, retención y restauración selectiva. El valor por defecto crea una tarea diaria a las 01:00 con makeBackup y decimateBackups desde loadDefaultData; hay que verificar configuración/actividad del scheduler y dumpDir/binPath en cada instalación.

PostgreDataAdapter usa pg_dump en custom format o directory multithreaded. La restauración selectiva usa pg_restore en una base temporal, para leer tablas/columnas y reintroducir datos al modelo lógico; no es sustituto de restaurar toda la base.

**Riesgo upstream concreto:** customRestoreDB devuelve el nombre de la DB temporal desde el catch de IOException de pg_restore y no hace dropDB en ese catch. Por tanto, un retorno no nulo no demuestra una restauración correcta y puede dejar una DB parcial. No usar restauración selectiva para recuperar datos críticos hasta agregar/regresar esa condición y validar limpieza.

La rutina Rubrova native-postgres-backup.py ya crea un paquete con manifiesto/SHA-256 y restaura sólo en una DB nueva, protegiendo la original. Mantenerla como complemento; sumar copia fuera del equipo y cobertura de archivos/adjuntos/configuración/secretos.

## 6. Integraciones regionales: patrones sí, activación no

### ATOL / driver fiscal local

CashRegister.lsf define CashDriver por POS. CashRegisterAtol extiende esa clase con bridge local HTTP, autenticación Basic y hooks openShift/closeShift/cashIn/cashOut/sell/sellReturn. Es un patrón valioso para futura impresora/driver fiscal argentino. El payload ATOL, los tipos de impuestos y el protocolo corresponden a Rusia; no se pueden reutilizar tal cual para ARCA.

### Wazzup / WhatsApp CRM

Wazzup sincroniza Leads por POST y recibe eventos de contactos/deals. El handler revisado lleva @@api @@noauth, registra el body completo y no muestra verificación de firma. No copiar ese comportamiento: Rubrova requiere verificar origen/firma, deduplicar durablemente, no loguear PII innecesaria y guardar credenciales en un secreto seguro.

### EnterpriseData, KSeF, WMS y telefonía

EnterpriseData importa/exporta estructura de pagos y cuentas estilo 1C; KSeF gestiona certificado/token, sesión, envío y consulta de documentos polacos; FusionWMS integra almacén; CRPT/trazabilidad, DaData y Mango/Zadarma son regionales. Son ejemplos para estudiar la arquitectura del adapter, no integraciones listas para Argentina.

## 7. Qué utiliza Rubrova hoy y qué no

| Módulo Rubrova | Estado real |
|---|---|
| RubrovaPOSLocalization | extensión visual/configuración de MyCompany; no sustituye venta/pagos nativos |
| RubrovaReplenishmentExport | exportación de sólo lectura de hechos nativos y semántica versionada |
| RubrovaIntegrationResilience | incidencias, clasificación HTTP y helper GET con timeout; no es cliente POST genérico ni motor de reintentos |
| RubrovaPaymentTerminals | modelo de cuentas/terminales/intenciones/intentos/eventos/reintegros/liquidaciones; no ejecuta cobros reales ni bridge/webhook |
| RubrovaRetailReturns | extensión de CreditNote.fill para cantidades remanentes, en PR #13; todavía requiere aceptación funcional y merge |
| RubrovaCISalesFixture | datos y escenarios sintéticos de CI; no son operaciones comerciales reales |

No se debe interpretar “modelo de datos”, “módulo requerido” o “compila” como “integración operativa”.

## 8. Matriz de reutilización prioritaria

| Prioridad | Capacidad Rubrova | Base que se debe reutilizar | Extensión propia justificada |
|---|---|---|---|
| P0 | POS/ventas/devoluciones | Invoice, Bill, Payment, Session, ledgers | brechas de devolución acumulada, auditoría y UX |
| P0 | Inventario físico | Adjustment/AdjustmentList/InvAdjustment | conteo ciego, reconteo, asignación y autorización |
| P0 | Caja | Session/Payment/depósitos/retiros | arqueo físico de efectivo y diferencias |
| P0 | Permisos | Security/LocationEmployee | matriz específica de operaciones y trazabilidad |
| P1 | Rentabilidad | CostLedger/InventoryValuation/SalesLedger | análisis por área/canal y verificación de coste real |
| P1 | Compras/ventas mayoristas | PurchaseOrder/SalesOrder, recepciones/despachos parciales | compra sugerida, condiciones, logística y canales |
| P1 | E-commerce/marketplaces | Item/Category/Price/Order/Inventory APIs | wrapper versionado, stock disponible, idempotencia y reconciliación |
| P1 | Lotes/vencimientos | Lot/ReceiptLot/ShipmentLot/POS lot | FEFO, alertas y políticas locales |
| P1 | Fabricación | BOM/ManufacturingOrder/WorkOrder/costos | planificación de capacidad y análisis de demanda |
| P2 | CRM/proyectos/HR/flota | dominios completos existentes | activar módulos según necesidad del negocio |
| P2 | ARCA | Tax genérico y documentos base | adapter fiscal argentino homologado |
| P2 | Terminales | CashDriver y patrón ATOL como referencia | driver argentino, bridge, webhook, idempotencia y hardware E2E |

## 9. Método obligatorio antes de implementar

1. Localizar el módulo dueño y el módulo raíz que lo carga.
2. Leer documento, líneas, estados, constraints, hooks y datos iniciales.
3. Seguir la relación hasta el ledger y los informes que consumen el hecho.
4. Comprobar cancelación, devolución, edición, duplicados y concurrencia.
5. Consumir el proceso/API nativa cuando cubra el caso.
6. Crear wrapper o hook Rubrova sólo para lo que falta y documentar su contrato.
7. Añadir pruebas de vacío/NULL, parcial, duplicado, límite, permiso, cancelación, concurrencia, reinicio y datos históricos.
8. Ejecutar preflight, compilación, carga real, API autenticada y E2E con DB controlada.
9. Mantener la diferencia entre inspección de código, aceptación CI, datos reales y producción.

## 10. Riesgos que deben convertirse en tests

| Riesgo | Prueba requerida |
|---|---|
| FIFO con fechas retroactivas | salida antes de entrada, varias capas, transferencia y recálculo |
| SalesLedger | factura con/sin ShipmentLine; devolución con/sin ReceiptLine; prioridad planificado vs real |
| Stocktake | cero, omitido, duplicado entre hojas, reconteo, cambio de stock después de fecha teórica y doble confirmación |
| Efectivo físico | contado vs esperado, diferencias, permisos, motivos y ajuste sin tocar Payment.balance |
| SalesOrderAPI | número duplicado con payload distinto, draft vs confirmado, cliente/empresa/ubicación inválidos, timeout tras APPLY |
| Inventory API | onHand vs available, reservas, múltiples ubicaciones y colección vacía |
| Webhook | firma inválida, replay, duplicado, evento tardío, PII y secreto |
| Bridge fiscal | timeout después de aceptar, UUID idempotente, polling, reinicio, cancelación y reimpresión |
| Backup | fallo de pg_restore, DB temporal parcial, tareas inactivas, retención y restauración real |
| Permisos | rol, depósito, compañía y acción administrativa |

## 11. Referencias de código

- platform/source-lock.json
- platform/mycompany-6.2.lock.json
- vendor/UPSTREAM_SOURCES.md
- vendor/mycompany/CHANGELOG.md
- vendor/mycompany/src/main/lsfusion/MyCompany.lsf
- vendor/mycompany/src/main/lsfusion/inventory/adjustments/
- vendor/mycompany/src/main/lsfusion/inventory/ledgers/
- vendor/mycompany/src/main/lsfusion/inventory/reporting/
- vendor/mycompany/src/main/lsfusion/sales/ledgers/
- vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrderAPI.lsf
- vendor/mycompany/src/main/lsfusion/retail/
- vendor/mycompany/src/main/lsfusion/region/
- vendor/platform/server/src/main/lsfusion/system/Security.lsf
- vendor/platform/server/src/main/lsfusion/utils/Backup.lsf
- vendor/platform/server/src/main/lsfusion/system/Scheduler.lsf
- vendor/platform/server/src/main/java/lsfusion/server/data/sql/adapter/PostgreDataAdapter.java

Documentación pública de apoyo:
- lsFusion 6.x Modules: https://docs.lsfusion.org/v6/Modules/
- lsFusion 6.x Extensions: https://docs.lsfusion.org/v6/Extensions/
- lsFusion 6.x Action extension: https://docs.lsfusion.org/v6/How-to_Action_extension/
- lsFusion 6.x Security policy: https://docs.lsfusion.org/v6/Security_policy/
- lsFusion 6.x Scheduler: https://docs.lsfusion.org/v6/Scheduler/
- lsFusion 6.x EXTERNAL: https://docs.lsfusion.org/v6/Access_to_an_external_system_EXTERNAL/
- MyCompany portal v6: https://mycompany-docs.lsfusion.org/v6/

**Límite documental:** el portal MyCompany /v6/ se identifica como documentación 6.0. Para afirmar comportamiento exacto de 6.2 prevalecen CHANGELOG.md y las fuentes vendorizadas fijadas por Rubrova.


<a id="b-integration"></a>

## Anexo B — Guía de integración lsFusion 6.2 y MyCompany 6.2

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Estado:** investigación de fuentes fijadas; mapa inicial contrastado con el código incluido en Rubrova.  
**Corte de código:** Rubrova main d9791ff1c7894346d31ea5e0d240077940ba788c.  
**Fuentes upstream:** lsFusion 6.2 dd4dbe5bf9b136e73e18fe25d741253929324350; MyCompany 6.2 d21ca6978717b98b6300d90267f9767db7414008.  
**Alcance:** arquitectura, contratos de módulos, extensión, transacciones, integración externa y circuitos POS/ventas, devoluciones, pagos, caja e inventario. No constituye aceptación productiva.

Para el inventario más amplio de funciones ya incorporadas, las APIs existentes y las capacidades que debemos reutilizar antes de programar equivalentes, consultar la [Auditoría de reutilización de la base incorporada](#a-reuse-first).

> Regla de precedencia: para saber qué hace la instalación Rubrova, prevalecen las fuentes 6.2 vendorizadas, sus parches explícitos y los tests sobre esa misma revisión. La documentación pública explica conceptos y escenarios, pero no sustituye la inspección del código exacto. El portal MyCompany v6 identifica su manual como 6.0 y parte de la documentación actual está en 7.0; se usa como apoyo conceptual, no para asumir compatibilidad sin verificar.

## 1. Conclusión arquitectónica

Rubrova parte de una aplicación ERP/POS integrada construida sobre lsFusion. Sus módulos LSF no son microservicios independientes: se cargan en una misma instancia lógica, participan de un mismo modelo de clases/propiedades/acciones y trabajan sobre la persistencia configurada para esa instancia.

La composición actual es:

- **vendor/platform/**: motor, servidor, API y clientes lsFusion 6.2.
- **vendor/mycompany/**: módulos de negocio MyCompany 6.2.
- **extensions/lsfusion/**: módulos Rubrova que dependen del modelo nativo.
- **patches/lsfusion/**: cambios puntuales al motor, sólo si una extensión LSF no alcanza.
- **build/rubrova/pom.xml**: reactor de compilación propio.

El módulo de entrada es **RubrovaCustom** (extensions/lsfusion/RubrovaCustom.lsf). Este requiere **MyCompany** y las extensiones Rubrova. A su vez, MyCompany declara el agregado de módulos de Inventario, Invoicing, Purchase, Sales, Retail, Manufacturing, Project Management, CRM, RR. HH., Fleet y otros.

Esto define dos clases de comunicación que no deben confundirse:

1. **Dentro de la aplicación lsFusion:** dependencia de módulos, propiedades tipadas, acciones, eventos, restricciones y puntos de extensión. No corresponde llamar por HTTP a un módulo vecino que ya reside en la misma instancia.
2. **Fuera de esa instancia:** Action API HTTP, exportaciones de datos, llamadas EXTERNAL, webhooks, dispositivos o procesos independientes. Aquí sí hacen falta esquemas versionados, autenticación, timeouts, idempotencia y conciliación.

Una función sólo debe convertirse en servicio separado si tiene una frontera útil y demostrable: dueño de datos, almacenamiento, contrato, ciclo de despliegue, migraciones, backup/restauración, observabilidad y pruebas independientes. Separar módulos LSF por carpetas no los convierte en microservicios.

## 2. Versiones, procedencia y reproducibilidad

La fuente de verdad está en:

- platform/source-lock.json
- platform/mycompany-6.2.lock.json
- vendor/platform/.rubrova-source.json
- vendor/mycompany/.rubrova-source.json
- vendor/UPSTREAM_SOURCES.md

| Componente | Tag fijado | Commit | Licencia | Ruta |
|---|---|---|---|---|
| lsFusion platform | 6.2 | dd4dbe5bf9b136e73e18fe25d741253929324350 | LGPL-3.0 | vendor/platform/ |
| MyCompany | 6.2 | d21ca6978717b98b6300d90267f9767db7414008 | Apache-2.0 | vendor/mycompany/ |

Estas carpetas son snapshots completos versionados dentro del repo, no submódulos ni referencias flotantes. No deben reemplazarse por latest, una rama remota o un JAR que oculte el origen. Las actualizaciones se preparan en un área temporal, se comparan archivo por archivo, se revisan licencias/dependencias, se registra el nuevo commit y se ejecuta la matriz completa antes de adoptarlas.

## 3. Cómo funciona la composición de módulos

### 3.1 El contrato del encabezado

Un módulo LSF se declara, por ejemplo:

~~~text
MODULE RubrovaFeature;
REQUIRE MyCompany, AnotherBaseModule;
NAMESPACE Rubrova;
~~~

- **MODULE** identifica una unidad lógica de código; su nombre debe ser único.
- **REQUIRE** declara dependencias y fija el orden de inicialización: los módulos requeridos se inicializan antes. No se permiten ciclos.
- **NAMESPACE** determina dónde se crean/resuelven los elementos declarados. Los módulos existentes usan namespaces como Retail, Invoicing, Inventory y Sales.

Por tanto, REQUIRE MyCompany no significa que Rubrova se conecte a un servicio remoto. Significa que el módulo consume los elementos de MyCompany dentro de la misma composición.

La cadena de dependencias debe ser intencional. Una extensión no debe depender de módulos de presentación sólo para alcanzar una entidad de dominio; siempre que sea posible debe depender del módulo que declara el contrato de negocio.

### 3.2 Elementos que forman el contrato

| Elemento | Significado operativo | Uso recomendado |
|---|---|---|
| CLASS | Tipo de objeto del dominio | Crear una clase propia sólo cuando no exista una clase nativa equivalente |
| DATA | Propiedad asociada a clases/objetos, persistente salvo variantes locales | Guardar datos propios o relaciones |
| Propiedad calculada | Expresión declarativa sobre objetos/propiedades | Consultas, saldos, derivaciones y reglas |
| ABSTRACT de propiedad | Contrato para añadir implementaciones | Desacoplar una fórmula base de módulos consumidores |
| Acción | Cambio de estado / ejecución imperativa | Casos de uso y comandos |
| ABSTRACT LIST | Punto de extensión donde pueden agregarse acciones compatibles | Enriquecer un flujo upstream sin modificar su acción concreta |
| WHEN / eventos | Reacción a cambios conforme a los operadores de sesión | Automatismos con momento y orden conocidos |
| CONSTRAINT | Invariante que debe respetarse al validar/aplicar | Proteger dinero, cantidad, relaciones y estados |
| EXTEND FORM / DESIGN | Extensión de interfaz | Presentar comportamiento de dominio, no alojar la regla crítica |

### 3.3 Cómo extender correctamente

Patrones observados en MyCompany 6.2:

**Propiedad abstracta:** se declara el contrato en el módulo base y se añaden fórmulas compatibles desde módulos dependientes mediante +=. Las clases y parámetros de las implementaciones deben coincidir con el contrato. No sobrescribir silenciosamente una propiedad concreta esperando que el comportamiento se acumule.

**Acción abstracta:** el módulo base declara un punto extensible, por ejemplo:

~~~text
fill ABSTRACT LIST (BillLine, InvoiceLine);
~~~

Un módulo dependiente agrega una implementación compatible:

~~~text
fill (BillLine line, InvoiceLine sourceLine) + {
    // completar sólo los datos que pertenecen a esta extensión
}
~~~

Para una acción abstracta el operador es ACTION+ / +, no += (que es la forma usada para extender propiedades).

**Acción concreta:** una acción con cuerpo, como CreditNote.create(Bill, Invoice), no se convierte automáticamente en un punto de extensión. No intentar create(...) + si el código upstream no la declaró abstracta. Buscar en orden: punto abstracto existente; evento o propiedad soportados; extensión pública de clase; y sólo como último recurso un parche aislado y versionado al código upstream.

**Extensión de formularios:** EXTEND FORM y DESIGN permiten sumar objetos, propiedades, eventos visuales y disposición. Son contratos sensibles a la estructura de la pantalla base: si upstream renombra o reubica objetos, filtros o grupos, la extensión puede dejar de compilar o comportarse distinto. Toda extensión de interfaz debe acompañarse de una prueba de carga y navegación en la pantalla real.

Ejemplos nativos para estudiar:

- CreditNote.lsf: fill(BillLine, InvoiceLine) y fill(Bill, Invoice).
- CreditNoteContract.lsf: copia la relación contractual en fill(Bill, Invoice).
- CreditNoteReceipt.lsf: copia la ubicación en el mismo punto de extensión.
- InvoiceShipment.lsf: expone puntos fill para Shipment/Invoice y líneas.
- Session.lsf: beforeOpen, afterOpen, beforeClose, afterClose.
- PosDashboard.lsf: afterCreateInvoice y processBarCode.
- PosDashboardPayment.lsf: afterPosPayment(Invoice).
- PosDashboardReturnPayment.lsf: afterPosPayment(Bill).

No todo punto abstracto es un hook de ejecución equivalente: revisar el tipo (LIST, MULTI, CASE, etc.), firma, orden y condiciones de selección antes de implementarlo.

## 4. Modelo de ejecución y transacciones

### 4.1 Separación entre consulta y comando

La lógica de lsFusion combina propiedades declarativas (valores consultables/derivados) con acciones imperativas (cambios de estado). Para mantener reglas consistentes:

- usar propiedades para expresar cálculos y relaciones;
- usar acciones para coordinar comandos y cambios;
- usar constraints para invariantes que deban bloquear el APPLY;
- evitar recalcular en la interfaz algo que ya tiene una propiedad de dominio autoritativa.

Una propiedad DATA LOCAL no es un registro durable. Es temporal y pertenece al contexto/sesión de ejecución. Los operadores de manejo de sesión pueden resetear propiedades locales; si deben sobrevivir a una sesión anidada o a un APPLY, hay que declarar/solicitar la semántica de anidamiento correspondiente.

### 4.2 APPLY, CANCEL, NEWSESSION y NESTEDSESSION

- **APPLY** intenta aplicar los cambios como una transacción atómica: valida constraints, procesa eventos globales síncronos, actualiza materializaciones y persiste. Si falla la validación o la base de datos, se revierte.
- **CANCEL** cancela los cambios del ciclo correspondiente; no debe confundirse con cancelar un documento ya contabilizado.
- **NEWSESSION** crea un ciclo/sesión de cambios separado; las propiedades locales normalmente se reinician.
- **NESTEDSESSION** permite trabajar sobre cambios locales anidados y devolverlos a la sesión padre. Un APPLY dentro de esa sesión puede copiar cambios al padre sin persistir todavía en la base.

El patrón común de MyCompany es APPLY, comprobar canceled(), y después entrar a NEWSESSION para completar otra etapa. No copiarlo mecánicamente: entender qué se ha confirmado y qué sigue siendo reversible en cada punto.

**Cómo conservar evidencia de un APPLY rechazado en una fixture/API:**

- Una constraint cancela el APPLY y revierte sus cambios persistentes. Cualquier marca escrita en una propiedad DATA normal dentro de esa misma sesión fallida puede perderse al cerrar NEWSESSION; no sirve como evidencia durable del rechazo.
- Para transportar el resultado fuera de una NEWSESSION, declarar una propiedad transitoria como DATA LOCAL NESTED BOOLEAN. Después de APPLY, si canceled(), establecer la marca local. Al cerrar NEWSESSION, el valor local nested vuelve a la sesión exterior.
- Sólo después de que la sesión exterior haya recibido esa marca, persistir el resultado en una transacción limpia y exitosa si la API/fixture debe demostrarlo después de un reinicio.
- No usar esa marca como fuente de verdad de negocio ni cambiar la constraint para facilitar la prueba. La evidencia debe reflejar la cancelación real de MyCompany.

Este patrón se apoya en la semántica v6 de [Session management](https://docs.lsfusion.org/v6/Session_management/), [APPLY](https://docs.lsfusion.org/v6/Apply_changes_APPLY/) y [NEWSESSION/NESTEDSESSION](https://docs.lsfusion.org/v6/New_session_NEWSESSION_NESTEDSESSION/).

**Regla crítica:** la acción aplicada dentro de APPLY puede ejecutarse más de una vez si la transacción se reintenta por conflicto, deadlock o timeout. No enviar un cobro, emitir un documento fiscal, imprimir un ticket no repetible ni llamar a un proveedor externo como efecto irreversible dentro de esa transacción. En su lugar:

1. crear/persistir una intención con ID e idempotencia;
2. confirmar localmente el estado pendiente;
3. ejecutar el adaptador externo fuera de la transacción crítica;
4. guardar respuesta/evento y correlación;
5. conciliar el resultado antes de crear el siguiente efecto contable.

Para pagos o emisión fiscal, la respuesta incierta no significa rechazo: puede haberse confirmado en el proveedor aunque se pierda la respuesta. Consultar por la referencia/idempotency key antes de reintentar.

### 4.3 WHEN y eventos

Las expresiones WHEN, ON CHANGE, ON INIT y los eventos locales/globales no son todos equivalentes. Su momento de ejecución depende de la clase de evento y del ciclo de sesión. Un cambio a una propiedad no significa que todas las reacciones globales ya se hayan aplicado. El APPLY procesa los eventos globales síncronos y las restricciones dentro de la transacción.

Los handlers que pueden ejecutarse más de una vez deben ser deterministas e idempotentes. No usar eventos declarativos como sustituto de una llamada externa transaccionalmente segura ni para un efecto físico irreversible.

## 5. Comunicación con sistemas externos

### 5.1 Entrada a lsFusion

La Action API expone acciones concretas por HTTP (por ejemplo /exec), con parámetros y, cuando se configura, propiedades de resultado. lsFusion distingue EXEC, EVAL y EVAL ACTION.

Norma Rubrova:

- exponer acciones nominales específicas con @@api;
- mantener enableAPI=0 y autenticación obligatoria;
- no habilitar @@noauth;
- no habilitar evaluación arbitraria (/eval, /eval/action) para integraciones ordinarias;
- dentro de cada acción comprobar permisos/rol y validar los argumentos; @@api no es por sí mismo una autorización granular por usuario;
- publicar un esquema de respuesta versionado, no el modelo físico completo.

El endpoint de integración debe indicar schemaVersion, unidades, precisión, fecha de corte, significado de NULL, cero, ausencia y listas vacías, errores y semántica de reintentos. Un HTTP 200 no prueba que el JSON sea válido ni completo.

Precaución de v6: una respuesta JSON formada sólo por propiedades NULL o sin registros puede resultar en un valor JSON nulo/cuerpo vacío. No inferir que equivale a []. Cuando un consumidor necesite representar listas vacías, incluir contadores explícitos y probar el cuerpo HTTP real.

### 5.2 Salida desde lsFusion

El operador EXTERNAL permite que la instancia haga llamadas a otro sistema, entre ellas HTTP GET/POST/PUT/PATCH/DELETE. Por defecto la llamada se realiza desde el servidor de aplicaciones; la ejecución en cliente cambia la conectividad y limitaciones.

- cada llamada debe usar timeout finito;
- no reenviar credenciales en logs ni guardar cuerpos sensibles;
- distinguir timeout, error HTTP, autenticación, autorización, conflicto y respuesta inválida;
- reintentar sólo cuando el método/operación y el proveedor permiten hacerlo con seguridad;
- un GET de lectura no equivale a un POST de cobro;
- guardar referencia local, referencia remota opaca e ID de correlación;
- validar firma de webhooks y deduplicar eventos de proveedor.

RubrovaIntegrationResilience ya persiste incidencias, clasifica HTTP y aplica un máximo de 30 segundos a su helper GET; no reintenta automáticamente y no implementa todavía un cliente HTTP genérico para POST/PUT/DELETE. RubrovaPaymentTerminals define el modelo persistente y las pantallas de configuración/trazabilidad de cuentas, terminales, asignaciones, intenciones, intentos, eventos, reintegros y liquidaciones. **Es infraestructura de dominio preparada, no una integración operativa:** el módulo no contiene aún la acción que inicia un cobro real ni la recepción/validación de webhooks o el protocolo del puente local. En todos los casos, estos datos auxiliares no deben convertirse en un segundo ledger contable.

### 5.3 Frontera de autoridad

Un módulo de adaptación es dueño de la conversación con el proveedor (credenciales, correlación, reintentos, payload normalizado y reconciliación). No es dueño de la venta, el dinero en caja o el stock nativo.

Ejemplo: una intención de cobro puede referenciar Invoice, Retail.Pos y Retail.PaymentMethod; el resultado confirmado se registra como Invoicing.IncomingPayment. La referencia del proveedor y la conciliación pertenecen a Rubrova; el movimiento financiero oficial pertenece a MyCompany.

### 5.4 Estado real de terminales y próximos contratos

La revisión de extensions/lsfusion/RubrovaPaymentTerminals.lsf confirma que actualmente están modeladas las entidades:

- PaymentProviderAccount: proveedor, ambiente, referencia de comercio y referencia al secreto del sistema. No guarda el secreto en claro.
- PaymentTerminal y PaymentTerminalAssignment: terminal, transporte, bridge host/port y asociación a caja y medio de pago.
- PaymentTerminalIntent y PaymentTerminalAttempt: factura/caja/medio, importe, moneda, estado, referencias locales/remotas y claves de idempotencia.
- PaymentProviderEvent: clave de evento, tipo, operación, intento, verificación de firma y estado de procesamiento. No se persiste el cuerpo HTTP completo.
- PaymentRefund: relación con intento original, Bill y OutgoingPayment.
- PaymentSettlement y PaymentSettlementLine: bruto, comisiones, impuestos/retenciones, neto y conciliación con IncomingPayment.

El archivo implementa clases, datos, relaciones y formularios de consulta/configuración. No implementa aún el protocolo de cobro contra una terminal, el HTTP POST del proveedor, el worker local, el receptor de webhooks ni las transiciones operativas de los estados. El documento de instalación del runtime ya describe esta pieza como base de configuración y trazabilidad y aclara que todavía no ejecuta cobros reales. La ausencia de acciones EXTERNAL HTTP POST en el código LSF inspeccionado confirma que no se debe vender como integración de terminal terminada.

RubrovaIntegrationResilience:

- Persiste IntegrationIncident en una sesión independiente (NEWSESSION/APPLY); si falla la base principal, intenta un log local de emergencia.
- Clasifica 429, 408/425, 5xx, 401, 403, 409 y fallos de red/timeout.
- Su helper rubrovaHttpGet ejecuta EXTERNAL HTTP GET, tiene timeout configurable de 1 a 30.000 ms, y devuelve estado/categoría para que el llamador decida.
- No reintenta por sí mismo, no expone un cliente HTTP genérico POST/PUT/DELETE y el helper no demuestra todavía firma/verificación de webhooks ni protocolo de terminal local.
- La respuesta, URL completa, cabeceras sensibles y excepción cruda no se persisten en la incidencia.

**Contrato pendiente antes de una integración real:**

1. Definir adapter por proveedor/terminal con operaciones Create/Charge, QueryStatus, Cancel y Refund, más el protocolo de puente local cuando corresponda.
2. Congelar una intención de cobro ligada a una Invoice exacta, caja, medio, moneda e importe; una venta editada debe invalidar o expirar la intención anterior.
3. Derivar una clave estable por intención. Cada reintento de la misma operación remota debe reutilizar la misma clave; una nueva operación comercial recibe otra clave.
4. Distinguir estados terminales confirmados de respuestas inciertas. Timeout después de enviar el cobro significa resultado desconocido y requiere conciliación, no rechazo. Consultar por referencia antes de reintentar.
5. Verificar firma/autenticidad del evento, deduplicar por clave de evento de manera durable y relacionarlo con PaymentTerminalAttempt. Manejar eventos tardíos y fuera de orden.
6. Sólo después de confirmar el cobro, registrar el movimiento autoritativo como Invoicing.IncomingPayment; la intención y el intento no son dinero contabilizado.
7. Conciliar bruto, comisión, impuestos/retenciones y neto en PaymentSettlement/PaymentSettlementLine con el cobro nativo. Las comisiones no deben reducir silenciosamente el total de venta ni duplicarse como egreso.
8. Para un reintegro, enlazar PaymentRefund con el Bill y el OutgoingPayment; distinguir pedido al proveedor, confirmado, rechazado y desconocido. No registrar como reintegrado un importe que sólo fue solicitado.
9. El adaptador debe fallar de manera aislada: efectivo y otras funciones locales siguen operativas aunque el proveedor o el puente estén desconectados.
10. Validar con simulador determinista y luego hardware real: desconexión antes/después de enviar; respuesta perdida; doble click; webhook duplicado/tardío/firma inválida; reinicio; pago parcial; cancelación; reintegro; liquidación con comisión; conciliación tras recuperar red.

El modo offline local no implica que una terminal bancaria o un QR puedan autorizar un pago sin conectividad. Debe preservarse la venta local en efectivo y dejar explícitamente pendiente cualquier método que requiera el proveedor, según las capacidades reales del dispositivo y adquirente. No inventar un pago aprobado offline.

## 6. Mapa de dominios y circuitos comprobados en MyCompany 6.2

### 6.1 Composición superior

MyCompany.lsf incluye como mínimo estos dominios: MasterDataP, Inventory, Invoicing, InvoicingInventory, Purchase, Sales, Retail, Manufacturing, ProjectManagement, HumanResources, CRM y Fleet.

El hecho de que estén incluidos no significa que todas sus opciones estén activadas ni que todos los circuitos se hayan probado en Rubrova. Esta guía profundiza en el núcleo POS, pagos, caja, stock y devoluciones. Compras, mayorista, fabricación, fiscalidad, CRM y demás módulos requieren mapas de uso específicos antes de extenderlos.

### 6.2 Venta POS: de la caja al ledger físico

~~~text
Retail.Pos
  └─ Retail.Session (apertura de turno)
       └─ Invoicing.Invoice
            ├─ Invoicing.InvoiceLine
            └─ Invoicing.IncomingPayment (uno por medio de pago)
                  └─ Invoicing.Payment / saldo de cuenta
       └─ Invoicing.InvoiceShipment
            └─ Inventory.Shipment
                 └─ Inventory.ShipmentLine
                      └─ Inventory.ShipmentInvLedger
                           └─ Inventory.InvLedger / onHand
~~~

Contratos observados:

1. Pos es el objeto de caja. Guarda empresa y asignación a equipo; no es necesario crear una caja espejo para relacionarla con el turno.
2. Session representa el período operativo. Tiene apertura, cierre, caja y propiedades agregadas. openedSession(Pos) selecciona el turno abierto por caja.
3. PosDashboard crea la factura actual asociada al turno y llama al punto abstracto afterCreateInvoice.
4. PosDashboardPayment toma importes por PaymentMethod. Crea un IncomingPayment por cada importe, configura tipo, empresa, cuenta, cliente y factura, lo marca done, marca la factura ready, ejecuta APPLY y después afterPosPayment.
5. PaymentMethod asocia los tipos de ingreso/egreso que debe utilizar. PosPaymentMethod define medios habilitados por POS y cuentas financieras.
6. En MyCompany 6.2, InvoiceShipmentInitial configura el tipo retail con tipo de despacho y autoCreateShipment=true.
7. Cuando la factura minorista queda ready, InvoiceShipment crea automáticamente un Shipment. Si el despacho no es planificado, lo marca inmediato y completo; las líneas toman las cantidades vendidas.
8. ShipmentInvLedger transforma la diferencia entre cantidad efectuada y cantidad ya llevada al ledger en movimientos físicos. El ledger usa la condición active(shipment).

Así, el efecto de stock no es una resta improvisada en la pantalla del POS. Es un movimiento enlazado a la factura y al despacho.

### 6.3 Devolución POS: documento, reintegro y stock

~~~text
Invoice original
  └─ CreditNote.create(Bill, Invoice)
       ├─ Bill / BillLine
       │    └─ invoiceLine(BillLine) → InvoiceLine original
       ├─ OutgoingPayment (por medio de devolución)
       └─ autoCreateReceipt(retailreturn)
            └─ Inventory.Receipt / ReceiptLine
                 └─ Inventory.ReceiptInvLedger
                      └─ InvLedger / onHand
~~~

Contratos observados:

- CreditNote.create(Bill, Invoice) es una acción concreta. Copia tipo, cliente/proveedor, cuentas, empresa, nota, producto, cantidad y relación con la línea original. Por cada línea llama a fill(BillLine, InvoiceLine) y luego llama a fill(Bill, Invoice).
- La relación BillLine → InvoiceLine no es opcional: preserva la procedencia del artículo y permite calcular lo ya devuelto.
- MyCompany valida que la contraparte y el producto de la devolución coincidan con la factura original.
- returned(InvoiceLine) suma cantidades de BillLine de devoluciones activas vinculadas a esa línea.
- La constraint que impide superar la cantidad original sólo se aplica cuando checkReturnedQuantity(type(invoiceLine)) está habilitado.
- CreditNoteInitial asocia retailreturn con el tipo de factura retail; CreditNoteReceiptInitial mapea ese tipo a una recepción de devolución y activa autoCreateReceipt(retailreturn).
- PosDashboardReturnPayment crea documentos OutgoingPayment, los relaciona con Bill y medio de pago, y marca la devolución ready.
- BillReceipt crea una Receipt automáticamente al quedar lista una Bill cuyo tipo tiene autoCreateReceipt; el documento y líneas de recepción se crean completos. ReceiptInvLedger transforma la cantidad completada en entrada física.
- La cantidad física devuelta se acredita a través del ledger de Receipt; no se debe volver a sumar manualmente al stock en un módulo Rubrova.

**Límite funcional relevante:** el formulario nativo limita el importe por medio de pago al importe originalmente pagado con ese medio en la factura, y exige que la suma reintegrada sea igual al importe de la nota. Sin embargo, consulta la factura original y no resta lo reintegrado en devoluciones anteriores. Por tanto, el límite es por cada devolución, no acumulativo para varias devoluciones parciales. Hay que agregar una protección acumulativa Rubrova antes de aceptar ese circuito para operación real.

**Límite técnico:** las devoluciones parciales deben ajustar la línea copiada usando el punto abstracto CreditNote.fill(BillLine, InvoiceLine) antes de completar el documento. No crear una segunda nota de crédito independiente ni modificar manualmente las líneas ya confirmadas. La extensión Rubrova de ese flujo está propuesta en PR #13 y debe superar el smoke funcional completo antes de integrarse a main.

### 6.4 Caja: pagos, cuentas y turno

MyCompany usa una clase financiera común Invoicing.Payment:

- IncomingPayment contribuye con importe positivo a signedAmount.
- OutgoingPayment contribuye con importe negativo.
- Payment.balance(Account) agrega movimientos activos por cuenta; cashBalance(Company) agrega saldos de cuentas de caja.
- Retail.PaymentMethod vincula medios a tipos de ingreso/egreso.
- Retail.PosPaymentMethod vincula cada medio con una cuenta y define cashAccount(Pos) a partir del medio marcado como efectivo.
- Retail.cashBalance(Pos) consulta el saldo de la cuenta de caja de ese POS.
- Los depósitos/retiros del POS crean documentos de ingreso/egreso separados y los relacionan con la sesión. No son una venta ni una devolución.
- SessionPayment calcula lo pagado por medio como cobros de facturas menos egresos de devoluciones para esa sesión.

No confundir:

| Medida | Qué representa |
|---|---|
| Total de ventas | Importe de facturas del turno |
| Total de devoluciones | Importe de notas de crédito del turno |
| Neto comercial del turno | Ventas menos devoluciones |
| Neto por medio | Cobros asociados a ventas menos reintegros asociados a devoluciones |
| Saldo de la cuenta de caja | Ledger de pagos activos de esa cuenta, que también puede incluir depósitos y retiros |
| Arqueo físico | Conteo real de billetes/monedas; no se obtiene automáticamente del ledger |

El modelo de sesión no equivale a un arqueo físico. Diferencias entre efectivo teórico y contado deben tener un documento/registro, motivo, operador, hora y auditoría; no se deben corregir sobrescribiendo el saldo financiero.

Session expone beforeOpen, afterOpen, beforeClose y afterClose. El método habitual openSession(Pos) evita abrir un segundo turno abierto para la misma caja. La lista de sesiones también permite operaciones manuales NEW/EDIT/DELETE: esas operaciones no deben tratarse como equivalentes al caso de uso normal de abrir desde el POS, porque no ejecutan las mismas comprobaciones.

### 6.5 Inventario: físico, reservas y disponible

El ledger físico de MyCompany se construye así:

- InvLedger.quantity es una cantidad abstracta que implementan movimientos concretos.
- inQuantity(location, product) suma movimientos activos y aceptados hacia la ubicación.
- outQuantity(location, product) suma movimientos activos desde la ubicación.
- onHand(location, product) = inQuantity - outQuantity.

Las reservas viven en un modelo separado:

- ResLedger.reserved es el valor firmado del movimiento de reserva.
- Las cantidades positivas representan unidades reservadas.
- Las cantidades negativas representan entradas esperadas.
- planned considera las reservas que no están excluidas (skipAvailable).
- available(location, product) = onHand - planned.

En consecuencia:

- onHand es la existencia física/contable derivada de movimientos ya ejecutados.
- available es lo que queda utilizable después de los compromisos que MyCompany descuenta.
- expected y reserved son componentes de la planificación y no son sinónimos del saldo físico.
- una reserva de despacho no debe restar del ledger físico antes de completar el movimiento;
- una recepción prevista no incrementa necesariamente el disponible hasta que se cumplen los estados/configuraciones de recepción.

InvLedgerAPI.getInventory exporta onHand, no el disponible completo. Para consumir disponible, Rubrova debe usar una propiedad/acción que lo exponga expresamente o derivar el cálculo a partir de componentes compatibles y conciliados; no renombrar onHand como available.

### 6.6 Estados documentales: no inferir semántica desde el nombre

En el código inspeccionado, active se define de forma distinta según el documento:

| Tipo | Expresión observada | Qué habilita |
|---|---|---|
| Invoice | ready AND NOT canceled | Participar como factura activa en los ledgers que la consultan |
| Bill | ready AND NOT canceled | Participar como devolución/factura de proveedor activa |
| IncomingPayment | done AND NOT canceled | Participar en el saldo financiero |
| OutgoingPayment | (ready OR done) AND NOT canceled | Participar en el saldo financiero |
| Shipment | done AND NOT canceled | Participar en el ledger físico de salida |
| Receipt | done AND NOT canceled | Participar en el ledger físico de entrada |

ready y done son propiedades separadas y su significado varía según el módulo. No diseñar código Rubrova que concluya contabilizado, pagado o stock movido sólo por la presencia del documento o por un estado visual. Seguir exactamente la expresión active(...) que consume el ledger que interesa.

### 6.7 Compras y recepción: procure-to-pay

~~~text
Purchase.Order / OrderLine
  └─ confirm Order
       └─ Inventory.Receipt (ready; expected inbound)
            └─ ReceiptLine (initialDemand = residual ordered quantity)
                 ├─ ReceiptResLedger (negative reservation / expected)
                 └─ mark Receipt done
                      └─ ReceiptInvLedger (positive physical stock)
       └─ Invoicing.Bill / BillLine
            └─ Invoicing.BillDebt (supplier liability)
                 └─ OutgoingPayment (supplier payment)
                      └─ Payment / account ledger
~~~

**Confirmación y recepción:**

- Purchase.Order pertenece al namespace Purchase; contiene vendor, company, location, currency, payment terms, representative, lines, quantity y price.
- PurchaseOrderConfirmed.confirm(Order) cambia el pedido a confirmed dentro de una sesión nueva y APPLY.
- PurchaseOrderReceipt relaciona Order/OrderLine con Receipt/ReceiptLine. Calcula recibido como suma de done(ReceiptLine) para recepciones activas y toReceive = ordered - received.
- Cuando el pedido está confirmado, tiene ubicación y su tipo tiene receiptType, el automatismo crea o reutiliza una recepción ready, añade líneas con el remanente toReceive y actualiza sus cantidades previstas. Esto no significa que la mercadería ya haya ingresado físicamente.
- La constraint impide recibir por encima de la cantidad pedida. Varias recepciones parciales se suman por la referencia a la línea de orden original.
- ReceiptResLedger registra reservas esperadas con signo negativo mientras la recepción está ready y no done. La opción increaseAvailableStock(ReceiptType) determina si la recepción esperada se descuenta o no del disponible. No asumir que toda compra confirmada incrementa el stock vendible.
- Al completar la recepción, ReceiptInvLedger crea la entrada física; la existencia pasa a onHand a través del ledger, no por el estado de la orden de compra.
- La recepción enlazada conserva proveedor, ubicación, orden y línea original. La configuración del tipo de orden puede impedir bloquear pedidos con recepciones activas o con faltantes pendientes.

**Costo de mercadería:**

- PurchaseOrderReceiptCost aporta costo de ReceiptLine desde el precio de la línea de orden y la cantidad recibida, ajustada por el coeficiente SKU.
- Es una fuente para enlazar el costo de compra con el movimiento físico, pero no basta por sí sola para aceptar toda la valoración de inventario: todavía hay que mapear lotes, diferencias de precio, moneda, impuestos, ajustes posteriores y política de costo efectiva del resto de módulos.

### 6.8 Factura de proveedor y pago

- PurchaseOrderBill relaciona Order/OrderLine con Bill/BillLine.
- La política InvoicingPolicy.ordered permite facturar el remanente de cantidad pedida que todavía no aparece facturado. La cantidad facturada se calcula desde BillLine de Bills ready y no canceladas.
- La extensión PurchaseOrderBillReceipt añade la política delivered: sólo habilita cantidades de ReceiptLine activas, completadas (done > 0) y todavía no asociadas a una BillLine. Al crear la Bill, copia las cantidades efectivamente recibidas y mantiene los enlaces a la línea original de compra y a la recepción.
- Por ello, pedido, recepción y factura son documentos relacionados pero distintos. Facturar una cantidad no es prueba de que se haya recibido; recibir una cantidad no es prueba de que el proveedor ya haya sido pagado.
- **Precaución de lectura:** en PurchaseOrderBill, la propiedad de línea llamada paid agrega quantity(BillLine) para Bills done. Es una medida basada en estado/cantidad de documento, no un monto monetario liquidado al proveedor. No reutilizarla como importe de caja ni saldo de deuda.
- BillDebt integra Bill al modelo de deuda como IncomingDebt. OutgoingPaymentDebt integra OutgoingPayment como OutgoingDebt; sus acciones de matching relacionan obligaciones y pagos mediante importes pagados y pendientes.
- BillPayment.registerPayment crea un OutgoingPayment vinculado al proveedor, sus cuentas, empresa, moneda y Bill; propone el saldo pendiente y permite registrar el pago. Al completar la conciliación configurada, BillDebt puede cambiar el estado de la Bill a done. Las cuentas y los saldos financieros continúan siendo propiedad del ledger común Payment.

**Invariantes que Rubrova debe preservar:** límite de recibido <= pedido; límite de facturado según la política (pedido o recibido); la misma cantidad recibida/facturada no puede duplicarse por recepciones parciales; deuda y pago se concilian por importe, no por cantidad de producto.

### 6.9 Ventas mayoristas: pedido, reserva, despacho parcial y factura

~~~text
Sales.Order / OrderLine
  └─ confirm Order
       └─ Inventory.Shipment (waiting / reserve)
            ├─ ShipmentResLedger (planned outgoing reservation)
            └─ mark as Ready / Done
                 └─ ShipmentInvLedger (physical outgoing stock)
       └─ Invoicing.Invoice / InvoiceLine
            └─ SalesLedgerInvoice (sales reporting)
~~~

**Pedido y despacho:**

- Sales.Order mantiene customer/department, ubicación, dirección de entrega, moneda, plazo de pago, referencia del cliente, cantidades, precios, descuentos y datos fiscales del pedido.
- SalesOrderConfirmed confirma el pedido con APPLY/NEWSESSION.
- SalesOrderShipment crea o reutiliza un Shipment waiting para el remanente de cada línea confirmada. Ejecuta precheckAvailability, que compara la demanda contra disponible y registra reservas; por tanto, la reserva no es todavía una salida física.
- done(OrderLine) suma unidades despachadas en Shipment activos; toShip es la cantidad pedida menos la despachada. Una constraint impide sobre-despachar.
- El circuito contempla despachos parciales: shipPartially genera un Shipment para el remanente no reservado. Los links a OrderLine permiten conciliar el total despachado a lo largo de varios documentos.
- ShipmentResLedger agrega las reservas netas no completadas; ShipmentInvLedger registra la diferencia efectivamente completada. El stock físico se reduce en el ledger cuando el despacho pasa a su estado final correspondiente, no cuando se confirma el pedido.

**Facturación:**

- SalesOrderInvoice permite facturar lo que queda de la cantidad pedida (InvoicingPolicy.ordered).
- SalesOrderInvoiceShipment agrega la política delivered. La inicialización de ese módulo fija delivered como política predeterminada para los OrderType de Sales.
- Bajo delivered, toInvoiceShipped suma cantidades done de ShipmentLine activas que todavía no tienen InvoiceLine asociada. El hook fill(Invoice, Order) copia sólo las cantidades ya despachadas, mantiene referencia a OrderLine y marca la relación ShipmentLine → InvoiceLine para evitar facturación duplicada.
- En consecuencia, el pedido comercial, la reserva, la salida física y la factura son etapas separadas. Hay que conciliar cada cantidad y no utilizar el estado confirmado como sinónimo de despachado o facturado.

### 6.10 Relación entre venta y aprovisionamiento

SalesOrderPurchase relaciona líneas de Sales.OrderLine con Purchase.OrderLine y permite navegar desde un pedido de venta a sus órdenes de compra relacionadas y viceversa. Suma cantidades de las líneas vinculadas y conserva la trazabilidad de ambas órdenes.

Esto es un vínculo de negocio importante para compras bajo pedido, faltantes, distribución y futura planificación. **No se debe inferir sólo por esta relación que MyCompany compra automáticamente todo lo vendido ni que cada vínculo representa una reserva física**: la generación de compra, las políticas de aprovisionamiento, MOQ, múltiplos, proveedor preferente y cobertura deben mapearse y probarse en módulos separados antes de crear automatismos Rubrova.

### 6.11 Analítica comercial y costo

SalesLedger proporciona una clase abstracta de hechos para informes por producto, cliente, ubicación, fecha, cantidad, precio, costo, margen, impuestos e importe. SalesLedgerInvoice incorpora las líneas de facturas activas con cantidades/importes positivos; SalesLedgerBill incorpora notas de crédito activas con cantidades/importes negativos.

El costo base se deriva de cost(item, date) por cantidad. Esta estructura es preferible a reconstruir ventas desde el formulario POS. Antes de utilizar el margen para decisiones productivas, Rubrova debe verificar la política de costo temporal, ajustes retroactivos, devoluciones parciales, descuentos, impuestos y moneda, y reconciliarlo contra el ledger de costos de inventario.

**Implicación de arquitectura:** los canales local, POS y mayorista deben converger a los documentos y ledgers de origen adecuados; los informes analíticos deben leer esas fuentes con claves de canal/área preservadas. No generar un segundo inventario o una tabla de ventas paralela para cada canal.


### 6.12 Conteo físico de mercadería y logística interna

MyCompany ya incluye el circuito de stocktake mediante Adjustment, AdjustmentInProgress, AdjustmentDone y AdjustmentList. La cantidad teórica se calcula a la fecha del ajuste desde el ledger; la cantidad real se registra durante el estado inProgress y puede capturarse por listas separadas con búsqueda por código de barras. Al validar, el sistema genera InvAdjustment con la diferencia y la publica en InvLedger. No se debe crear un segundo stocktake ni editar onHand directamente.

También están incluidos transferencias en lote/móviles, aceptación en destino, picking por ubicación, put-away de recepción, mermas y gestión de lotes/series. El arqueo físico de efectivo es otro proceso: el modelo Session/POS inspeccionado registra pagos, depósitos y retiros, pero no se encontró en él un formulario/campo central de billetes/monedas contados. La diferencia de efectivo debe quedar documentada como una capacidad Rubrova separada.

## 7. Hallazgos que se deben convertir en regresiones

| Hallazgo | Evidencia en fuente 6.2 | Regla para Rubrova |
|---|---|---|
| GROUP SUM vacío no implica cero | agregados de Session y otras áreas no tienen default intrínseco | Normalizar con OVERRIDE ..., 0 cuando la regla de negocio requiera identidad cero; probar vacío y no vacío |
| El límite de reintegro por medio no es acumulativo | PosDashboardReturnPayment.lsf compara cada Bill con lo pagado en Invoice original | Calcular cuánto ya fue reembolsado en Bills/OutgoingPayments activos y rechazar exceso acumulado |
| La constraint de cantidad devuelta es configurable | CreditNote.lsf condiciona la constraint a checkReturnedQuantity | Activarla explícitamente para retail y probar bypass/rechazo en servidor |
| JSON nulo no es una lista vacía | Action API v6 y exportaciones JSON | Especificar contadores y forma de respuesta; validar cuerpo HTTP |
| APPLY puede reintentarse | contrato transaccional de la plataforma | Nada irreversible dentro de efectos que puedan repetirse |
| Los hooks tienen firma y selección | ABSTRACT LIST / ACTION+ / fill | Extender sólo puntos abstractos y compatibles |
| Formularios dependen del diseño upstream | EXTEND FORM / DESIGN | Probar la pantalla después de cada cambio de base/fork |
| Caja neta no equivale a arqueo | SessionPayment y Payment.balance consultan agregados distintos | Mantener el arqueo físico como registro aparte |
| Las sesiones manuales no son el flujo normal POS | el formulario sessions permite CRUD directo | Abrir/cerrar desde acciones POS controladas; auditar operaciones administrativas |

**Anomalía a verificar:** en el bloque de cancelación de PosDashboardReturnPayment.lsf aparece una eliminación filtrada por IncomingPayment aunque el bloque de confirmación crea OutgoingPayment. No se concluye aún que sea un bug: antes hay que demostrar si la cancelación del diálogo revierte toda la sesión o deja efectos persistentes. Añadir una prueba de cancelación del diálogo y consultar los ledgers antes de tocar el código upstream.

## 8. Método Rubrova para construir sin duplicar ni adivinar

Antes de implementar una capacidad:

1. **Buscar el dueño existente.** Localizar clase, propiedades, acciones, constraints, estados, formularios, REQUIRE y los módulos que los inicializan.
2. **Seguir el caso de uso completo.** No quedarse en la pantalla: documento → pago → ledger → estado → informes → cancelación/reverso.
3. **Identificar la autoridad.** Decidir cuál objeto/ledger es la fuente única de verdad y qué datos nuevos necesita Rubrova.
4. **Buscar un punto de extensión.** Preferir ABSTRACT LIST, ACTION+, propiedad abstracta, EXTEND CLASS o una interfaz expuesta a editar una acción concreta.
5. **Definir el contrato explícito.** Firma, tipos, unidad, moneda, precisión, estados, null/empty, idempotencia, errores, transacción y compatibilidad.
6. **Añadir tests del contrato antes del flujo E2E.** Probar semántica positiva, negativa, vacía, parcial, duplicada, concurrente y cancelada.
7. **Integrar por capas.** Prevalidación estática → compilación → carga real de módulos → API autenticada → caso de uso completo → reinicio/persistencia → backup/restore.
8. **Documentar evidencia.** Commit exacto, runtime, plataforma, resultado, logs y límites de aceptación.

### Matriz de decisiones

| Necesidad | Primera elección | Evitar |
|---|---|---|
| Nuevo campo del dominio existente | DATA sobre la clase nativa, desde módulo Rubrova | tabla espejo independiente para el mismo hecho |
| Nueva regla derivada | propiedad declarativa o constraint sobre fuente nativa | recalcular sólo en UI |
| Enriquecer una acción existente | hook abstracto compatible | ACTION+ sobre acción concreta |
| Mostrar datos Rubrova en pantalla MyCompany | EXTEND FORM + DESIGN | copiar toda la pantalla base |
| Integración con proveedor | adapter + intención + idempotencia + conciliación | bloquear la venta mientras el proveedor está lento |
| Consulta externa del ERP | acción @@api autenticada y esquema versionado | exponer evaluador arbitrario |
| Analítica | proyección/exportación read-only desde ledger y documentos | escribir sobre hechos históricos |
| Capacidad independiente real | servicio con datos y contrato propios | servicio nominal que comparte tablas sin dueño claro |

## 9. Plan de conocimiento pendiente

El repositorio contiene cientos de módulos MyCompany; no es honesto afirmar que todos sus contratos están completamente mapeados por esta primera investigación. Esta guía cubre en profundidad el recorrido POS más crítico. El inventario debe crecer por dominio y evidencia:

1. Compras y abastecimiento: PurchaseOrder → recepción parcial/completa → costos → factura proveedor → pagos.
2. Ventas no POS y mayorista: SalesOrder → despacho parcial → facturación → cobros/deuda.
3. Devoluciones/reembolsos fuera de Retail y notas de crédito no minoristas.
4. Impuestos, documentos fiscales y localización argentina/ARCA.
5. Costos, lotes, vencimientos, fabricación, recetas y mermas.
6. CRM/clientes, cuentas corrientes y límites de crédito.
7. Usuarios, permisos, auditoría y aislamiento por compañía.
8. Integraciones de archivos, impresión, dispositivos y sincronización offline.

Por dominio, producir: mapa de módulos y dependencias; clases y relaciones; acciones públicas; puntos de extensión; estados e invariantes; ciclo de vida del ledger; API/formatos; escenarios de excepción; matriz de tests. No inferir que un módulo es seguro de extender sólo porque su nombre coincide con la necesidad.

## 10. Referencias de código y documentación

### Fuentes exactas de Rubrova

- [Lock MyCompany 6.2](../../platform/mycompany-6.2.lock.json)
- [Lock de fuentes](../../platform/source-lock.json)
- [MyCompany top module](../../vendor/mycompany/src/main/lsfusion/MyCompany.lsf)
- [Retail module](../../vendor/mycompany/src/main/lsfusion/retail/Retail.lsf)
- [POS dashboard](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboard.lsf)
- [POS payment](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboardPayment.lsf)
- [POS return](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturn.lsf)
- [POS return payment](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturnPayment.lsf)
- [Session](../../vendor/mycompany/src/main/lsfusion/retail/sessions/Session.lsf)
- [Session invoices](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionInvoice.lsf)
- [Session payment totals](../../vendor/mycompany/src/main/lsfusion/retail/sessions/SessionPayment.lsf)
- [CreditNote](../../vendor/mycompany/src/main/lsfusion/invoicing/invoices/creditnotes/CreditNote.lsf)
- [CreditNoteReceipt](../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/CreditNoteReceipt.lsf)
- [BillReceipt](../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/receipts/BillReceipt.lsf)
- [InvoiceShipment](../../vendor/mycompany/src/main/lsfusion/invoicing/inventory/shipments/InvoiceShipment.lsf)
- [ShipmentInv ledger](../../vendor/mycompany/src/main/lsfusion/inventory/shipments/ShipmentInv.lsf)
- [ReceiptInv ledger](../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptInv.lsf)
- [Physical inventory ledger](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/inv/InvLedger.lsf)
- [Reservation ledger](../../vendor/mycompany/src/main/lsfusion/inventory/ledgers/res/ResLedger.lsf)
- [Payment ledger](../../vendor/mycompany/src/main/lsfusion/invoicing/ledgers/Payment.lsf)
- [POS payment method/account mapping](../../vendor/mycompany/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf)
- [Cash movements](../../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/cash/PosDashboardCash.lsf)

### Documentación oficial

- [lsFusion 6.x — Modules](https://docs.lsfusion.org/v6/Modules/)
- [lsFusion 6.x — Extensions](https://docs.lsfusion.org/v6/Extensions/)
- [lsFusion 6.x — Action extension](https://docs.lsfusion.org/v6/How-to_Action_extension/)
- [lsFusion 6.x — Session management](https://docs.lsfusion.org/v6/Session_management/)
- [lsFusion 6.x — APPLY](https://docs.lsfusion.org/v6/Apply_changes_APPLY/)
- [lsFusion 6.x — Integration](https://docs.lsfusion.org/v6/Integration/)
- [lsFusion 6.x — Access from an external system](https://docs.lsfusion.org/v6/Access_from_an_external_system/)
- [lsFusion 6.x — EXTERNAL](https://docs.lsfusion.org/v6/Access_to_an_external_system_EXTERNAL/)
- [MyCompany v6 — System modules overview](https://mycompany-docs.lsfusion.org/v6/)
- [MyCompany v6 — Sessions](https://mycompany-docs.lsfusion.org/v6/retail/sessions/)

Los manuales MyCompany v7 sobre POS, pagos y devoluciones son referencias complementarias para el usuario final, no prueba directa del comportamiento de la fuente 6.2 fijada:
- [POS](https://mycompany-docs.lsfusion.org/retail/pos/)
- [Payments](https://mycompany-docs.lsfusion.org/retail/payments/)
- [Returns](https://mycompany-docs.lsfusion.org/retail/returns/)


<a id="c-contracts"></a>

## Anexo C — Contratos de integración históricos

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Estado general:** catálogo inicial; los contratos específicos de MyCompany están en estado candidato, pendientes de aceptación funcional nativa y conciliación real.  
**Regla:** el contrato es el acuerdo entre productor y consumidor. El código, los tests y la documentación deben coincidir.

## 1. Contrato común de módulos

### 1.1 Propiedad y límites

- Cada módulo declara qué conceptos y datos posee.
- El módulo propietario define las reglas de escritura y exposición.
- En una misma instancia lsFusion integrada, otros módulos consumen los elementos lógicos públicos mediante dependencias REQUIRE, clases, propiedades, acciones, restricciones y puntos abstractos de extensión. Esto no equivale a una API HTTP entre microservicios.
- No se debe eludir el modelo lógico escribiendo directamente por SQL en las tablas físicas que sostienen otro módulo ni depender de detalles internos no declarados como contrato.
- Entre servicios/procesos independientes, cada sistema conserva su almacenamiento y los datos se intercambian mediante APIs/eventos/archivos versionados; no hay escrituras cruzadas.
- Un adaptador transforma formatos y significados, pero no se convierte en dueño del dato original.
- La analítica conserva la procedencia y el período de los datos; no reemplaza el registro transaccional.

Para el contrato específico de módulos, extensiones y transacciones lsFusion/MyCompany 6.2, ver la [Guía de integración](#b-integration).

### 1.2 Intercambio síncrono

Toda API debe definir:

- nombre y versión del endpoint;
- método y transporte;
- autenticación y autorización;
- parámetros, formato, tamaño y validación;
- esquema de respuesta y tipos;
- significado de ausente, NULL, cero y colección vacía;
- unidad, precisión, moneda y zona horaria;
- errores funcionales y técnicos;
- timeout, concurrencia, límites y política de reintento;
- idempotencia, consistencia y trazabilidad;
- compatibilidad y política de retiro.

HTTP 200 sólo indica el estado de transporte. El consumidor valida el cuerpo y el contrato completo.

### 1.3 Eventos y procesos asíncronos

Cuando se incorpore mensajería/eventos:

- el evento representa un hecho ocurrido y no una orden implícita;
- lleva eventId, tipo, versión, fecha de ocurrencia, emisor, identificador de correlación y referencia de agregado;
- el consumidor deduplica de forma durable;
- la entrega puede ser al menos una vez; no se promete exactamente una vez sin evidencia;
- los estados finales no retroceden ante mensajes tardíos;
- se documenta orden esperado, particionado y estrategia de replay;
- los cambios incompatibles requieren versión/migración y ventana de coexistencia.

### 1.4 Reintentos y errores

- Todo llamado externo tiene timeout finito.
- Sólo se reintentan operaciones idempotentes o protegidas con una clave de idempotencia.
- Los errores distinguen validación, autorización, conflicto, saturación, timeout, indisponibilidad y fallo interno.
- Se registra correlación de extremo a extremo, sin exponer credenciales ni datos sensibles.
- La caída de una integración no debe derribar capacidades que no dependen de ella.

## 2. Contrato MyCompany 6.2 — fuente nativa de reposición

**Estado: candidato, no productivo.**

### 2.1 Identificación y seguridad

| Elemento | Contrato |
|---|---|
| Plataforma fijada | MyCompany 6.2 / lsFusion 6.2 |
| Módulo | RubrovaReplenishmentExport |
| Namespace | Rubrova |
| Acción principal | rubrovaExportReplenishmentSource |
| Sondas | rubrovaProbeInventory, rubrovaProbeOutgoingCommitments, rubrovaProbeReceipts |
| Exposición | acciones específicas con @@api |
| Seguridad | mantener enableAPI=0; llamadas autenticadas; no usar @@noauth ni habilitar evaluación arbitraria |
| Naturaleza | sólo lectura; no crea, modifica, confirma ni elimina documentos de MyCompany |

**Compatibilidad de sintaxis:** la línea base del proyecto es lsFusion 6.2. En esa versión RETURN es un operador de salida sin expresión; la forma RETURN JSON FROM no es válida para el parser 6.2. Los endpoints existentes de Rubrova para CI usan EXPORT JSON FROM sin destino explícito, según el patrón de la API de esa versión. No trasladar sintaxis de documentación 7.x sin comprobarla contra la versión fijada. Referencias:
- [lsFusion 6.x — Access from an external system](https://docs.lsfusion.org/v6/Access_from_an_external_system/)
- [lsFusion 6.x — RETURN operator](https://docs.lsfusion.org/v6/RETURN_operator/)
- [lsFusion 6.x — EXPORT operator](https://docs.lsfusion.org/v6/EXPORT_operator/)

La semántica de respuesta y la selección de propiedades de resultado deben seguir la documentación v6 y los endpoints existentes. El test estático protege el patrón sintáctico; el smoke autenticado debe confirmar el cuerpo HTTP real.

### 2.2 Esquema de nivel superior

| Campo | Tipo / regla | Significado |
|---|---|---|
| schemaVersion | entero, actualmente 2 | versión del esquema de Rubrova; v2 exporta componentes nativos de reserva por ShipmentLine |
| snapshotType | string fijo | mycompany-replenishment-source-export |
| sourceSystem | string fijo | MyCompany |
| sourceVersion | string fijo | 6.2 |
| asOf | fecha ISO YYYY-MM-DD | fecha de corte |
| asOfDateTime | fecha-hora ISO actual del servidor | instante de corte; la zona/offset explícitos siguen pendientes de formalización |
| quantityUnit | string fijo | product-uom; la cantidad está en la unidad del producto |
| quantityPrecision | entero fijo 3 | precisión de cantidades; no redondear silenciosamente |
| readOnly | booleano true | declaración del carácter de sólo lectura |
| sourceSemantics | objeto | diccionario explícito de significado de cada campo |
| inventoryCount | entero no negativo | conteo independiente bajo el mismo filtro de inventario |
| outgoingCommitmentsCount | entero no negativo | conteo independiente bajo el mismo filtro de compromisos |
| outgoingReservationsCount | entero no negativo | conteo independiente de líneas de envío enlazadas a compromisos abiertos |
| receiptsCount | entero no negativo | conteo independiente bajo el mismo filtro de recepciones |
| inventory | lista de objetos | hechos de inventario por producto/ubicación |
| outgoingCommitments | lista de objetos | líneas de venta confirmadas aún abiertas |
| outgoingReservations | lista de objetos | hechos nativos por ShipmentLine, separados por despacho parcial |
| receipts | lista de objetos | recepciones de compra elegibles pendientes |

### 2.3 Semántica de inventario

No intercambiar estas magnitudes:

- onHand: existencia física nativa, derivada del ledger físico de MyCompany.
- available: disponible nativo calculado por MyCompany.
- plannedNetReservation: reserva neta firmada que participa en el disponible.
- La conciliación adoptada por el adaptador es available = onHand - plannedNetReservation. Si no coincide a precisión de tres decimales, se bloquea el snapshot.
- grossReserved y expectedInbound no son sinónimos de la reserva neta; se conservan por separado.
- Los campos *Native preservan el valor nativo crudo cuando puede ser NULL; los campos efectivos usan respaldo numérico explícito cuando la regla del contrato lo permite.

La definición de expectedInbound cubre las reservas entrantes negativas de los ledgers para la ubicación/producto exactos; no equivale automáticamente a la lista de recepciones que el planificador considera elegibles.

### 2.4 Compromisos de salida

- Origen: Sales.OrderLine de una orden confirmada.
- Sólo se exportan líneas con Sales.toShip(ol) > 0.
- openQuantity representa lo que todavía queda por despachar.
- outgoingReservations emite una fila por ShipmentLine enlazada a una Sales.OrderLine confirmada y todavía abierta. Incluye reservedQuantityNative = OVERRIDE Inventory.reserved(ShipmentLine), 0, ledgerReservedQuantityNative = OVERRIDE Inventory.ledgerReserved(ShipmentLine), 0, shipmentId, shipmentLineId, sourceLineId y reserveEligible; ambos campos se serializan aunque el valor nativo sea NULL.
- El adaptador normaliza cada componente NULL a cero y calcula lineReserved = reservedQuantityNative - ledgerReservedQuantityNative; sólo suma diferencias positivas cuando reserveEligible=true, agrupadas por sourceLineId.
- Varios despachos parciales no deben duplicar una línea abierta.
- Identidad compuesta acordada: número de orden + índice de línea. La identidad debe ser estable dentro del documento y no debe inventarse a partir de IDs no expuestos por MyCompany.

### 2.5 Recepciones previstas

- Origen: ReceiptResLedger y su línea/recepción relacionada.
- Elegibilidad actual: recepción ready, no done, no cancelada y orden de compra confirmada.
- expectedReservationSigned conserva el signo nativo negativo.
- expectedQuantity es la magnitud positiva calculada como 0 - expectedReservationSigned.
- Se conserva increaseAvailableStock; no se debe asumir que toda recepción incrementa el disponible inmediatamente.
- La identidad compuesta conserva número de recepción + índice de línea y referencia a la línea de orden de compra.

### 2.6 Colecciones vacías y conteos

El consumidor nunca debe convertir una respuesta ausente en lista vacía sin evidencia.

Regla:
1. cada consulta calcula un contador nativo independiente con el mismo filtro que su colección;
2. si la propiedad JSON está ausente y el contador es exactamente cero, el adaptador puede normalizarla a [];
3. si el contador es mayor que cero y la propiedad está ausente, se rechaza;
4. si la lista está presente pero su longitud no coincide con el contador, se rechaza;
5. un NULL, cuerpo vacío, texto plano o JSON con otra forma no equivale a una lista vacía.

Este control evita confundir “no hay filas” con “la API no entregó la colección”.

### 2.7 Adaptador y límites de responsabilidad

- adapt_mycompany_native_export.py sólo lee un documento JSON ya exportado.
- No abre conexiones a PostgreSQL, RMI, HTTP ni al servidor MyCompany.
- Convierte cantidades a milésimas enteras sin redondear.
- Valida cabecera, versión, semánticas, conteos, claves únicas, política de planificación y conciliación antes de producir un snapshot del planificador.
- No inventa demanda, lead time, stock de seguridad, MOQ ni múltiplos.
- No crea ni modifica objetos en MyCompany.

### 2.8 Pruebas de contrato exigidas

- JSON de raíz válido y cabecera exacta.
- Las cuatro colecciones presentes o ausentes sólo bajo la regla de conteos.
- Conteo = longitud de filas.
- Elementos de cada colección son objetos.
- Campos obligatorios, tipos, unidades y precisión.
- IDs compuestos únicos y estables.
- Magnitudes y signos conciliados.
- Despachos parciales consolidados.
- Recepciones elegibles, no elegibles e increaseAvailableStock.
- Inventario físico/disponible/reservado diferenciado.
- Rechazo seguro ante versión desconocida, campos incompatibles o datos no conciliados.
- Sólo lectura comprobada por revisión del módulo y permisos.

## 3. Estados de madurez de un contrato

- **Propuesto:** diseño documentado, aún no implementado.
- **Candidato:** implementado y con pruebas locales/unitarias, pero no aceptado en todos los runtimes o con datos reales.
- **Aceptado en CI:** pruebas de contrato y runtimes requeridos aprobados sobre un SHA identificable.
- **Aceptado con datos reales:** además concilia contra una base de origen real controlada, con evidencia anonimizada.
- **Productivo:** supera instalación, operación, seguridad, backup/restore, monitoreo y procedimientos de recuperación del entorno objetivo.
- **Retirado:** sustituido por otro contrato; se conserva la referencia histórica y la guía de migración.

No usar “terminado” como estado ambiguo.


## 4. Reutilización de módulos incorporados

Antes de proponer una entidad, API o proceso nuevo, consultar la [auditoría de reutilización de la base incorporada](#a-reuse-first). Allí se catalogan los circuitos de MyCompany 6.2, módulos regionales opcionales, APIs existentes y límites conocidos que deben superar pruebas antes de uso productivo. La regla es reutilizar primero el dueño/ledger nativo y añadir una extensión Rubrova sólo para el comportamiento que realmente falta.


<a id="d-domain-relationships"></a>

## Anexo D — Relaciones y propiedad de datos (histórico)

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Alcance inicial:** integración de reposición con MyCompany 6.2.  
**Estado:** extensión integrada en `main`; el smoke macOS ARM64 [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) ejecutó las sondas y verificó las colecciones de exportación contra fixtures sintéticas. Sigue pendiente la conciliación contra una base MyCompany local con datos comerciales controlados.  
**Regla de lectura:** una expresión de relación usada por el código es evidencia de cómo el módulo navega el modelo; no implica que conozcamos todas las restricciones internas, cardinalidades o claves físicas del ERP.

## 1. Recorrido entre componentes

```text
MyCompany 6.2 / lsFusion 6.2
    |
    | consultas autenticadas @@api (solo lectura)
    v
RubrovaReplenishmentExport
    |-- inventario por ubicación/producto
    |-- compromisos por línea de venta
    |-- recepciones por ledger
    |
    v
JSON nativo versionado
    |
    +--> inspect-mycompany-ui.py
    |       valida HTTP, esquema, conteos y conciliaciones en el smoke
    |
    +--> adapt_mycompany_native_export.py
            valida y normaliza un archivo JSON
                |
                v
        import_mycompany_snapshot.py
                |
                v
        plan_replenishment.py
```

El adaptador Python no consulta directamente la base de datos ni llama a RMI/HTTP de MyCompany. La comunicación con el ERP está aislada en las acciones nativas autenticadas y en el proceso de inspección del smoke.

## 2. Matriz de propiedad

| Concepto | Fuente propietaria actual | Consumidor | Observación |
|---|---|---|---|
| Stock físico | MyCompany `Inventory` | Exportación / planificador | Ledger de movimientos físicos |
| Disponible nativo | MyCompany `Inventory.available` | Exportación / planificador | No recalcularlo sustituyendo la propiedad nativa |
| Reserva neta planificada | MyCompany `Inventory.planned` | Exportación / planificador | Conserva signo y semántica del ERP |
| Línea abierta de venta | MyCompany `Sales.OrderLine` | Exportación / planificador | La cantidad abierta procede de `Sales.toShip` |
| Reserva de despacho | MyCompany `ShipmentResLedger` | Exportación / planificador | Se consolida por línea de venta |
| Recepción prevista | MyCompany `ReceiptResLedger` y entidades relacionadas | Exportación / planificador | Se mantiene el signo del ledger |
| Política de planificación | Fixture/configuración explícita de Rubrova | Adaptador / planificador | No se infiere a partir de stock ni de ventas |
| Snapshot de planificación | Adaptador de Rubrova | Planificador | Es una representación derivada, no reemplaza el origen |

## 3. Relaciones observadas en las expresiones LSF

### 3.1 Inventario por ubicación y producto

La consulta usa el par `(Location, Product)` como ámbito de inventario y consulta las propiedades:

- `Inventory.inQuantity(l, p)`
- `Inventory.outQuantity(l, p)`
- `Inventory.onHand(l, p)`
- `Inventory.available(l, p)`
- `Inventory.reserved(l, p)`
- `Inventory.planned(l, p)`
- `Inventory.expected(l, p)`

**Interpretación adoptada:** la clave de conciliación del inventario exportado es `(productId, locationId)`. Es obligatorio rechazar pares duplicados.

**Distinción de dominio:** `onHand` representa existencia física; `available` es el valor nativo del ERP; `planned` representa reservas netas firmadas que participan en el cálculo de disponible. No son campos intercambiables.

**Conciliación actual del adaptador:** `available = onHand - plannedNetReservation`. Se rechaza cualquier diferencia a la precisión que declara el contrato. Esta regla tiene que mantenerse compatible con la versión fijada de MyCompany y volver a comprobarse ante cambios de versión o de configuración de inventario.

### 3.2 Compromisos de salida

Las relaciones navegadas por el módulo son:

1. `Sales.OrderLine ol` identifica la línea.
2. `Sales.order(ol)` navega a la orden.
3. `Sales.shippedProduct(ol)` obtiene el producto.
4. `Sales.location(Sales.order(ol))` obtiene la ubicación asociada a la orden.
5. `Sales.toShip(ol)` determina la cantidad todavía abierta.
6. `Sales.scheduledDateTime(Sales.order(ol))` determina la fecha prevista.
7. `Inventory.ShipmentResLedger rr` se relaciona con la línea de MyCompany mediante `Sales.orderLine(Inventory.line(rr)) = ol`.
8. La suma de `Inventory.lineReserved(Inventory.line(rr))` se agrupa por la línea `ol`.

Filtro exportado: orden confirmada, cantidad abierta mayor que cero y producto/ubicación navegables.

**Interpretación:** una línea de venta parcialmente despachada se representa una sola vez con la cantidad que falta despachar y la reserva efectiva agregada. No generar un compromiso por cada movimiento parcial del ledger.

**Identidad de intercambio:** `Sales.number(Order) + Sales.index(OrderLine)`. Esta clave compuesta es una identidad de contrato, no una promesa de que sea el identificador primario interno de la base.

### 3.3 Recepciones previstas

Relaciones navegadas:

1. `Inventory.ReceiptResLedger rr` identifica la reserva de recepción.
2. `Inventory.line(rr)` navega a la línea de inventario.
3. `Inventory.receipt(Inventory.line(rr))` navega a la recepción.
4. `Purchase.orderLine(Inventory.line(rr))` obtiene la línea de orden de compra relacionada.
5. `Purchase.order(...)` obtiene la orden de compra.
6. `Inventory.product(Inventory.line(rr))` obtiene el producto.
7. `Inventory.location(Inventory.receipt(...))` obtiene la ubicación asociada.
8. `Inventory.scheduledDateTime(...)` determina la fecha prevista.
9. `Inventory.increaseAvailableStock(Inventory.type(...))` conserva la política del tipo de recepción.

Filtro exportado: recepción lista, no completada, no cancelada y orden de compra confirmada.

**Semántica de cantidad:** `Inventory.reserved(rr)` conserva el signo negativo del ledger; `expectedQuantity` se representa como `0 - reserved`, una magnitud positiva.

**Identidad de intercambio:** número de recepción + índice de línea. Se exporta además la referencia compuesta a la línea de compra para trazabilidad.

## 4. Relaciones que todavía no deben asumirse

- No asumir que el número visible de un documento es una clave primaria global, ni que lo es fuera de la compañía/serie correspondiente.
- No asumir cardinalidad uno-a-uno entre una línea de venta y sus movimientos de despacho: precisamente se agregan varios registros del ledger por línea.
- No asumir que cada reserva negativa del ledger representa una recepción elegible: la política de elegibilidad filtra las recepciones que el planificador puede tratar como entrada confirmada.
- No asumir que todas las recepciones incrementan el disponible de inmediato: conservar `increaseAvailableStock`.
- No asumir que una ubicación con cero movimientos debe aparecer en el listado actual: el filtro de inventario selecciona pares con cantidades o reservas relevantes.
- No inferir moneda, unidad de medida, conversión de unidades o zona horaria a partir de nombres o valores; deben ser campos explícitos del contrato.
- No tratar identificadores compuestos del contrato como claves de escritura hacia MyCompany.

## 5. Pendientes para confirmar con base real

1. Obtener una exportación autenticada desde una base MyCompany local controlada.
2. Comparar `inventoryCount` y longitudes de listas con una consulta de referencia dentro del ERP.
3. Confirmar conteos y cardinalidades de líneas parcialmente despachadas y recepciones parciales.
4. Verificar ubicaciones, productos inactivos, productos sin movimiento y registros sin referencia comercial.
5. Comprobar fechas con configuración regional/zona horaria y cambios de horario.
6. Verificar la unicidad práctica de las identidades compuestas en las series y compañías que soporte la instalación objetivo.
7. Registrar cualquier diferencia entre fixture, código y datos reales como decisión o iteración nueva.

## 6. Regla para ampliar este mapa

Cada módulo nuevo debe añadir:

- dueño de cada dato;
- entidad/propiedad de origen;
- relaciones usadas y sentido de navegación;
- cardinalidad observada o desconocida;
- clave técnica y clave de intercambio (si son distintas);
- invariantes y filtros;
- consumidores;
- nivel de evidencia;
- comportamiento ante ausencia, duplicado, borrado lógico y cambio de versión.

La falta de conocimiento se registra como desconocida; nunca se completa inventando una relación.


<a id="e-decisions"></a>

## Anexo E — Decisiones de arquitectura (histórico)

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

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
- **Evidencia:** guía [Anexo B](#b-integration); fuentes 6.2 CreditNote.lsf, InvoiceShipment.lsf, ShipmentInv.lsf, ReceiptInv.lsf, Payment.lsf; PR #13, commit correctivo 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53.
- **Límites:** el mapa cubre en profundidad POS, devoluciones, pagos, caja e inventario; no afirma que Compras, mayorista, ARCA, fabricación o seguridad estén completamente inventariados.


## ADR-0010 — Separar pedido, movimiento físico, factura y liquidación

- **Estado:** Aceptada como regla de modelado; los módulos que la implementan se deben validar con pruebas de escenarios parciales.
- **Ámbito:** compras, ventas mayoristas, POS, stock, cuentas por cobrar/pagar e informes.
- **Contexto:** las fuentes MyCompany 6.2 muestran flujos desacoplados por documentos relacionados: Purchase.Order puede originar Receipt y Bill; Sales.Order puede originar Shipment e Invoice; los pagos se registran y concilian en el modelo común Debt/Payment. Las cantidades se enlazan por líneas originales a través de entregas parciales.
- **Decisión:** Rubrova debe tratar cuatro etapas diferentes: (1) pedido/compromiso comercial; (2) recepción o despacho físico; (3) factura/nota de crédito y deuda; (4) cobro/reintegro/pago y liquidación. El estado de una etapa no implica que las otras hayan ocurrido. Las políticas ordered/delivered se seleccionan explícitamente por tipo de documento.
- **Consecuencias:** los límites y reportes concilian cantidades ordenadas, recibidas/despachadas, facturadas y dinero pagado en dimensiones independientes. El stock físico procede del ledger de inventario; las reservas proceden del ledger de reservas; las deudas y pagos proceden del modelo financiero. Los reportes de ventas usan SalesLedger y preservan el origen del dato.
- **Advertencias:** el campo de línea PurchaseOrderBill.paid representa cantidad asociada a Bills done, no un valor monetario. El enlace SalesOrderPurchase une líneas de órdenes, pero por sí mismo no prueba compra automática ni reserva de inventario.
- **Evidencia:** guía [Anexo B](#b-integration), secciones 6.7–6.11; fuentes PurchaseOrderReceipt, ReceiptRes, ReceiptInv, PurchaseOrderBill, PurchaseOrderBillReceipt, BillDebt, BillPayment, SalesOrderShipment, ShipmentRes, SalesOrderInvoiceShipment, SalesOrderPurchase y SalesLedger.


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
- **Evidencia:** [Anexo A](#a-reuse-first), sección 4; fuentes ItemAPI.lsf, CategoryAPI.lsf, ItemAttributeAPI.lsf, SalesPricelistAPI.lsf, InvLedgerAPI.lsf, SalesOrderAPI.lsf y TaskAPI.lsf.


## ADR-0013 — Mantener el costo planificado separado del costo real de inventario

- **Estado:** Aceptada como regla de analítica; valoración FIFO histórica pendiente de regresión.
- **Ámbito:** compras, inventario, devoluciones, fabricación y rentabilidad.
- **Contexto:** MyCompany implementa ItemCost (planificado por fecha) y CostLedger (FIFO/AVCO/standardPrice), enlaza costos de Receipt/Shipment/Adjustment/Manufacturing con movimientos y extiende SalesLedger con costo real de ShipmentLine y ReceiptLine.
- **Decisión:** no calcular margen sólo desde ItemCost cuando existe costo real de movimiento. Conservar fuente, método, fecha, ubicación y documento de origen; reportar desde SalesLedger y ledgers nativos.
- **Riesgo:** CostLedger.lsf tiene comentados filtros temporales dateTime(inCost) <= dateTime(outCost) en dos asignaciones FIFO. No se concluye bug sin reproducir; bloquear afirmaciones sobre FIFO retroactivo hasta cubrir salidas anteriores a entradas y recálculo.
- **Evidencia:** [Anexo A](#a-reuse-first), sección 3.6; ItemCost, CostLedger, ReceiptCost, ShipmentCost, SalesLedgerInvoiceShipment y SalesLedgerBillReceipt.


## ADR-0014 — Reutilizar stocktake nativo y separar arqueo de efectivo

- **Estado:** Aceptada.
- **Ámbito:** stock, caja y auditoría física.
- **Contexto:** MyCompany tiene Adjustment/AdjustmentList, estados de conteo, cantidad teórica, cantidad real, hojas y barcode; la validación genera InvAdjustment en el ledger. Session/POS registra pagos, depósitos y retiros, pero no se encontró conteo físico de billetes/monedas en el modelo POS central inspeccionado.
- **Decisión:** stocktake Rubrova extenderá Adjustment para conteo ciego/reconteo/autorización. El arqueo físico de efectivo será una capacidad separada ligada a Session/Pos que compare saldo esperado y contado con motivo, operador y autorización; nunca sobrescribe Payment.balance.
- **Evidencia:** [Anexo A](#a-reuse-first), sección 3.4; Adjustment.lsf, AdjustmentInProgress.lsf, AdjustmentDone.lsf, AdjustmentList.lsf, Session.lsf y PosDashboardCash.lsf.


## ADR-0015 — Complementar backup nativo con paquete verificado y recuperación probada

- **Estado:** Aceptada; riesgo en restore selectivo upstream pendiente de regresión.
- **Ámbito:** operación local y recuperación.
- **Contexto:** lsFusion trae backup completo/parcial, retención, scheduler y restauración selectiva; Rubrova tiene paquete PostgreSQL con manifiesto/SHA-256 y restauración a base nueva.
- **Decisión:** mantener ambos como complementarios hasta demostrar equivalencia: nativo aporta selección lógica; Rubrova aporta paquete, integridad y recuperación completa. Toda restauración crítica debe validar resultado y limpiar temporales ante error.
- **Hallazgo:** PostgreDataAdapter.customRestoreDB devuelve el nombre de la DB temporal desde el catch de IOException de pg_restore y no hace dropDB en ese catch. Debe probarse el fallo y evitar tratar el retorno no nulo como éxito.
- **Evidencia:** [Anexo A](#a-reuse-first), sección 5.3; Backup.lsf; BackupAction.java; PostgreDataAdapter.java; native-postgres-backup.py.


## ADR-0016 — Activar integraciones regionales sólo con adaptación local y seguridad

- **Estado:** Aceptada.
- **Ámbito:** ARCA, terminales, WhatsApp, e-commerce, WMS y telecomunicaciones.
- **Contexto:** el snapshot incluye raíces optativas RU/PL/BG con ATOL, Wazzup, EnterpriseData, KSeF, WMS, CRPT y telefonía; MyCompany.lsf no las requiere y el árbol no incluye raíz Argentina/ARCA.
- **Decisión:** no añadir raíces regionales al topModule argentino indiscriminadamente. Reutilizar patrones sólo después de definir contrato legal/proveedor local, autenticación, secreto, idempotencia, replay, timeout y reconciliación.
- **Riesgo concreto:** WazzupWebhook usa @@noauth y registra el body completo; el handler revisado no evidencia verificación de firma. No copiar esa política a endpoints Rubrova.
- **Evidencia:** [Anexo A](#a-reuse-first), secciones 2.2 y 6; MyCompanyRu.lsf, MyCompanyPl.lsf, CashRegisterAtol.lsf y WazzupWebhook.lsf.


## ADR-0017 — Transportar el resultado de un APPLY rechazado sin perderlo al cerrar la sesión

- **Estado:** Aceptada para fixtures, APIs y diagnósticos transaccionales.
- **Ámbito:** pruebas de constraints, rechazo funcional y persistencia de evidencias.
- **Contexto:** en run 45872444450, MyCompany rechazó la sobredevolución de 0,7 unidades sobre un remanente de 0,6, pero la fixture escribió el indicador durable dentro de la misma NEWSESSION cuyo APPLY fue cancelado. Al cerrarse esa sesión, la marca no llegó al API; la respuesta contenía overReturnRejected = NULL aunque el servidor había registrado el mensaje de constraint.
- **Decisión:** usar DATA LOCAL NESTED para transportar la marca de cancelación hacia la sesión padre. Fuera de la sesión fallida, persistir una evidencia durable mediante un APPLY independiente y exitoso cuando el contrato de prueba requiera observarla después del reinicio.
- **Consecuencia:** una prueba nunca debe sustituir una constraint real por una asignación de bandera optimista ni escribir la evidencia en la transacción que se espera cancelar.
- **Evidencia:** fuente v6 Session management/APPLY/NEWSESSION; [Anexo B](#b-integration), sección 4.2; PR #13.


<a id="f-iterations"></a>

## Anexo F — Investigaciones y pruebas cronológicas (histórico)

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

Registro cronológico de hechos y resultados. No reemplaza a los commits ni a los logs originales: los enlaza y conserva la explicación necesaria para no repetir diagnósticos.

## 2026-11-25 — REP-001 — Primeras sondas nativas de reposición

- **Pull request:** [#8](https://github.com/JavierGrecco/Rubrova/pull/8).
- **Run:** [45727626334](https://github.com/JavierGrecco/Rubrova/actions/runs/45727626334).
- **Resultado:** en Linux x86_64 y macOS ARM64 arrancaron PostgreSQL, el servidor lsFusion y Tomcat; el login y la navegación funcionaron.
- **Hecho observado:** las sondas de inventario, compromisos y recepciones devolvieron HTTP 200 y JSON parseable. El inspector rechazó `outgoingCommitments` porque no era una lista. El access log mostró respuestas de 12 bytes para la sonda de compromisos.
- **Interpretación:** el transporte y la autenticación no eran suficientes para demostrar el contrato. La estructura del JSON no contenía la colección esperada.
- **Decisión/cambio:** añadir conteos nativos independientes a las colecciones y comprobar raíz, tipo, filas y conteo. El consumidor sólo interpreta ausencia como lista vacía si el conteo confirma cero.
- **Estado:** regla incorporada al módulo, adaptador, inspector y fixtures; aceptación nativa pendiente.

## 2026-11-25 — REP-002 — Incompatibilidad de sintaxis entre lsFusion 6.2 y 7.x

- **Pull request:** [#8](https://github.com/JavierGrecco/Rubrova/pull/8).
- **Run:** [45730502272](https://github.com/JavierGrecco/Rubrova/actions/runs/45730502272).
- **Commit probado:** `b189e2c7d526d5b9eebcf39590d845016ed8f742`.
- **Hecho observado:** build de lsFusion/MyCompany y publicación de artefactos completaron. En el arranque nativo Linux y macOS, el parser reportó `RubrovaReplenishmentExport:11:12 mismatched input 'JSON' expecting ';'` en `RETURN JSON FROM`, seguido por errores en cascada en las columnas del mismo bloque. El contenedor Docker presentó la misma causa de inicio; no fue un problema exclusivo de arquitectura ARM.
- **Interpretación confirmada por fuente:** el proyecto está fijado a lsFusion 6.2. Su documentación define `RETURN` sin expresión y documenta los resultados de API v6 mediante propiedades de resultado. El patrón de endpoints existentes de Rubrova utiliza `EXPORT JSON FROM`. La forma `RETURN JSON FROM` consultada pertenece a documentación 7.x.
- **Corrección aplicada:** reemplazar `RETURN JSON FROM` por `EXPORT JSON FROM` en los cuatro endpoints y cambiar la prueba estática para impedir que se vuelva a introducir sintaxis 7.x en módulos 6.2.
- **Advertencia metodológica:** la recomendación anterior de reemplazar `EXPORT` por `RETURN JSON FROM` fue incorrecta para la versión fijada. Se conserva aquí para evitar repetirla.
- **Resultado esperado:** el servidor debe poder parsear y cargar el módulo; después se debe validar el cuerpo HTTP y la estructura de las tres colecciones.
- **Estado al actualizar este registro:** corrección subida a la rama del PR; aún no hay un run de aceptación sobre el nuevo SHA.

## 2026-11-25 — REP-003 — Fijación de sintaxis y protección del contrato

- **Cambios:**
  - `extensions/lsfusion/RubrovaReplenishmentExport.lsf`: volver al patrón `EXPORT JSON FROM`.
  - `scripts/platform/validate-mycompany-extension.test.mjs`: exigir ese patrón para las cuatro acciones API y rechazar `RETURN JSON FROM`.
  - Se conservan los conteos independientes y la política de colecciones ausentes.
- **Commits:** `e8e20e8c28e1e1f2479d07604668030603598c1f` y `c99c9941836571a7465066eefda31179dd6a26c5`.
- **Validación:** pendiente de la ejecución de CI sobre el SHA resultante.

## Plantilla de nuevo registro

Copiar el formato de [RECORD_TEMPLATE.md](#g-record-template). Registrar también las hipótesis descartadas y las limitaciones que siguen abiertas.

## 2026-11-25 — REP-004 — Regresión del matcher estático y verificación de endpoints

- **Workflow afectado:** [45732148752](https://github.com/JavierGrecco/Rubrova/actions/runs/45732148752).
- **Hecho observado:** el job de validación estática falló antes de compilar; `assert.equal(replenishmentApiActions.length, 4)` recibió cero acciones.
- **Causa raíz:** la expresión regular del test se escribió con escapes duplicados. El archivo fuente tenía cuatro acciones; el matcher no las reconocía por un defecto del test.
- **Corrección:** se fijó el patrón de captura y se comprobó contra el contenido real de `RubrovaReplenishmentExport.lsf`: cuatro acciones detectadas, las cuatro empiezan con `EXPORT JSON FROM` y ninguna con `RETURN JSON FROM`.
- **Commit correctivo:** `073a22915b34baf0816a456d2b815bb355726be8`.
- **Estado:** el matcher quedó corregido y verificado contra los archivos recuperados del branch; todavía falta una ejecución de CI que confirme el test en GitHub Actions.

## 2026-11-26 — REP-005 — Verificación de la regresión, mapa de relaciones y divergencia con main

- **Cambios documentales:** se añadió [DOMAIN_RELATIONSHIPS.md](#d-domain-relationships), con el recorrido entre módulos, matriz de propiedad, relaciones navegadas de inventario, venta, ledger de despachos y recepciones; también se añadió ADR-0004 para la identidad compuesta de líneas de venta.
- **Hecho observado:** la rama feature define `sourceLineId` como número comercial de orden + índice de línea, mientras que la versión actual de `main` todavía tiene una descripción antigua basada en `Sales.OrderLine.id`. La extracción de esta rama agrupa por el objeto `Sales.OrderLine` y serializa una clave compuesta; el contrato debe conservar esa distinción.
- **Verificación estática local del contenido recuperado:** cuatro acciones API detectadas; todas utilizan `EXPORT JSON FROM`; ninguna utiliza `RETURN JSON FROM`; los tres contadores aparecen en la exportación y en su sonda; adaptador e inspector validan conteo y longitud; fixture JSON válido; están presentes las tres pruebas nuevas de colecciones vacías/conteos.
- **Límite de esa verificación:** es una comprobación del contenido del branch; no sustituye Node, Python, el parser de lsFusion ni el runtime real de CI.
- **Estado de CI:** el último workflow de plataforma visible sigue siendo [45732148752](https://github.com/JavierGrecco/Rubrova/actions/runs/45732148752), que falló por un matcher estático defectuoso antes de compilar. El matcher se simplificó luego a verificaciones inequívocas, pero todavía no hay una ejecución registrada sobre el SHA actual.
- **Divergencia de ramas:** el PR #8 continúa apuntando al SHA base anterior `bab975fd...`; `main` avanzó 21 commits documentales y GitHub informa `mergeable_state=dirty`. Antes de fusionar hay que incorporar los cambios de `main` y reconciliar, como mínimo, README, Calidad y pruebas, soporte macOS, instalación MyCompany y el documento de stock proyectado; no se debe resolver sobrescribiendo documentación sin revisión.
- **Criterio de cierre:** validar el test estático en CI; compilar y cargar lógica en Linux/macOS; verificar la respuesta autenticada y las colecciones; después sincronizar con `main` y volver a ejecutar los gates del SHA final.


## 2026-11-25 — REP-006 — Prevalidación compartida y reducción del ciclo CI

- **Hechos de duración:** en [45637101959](https://github.com/JavierGrecco/Rubrova/actions/runs/45637101959) el workflow tardó 31m32s: el build del fork duró 401s, el diagnóstico Docker/Linux 1.005s y el smoke nativo macOS 417s. En [45723325906](https://github.com/JavierGrecco/Rubrova/actions/runs/45723325906), el build duró 363s, Docker/Linux 226s y el smoke macOS 294s.
- **Diagnóstico:** Docker/Linux era un job no bloqueante y no era el entorno local prioritario; su coste puede superar el de todos los tests rápidos juntos. No aporta evidencia superior a la ruta nativa cuando la aceptación prioritaria es macOS ARM64.
- **Cambio:** se añadió `scripts/platform/local-preflight.sh` con modos `--platform`, `--replenishment` y `--all`. Los workflows llaman a las mismas rutinas para evitar que la validación local difiera de CI.
- **Cambio CI:** el build completo y el smoke nativo macOS ARM64 permanecen automáticos. Los jobs Linux nativo y Docker/Linux quedan bajo ejecución manual. Se añade concurrencia a nivel workflow para cancelar una corrida antigua al llegar un commit nuevo al mismo PR.
- **Integración de ramas:** se creó `integration/replenishment-mainline-preflight` desde `main` (base `699eb8343706acd9631ca83150eb54ba8fba71e3`) para reconstruir un PR corto y evitar arrastrar los 118 commits divergentes del PR #8.
- **Límite de validación:** esta entrada registra la decisión y la implementación del preflight/workflows; hasta que el nuevo PR ejecute Actions, no se marca la nueva capa como aprobada. El script rápido tampoco carga lsFusion ni consulta una base MyCompany.
- **Próximo criterio de cierre:** nueva ejecución de CI para el commit integrado; build + smoke macOS ARM64 + respuesta JSON válida de las cuatro acciones y conteos conciliados; después probar el runtime en el MacBook local.


## 2026-11-26 — REP-007 — Primera ejecución del preflight unificado

- **PR:** [#10](https://github.com/JavierGrecco/Rubrova/pull/10).
- **Run:** [45735337191](https://github.com/JavierGrecco/Rubrova/actions/runs/45735337191), SHA `5ac3c75f`.
- **Hecho observado:** el workflow ejecutó el nuevo preflight. En la suite Node pasaron 28 de 29 pruebas; falló una aserción de concurrencia en `validate-mycompany-extension.test.mjs`, que esperaba cuatro apariciones globales de `cancel-in-progress: true`.
- **Causa:** el nuevo `concurrency` a nivel workflow añadió una quinta regla global, mientras que los cuatro controles por job siguen siendo correctos. La aserción existente contaba ambos niveles como si fueran una sola política.
- **Corrección:** distinguir en el test la regla global por PR de las cuatro reglas por job; añadir una regresión que verifica que Linux/Docker son manuales y que el smoke macOS ARM64 permanece automático; comprobar que ambos workflows invocan el mismo preflight local.
- **Alcance del fallo:** no llegó a la compilación Maven ni al smoke de runtime porque el job `validate` es una dependencia previa. Windows pasó y el workflow del planificador terminó en verde.
- **Estado:** corrección subida al branch; la segunda ejecución sobre el nuevo SHA debe confirmar el arreglo.


## 2026-11-26 — REP-008 — Preflight unificado aprobado en la nueva rama principal

- **PR:** [#10](https://github.com/JavierGrecco/Rubrova/pull/10), SHA probado `9b9083c35570675a1bb7055fd86d235bf9ab4fde`.
- **Preflight de plataforma:** [run 45735930978](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930978), job `Prevalidación local compartida`: aprobado.
- **Resultados:** 30/30 tests Node de la extensión; 34/34 tests Node de evaluación; 10 tests de configuración Python, 5 de URL/runtime nativo y 18 de supervisor nativo; pruebas de listener y despliegue aprobadas. La validación sintáctica de Windows también pasó.
- **Preflight de reposición:** [run 45735930945](https://github.com/JavierGrecco/Rubrova/actions/runs/45735930945): aprobado, usando `local-preflight.sh --replenishment`.
- **Corrección de iteración:** las ejecuciones iniciales del PR #10 descubrieron (a) una aserción que mezclaba concurrencia global y por job, y (b) que el workflow de reposición conservaba sus pasos anteriores. Ambos casos se corrigieron y se añadieron pruebas estáticas para que no vuelva a producirse la divergencia.
- **Concurrencia:** al llegar el SHA corregido, la corrida anterior fue cancelada; no se debe tomar como fallo funcional de código.
- **Estado:** primera capa de validación rápida aprobada en GitHub. La compilación completa del fork continúa; el smoke macOS ARM64 y la API nativa siguen pendientes.

## 2026-11-26 — REP-011 — Conflicto de concurrencia al persistir el idioma del usuario

- **PR:** #10.
- **Evidencia:** [run 45741635022](https://github.com/JavierGrecco/Rubrova/actions/runs/45741635022), log PostgreSQL y `server-console.log`.
- **Síntoma:** dos transacciones del usuario admin (`CustomUser.key0=786`) intentaron actualizar `Authentication_clientLanguage_CustomUser` con `en` al mismo tiempo. PostgreSQL devolvió `could not serialize access due to concurrent update`; el log de lsFusion registró `SQLConflictException: UPDATE_CONFLICT` para el mismo `UPDATE Authentication_customUser`.
- **Alcance:** el servidor terminó su inicio y la UI alcanzó `UI_LOGIN_STATUS=authenticated:admin`; por tanto, el conflicto no fue la causa inmediata del fallo de esa corrida, que se detuvo por una reserva de salida igual a cero. Se registra como fallo concurrente independiente.
- **Causa localizada:** `RemoteConnection.initConnectionContext()` crea una sesión por conexión RMI y `saveUserContext()` escribe los cinco datos de locale/formato en la fila compartida de `CustomUser`. El cliente web puede inicializar varias conexiones para el mismo usuario en paralelo.
- **Corrección:** bloqueo por stripe derivado del login, adquirido antes de `getExecSession()`. La creación de conexiones del mismo usuario queda serializada; los demás usuarios conservan concurrencia.
- **Regresión:** el preflight comprueba estáticamente el orden bloqueo→sesión; el smoke nativo busca el conflicto específico en los logs y debe imprimir `RUBROVA_AUTH_USER_CONTEXT_SERIALIZATION=passed`.
- **Estado:** fix subido; compilación y smoke nativo de un SHA nuevo pendientes.

## 2026-11-26 — REP-012 — Error de parseo lsFusion en fixture de reposición

- **PR:** [#10](https://github.com/JavierGrecco/Rubrova/pull/10), rama de integración existente.
- **Evidencia:** [run 45744747100](https://github.com/JavierGrecco/Rubrova/actions/runs/45744747100), job macOS ARM64.
- **Síntoma:** el proveedor simulado y PostgreSQL iniciaron, pero el supervisor terminó durante el arranque del servidor. `stderr.log` señaló `RubrovaCIReplenishmentFixture:71:61 — WHERE clause is forbidden with GroupingType`.
- **Causa raíz:** `rubrovaCIOutgoingOrder() = GROUP MAX Sales.Order o WHERE ...` usa una cláusula no admitida por ese tipo de agrupación en lsFusion 6.2.
- **Corrección:** se reemplazó `WHERE` por `IF`, siguiendo la sintaxis de agrupación ya usada por `RubrovaCISalesFixture.lsf` y otros módulos del repositorio.
- **Regresión:** se añadió al preflight una aserción positiva para `GROUP MAX ... IF` y otra negativa para `GROUP MAX ... WHERE`.
- **Alcance:** esta corrección resuelve el error de parseo identificado; no se declara validada hasta que el servidor arranque y el smoke macOS pase las sondas y la exportación.


## 2026-11-26 — REP-013 — Consolidación main y aceptación nativa integrada

- **Commit canónico:** [`f545c907`](https://github.com/JavierGrecco/Rubrova/commit/f545c907b12a9eed4cf5e532edd3434babb64139).
- **Estado del repositorio:** una única rama visible (`main`) y cero pull requests abiertos. La exportación nativa de reposición y el runtime quedaron integrados; no continuar desarrollando ramas paralelas para el mismo alcance.
- **Validación:** [run 45847755524](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755524), concluido con `success`; [planificador run 45847755643](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755643), concluido con `success`.
- **Hechos observados en macOS ARM64:** login autenticado; sondas de inventario, compromisos y recepciones HTTP 200; exportación con conteos y filas verificables; venta sintética ARS 1.250; pago exacto en efectivo; stock 10 → 9; turno `CLOSED`; persistencia después del reinicio; Demo aislada aprobada.
- **Límites:** egress externo habilitado (`RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`); Linux nativo y Docker/Linux `skipped`; los datos son sintéticos y todavía no hay aceptación en el Mac físico ni jornada productiva.

## 2026-11-26 — REP-014 — Primer respaldo lógico PostgreSQL nativo

- **Motivo:** el supervisor ya conservaba la base entre reinicios, pero aún no existía un paquete comprobable ni una restauración protegida.
- **Implementación:** `scripts/platform/native-postgres-backup.py` crea un paquete de base PostgreSQL en formato custom, con manifiesto y SHA-256; verifica el paquete y restaura sólo a una base nueva, nunca sobre `rubrova_dev`.
- **Seguridad:** comprueba que el servidor sea PostgreSQL 18 y que el directorio de datos y puerto correspondan al clúster privado de Rubrova; sólo conecta a loopback; no exporta secretos; ante un fallo intenta retirar únicamente la base nueva incompleta.
- **Pruebas añadidas:** corrupción de dump/manifiesto, entradas extra, directorio de datos ajeno, confirmación explícita, base ya existente y limpieza de una restauración fallida.
- **Aceptación:** preflight y smoke nativo macOS ARM64 aprobados en [run 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565). El log confirma creación, SHA-256, verificación y restauración a `rubrova_restore_ci`; se emitió `RUBROVA_NATIVE_POSTGRES_BACKUP_RESTORE=passed`.
- **Límite:** protege PostgreSQL, no adjuntos, documentos, configuración del SO ni credenciales. La aceptación local en Mac físico/Windows y el paquete completo siguen pendientes.


## 2026-11-26 — REP-015 — Aceptación nativa integrada y restauración PostgreSQL

- **Commit probado:** `ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a`.
- **Workflow:** [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565), terminado con `success`.
- **Build:** preflight compartido, validación sintáctica Windows y compilación completa del servidor, cliente GWT y lógica MyCompany aprobados.
- **Smoke macOS ARM64:** login, API autenticada de reposición sobre fixtures, venta ARS 1.250, efectivo exacto, factura/pago, stock 10 → 9, cierre de turno, reinicio/persistencia y Demo aislada aprobados.
- **Backup/restore:** paquete PostgreSQL creado y verificado por SHA-256 y `pg_restore --list`; restauración a `rubrova_restore_ci`; la base original `rubrova_dev` no se sobrescribió.
- **Límites:** egress estuvo habilitado (`offline acceptance not tested`); Linux/Docker fueron `skipped`; Windows sólo comprobó sintaxis; aún no hay prueba en Mac físico, base comercial real, periféricos ni jornada real.
- **Siguiente iteración:** proteger devolución parcial/total y reintegro contra sobredevolución; luego movimientos y arqueo físico, utilizando los ledgers originales de MyCompany sin duplicarlos.


## 2026-11-26 — REP-016 — Investigación de contratos lsFusion/MyCompany y parser de booleanos

- **Repositorio:** https://github.com/JavierGrecco/Rubrova
- **Documentación consolidada:** commit ef008fe0f3bf6bad5bf27aa1440c8acb760cf0fb; guía [Anexo B](#b-integration), índice de ingeniería y contrato general.
- **Fuentes fijadas:** lsFusion 6.2 commit dd4dbe5bf9b136e73e18fe25d741253929324350; MyCompany 6.2 commit d21ca6978717b98b6300d90267f9767db7414008.
- **Alcance investigado:** modelo de módulos y dependencias; REQUIRE/NAMESPACE; propiedades declarativas y DATA; acciones; hooks abstractos; constraints; formularios; eventos; APPLY/CANCEL/NEWSESSION/NESTEDSESSION; Action API y EXTERNAL; POS, facturas, notas de crédito, cobros/reintegros, sesiones, caja, despachos, recepciones, ledger físico y reservas.
- **Hechos observados:** runtime LSF integrado, no conjunto de microservicios; el POS conecta Session/Invoice/IncomingPayment/Shipment/InvLedger y la devolución conecta Bill/BillLine/OutgoingPayment/Receipt/InvLedger. onHand y available son magnitudes distintas. La fórmula active(...) varía según el documento. Los agregados vacíos pueden retornar NULL y no deben compararse como cero sin normalización explícita.
- **Riesgo de negocio descubierto:** el formulario nativo de reintegro limita cada nota frente a lo cobrado originalmente por medio de pago, pero no resta los reintegros de devoluciones anteriores; la validación acumulativa es una brecha a proteger en Rubrova.
- **Hecho observado de CI:** run 45870077864, SHA 698cba2db3567f07478dede2950b07b6e4a265f5: preflight, validación Windows y compilación pasaron; el arranque macOS ARM64 falló al inicializar la lógica con RubrovaCISalesFixture:206:83 use NULL instead of FALSE. El parser llegó a procesar 719 de 722 módulos; no fue un fallo de PostgreSQL ni de compilación.
- **Corrección aplicada:** commit 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53 de la rama del PR #13 cambia los dos campos de diagnóstico a enteros 1/0 y actualiza las aserciones estáticas. Evita usar FALSE, que no es el literal de falso aceptado por el lenguaje/versión.
- **Validación posterior:** run 45872444450, SHA 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53: prevalidación y Windows aprobados; compilación Maven completa en curso al registrar esta iteración; smoke nativo aún no ha comenzado. No se declara corregido hasta que el parser cargue los módulos y el escenario E2E pase.
- **Pendientes de investigación:** Compras/abastecimiento; pedidos mayoristas y canales; fiscalidad ARCA; lotes/costos/producción; CRM/cuenta corriente; autorizaciones/auditoría; instalación local Mac físico y Windows; periféricos, desconexión de red y backup completo.


## 2026-11-26 — REP-017 — Flujos de compras, ventas mayoristas y analítica comercial

- **Base:** MyCompany 6.2 vendorizado en Rubrova, revisión fijada en platform/mycompany-6.2.lock.json.
- **Documentación:** se amplió [Anexo B](#b-integration) (secciones 6.7–6.11) en commit 5484d1beece3bcc5ec6c40b9c569b1890e1dbf9c.
- **Compras:** Purchase.Order confirmado puede generar Receipt ready con ReceiptLine/initialDemand. ReceiptResLedger representa la entrada esperada como reserva firmada; increaseAvailableStock condiciona su efecto en available. ReceiptInvLedger sólo incorpora la cantidad efectivamente completada al inventario físico. PurchaseOrderReceipt limita recibido a la cantidad pedida.
- **Facturación proveedor:** PurchaseOrderBill soporta cantidad pedida no facturada; PurchaseOrderBillReceipt añade facturación por cantidad recibida y evita reutilizar ReceiptLine ya vinculadas. BillDebt y OutgoingPaymentDebt conectan obligaciones y pagos; BillPayment.registerPayment crea OutgoingPayment.
- **Ventas mayoristas:** SalesOrderShipment crea/reutiliza Shipment waiting para el remanente, ejecuta precheckAvailability y registra reservas antes de la salida física. Los despachos parciales se concilian por Sales.OrderLine; una constraint evita sobre-despacho. ShipmentInvLedger registra la salida física final.
- **Facturación de venta:** SalesOrderInvoice permite la política ordered; SalesOrderInvoiceShipment añade delivered y factura sólo ShipmentLine completadas, activas y aún no facturadas, preservando los enlaces de línea.
- **Relación venta-compra:** SalesOrderPurchase enlaza líneas de Sales.OrderLine con Purchase.OrderLine para trazabilidad. No se interpreta como compra automática ni como reserva física sin evidencia adicional.
- **Analítica:** SalesLedger agrega hechos por producto, cliente, ubicación y tiempo, con cantidad, importe, costo y margen; SalesLedgerInvoice aporta ventas positivas y SalesLedgerBill aporta notas de crédito negativas. La política exacta de costo/retroactividad requiere una investigación específica antes de usar el margen en decisiones productivas.
- **Reglas incorporadas:** pedido, recepción/despacho, factura y pago son etapas distintas; las cantidades y los importes deben conciliarse por separado; los ledgers nativos siguen siendo la fuente de verdad.
- **Límites pendientes:** políticas de valoración de stock, lotes y costos ajustados; impuestos/ARCA; compras automáticas, MOQ/múltiplos y proveedor preferente; stock de seguridad, plazo de entrega y abastecimiento multi-sucursal; seguridad/roles y escenarios con datos reales.


## 2026-11-26 — REP-018 — Del modelo de terminales al estado real de integración

- **Fuentes inspeccionadas:** extensions/lsfusion/RubrovaPaymentTerminals.lsf, extensions/lsfusion/RubrovaIntegrationResilience.lsf, scripts/platform/fixtures/RubrovaCIIntegrationFixture.lsf, docs/MYCOMPANY_RUNTIME_INSTALL.md.
- **Hecho observado:** PaymentTerminals define persistencia y formularios para cuenta de proveedor, terminal, asignación POS/medio, intención, intento, evento, reintegro y liquidación. Contiene claves de idempotencia y una bandera de firma verificada, y deliberadamente no guarda el cuerpo HTTP entero.
- **Límite probado por inspección:** no hay acciones de cobro real ni EXTERNAL HTTP POST en el código LSF del módulo; no hay receptor de webhook ni bridge local implementado. El propio documento de instalación califica el módulo como configuración/trazabilidad y dice que aún no ejecuta cobros reales.
- **Resiliencia actual:** rubrovaHttpGet clasifica respuestas 429, 408/425, 5xx, 401, 403, 409 y fallo de conexión/timeout, establece timeout entre 1 y 30.000 ms y persiste una incidencia separada. No realiza reintentos automáticos ni implementa métodos HTTP de escritura.
- **Decisión:** la integración electrónica queda clasificada como modelo preparado, no operativa. Los intentos e intenciones no son el movimiento contable. El cobro confirmado debe registrarse como IncomingPayment; el reintegro confirmado debe conciliarse con Bill y OutgoingPayment; las liquidaciones separan bruto, comisión, retenciones y neto.
- **Pruebas requeridas:** doble envío, timeout con resultado remoto desconocido, consulta de estado, webhook duplicado/tardío/firma inválida, reinicio, reintegro y conciliación con liquidación; pruebas con bridge y hardware real.


## 2026-11-26 — REP-019 — Auditoría ampliada de reutilización de la base incorporada

- **Revisión auditada:** Rubrova main 475ca9224520d296b23990071b1c79f00d6dced9; lsFusion 6.2 dd4dbe5bf9b136e73e18fe25d741253929324350; MyCompany 6.2 d21ca6978717b98b6300d90267f9767db7414008.
- **Inventario confirmado:** 1.335 archivos MyCompany, 800 módulos LSF y 18.067.796 bytes; 4.887 archivos lsFusion, 3.330 fuentes Java y 62.696.269 bytes. El módulo principal carga los dominios de datos maestros, inventario, facturación, compras, ventas, retail, fabricación, proyectos, RR. HH., CRM y flota, junto con servicios transversales. Las raíces regionales quedan fuera del REQUIRE de core.
- **Capacidades no aprovechadas identificadas:** stocktake Adjustment/AdjustmentList/barcode/InvAdjustment; transferencias, aceptación, picking, put-away y lotes; costeo FIFO/AVCO/standard, valoración histórica y asignación de costos de servicios/fabricación; SalesLedger con costo real de ShipmentLine/ReceiptLine; APIs nativas Item/Category/Attribute/Price/Inventory/SalesOrder/Task; permisos Security/LocationEmployee; Backup/Scheduler/ProcessMonitor/Documentation; CRM Lead→SalesOrder y Marketing attribution.
- **Hallazgo de stocktake:** la base calcula teórico histórico desde prevOnHandB, registra realQuantity, permite hojas separadas y barcode, y genera diferencias en InvLedger al validar. No se debe desarrollar un stocktake paralelo. El arqueo de efectivo es distinto y sigue pendiente en el POS central inspeccionado.
- **Hallazgos de integración:** SalesOrderAPI.newOrders es alta por número y no upsert; deleteOrders sólo borra drafts; InvLedgerAPI devuelve onHand, no available. Las APIs se deben envolver/adaptar si el contrato necesita idempotencia, paginación, versión o sincronización bidireccional.
- **Costos:** ItemCost planificado no equivale a CostLedger real. SalesLedger tiene rutas para costos reales ligados a despacho/recepción. Los filtros temporales FIFO comentados son riesgo de backdating por reproducir, no bug declarado.
- **Backup:** se detectó que el restore selectivo puede devolver el nombre de DB temporal al capturar error pg_restore, sin eliminarla en ese catch. Requiere prueba/mitigación antes de usarlo en recuperación crítica. El backup Rubrova con SHA y restore a DB nueva se mantiene como complemento.
- **Regionales:** no hay raíz ARCA; ATOL, Wazzup, EnterpriseData, KSeF y otros son patrones opcionales. WazzupWebhook registra el body y usa @@noauth en el handler revisado; no copiar sin firma/deduplicación/protección de PII.
- **Documento:** [Anexo A](#a-reuse-first), enlazado desde índice, contratos y guía.
- **Pendiente:** pruebas de runtime del stocktake, FIFO retroactivo, coste real por documento, API duplicada, restore selectivo fallido, permisos por depósito y arqueo físico de efectivo.


## 2026-11-26 — REP-020 — Evidencia de rechazo transaccional y pago de devolución parcial

- **Run:** [45872444450](https://github.com/JavierGrecco/Rubrova/actions/runs/45872444450), SHA 26a60fd1f88fd2b355b8a72baafbd9688ed5ff53.
- **Hechos del runtime:** parser y carga de los 722 módulos aprobados; servidor nativo macOS ARM64 inició en 158.053 ms. El smoke funcional creó la primera devolución de 0,4 unidades, importe ARS 500 y el stock subió de 9 a 9,4. La constraint nativa produjo el mensaje “The returned quantity on the invoice line exceeds the original quantity” al intentar 0,7 sobre remanente 0,6.
- **Causa del primer fallo de fixture:** el indicador overReturnRejected se escribía como DATA persistente dentro de la NEWSESSION cuyo APPLY quedaba cancelado; ese valor no sobrevivía al cierre de la sesión. La API devolvía NULL y no ejecutaba el paso posterior de 0,6.
- **Corrección en PR #13:** commit f2c35de9965842b64861d49a78367d1d10f2d3f8 usa DATA LOCAL NESTED BOOLEAN para llevar el resultado al padre y registra la marca durable después, en un APPLY independiente. El helper de devolución también crea directamente el OutgoingPayment nativo en efectivo, sin depender del buffer LOCAL usado por la pantalla de cobro.
- **Regresión estática inicial:** run 45876753464 falló antes del build por cuatro secuencias literales \\n insertadas al editar el test JavaScript; no ejecutó lógica de producto.
- **Corrección del test:** commit d5edc886c2c9fa827d8eedff9e7951eeefb36194 reemplazó esos cuatro escapes por saltos de línea reales.
- **Estado:** run [45876903441](https://github.com/JavierGrecco/Rubrova/actions/runs/45876903441) sobre d5edc88 quedó en cola al registrar este documento. La validación final sigue pendiente; no afirmar todavía que la segunda devolución, los reintegros y la persistencia E2E hayan pasado.


<a id="g-record-template"></a>

## Anexo G — Plantilla histórica de registro

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

## Identificación

- Fecha local:
- ID:
- PR:
- Commit SHA:
- Workflow/run/job:
- Plataforma/arquitectura:
- Versión de runtime:

## Síntoma

Describir el comportamiento observable sin atribuir causa.

## Evidencia reproducible

- Logs/rutas/fragmentos:
- Entrada o fixture:
- Resultado esperado:
- Resultado observado:

## Clasificación

- Hechos:
- Interpretación:
- Hipótesis pendientes:
- Hipótesis descartadas:

## Causa raíz

Explicar el mecanismo y enlazar código/documentación de la versión afectada.

## Cambio realizado

- Código:
- Contrato/documentación:
- Test de regresión:
- Migración/compatibilidad:
- Riesgos:

## Validación

- Comandos/tests ejecutados:
- SHA exacto:
- Entorno:
- Resultado:
- Artefactos y digest:
- Qué no se probó:

## Cierre

- Estado: abierto / corregido sin validar / validado en CI / validado con datos reales / productivo.
- Criterio objetivo para cerrar:
- Decisión relacionada:
- Contrato relacionado:
- Próxima revisión:


## Anexo H — Roadmap previo, preservado

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Revisión:** 26 de noviembre de 2026  
**Dirección prioritaria:** POS y operación comercial → ERP de gestión → contabilidad/fiscalidad → análisis y reportes → perfiles sectoriales y canales → logística avanzada.
**Gobierno del repositorio:** seguir [Política de ramas e integración](BRANCHING_STRATEGY.md); `main` es la única fuente de verdad y se mantiene `main` como única rama persistente; cualquier rama temporal se cierra al integrar el hito.

## Estado real

Rubrova está en **Fase 0: piloto integrado POS + ERP**, con el runtime nativo y la exportación de reposición integrados en `main`. El commit actual es [`ac758d0`](https://github.com/JavierGrecco/Rubrova/commit/ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a). El workflow [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) aprobó preflight, compilación completa y smoke nativo macOS ARM64.

El smoke verificó login, sondas de inventario/compromisos/recepciones, exportación nativa sobre fixtures, venta sintética ARS 1.250, pago exacto en efectivo, stock 10 → 9, cierre de turno y persistencia tras reinicio. También creó un backup lógico PostgreSQL, comprobó su SHA-256 y lo restauró en una base nueva sin sobrescribir la activa.

El backup cubre **sólo PostgreSQL**; todavía faltan adjuntos, documentos externos, retención, copia externa y recuperación guiada. La exportación de reposición requiere conciliación contra una base MyCompany comercial real.

El run reciente dejó `RUBROVA_NATIVE_EGRESS_BLOCKED=false` y `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. Los diagnósticos Linux/Docker fueron `skipped`, y Windows sólo validó sintaxis PowerShell. No hay aún aceptación en el Mac físico ni jornada comercial.

Los árboles fuente de lsFusion 6.2 y MyCompany 6.2 siguen fijados en `vendor/platform/` y `vendor/mycompany/`; servidor, cliente GWT y lógica se compilan desde Rubrova. El camino local prioritario continúa siendo Java 21, PostgreSQL 18 y Tomcat 9 sin Docker.

La capa de pagos presenciales conserva arquitectura y trazabilidad iniciales, pero no hay conector homologado ni cobros reales. La siguiente prioridad funcional es devolución/reintegro vinculados a la factura original y movimientos de efectivo, utilizando los ledgers nativos de MyCompany.

## Prioridad del producto

El seguimiento de envíos **no es una prioridad de inicio**. Se conserva en el modelo de dominio para que una venta pueda despacharse después y tenga uno o varios envíos, pero los conectores de transportistas se dejan para la última etapa.

| Orden | Resultado | Qué tiene que resolver |
|---:|---|---|
| 1 | POS y venta | Carrito, catálogo, clientes, precios, descuentos, cobro, vuelto, pagos mixtos, caja, devoluciones y ticket |
| 2 | ERP de gestión | Stock, depósitos, compras, proveedores, recepción, costo, clientes, cuentas corrientes y sucursales |
| 3 | Contabilidad y fiscalidad argentina | Libro mayor, cuentas, bancos, impuestos, ARCA, facturas, notas y conciliación |
| 4 | Reportes, control de gestión e inteligencia comercial | Ventas, caja, compras, inventario, rentabilidad por producto/marca/canal/área, preferencias de marcas, tendencias y pronósticos trimestrales/estacionales |
| 5 | Capacidades sectoriales | Recetas, producción, mermas, lotes, vencimientos, mayorista, distribución y servicios B2B |
| 6 | Canales externos | Ecommerce, Mercado Libre, WhatsApp, delivery y pedidos de otras plataformas |
| 7 | Logística avanzada | Transportistas, tarifas, etiquetas, retiro, entrega, tracking y reclamos |

Las dimensiones que afectan costos y reportes (unidad de negocio, canal, sucursal, centro de costo, depósito y proyecto) se incorporan desde el primer modelo. Se posterga el desarrollo sofisticado de BI, no la captura correcta de sus datos.

## Fase 0 — arrancar el piloto MyCompany 6.2

**Objetivo:** instalar una suite POS + ERP reproducible, extenderla desde fuera de su núcleo y probar el circuito antes de crear módulos equivalentes.

### Orden de ejecución

1. **MyCompany 6.2 / lsFusion:** primer piloto integrado; utilizar Retail POS, sesiones, pagos, devoluciones, inventario, costos, compras y facturación.
2. **Tryton 8.0 + tryton-ar 8.0:** contraste fiscal argentino y alternativa si MyCompany no supera las puertas.
3. **ERPNext 16 / Frappe 16:** reserva; reabrir sólo ante una brecha funcional o técnica medida.
4. **Dolibarr 24.0.3:** filtro corto si las opciones principales no superan las puertas.
5. **Posnic 1.9.2:** referencia POS secundaria, nunca dueño paralelo de ventas o inventario.

El lock de versión, la extensión modular, los scripts de preparación y el detalle de módulos están en [Inicio de implementación](IMPLEMENTATION_START.md).

### Tareas de esta fase

- [x] Fijar MyCompany 6.2 por tag y commit; registrar los hashes oficiales del instalador Windows y del JAR.
- [x] Inspeccionar el código fuente de POS, sesiones, pagos mixtos, efectivo, devoluciones, inventario, costos y compras.
- [x] Crear el punto de entrada RubrovaCustom y el módulo separado RubrovaPOSLocalization, con el glosario es_AR.
- [x] Agregar captions localizados para el primer flujo POS en RubrovaPOSLocalization; validar que los 36 identificadores propios tienen traducción.
- [ ] Cargar los dos módulos Rubrova en MyCompany 6.2 real, confirmar los captions y traducir filtros/mensajes de error heredados.
- [x] Incorporar validación automática del lock, composición de módulos y traducciones; workflow correcto en CI.
- [x] Probar el staging de despliegue Docker en un directorio temporal: copia de los tres archivos, conservación de settings y backups, sin invocar Docker.
- [x] Preparar scripts de despliegue de RubrovaCustom + RubrovaPOSLocalization para Docker, Linux nativo y Windows nativo, con copia previa de settings y módulos existentes.
- [x] Registrar limitación de arquitectura de imagen Docker MyCompany 6.2 en ARM64.
- [ ] Ejecutar la instalación y carga en el equipo anfitrión; la CI no puede sustituir esta prueba.
- [ ] Descargar los artefactos, verificar hashes en la máquina de ejecución e instalar en entorno local aislado.
- [ ] Ejecutar apertura → escaneo → carrito → pagos mixtos/vuelto → venta → stock → devolución → cierre.
- [ ] Probar dos cajas, pagos pendientes/repetidos, caída/reinicio, exportación, backup y restauración.
- [ ] Contrastar con Tryton 8.0 fiscalidad y comprobantes; homologar ARCA antes de producción.

**Criterio de salida:** instalación reproducible, extensión cargada, POS completo en español, permisos, integridad de ventas/pagos/caja/stock, recuperación, exportación y restauración demostradas. Hasta entonces el piloto no se habilita para uso diario.

### Cierre actual de Fase 0 y próximo bloque

- [x] MyCompany 6.2 y lsFusion 6.2 fijados; fuentes completas vendorizadas y compiladas desde Rubrova.
- [x] Runtime nativo macOS ARM64 con Java 21, PostgreSQL 18 y Tomcat 9; sin Docker.
- [x] Login, navegación Comercio → Punto de venta y apertura de turno sintético.
- [x] Venta ARS 1.250, pago exacto en efectivo, factura persistida y stock conciliado (10 → 9).
- [x] Cierre básico del turno y conciliación de efectivo.
- [x] Exportación nativa de reposición de sólo lectura y sondas autenticadas verificadas contra fixtures.
- [x] Persistencia después de reiniciar el runtime y segunda instancia Demo aislada.
- [x] Backup lógico PostgreSQL creado, verificado y restaurado a una base nueva en el smoke nativo.
- [ ] Devolución parcial/total vinculada a la factura original, con límite de cantidad, reintegro y reposición de stock.
- [ ] Ingresos/retiros, arqueo físico y diferencias de caja.
- [ ] Vuelto, pagos mixtos, terminal real, cancelación y pagos pendientes.
- [ ] Exportación de reposición conciliada con una base MyCompany local con datos controlados.
- [ ] Continuidad offline macOS, prueba en Mac físico, Windows nativo y periféricos reales.
- [ ] Backup portable completo, copia externa, restauración guiada y rollback.

**Dirección inmediata:** completar devolución y reintegro usando las entidades/acciones de MyCompany; después probar ingresos/retiros y arqueo contado. No crear un segundo ledger de inventario ni de efectivo. A continuación cerrar modo offline, Windows y recuperación integral antes del piloto comercial.

## Fase 1 — primera entrega: POS con gestión mínima real

**Objetivo:** tener un circuito comercial que se pueda usar y auditar, no una pantalla de demostración.

Alcance:

- Organización, sucursal, usuarios, roles, dispositivos, caja y depósito básicos.
- Catálogo, variantes, códigos de barras, unidades, productos pesables, precios y clientes.
- Capturar desde el inicio marca, fabricante y segmento comercial configurable por categoría (primera/líder, segunda, económica, propia, alternativa/genérica), con vigencia desde/hasta, motivo, responsable e historial; no inferir el segmento sólo por precio.
- Capturar unidad base y comparable, contenido neto, equivalencias de pack/caja/bulto y precios/costos históricos con vigencias. La venta conserva el precio, costo de referencia, marca, segmento y presentación aplicados en ese momento.
- Registrar disponibilidad y existencia por producto/ubicación, reservas, tránsito, períodos sin stock, productos no vendibles, horarios, cambios de surtido, promociones y demanda no satisfecha cuando se pueda observar; son datos obligatorios para corregir la demanda censurada.
- Carrito editable antes del cobro; descuentos, promociones e impuestos recalculables.
- Efectivo, vuelto, medios mixtos y registro del resultado de cada pago.
- Apertura, movimientos, arqueo y cierre de caja.
- Venta, ticket propio, cancelación y devolución parcial/total.
- Reservas y movimientos de stock con una autoridad única y ledger trazable.
- Documento fiscal separado del ticket, con estados visibles.
- Lector e impresora mediante adaptadores; terminal de pago real sólo tras pruebas de sandbox/homologación.
- Panel operativo con ventas netas, devoluciones, medios de pago, diferencia de caja y productos vendidos.
- Persistencia local, idempotencia, audit trail, backup automático, portable y verificable, restauración guiada en Windows limpio y reinicio del proceso. La copia externa debe poder continuar en otro equipo.

**Criterio de salida:** una jornada repetible sin pérdida ni duplicación; ventas, pagos, caja, stock y documento fiscal conciliados; recuperación demostrada.

## Fase 2 — ERP administrativo

**Objetivo:** administrar el negocio de punta a punta detrás de la caja.

Alcance:

- Clientes/empresas, proveedores, contactos, condiciones y listas de precios.
- Cuenta corriente, crédito, vencimientos, saldos y límites con aprobación.
- Compras, órdenes, recepción parcial/total, devoluciones a proveedor y costos accesorios.
- Depósitos, transferencias, conteos, ajustes autorizados, reservas, lotes y vencimientos según el rubro.
- Ledger de inventario valorizado con método documentado (FIFO/promedio móvil u otro soportado por el núcleo elegido), costo de cada recepción, descuentos/bonificaciones, flete y costos puestos; distinguir costo histórico, costo vendido y costo de reposición.
- Costos variables atribuibles (comisiones de medios de pago/canales, embalaje, preparación y entrega) y gastos directos/compartidos con reglas de asignación versionadas; nunca publicar rentabilidad firme con costos ausentes.
- Importación masiva, normalización y validación de datos.
- Sucursales y varias áreas de negocio; captura de unidad de negocio y centro de costo por línea cuando corresponda.
- Documentos, adjuntos, historial y auditoría.

**Criterio de salida:** ventas, recepciones, compras, costo y disponibilidad coinciden; toda diferencia tiene origen, responsable y tratamiento.

## Fase 3 — contabilidad, fiscalidad y administración argentina

**Objetivo:** convertir los hechos comerciales en resultados contables/fiscales confiables.

Alcance:

- Libro mayor, plan de cuentas, diarios, períodos, cierres y asientos.
- Cuentas por cobrar/pagar, bancos, conciliación, medios de pago, liquidaciones y comisiones.
- Impuestos, tipos documentales, puntos de venta, numeración y reglas argentinas.
- ARCA en homologación; emisión, consulta, estados inciertos, nota de crédito/débito y recuperación.
- CUIT, condición fiscal, retenciones/percepciones aplicables.
- Exportación e importación idempotente para el estudio o sistema contable usado (Tango, Catedral, Bejerman, Xubio, Colppy u otro).
- Conciliación desde la venta hasta el pago, el movimiento de stock, el comprobante y el asiento.

Bigcapital sólo se prueba si la contabilidad de la plataforma elegida no alcanza. No se mantienen libros mayores paralelos.

**Criterio de salida:** débitos/créditos, saldos, impuestos, ventas y documentos conciliados; ARCA homologado antes de cualquier habilitación productiva.

## Fase 4 — reportes y control de gestión

### Capacidades obligatorias de inteligencia comercial

- Seguimiento diario, semanal, mensual, trimestral y por estación del hemisferio sur.
- Detección temprana de productos emergentes, acelerados, desacelerados, estancados y en caída.
- Pronóstico por SKU/familia, marca, categoría, sucursal, canal y área, con horizonte explícito.
- Comparación interanual equivalente y ajuste por días sin stock, promociones, cambios de precio y surtido.
- Alertas y recomendaciones de compra/reposición antes de cada trimestre y estación, considerando lead time, stock de seguridad y presupuesto.
- Rentabilidad absoluta y porcentual por producto/marca/categoría/cliente; distinguir facturación de contribución real.
- Perfil 360 por cliente/empresa: productos, categorías, marcas/segmentos, preferencias de canal, recurrencia, RFM, retención, CLV y contribución, con ventas anónimas preservadas.
- Recomendaciones por cliente (recompra, sustitución, complementos y recuperación) sólo con evidencia suficiente, permiso de contacto cuando corresponda y aprobación humana.
- Segmentación configurable de primeras marcas, segundas, económicas, propias y alternativas; medir participación por unidades, tickets, facturación y ganancia.
- Detección de sustitución y cambios de preferencia entre marcas, controlando faltantes y diferencias de presentación/precio por unidad.
- Simulación de precio, promoción, surtido y compra; toda ejecución requiere aprobación.
- Medición posterior del pronóstico frente al resultado real, con error y sesgo por horizonte/segmento.


**Objetivo:** transformar datos correctos en decisiones sin inventar costos o conclusiones.

Orden de construcción:

1. Cierre diario: ventas netas, tickets, ticket promedio, descuentos, devoluciones, pagos y caja.
2. Ventas: artículo, variante, marca, categoría, cajero, cliente, sucursal, canal y área.
3. Inventario: disponible, reservado, en tránsito, rotación, cobertura, quiebres, excedentes, antigüedad y vencimientos.
4. Costos y margen: costo vendido, margen bruto, contribución neta de comisiones, embalaje y logística, precio de reposición y GMROI.
5. Compras y proveedores: cumplimiento, plazos, costos, diferencias y propuesta de reposición.
6. Finanzas: cuentas por cobrar/pagar, mora, caja, bancos, flujo y estados contables.
7. Rentabilidad por área y consolidado: minorista, ecommerce, mayorista/distribución y servicios.
8. Perfil 360 por cliente: RFM, retención, marcas/productos preferidos, contribución y acciones sugeridas; exportar datos fuente y explicar cada segmento.

Primero usar los reportes nativos del ERP y validar su costo/ledger contra movimientos. Para proyecciones, probar StatsForecast como primera biblioteca de modelos estadísticos; MLForecast queda condicionado a datos exógenos e historial suficientes, y HierarchicalForecast para una etapa posterior cuando haya que reconciliar SKU/familia/marca/categoría/sucursal/canal. DemandSense se inspecciona como referencia MIT de demanda intermitente, backtesting y escenarios, pero su madurez es baja; DemandOS queda como referencia para inspección: la ausencia de licencia no concede permiso para copiar o modificar su código; reproducir ideas de forma independiente o pedir autorización. Para el análisis local, probar DuckDB sobre snapshots/Parquet canónicos y elegir como máximo una herramienta BI posterior (Metabase o Superset) si existe una necesidad multiusuario. La comparación de primera/segunda marca se implementa con reglas y métricas propias de Rubrova: no se sustituye por ABC ni por notebooks exploratorios. Ninguna herramienta analítica escribe en ventas, pagos, inventario o contabilidad. El detalle de licencias, decisiones y pruebas está en [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md).

**Criterio de salida:** las métricas cuadran con los movimientos originales, muestran fórmula/fuente/filtros/actualización y declaran costos o datos faltantes. Los reportes no bloquean la caja. La inteligencia comercial demuestra backtesting, análisis ajustado por disponibilidad, tableros de rentabilidad y participación de marcas, y perfil 360 reproducible por cliente; las recomendaciones declaran confianza y no ejecutan compras/precios automáticamente.

## Fase 5 — perfiles sectoriales y capacidades de expansión

- Gastronomía, panadería y rotisería: recetas, BOM, rendimiento, merma, tandas de producción, comandas, cocina, pesables y vencimientos.
- Mayorista/distribución: mínimos, múltiplos, escalas, listas por cliente, crédito, entregas parciales y costo de servir.
- Servicios B2B: contratos, recurrencias, agenda, SLA, órdenes de trabajo, técnicos, horas, materiales, viáticos y rentabilidad.
- Varias áreas: permisos, recursos y resultados separados; consolidado sin ingresos internos ficticios.

**Criterio de salida:** perfiles que reutilizan los mismos maestros y servicios, sin duplicar clientes, ventas, inventario ni reglas contables.

## Fase 6 — canales e integraciones comerciales

- Ecommerce, pedidos por WhatsApp, Mercado Libre, delivery y otros canales reales.
- Integrar un canal por vez; probar pedidos, cancelaciones, pagos, comisiones y devoluciones.
- Webhooks firmados, idempotencia, estados externos, conciliación y prevención de doble factura/sobreventa.
- Spree o Saleor sólo como posible canal ecommerce, nunca como ERP/POS paralelo.
- PowerSync sólo si una prueba demuestra valor para lecturas/tareas offline; no coordina la última unidad de stock.

**Criterio de salida:** cada pedido externo se reconcilia con venta, pago, inventario y fiscalidad sin duplicados.

## Fase 7 — logística avanzada

El modelo de fulfillment y la posibilidad de agregar una guía después de vender existen desde el diseño inicial. La construcción de integraciones se posterga:

1. Retiro por cliente y entrega/reparto propio.
2. Carga manual de operador, guía, paquete y eventos.
3. Andreani, Correo Argentino PAQ.AR y OCA con credenciales de QA.
4. Vía Cargo como tracking externo mientras no haya API de booking verificada.
5. Agregadores, cotización, etiquetas, manifiestos, reclamos y analítica logística.
6. Kangu sólo si se confirma operación argentina.

**Criterio de salida:** los transportistas no controlan venta, pago ni stock maestro; cada envío conserva su vínculo con el pedido y su trazabilidad.

## Calidad transversal y definición de terminado

Todas las fases deben pasar las pruebas que correspondan:

- POS: rapidez, accesibilidad, teclado, lector, pantalla táctil, carrito editable, devoluciones y permisos.
- Integridad: idempotencia, CAS para stock, caja reconciliada y ausencia de doble emisión.
- Resiliencia: corte de red, terminación abrupta del proceso, reintentos, broker caído, restore y rollback.
- Seguridad: permisos en servidor, aislamiento por negocio/sucursal, gestión de secretos y auditoría.
- Datos: importación validada, fórmulas trazables, moneda/redondeos y costo explícito.
- Operación: instalación local, actualización, documentación en español y recuperación guiada por una persona autorizada después de reinstalar Windows o cambiar la PC.
- Reutilización: versión/commit, licencia por archivo/dependencia, avisos, pruebas y costo de mantenimiento.

Ninguna capacidad se marca terminada porque exista una pantalla, documentación o demo. Se requiere evidencia reproducible.

## Entregables de investigación ya completados

- [x] Catálogo de código reutilizable y estrategia reuse-first.
- [x] Requisitos POS, checkout, efectivo, vuelto, pagos mixtos y terminales.
- [x] Modelo de dominio que separa venta, pago, stock, comprobante y envío.
- [x] Arquitectura de servicios de dominio, APIs/eventos, ownership, idempotencia, CAS, Outbox/Inbox y recuperación.
- [x] Dataset de evaluación y validador automático: 34/34 pruebas de fixture aprobadas en CI (20/11/2026).
- [x] Benchmark mensual de demanda regular e intermitente con StatsForecast 2.1.1 y baselines; CI aprobado sobre 48 meses sintéticos por serie (20/11/2026).
- [x] Primer experimento aislado de demanda censurada por stockout: ajuste conservador por días disponibles, fixture de 36 meses, umbrales explícitos, cobertura/exclusiones y 9/9 pruebas en CI (25/11/2026); no usa datos reales ni escribe en el POS/ERP.
- [x] Investigación de ERPNext, MyCompany/lsFusion, Tryton, Dolibarr y Posnic.
- [x] Revisión de la localización argentina Odoo y de tryton-ar; se encontraron ocho ramas coordinadas 8.0 con manifiestos y tests; instalación y homologación pendientes.
- [x] Shortlist de componentes para fiscalidad, importación, hardware, analítica, producción, ecommerce, backup y logística.
- [x] Requisitos de reportes, métricas y rentabilidad por área.
- [x] Diseño detallado de demanda, pronósticos, rentabilidad y análisis de primeras/segundas marcas con herramientas y licencias candidatas registradas.
- [x] Especificación de captura temporal para canales, formatos, compras, recepción, disponibilidad, pagos, caja, cajeros, promociones, reclamos y devoluciones.
- [x] Matriz de exportación portable e investigación de DuckDB, Parquet/Arrow, Polars, dbt Core, Evidence, Superset y Metabase.
- [x] Diseño de identidad de pagos por canal, conciliación y límites de uso de datos de pagador; shortlist de SDK/API de Mercado Pago, Payway, Getnet, MODO y Fiserv.
- [x] Evaluación de S-Tech como proveedor potencial de terminales, efectivo inteligente y autoservicio.

## Próximos pasos concretos

1. Ejecutar el filtro comparativo POS + ERPNext 16 y MyCompany 6.2 con el mismo dataset y circuito.
2. Ejecutar Tryton 8.0 en paralelo con las ramas argentinas 8.0; instalar el conjunto, ejecutar tests y homologar. Tryton 8.2 se evalúa como actualización posterior.
3. Pasar Dolibarr 24.0.3 por el filtro corto y llevar como máximo dos finalistas a P01–P67.
4. Resolver las puertas de licencia, API, localización argentina, exportación, backup/restore y límite de dominio. P49 añade la comprobación de historial comercial; P50–P57 validan temporalidad, caja, promociones, reclamos y exportaciones; P58–P60 validan el perfil 360; P61–P67 validan identidad de pagos, conciliación, privacidad, PCI e integraciones.
5. Elegir la base del primer circuito y recién entonces implementar/adaptar las brechas concretas.
6. Extender el experimento inicial de quiebres de stock —ya incorporado con datos sintéticos— con promociones, cambios de precio, productos nuevos, granularidad diaria/horaria y más horizontes. Después preparar una entrada de datos reales conciliados una vez elegida la plataforma POS/ERP. Evaluar MLForecast y HierarchicalForecast sólo después de medir la mejora frente a baselines.

El requisito de copia portable y recuperación en PC nueva está en [Copias de seguridad y recuperación](BACKUP_AND_MIGRATION_STRATEGY.md). El backup de aplicación será portable y sin cifrado propio; se valida mediante checksums, reconciliación y restauración en PC nueva. El cifrado del disco completo puede habilitarse opcionalmente desde el sistema operativo.

La captura desde el primer día, los escenarios P50–P57 y la capa de BI/exportación se especifican en [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md). El Perfil 360 y las pruebas P58–P60 quedan en [Perfil 360 e inteligencia por cliente](CUSTOMER_360_AND_INTELLIGENCE.md). La comparación de alternativas de mercado se documenta en [Revisión competitiva](COMPETITIVE_MARKET_REVIEW.md). La arquitectura de terminales, sus tres modos, contratos y entidades está en [Arquitectura de terminales de pago](PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md); la identidad y el tratamiento de datos de pagador está en [Identidad del pagador y conciliación](PAYMENT_IDENTITY_AND_RECONCILIATION.md). S-Tech queda como proveedor complementario a evaluar en [S-Tech para Rubrova](S_TECH_EVALUATION.md), no como núcleo POS+ERP.

La [investigación logística argentina](ARGENTINA_LOGISTICS_INTEGRATION.md) se conserva, pero no desplaza estos pasos ni condiciona el inicio del producto.


## Anexo I — Estado previo, preservado

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Corte:** 26 de noviembre de 2026, 16:16 UTC  
**Rama canónica:** `main`  
**Commit integrado:** [`ac758d0`](https://github.com/JavierGrecco/Rubrova/commit/ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a)  
**Estado GitHub:** una única rama visible (`main`), cero pull requests abiertos. La rama no está protegida por ruleset de GitHub.

## Resumen ejecutivo

Rubrova dispone de un runtime propio de MyCompany 6.2 + lsFusion 6.2, compilado desde fuentes fijadas en el repositorio. El workflow [Validación del arranque de plataforma #417](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó correctamente e incluyó un smoke nativo macOS ARM64 sin Docker. La prueba pasó de inicio/login a venta, conciliación, cierre, reinicio y restauración lógica de PostgreSQL en una base nueva.

Esto habilita una siguiente etapa de ingeniería funcional sobre una base reproducible. **No significa que Rubrova esté listo para operación diaria ni producción.** Los datos del smoke son sintéticos, la exportación de reposición aún no se ha conciliado con una base comercial real y no se ha probado el runtime en el Mac físico del usuario.

## Última validación de plataforma

[Run 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565), SHA `ac758d01`, terminó con `success`.

| Trabajo | Resultado | Alcance real |
|---|---|---|
| Prevalidación local compartida | Aprobado | Suites Node/Python, contratos, scripts, configuración, listener y tests del backup |
| Validación Windows | Aprobado parcialmente | Sintaxis PowerShell; no instalación ni smoke funcional de Windows |
| Compilación del fork | Aprobado | Servidor lsFusion, cliente GWT y lógica MyCompany desde fuentes Rubrova |
| Smoke macOS ARM64 nativo | Aprobado | Java 21 ARM64, PostgreSQL 18, lsFusion/MyCompany, Tomcat y Chromium; sin Docker |
| Diagnóstico Linux nativo | Omitido | `skipped`; no es aprobación |
| Diagnóstico Docker/Linux | Omitido | `skipped`; no es aprobación |

La suite del planificador también aprobó en [run 45854940442](https://github.com/JavierGrecco/Rubrova/actions/runs/45854940442), sobre el commit anterior `c0dacb7`; el commit final `ac758d0` sólo corrigió el simulador de fallo de restauración.

## Evidencia funcional del smoke nativo

La ejecución [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) registró:

- Login autenticado con Chromium y navegación a Comercio → Punto de venta.
- Sondas autenticadas de inventario, compromisos de salida y recepciones con HTTP 200.
- Exportación nativa de sólo lectura, con colecciones verificadas contra fixtures sintéticas; no es aún conciliación con una base comercial real.
- Venta sintética de ARS 1.250, factura y pago en efectivo exacto; el inventario pasó de 10 a 9 unidades.
- Cierre del turno `SM/000001`, estado `CLOSED`, neto y efectivo de ARS 1.250.
- Reinicio de PostgreSQL/servidor/cliente y verificación de persistencia de factura, pago, stock, turno cerrado e incidencias.
- Segunda instancia Demo con configuración, puertos y base separada; abrió turno y encontró el artículo de muestra.
- Creación de respaldo lógico PostgreSQL; paquete y SHA-256 verificados; restauración a `rubrova_restore_ci`; la base activa `rubrova_dev` no se sobrescribió.
- Marcador de aceptación: `RUBROVA_NATIVE_POSTGRES_BACKUP_RESTORE=passed`.

El backup es **sólo PostgreSQL**. No incluye adjuntos, documentos externos, imágenes, binarios ni secretos. Tampoco existe todavía un asistente visual de restauración.

La ejecución usó `RUBROVA_NATIVE_EGRESS_BLOCKED=false` y dejó `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. No se certifica aún continuidad offline en macOS.

## Estado por capacidad

| Capacidad | Estado | Límite pendiente |
|---|---|---|
| Fuentes propias fijadas y compilación | Aprobado en CI | Mantener locks y revisión upstream |
| Runtime nativo macOS ARM64 | Smoke aprobado en runner | Ejecutar en el Mac físico |
| Login, navegación y POS básico | Aprobado con fixture sintético | No equivale a una jornada real |
| Venta, factura, pago y stock | Aprobado | Vuelto, medios mixtos, descuentos complejos y cancelaciones |
| Cierre básico de turno | Aprobado | Arqueo físico, diferencias e ingresos/retiros end-to-end |
| Persistencia tras reinicio | Aprobado | Recuperación integral y rollback |
| Exportación de reposición | API y fixtures aprobadas | Conciliar con base MyCompany local real |
| Planificador | Suite aprobada | Datos reales, cobertura y desempeño fuera de muestra |
| Backup lógico PostgreSQL | Creación, verificación y restore a nueva DB aprobados | Adjuntos, documentos, retención, disco externo y asistente |
| Devolución y reintegro | Componentes upstream existentes identificados | Activación del control de cantidad y recorrido E2E |
| Terminales de pago | Modelo y trazabilidad inicial | Proveedor, sandbox, hardware y homologación |
| ARCA/fiscalidad | Diseño e investigación | Integración y homologación |
| Offline macOS | Pendiente | Repetir con egress bloqueado |
| Windows nativo | Parcial | Instalación, operación, reinicio y persistencia funcional |
| Linux/Docker en último push | Omitido | Diagnóstico manual separado |
| Instalador y periféricos | Pendiente | PC limpia, lector, impresora, cajón, balanza y terminal |
| Uso productivo | No autorizado | Jornada supervisada, recuperación externa y homologación |

## Arquitectura y propiedad

- `vendor/platform/`: fuentes fijadas de lsFusion 6.2.
- `vendor/mycompany/`: fuentes fijadas de MyCompany 6.2.
- `extensions/lsfusion/`: módulos Rubrova y localización propia.
- `patches/lsfusion/`: cambios directos al motor sólo cuando una extensión no alcanza.
- `build/rubrova/pom.xml`: reactor de compilación propio.
- Runtime local prioritario: Java 21 + PostgreSQL 18 + Tomcat 9, sin Docker como requisito de ejecución.

La reposición es estrictamente de lectura: no ejecuta `fillAuto`, no crea órdenes ni altera inventario. Devoluciones, pagos y caja deben seguir usando los ledgers de MyCompany; Rubrova no debe introducir un segundo registro de existencias o efectivo.

## Próximas prioridades

1. **Devolución segura:** activar y probar el control de cantidad retornada contra la factura original; validar devolución parcial/total, reintegro al medio original y stock restaurado sin duplicaciones.
2. **Caja completa:** probar ingreso/retiro nativos, saldo teórico por medio y arqueo físico con diferencia registrada, responsable y hora.
3. **Prueba local en el Mac físico:** ejecutar preflight, doctor, arranque, venta, backup, restore y revisión de logs con Java 21 y PostgreSQL 18 ARM64.
4. **Continuidad offline macOS:** repetir el smoke con salida externa bloqueada y recuperación de integraciones pendientes.
5. **Windows x64:** instalación y smoke nativos completos.
6. **Backup integral:** adjuntos, documentos, manifiesto, checksums, retención, copia externa desconectable y restauración guiada en otro equipo.
7. **Reposición real:** capturar exportación autenticada de una base MyCompany local y conciliarla con sus ledgers antes de sugerir compras con datos reales.

## Protección de la rama principal

GitHub informa `protected: false` para `main`. No se debe confundir tener una sola rama con tener protección obligatoria. La protección debe activarse desde GitHub Settings con un ruleset que requiera los workflows aplicables, impida force-push y defina quién puede integrar. No se declara habilitada hasta verificarla.

## Límites de aceptación

No habilitar uso productivo hasta demostrar una jornada repetible con venta, devolución, pago/reintegro, caja, arqueo físico, stock, documentos fiscales, auditoría, modo offline, copia externa y restauración. Ningún smoke sintético sustituye esa aceptación.


## Anexo J — Plan maestro previo, preservado

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

**Revisión:** 26 de noviembre de 2026  
**Base técnica:** MyCompany 6.2 + lsFusion 6.2, con fuentes completas fijadas en el repositorio; Tryton 8.0 + tryton-ar 8.0 se conserva como contraste fiscal argentino, no como segundo núcleo operativo.

**Estado real:** el fork compila servidor, cliente GWT y lógica desde fuentes propias. El workflow [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó con `success` en el SHA `ac758d01`: preflight, compilación y smoke nativo macOS ARM64 aprobados. El POS básico sintético, persistencia tras reinicio, exportación de reposición contra fixtures y backup/restore PostgreSQL a una base nueva fueron verificados. No existe aceptación productiva.

**Hito activo:** consolidar el circuito comercial y su recuperación. El backup lógico PostgreSQL ya restaura a una base nueva sin sobrescribir la activa, pero aún no incluye adjuntos/documentos ni tiene asistente guiado. El puente de reposición sigue siendo sólo lectura y falta conciliarlo con una base MyCompany real. El siguiente bloque funcional reutiliza los módulos nativos de devolución/reintegro y caja de MyCompany, comenzando por activar y probar el límite de cantidad devuelta contra la factura original.

**Límites pendientes:** devoluciones/reintegros E2E, arqueo físico y diferencias de caja, ingresos/retiros probados, vuelto y pagos mixtos, ARCA/adquirentes reales, exportación conciliada con base real, offline macOS, Mac físico, Windows nativo, instalación limpia y backup portable completo.

## 1. Decisión ejecutiva

Rubrova no se debe desarrollar alrededor del seguimiento de envíos ni como una colección de integraciones. El centro es la **operación y gestión del negocio**.

La experiencia empieza en el POS, pero el POS tiene que usar desde el primer día datos y reglas del sistema de gestión: catálogo, precios, clientes, stock, pagos, caja, devoluciones y estado fiscal. Después se completa el ERP administrativo, se consolida contabilidad y costos, y recién entonces se construyen los análisis de gestión con resultados confiables.

La secuencia aprobada para dirigir el trabajo es:

1. **Operación comercial y POS:** vender, cobrar, devolver, abrir/cerrar caja y dejar el stock correcto.
2. **ERP de gestión:** productos, clientes, proveedores, compras, recepción, inventario, costos, cuentas corrientes, depósitos y sucursales.
3. **Contabilidad y fiscalidad argentina:** libro contable, impuestos, ARCA, comprobantes, conciliación, bancos, cuentas por cobrar/pagar y cierres.
4. **Reportes y control de gestión:** ventas, costos, márgenes y rentabilidad por producto/marca/canal/área/cliente; ficha 360, RFM, retención, compras, stock, caja y finanzas.
5. **Capacidades sectoriales y crecimiento:** producción, recetas, lotes, vencimientos, mayorista, distribución, servicios B2B y contratos.
6. **Canales externos:** ecommerce, Mercado Libre, WhatsApp, delivery y otras fuentes de pedidos.
7. **Logística avanzada:** fulfillment, agregadores, transportistas, etiquetas y seguimiento unificado.

No significa postergar toda la administración hasta terminar el POS: las dimensiones de negocio, centros de costo, sucursal, canal, cliente, depósito, trazabilidad y reglas de precios deben estar en el modelo inicial. Lo que se posterga es la profundidad funcional de cada área, no los cimientos que después serían caros de corregir.


### Decisión técnica para comenzar (20/11/2026)

El primer piloto será MyCompany 6.2: su código ya contiene Retail POS, sesiones, pagos mixtos, devoluciones, inventario, costos, compras y facturación dentro de una suite integrada. El tag y commit están fijados en el lock de plataforma. La suite comparte servidor y base, por lo que se evaluará como una aplicación integrada, no como microservicios.

Tryton 8.0 con el conjunto argentino fijado se mantiene como contraste para fiscalidad, comprobantes y recuperación. ERPNext 16 queda en reserva; no se mantendrán tres implementaciones activas en paralelo. La extensión Rubrova se carga por encima de MyCompany y los árboles fuente completos están vendorizados. CI ya probó venta en efectivo, factura/pago persistidos, salida de stock y cierre básico en la instancia efímera. La localización sigue en ampliación y debe superar el smoke actualizado; todavía faltan devoluciones, pagos mixtos/vuelto, ARCA, hardware, modo offline, persistencia tras reinicio, exportación y restauración en una instalación de uso. El plan detallado está en [Inicio de implementación](IMPLEMENTATION_START.md).

## 2. Qué tiene que ser la primera entrega

La primera entrega no es una demo de caja ni un CRUD de artículos. Es un **circuito comercial completo y repetible**, inicialmente en una sucursal y con datos sintéticos:

1. Alta/importación de un producto con código de barras, unidad, variante y precio.
2. Consulta del artículo por código o búsqueda desde el POS.
3. Carrito editable: agregar, quitar y cambiar cantidades antes de iniciar el cobro.
4. Recalcular descuentos, promociones, impuestos y total sin modificar ventas anteriores.
5. Asociar un cliente cuando corresponda, sin forzar una ficha para cada consumidor de mostrador.
6. Comprobar disponibilidad y reservar o confirmar el movimiento de stock con la autoridad del inventario.
7. Cobrar en efectivo, calcular vuelto exacto y admitir más de un medio de pago.
8. Confirmar el turno de caja, el movimiento de efectivo y el resultado de cada pago.
9. Registrar la venta y conservar ticket, voucher y documento fiscal como documentos diferentes.
   - Política de impresión: efectivo y transferencia verificada en impresora térmica de caja; QR/tarjeta preferentemente en terminal inteligente con ticket detallado generado por Rubrova y voucher; impresora de caja como respaldo si el modelo no admite impresión personalizada. Evitar duplicados y permitir reimpresión auditada.
10. Cerrar o reiniciar el POS/servicio y demostrar que la operación confirmada no se pierde ni se duplica.
11. Devolver parcial o totalmente una venta, vinculando la operación original y dejando los movimientos compensatorios.
12. Consultar un cierre básico: ventas netas, devoluciones, medios de pago, efectivo esperado, diferencia de caja y unidades vendidas.
13. Crear una copia portable verificable, sin cifrado propio de Rubrova, y restaurarla en una instalación Windows limpia o en una PC de reemplazo, verificando ventas, pagos, caja, stock, costos, documentos y auditoría antes de habilitar el uso.

**Para dar por terminada esta entrega:** cada total debe poder reproducirse; ventas, pagos, caja, inventario y fiscalidad deben conciliar; los errores y estados pendientes deben ser visibles; y la caja debe poder usarse con teclado, lector y pantalla táctil. No se declara una venta cobrada porque el POS haya mostrado una pantalla de éxito o porque el cliente presente una captura.

## 3. Fundaciones que se incorporan desde el primer día

Aunque se implementen progresivamente, estas dimensiones deben existir desde el comienzo para evitar migraciones destructivas:

- Organización y entidad legal; sucursal, caja, depósito, ubicación, usuario, rol y dispositivo.
- Producto/servicio, variante, código, unidad de medida, conversión, precio, costo, impuesto y proveedor.
- Marca y segmento comercial configurable por categoría (primera/líder, segunda, económica, propia o alternativa), unidad comparable, historial de precios/costos y vigencias.
- Historial de disponibilidad y quiebres de stock, cambios de surtido, promociones y períodos sin operación para distinguir demanda observada de demanda censurada.
- Cliente y proveedor; persona/empresa, CUIT cuando corresponda, condiciones comerciales, crédito y cuenta corriente.
- Unidad de negocio, canal, sucursal, centro de costo y proyecto como dimensiones distintas.
- Pedido, venta, pago, movimiento de stock, sesión de caja, comprobante fiscal y despacho como hechos distintos.
- Identificador externo, correlation ID, clave de idempotencia, auditoría y estado de sincronización.
- Tiempos de ocurrencia, registro y vigencia; historial de precio, marca/segmento, presentación, disponibilidad y costo; snapshots por línea; detalle de cajero/turno/caja, intentos y liquidaciones de pago, promociones, reclamos y devoluciones.
- Una clasificación separada de área, canal, formato sectorial, sucursal, depósito y método de cumplimiento. La matriz detallada de captura está en [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md).
- Política de respaldo desde el primer uso: copia completa portable, puntos incrementales, documentos/adjuntos, configuraciones y auditoría; secretos excluidos del paquete y re-vinculados por separado; restauración a equipo limpio.
- Fecha/hora, moneda, tipo de cambio, política de redondeo y fotografía de las condiciones aplicadas a la operación.

Una venta puede incluir líneas de áreas diferentes. La dimensión económica debe guardarse a nivel de línea cuando corresponda; el consolidado no debe duplicar ingresos, stock ni costos internos.

## 4. Arquitectura objetivo y límites de reutilización

Rubrova debe ser una **composición de módulos y servicios de dominio con responsabilidades reales**, no una aplicación propia gigante ni un conjunto de microservicios diminutos.

Los límites que se deben respetar son:

| Dominio | Qué posee | Prioridad de construcción |
|---|---|---|
| Identidad y organización | Usuarios, roles, permisos, entidades, sucursales, cajas y dispositivos | Fundación |
| Catálogo y precios | Productos, variantes, códigos, unidades, listas, reglas y vigencias | Fundación |
| Clientes y proveedores | Maestros, contactos, condiciones, crédito y cuentas de relación | Inicial |
| POS, pedidos y ventas | Carrito, pedido, venta, devoluciones, estados comerciales y ticket | Primera entrega |
| Inventario y almacenes | Ledger de stock, reservas, ubicaciones, lotes, conteos y disponibilidad | Primera entrega |
| Pagos y caja | Intentos, asignaciones, efectivo, vuelto, turnos, arqueos, reembolsos y liquidaciones | Primera entrega |
| Compras y abastecimiento | Órdenes, recepción, costos de compra, proveedores y reposición | Segunda entrega |
| Contabilidad y fiscal | Asientos, períodos, cuentas, impuestos, ARCA, comprobantes y conciliación | Segunda entrega; homologación antes de operar fiscalmente |
| Inteligencia y reportes | Métricas, proyecciones de lectura, dashboards y pronósticos | Reportes básicos iniciales; BI avanzado después de validar costos |
| Producción y servicios | Recetas/BOM, órdenes, consumos, rendimiento, mermas, contratos y SLA | Expansión sectorial |
| Canales e integraciones | Adaptadores, webhooks, importación/exportación y bandejas Inbox/Outbox | Según necesidad; ecommerce después del núcleo |
| Logística y fulfillment | Preparación, bultos, entrega, booking, guías, operadores y tracking | Modelo básico temprano; conectores y tracking al final |

Los servicios propios de Rubrova se comunican por API/eventos versionados, tienen datos y credenciales propios y se pueden desplegar/actualizar/recuperar sin actualizar todo Rubrova. Una suite integrada elegida como núcleo mantiene sus módulos internos dentro de su límite de aplicación y se consume sólo mediante interfaces soportadas; no se simula una independencia que no existe ni se permite acceso SQL cruzado desde otros módulos.

**No se exige un proceso por cada tabla o pantalla.** Se definen límites por consistencia y propiedad del dato. Las operaciones que deben ser inmediatas (por ejemplo, confirmar una reserva de stock) se resuelven en el servicio propietario. Las tareas asíncronas se implementan con Outbox/Inbox, mensajes durables e idempotencia. El número de tecnologías se mantiene pequeño.

Un ERP existente puede evaluarse como núcleo operativo integrado. Sus módulos internos no se describen como microservicios si comparten servidor, base o migraciones. Puede adoptarse si el conjunto completo forma una unidad operativa útil, es la autoridad única de los dominios que cubre y supera las puertas de uso, extensión, exportación, backup/restore, seguridad y actualización. Los componentes de Rubrova que queden fuera se aíslan por contratos y no duplican los datos del núcleo.

**Regla para elegir entre una suite integrada y servicios independientes:** una base POS+ERP existente puede adoptarse como **núcleo operativo integrado** aunque sus módulos compartan servidor, base de datos o ciclo de actualización. Esa integración no se llamará microservicios. Para nuestro uso privado local puede ser la opción más segura y eficiente si completa bien el circuito, mantiene una única autoridad para ventas, pagos/caja, inventario, compras, costos y contabilidad, tiene extensiones/API soportadas, exportación íntegra, backup y restauración en otro equipo, permisos auditables y una ruta de actualización razonable. La base compartida se registra como trade-off de acoplamiento y actualización, no como rechazo automático. Los servicios propios de Rubrova se separan sólo cuando exista una necesidad probada (por ejemplo, analítica de lectura, adaptadores o logística) y consumen contratos/exportaciones soportados; nunca replican el ledger ni escriben en tablas privadas. Se descarta la suite si no permite recuperar/exportar los datos, obliga a mantener autoridades duplicadas, requiere cambios inseguros del núcleo, impide controles críticos o no supera los escenarios operativos.


### Composición de referencia para las brechas que Rubrova deba desarrollar

La siguiente tabla expresa límites lógicos y posibles unidades propias de Rubrova; **no obliga a dividir en procesos separados una suite POS+ERP que se elija como núcleo integrado**. Si el candidato resuelve ventas, inventario, compras, pagos/caja y contabilidad dentro de una aplicación, esa aplicación será la autoridad de esos dominios. Sólo se extraerá un servicio cuando exista una razón operativa y una API/contrato estable. La prioridad es una instalación local recuperable y coherente, no multiplicar procesos.

| Unidad desplegable | Autoridad | Incluye al inicio |
|---|---|---|
| Gateway local | Entrada y enrutamiento, sin ser dueño de ventas/stock/dinero | Autenticación de dispositivo, routing, permisos de acceso, rate limits y correlation ID |
| Identidad y organización | Usuarios, roles, entidad, sucursal, caja, depósito y dispositivos | Administración básica de usuarios y contexto operativo |
| Catálogo y precios | Artículos, variantes, códigos, unidades, listas y reglas vigentes | Importación básica, búsqueda y snapshot de precios |
| POS / Ventas | Carrito, pedido, venta, líneas, descuentos y devoluciones | Interfaz de caja y estados comerciales |
| Inventario | Ledger, reservas, disponibilidad, movimientos y conteos | Reserva atómica, salida de venta y devolución |
| Pagos y Caja | Intentos de pago, medios, efectivo, vuelto, turnos, arqueos y reembolsos | Efectivo, medios manuales y un adaptador de terminal sólo cuando esté probado |
| Fiscal | Numeración fiscal, comprobantes, ARCA, notas y estados inciertos | Contrato y homologación; no se considera productivo hasta superar las pruebas fiscales |

Clientes/proveedores pueden comenzar dentro de una unidad de Maestros/Relaciones si la plataforma elegida lo exige; deben conservar identificadores y contratos propios para separarlos después sin migración destructiva. Compras, contabilidad general y BI se incorporan en las siguientes entregas, sin crear procesos vacíos sólo para completar un diagrama.

**Flujo coordinado de una venta:**

1. El POS consulta Catálogo/Precios y conserva la fotografía de artículo, precio, impuesto y promoción aplicada.
2. Ventas registra un carrito/operación con clave idempotente y solicita a Inventario una reserva con cantidad y versión esperada.
3. Si la reserva no se confirma, el checkout ofrece alternativas; no inicia el cobro por una unidad no reservada según la política.
4. Pagos procesa cada medio. Una respuesta incierta queda pendiente de consulta/conciliación y no permite enviar otro cobro a ciegas.
5. Cuando se cumplen las reglas comerciales y de pago, Ventas confirma la operación; Inventario transforma la reserva en movimiento definitivo mediante una operación idempotente.
6. Fiscal recibe el evento y emite/consulta el comprobante según la obligación fiscal; un fallo de ARCA no borra la venta ni genera doble factura.
7. Caja cierra el turno con cobros, vuelto, retiros, ajustes autorizados y diferencias conciliadas.

Cada unidad tiene almacenamiento y migraciones propios. En instalaciones pequeñas se pueden co-alojar en una misma máquina/instancia física, pero con bases o esquemas, roles, credenciales y despliegues separados. La comunicación es por APIs versionadas y eventos Outbox/Inbox, no por SQL cruzado.



## 5. Selección de plataformas: qué probar y qué no asumir

Las plataformas se comparan por el circuito POS + gestión que realmente necesitamos, no por la cantidad de módulos de su página de inicio. La prueba debe medir instalación, caja, inventario, reportes, localización argentina, APIs, extensión, portabilidad, recuperación, experiencia y costo de mantenimiento.

### Candidatos de primera evaluación

| Candidato | Por qué merece prueba | Riesgo/condición | Prioridad |
|---|---|---|---|
| **ERPNext 16 / Frappe 16** | Cobertura amplia de ERP, compras, inventario, manufactura, contabilidad, dimensiones y POS con perfiles, depósitos, impuestos y pagos | El POS debe medirse con una jornada real y hardware; stack y operación más pesados; localización argentina y adaptación fiscal deben probarse. Sus apps comparten el site/bench y persistencia: no equivale a microservicios. | Primera ronda |
| **MyCompany 6.2 / lsFusion** | Cobertura integrada de Retail POS, ventas, CRM, compras, inventario, fabricación, facturación y RR. HH.; módulos extensibles | Todos los módulos de una instalación comparten base. Verificar API, usabilidad real de caja, Argentina/ARCA, instalación y recuperación. No considerarlo arquitectura distribuida por ser modular. | Primera ronda |
| **Tryton 8.0 + tryton-ar 8.0** | ERP/POS con PostgreSQL; la localización cubre plan contable, CUIT/padrón, facturación WSFE/WSFEX, bancos, vouchers, cheques y reportes | Hay ocho ramas argentinas coordinadas con manifiestos 8.0.0/8.0.1 y tests. `sale_point` 8.0 cubre la operación minorista. Los módulos comparten servidor/base; no son microservicios independientes. Tryton 8.2 queda como actualización posterior, condicionada al port. | Primera ronda condicionada a instalación y pruebas |
| **Dolibarr 24.0.3** | CRM/ERP, API REST, hooks y triggers; TakePOS y módulos extensibles; posible camino de instalación más sencillo | Medir profundidad del POS, gestión de costos, producción y la localización argentina. Sus módulos también comparten una aplicación/base. | Filtro corto / alternativa |
| **Posnic 1.9.2** | POS dedicado, ventas, compras, clientes, caja, catálogo e inventario | No cubre el ERP integral; revisar AGPL, MongoDB SSPL y componente comercial de gráficos; orientado a reglas fiscales de India, no Argentina; su prueba offline pública es limitada y el paquete macOS no está resuelto. | Referencia POS, no base principal |

No se declara un ganador antes de instalar y recorrer la misma prueba. El filtro documental reduce candidatos; las pruebas reproducibles deciden.

### Hallazgos específicos que cambian la evaluación

- **ERPNext:** su POS Profile configura empresa, depósito, medios de pago, lista de precios, impuestos y cuentas. Su POS puede actualizar stock y alimentar contabilidad, admite varios medios de pago y ofrece reportes/dimensiones. Esto lo hace un candidato fuerte para demostrar rápido el circuito completo; no prueba por sí solo velocidad, experiencia de caja, terminales ni fiscalidad argentina.
- **MyCompany:** su cobertura funcional es muy amplia y el POS retail forma parte de la distribución. La base compartida es una restricción de arquitectura, no un detalle menor.
- **Tryton:** probar primero la serie 8.0 junto con las ramas argentinas 8.0 coordinadas. El POS oficial `sale_point` cubre ventas minoristas, pagos, vuelto, sesiones y efectos de stock/contabilidad. La localización 8.0 aporta plan contable, CUIT/padrón, WSAA/WSFE, comprobantes, bancos, pagos/cheques y reportes. Tryton 8.2 es más reciente, pero requiere adaptar y revalidar ese conjunto; no actualizar antes de completar una prueba funcional y fiscal en 8.0.
- **ARCA para Tryton:** ver el [lock reproducible del conjunto tryton-ar 8.0](TRYTON_ARGENTINA_8_0_LOCK.md). Incluye `account_invoice_ar` 8.0.1, `account_ar`, `party_ar`, `bank_ar`, vouchers, cheques, reportes y `sale_pos_ar` 8.0.0/8.0.1. `account_invoice_ar` incluye escenarios WSFE, FCE, WSFEX y recuperación; `party_ar` depende de `pyafipws` (LGPL-3). Instalar las ocho ramas juntas, fijar commits, ejecutar sus tests y homologar antes de confiarle emisión. La documentación histórica de instalación contiene referencias antiguas, por lo que mandan los manifiestos, dependencias y pruebas del código 8.0.
- **Odoo argentino:** el addon público l10n_ar cubre la localización contable base; no es el emisor WSFE por sí solo. La documentación menciona l10n_ar_edi, pero su código no apareció en el repositorio Community inspeccionado. El addon comunitario disponible para WSAA/WSFE se declara Beta. OCA l10n-argentina 19.0, al momento de la revisión, no contenía addons instalables.
- **Bigcapital:** conservar como candidato contable especializado sólo si la contabilidad nativa de los finalistas no alcanza. No sumar un segundo libro mayor ni otro inventario.

## 6. Cómo decidir: pruebas comparables y puertas obligatorias

Antes de ejecutar el protocolo completo, hacer un filtro rápido. ERPNext, MyCompany y Tryton 8.0 + tryton-ar 8.0 pasan por el mismo circuito corto; como máximo dos finalistas pasan a la evaluación profunda. Tryton 8.0 debe superar instalación conjunta, tests de los ocho módulos y homologación fiscal.

**Puertas obligatorias** (no compensables con puntaje):
1. Fuente, versión y licencia verificables de todos los componentes necesarios.
2. Instalación reproducible y operación local sin depender de un servicio cloud propietario.
3. Exportación de datos, backup y restauración en una instancia limpia.
4. APIs/contratos o mecanismos soportados; nada de integrarse escribiendo tablas privadas.
5. Una autoridad única por dato; sin duplicar ventas, pagos, stock, comprobantes o ledger.
6. POS completo: carrito editable, venta por código/peso, pagos, vuelto, turnos, devolución y auditoría.
7. Recuperación tras desconexión y terminación abrupta del proceso.
8. Camino argentino concreto: impuestos, CUIT, tipo de comprobante, punto de venta, ARCA/homologación y conciliación.
9. Interfaz en español, permisos por rol y experiencia viable para cajero y administrador.

**Ponderación después de superar las puertas:**

| Criterio | Peso |
|---|---:|
| POS y flujo de ventas/caja: velocidad, facilidad, devoluciones, pagos y hardware | 25% |
| ERP diario: catálogo, clientes/proveedores, compras, stock y costos | 20% |
| Contabilidad, fiscalidad y adaptación argentina | 15% |
| Arquitectura, APIs, extensibilidad y separación de datos | 15% |
| Reportes, dimensiones de negocio y trazabilidad hasta el movimiento | 10% |
| Confiabilidad, offline, backup, restore y actualización | 10% |
| Usabilidad administrativa y mantenimiento de la instalación | 5% |
| **Total** | **100%** |

El puntaje es evidencia de una prueba, no una preferencia subjetiva. Una plataforma que no supere una puerta se descarta para esa responsabilidad aunque tenga buen promedio.

### Circuito común de evaluación

- Catálogo: importación, variantes, códigos, unidad y peso.
- POS: escaneo, búsqueda, carrito editable, descuentos, impuestos, efectivo, vuelto y pago mixto.
- Caja: apertura, fondo inicial, movimientos, arqueo, cierre y diferencia.
- Ventas: contado, cuenta corriente, cancelación, devolución parcial/total y nota de crédito.
- Stock: reserva, salida, devolución, compra, recepción parcial, costo y conteo.
- ERP: proveedor, cliente, lista de precio, crédito, cuenta corriente y permisos.
- Finanzas: diarios, asiento, cuenta por cobrar/pagar, bancos y reportes.
- Argentina: CUIT, condiciones IVA, comprobantes A/B/C/E cuando correspondan y homologación ARCA.
- Robustez: proceso terminado abruptamente, red caída, reintento, webhook duplicado y restauración.
- Gestión: ventas por día/caja/operador/producto/área, stock, costo, margen y conciliación.

Los escenarios P01–P67 existentes siguen vigentes; la prioridad de ejecución se organiza por este circuito, no por el orden numérico ni por la facilidad de una integración.

## 7. Construcción e integración por entregas

### Entrega 0 — Seleccionar el núcleo (ahora)

- Fijar referencias: ERPNext 16, MyCompany 6.2, Tryton 8.0 + ocho módulos tryton-ar 8.0 y Dolibarr 24.0.3. Mantener Tryton 8.2 como objetivo de actualización posterior.
- Preparar laboratorio reproducible para cada candidato, sin datos reales ni credenciales productivas.
- Reutilizar el dataset sintético existente y ampliar los casos POS, inventario, caja y contabilidad.
- Probar ERPNext, MyCompany y Tryton 8.0 + localización argentina alineada con el mismo circuito POS+ERP; usar Dolibarr como filtro de menor complejidad. Sólo dos finalistas pasan a la evaluación profunda.
- Registrar capturas, tiempos, pasos, errores, salida exportada, licencias, hashes y resultados.
- Decidir qué capacidades del núcleo serán plataforma externa encapsulada, qué componentes se integran como servicios independientes y qué brechas requieren código propio.

**Salida:** decisión sustentada sobre el primer núcleo operativo; no se construyen todavía más módulos sobre una plataforma no seleccionada.

### Entrega 1 — POS operativo con el mínimo de gestión real

El primer despliegue implementa el flujo sobre las unidades del apartado anterior. Si un candidato externo cubre una parte completa, se encapsula detrás de su API y se mantiene su propia autoridad; no se convierte su base compartida en una base global de Rubrova.

- Identidad, roles, organización, sucursal, caja y depósito básicos.
- Catálogo, precios, variantes, códigos, unidades y clientes.
- Carrito y checkout de mostrador; efectivo, vuelto y medios mixtos.
- Pagos/caja, turnos, arqueos, devoluciones y anulaciones.
- Inventario con reservas y ledger; compras/recepción inicial para que exista costo de stock.
- Ticket propio, comprobante fiscal por estado separado y auditoría.
- Adaptador inicial para lector/impresora; terminal física sólo después del sandbox del adquirente.
- Panel operativo de cierre, venta neta y conciliación.

**Salida:** una jornada de prueba repetible, sin duplicados ni diferencias inexplicadas, con recuperación probada.

### Entrega 2 — ERP administrativo y control de inventario

- Artículos, listas, proveedores, clientes empresariales, condiciones y cuentas corrientes.
- Solicitud/orden de compra, recepción total/parcial, devoluciones a proveedor y costos accesorios.
- Múltiples depósitos, transferencias, conteos, ajustes autorizados, lotes y vencimientos según perfil.
- Métodos de valuación de inventario y costo histórico/reposición.
- Presupuestos, límites de crédito, aprobaciones, documentos y vencimientos.
- Importación masiva y validación de datos, sin fusionar automáticamente coincidencias dudosas.

**Salida:** compras, recepciones, stock, costo y ventas reconcilian; los reportes pueden explicar de dónde viene cada saldo.

### Entrega 3 — Contabilidad y Argentina

- Libro mayor y submayores; cuentas por cobrar/pagar; bancos y conciliaciones.
- Períodos, cierre, centros de costo y dimensiones por unidad de negocio, sucursal y canal.
- Impuestos, tipos de comprobante, numeración y punto de venta.
- ARCA en homologación con consulta/recuperación ante timeout y estados inciertos.
- Facturas, notas de crédito/débito, pagos, retenciones/percepciones según la operatoria real.
- Exportación al estudio/ERP que se use (Tango, Catedral, Bejerman, Xubio, Colppy u otros), con lotes idempotentes y conciliación.

**Salida:** ventas, stock, pagos, impuestos y ledger cuadran; no hay doble emisión ni asientos sin origen.

### Entrega 4 — Reportes de gestión y analítica

Primero usar los reportes nativos de la plataforma elegida y validar el Stock Ledger, la valuación y los reportes de utilidad bruta contra movimientos. Después construir read models analíticos de sólo lectura. DuckDB es la primera opción a probar para snapshots/Parquet; Metabase o Superset se comparan sólo si hay necesidad demostrada de BI multiusuario. La plataforma POS+ERP debe superar P49 y preservar datos históricos exportables para BI. StatsForecast 2.1.1 es la primera biblioteca de forecasting a evaluar mediante un benchmark walk-forward reproducible sobre series sintéticas regulares e intermitentes, comparada con naive, seasonal naive y promedios móviles; MLForecast sólo si variables exógenas e historial mejoran el backtesting; HierarchicalForecast queda para reconciliar agregados en una etapa posterior. DemandSense se inspecciona como referencia MIT de demanda intermitente y escenarios, no como motor de producción; DemandOS se estudia como referencia de diseño; la ausencia de licencia no permite copiar/modificar su código sin autorización. La segmentación de primeras/segundas marcas y el análisis de sustitución se implementan en el dominio Rubrova, no con una etiqueta ABC ni un notebook externo. Todas las herramientas analíticas trabajan sobre datos conciliados y no escriben en los ledgers transaccionales. Ver [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md).

Requisitos obligatorios de inteligencia comercial:

- Seguimiento diario, semanal, mensual, trimestral y por estación del hemisferio sur.
- Alertas tempranas de crecimiento, aceleración, desaceleración, estancamiento y caída por SKU, familia, marca, sucursal y canal.
- Pronóstico previo a cada trimestre/estación, con rangos, confianza, historial disponible, calendario y factores relevantes; comparar baselines y métodos de series regulares/intermitentes, ejecutar backtesting temporal y declarar cobertura/limitaciones. El benchmark mensual de referencia queda en scripts/forecasting y el dataset correspondiente en docs/fixtures.
- Ajuste por quiebres de stock, disponibilidad, promociones, precios y surtido.
- Rentabilidad por producto/marca: ganancia absoluta, margen porcentual, contribución neta de costos variables, costo de reposición, GMROI y capital inmovilizado.
- Matriz de alta/baja venta versus alta/baja rentabilidad.
- Clasificación configurable y con vigencia histórica de primeras marcas, segundas, económicas, propias y alternativas por categoría; medir participación por unidades, tickets, ventas netas, ganancia y contribución, precio comparable por unidad y sustitución con control de faltantes/promociones.
- Detección de sustitución y cambios de preferencia entre segmentos.
- Simulación de compras, precios y promociones; toda ejecución requiere aprobación.
- Backtesting y medición de error/sesgo de pronósticos.

Orden de informes:

1. Cierre diario: ventas netas, cantidad de tickets, ticket promedio, descuentos, devoluciones, medios de pago y diferencias de caja.
2. Ventas: producto, variante, marca, categoría, cajero, cliente, sucursal, canal y área.
3. Inventario: disponible, reservado, en tránsito, rotación, cobertura, quiebre, excedente, vencimiento y antigüedad.
4. Costos y rentabilidad: costo vendido, margen bruto, contribución después de comisiones/envíos, precio de reposición y GMROI.
5. Compras/proveedores: plazo, cumplimiento, costo, diferencias y propuestas de reposición.
6. Finanzas: caja, bancos, cuentas por cobrar/pagar, mora, flujo de caja y resultados.
7. Áreas: minorista, ecommerce, mayorista/distribución y servicios, además del consolidado.

Cada métrica documenta fórmula, fuente, filtros, fecha de actualización, manejo de datos faltantes y posibilidad de navegar al documento/movimiento de origen. No publicar margen si el costo está ausente o desactualizado sin mostrar esa limitación.

**Salida:** indicadores que concilian con el sistema transaccional y no bloquean el POS.

### Entrega 5 — Perfiles sectoriales y expansión comercial

- Gastronomía/panadería/rotisería: recetas, BOM, rendimiento, merma, producción por tandas, comandas, cocina y vencimientos.
- Mayorista/distribución: mínimos, múltiplos, escalas, listas por cliente, crédito, entregas parciales y costo de servir.
- Servicios B2B: cotización, contratos versionados, recurrencia, SLA, agenda, órdenes de trabajo, materiales, horas y rentabilidad.
- Multiárea: reglas y permisos por unidad, reportes por línea y consolidación sin ingresos internos ficticios.

**Salida:** los perfiles reutilizan los mismos contratos y datos base, sin duplicar POS, clientes o inventario.

### Entrega 6 — Omnicanalidad e integraciones

- Ecommerce, pedidos por WhatsApp, marketplaces y delivery.
- Integrar un canal por vez, empezando por el que tenga demanda real y documentación/sandbox.
- Importar pedido/pago/devolución/comisión con IDs externos e idempotencia.
- Evitar doble emisión fiscal y sobreventa; preservar quién es la autoridad del pedido, pago y stock.

Spree y Saleor quedan como candidatos para canal ecommerce, no como ERP/POS principal. PowerSync se prueba para lectura/tareas offline no conflictivas, no para decidir quién vende la última unidad.

**Salida:** los pedidos externos se concilian con ventas, pagos, impuestos y stock sin duplicados.

### Entrega 7 — Logística avanzada

- Fulfillment independiente de la venta desde el modelo inicial.
- Primero retiro y entrega propia/manual.
- Después Andreani, Correo Argentino PAQ.AR y OCA según credenciales y pruebas de QA.
- Vía Cargo mediante tracking externo hasta confirmar API operativa; Kangu sólo si se verifica servicio argentino.
- Agregadores, tarifas, etiquetas, webhooks, seguimiento, reclamos e indicadores logísticos.

**Salida:** ningún transportista controla la venta ni el inventario maestro; cada guía y evento conserva el vínculo al pedido y a la entrega.

## 8. Estrategia de reutilización según la fase

| Necesidad | Candidato | Momento | Qué no delegar |
|---|---|---|---|
| POS + ERP base | ERPNext, MyCompany, Tryton, Dolibarr | Entrega 0 | Decisión de arquitectura y prueba de caja |
| POS específico | POS incluido; Posnic sólo referencia | Entrega 0–1 | Fuente única de stock, pagos y venta |
| Hardware | QZ Tray / pos-toolkit | Entrega 1 | Reglas comerciales y autorización del pago |
| Fiscal argentina | Addons Tryton/Odoo verificados; arca-sdks / LaPyme / pyafipws según stack | Entrega 0–3 | Idempotencia, conciliación y estado fiscal final |
| Importación/normalización | OpenRefine, Frictionless, RapidFuzz, python-stdnum, Pint | Entrega 1–2 | Aprobación/fusión humana de registros ambiguos |
| Contabilidad especializada | Nativa del ERP; Bigcapital sólo como alternativa completa | Entrega 0–3 | Dos libros mayores simultáneos |
| Analítica | Reportes nativos; DuckDB; Metabase/Superset | Entrega 4 | Escrituras sobre ledgers operativos |
| Producción | Módulos de fabricación del núcleo; InvenTree/OCA sólo si encajan | Entrega 5 | Segundo dueño de stock |
| Ecommerce | Spree o Saleor, uno como máximo | Entrega 6 | Autoridad del catálogo, precio e inventario |
| Offline | Capacidades nativas, después PowerSync si aporta valor | Entrega 1–6 | Reservas/stock sin coordinación |
| Logística | Adaptadores directos, Karrio/agregador si conviene | Entrega 7 | Venta, cobro y stock maestro |
| Observabilidad/SSO | Logs nativos primero; OpenTelemetry/Grafana/Keycloak si la escala lo exige | Cuando haya varios servicios | Operación básica y permisos del dominio |

Regla general: primero capacidades nativas y extensiones soportadas; luego aplicación de dominio externa; después biblioteca/SDK; por último desarrollo propio de la brecha. Registrar tag/commit, licencia de cada componente y dependencia, pruebas, backup, exportación y costo de actualizar.

## 9. Criterios de terminado por entrega

Ninguna entrega se cierra por tener pantallas o completar un README. Requiere:

- Flujo principal, errores y estados pendientes documentados.
- Pruebas unitarias, integración, contrato y end-to-end según alcance.
- Permisos, auditoría y aislamiento verificados.
- Idempotencia para comandos reintentables y webhooks.
- Concurrencia de stock y caja controlada.
- Backup y restauración probados; actualización y rollback definidos.
- Rendimiento medido en caja y reportes sin bloquear la operación.
- Textos y errores en español, experiencia accesible y documentación de uso.
- Dependencias, licencias, hashes y avisos inventariados.
- Evidencia de pruebas y limitaciones conocidas; nada se marca aprobado sin ejecutar.

## 10. Qué queda deliberadamente fuera del inicio

No construir primero tracking multioperador, ecommerce complejo, asistente con IA, pronósticos avanzados, dashboards sofisticados, WMS completo, nómina, infraestructura de Kubernetes/Kafka ni numerosos microservicios. Los pronósticos avanzados y tableros quedan diferidos a Entrega 4, pero sus datos fuente se capturan desde el POS/ERP y sus pruebas se preparan con fixtures. Tampoco elegir Bigcapital, InvenTree, PowerSync, Metabase, Superset, Keycloak o Grafana sólo porque existan.

Cada uno podrá entrar cuando una brecha concreta y medible justifique su costo de instalación, integración, actualización y soporte.

## 11. Decisiones que necesitamos cerrar con evidencia

1. ¿Qué candidato permite la mejor experiencia POS y el circuito de ventas/caja/inventario sin parches invasivos?
2. ¿Cuál cubre el ERP diario y los cálculos de costos con menos adaptación?
3. ¿Qué límites de servicio se pueden mantener sin convertir un ERP integrado en la base de todos los dominios?
4. ¿Existe localización argentina mantenida y compatible con la versión exacta? ¿Qué parte requiere un servicio fiscal propio?
5. ¿Se puede exportar y restaurar sin dependencia del proveedor?
6. ¿Cuánto cuesta mantener las extensiones en cada actualización?

La decisión no se tomará por cantidad de funciones ni por estrellas de GitHub. Se elegirá la composición que complete mejor el circuito operativo, respete límites de datos, sea recuperable y tenga el menor costo total de adaptación y mantenimiento.

## Referencias principales

- [ERPNext — POS Profile](https://docs.frappe.io/erpnext/pos-profile)
- [ERPNext — Point of Sale](https://docs.frappe.io/erpnext/point-of-sale)
- [ERPNext — Accounting Introduction](https://docs.frappe.io/erpnext/accounting-introduction)
- [ERPNext — Accounting Dimensions](https://docs.frappe.io/erpnext/accounting-dimensions)
- [Tryton 8.0 — Sale Point](https://docs.tryton.org/8.0/modules-sale-point/design.html)
- [Tryton 8.2 — Sale Point, actualización posterior](https://docs.tryton.org/8.2/modules-sale-point/design.html)
- [Localización argentina Tryton — ramas 8.0](https://github.com/tryton-ar)
- [Tryton 8.2 — Accounting releases](https://docs.tryton.org/8.2/modules-account/releases.html)
- [MyCompany 6.2](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [Dolibarr — API, triggers and hooks](https://www.dolibarr.org/presentation-api.php)
- [Estrategia reuse-first](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md)
- [Evaluación de plataformas](PLATFORM_EVALUATION.md)
- [Requisitos del POS](POS_REQUIREMENTS.md)
- [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md)
- [Inteligencia del negocio](BUSINESS_INTELLIGENCE.md)
- [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md)
- [Perfil 360 e inteligencia por cliente](CUSTOMER_360_AND_INTELLIGENCE.md)
- [Identidad del pagador, pagos y conciliación](PAYMENT_IDENTITY_AND_RECONCILIATION.md)
- [Evaluación de S-Tech](S_TECH_EVALUATION.md)
- [Revisión competitiva del mercado](COMPETITIVE_MARKET_REVIEW.md)
- [Inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md)
- [Copias de seguridad y recuperación](BACKUP_AND_MIGRATION_STRATEGY.md)
- [Continuidad y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md)


## Anexo K — Calidad y pruebas previas, preservadas

> **Archivo histórico consolidado.** El contenido original se preserva; su estado está subordinado a las secciones vigentes de este manual.

## Regla

Una capacidad no se considera terminada por mostrar una pantalla. Debe cumplir reglas, permisos, persistencia, integridad, accesibilidad, recuperación y pruebas.

## Memoria técnica y contratos

Toda modificación de lógica, datos o integración debe actualizar este manual: [contratos](#c-contracts), [decisiones](#e-decisions), [relaciones entre dominios](#d-domain-relationships) e [iteraciones](#f-iterations). La documentación conserva la razón y la evidencia; no reemplaza a los tests.

## Prevalidación local compartida con CI

Antes de publicar cambios, ejecutá desde la raíz:

```bash
bash scripts/platform/local-preflight.sh
```

Las capas se pueden ejecutar por separado:

```bash
bash scripts/platform/local-preflight.sh --platform
bash scripts/platform/local-preflight.sh --replenishment
```

El mismo script se invoca en GitHub Actions. Comprueba Node/Python, extensiones estáticas, tests del supervisor, scripts y shell, suite del planificador, fixtures y el puente JSON nativo. Es una primera barrera rápida y repetible; **no** demuestra que el módulo lsFusion pueda cargarse, ni que la API autenticada funcione contra MyCompany.



## Estrategia

- Unitarias: cálculos, reglas, validaciones y estados.
- Integración: base de datos, transacciones, eventos y adaptadores.
- Contrato: APIs internas y externas.
- Componentes: interfaz y estados visibles.
- End-to-end: recorridos completos por perfil y canal.
- Resiliencia: desconexiones, reinicios, reintentos y fallos parciales.
- Seguridad: permisos, aislamiento, abuso y datos sensibles.
- Rendimiento: caja, búsqueda, sincronización y reportes.

## Entorno de ejecución para pruebas

Para el desarrollo local se prioriza el runtime nativo, sin Docker: Java 21, PostgreSQL 18 y Tomcat 9.0.124. El supervisor utiliza una carpeta PostgreSQL exclusiva, no adopta ni detiene servicios personales de la máquina y conserva los datos cuando se detienen los procesos.

En CI, la puerta principal del runtime es el smoke nativo macOS ARM64, ejecutado después de la compilación completa. Los diagnósticos Linux nativo y Docker/Linux se ejecutan manualmente mediante `workflow_dispatch`; no retrasan cada pull request y no son gates de aceptación. Un job con `continue-on-error` nunca se interpreta como aprobación funcional.

### Estado de evidencia

- La revisión canónica actual es `ac758d01`. El workflow [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó con `success`: preflight compartido, compilación completa y smoke nativo macOS ARM64.
- El smoke autenticó mediante Chromium, confirmó las sondas de inventario/compromisos/recepciones HTTP 200 y verificó la exportación de reposición contra fixtures.
- La prueba ejecutó venta sintética ARS 1.250, pago exacto en efectivo, factura/pago persistidos, salida de stock 10 → 9 y cierre de turno conciliado.
- Tras reiniciar el runtime, factura, pago, stock, turno e incidencias siguieron disponibles en PostgreSQL. La Demo usó otra base y puertos aislados.
- El backup lógico PostgreSQL se ejecutó contra PostgreSQL 18 real de CI: paquete custom, manifiesto, SHA-256 y verificación `pg_restore --list`; la restauración a `rubrova_restore_ci` terminó correctamente sin modificar `rubrova_dev`.
- La suite de backup contiene 9 pruebas; contempla checksum/manifiesto alterados, entradas extra, clúster ajeno, nombre/confirmación de destino, base ya existente y limpieza tras restauración fallida.
- El alcance del paquete es **sólo PostgreSQL**. No contiene archivos adjuntos, imágenes, documentos externos, secretos ni binarios; no equivale a un backup portable completo.
- La ejecución dejó `RUBROVA_NATIVE_EGRESS_BLOCKED=false` y `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. El modo offline macOS sigue pendiente.
- Linux nativo y Docker/Linux fueron `skipped` en el push actual. La validación Windows fue de sintaxis, no de instalación funcional.
- La exportación de reposición requiere conciliación con una base MyCompany local real; los fixtures son sintéticos. También falta aceptación en el Mac físico, periféricos y jornada supervisada.

### Controles del smoke nativo

- Inicio desde una base vacía, verificación del servidor, RMI, `onStarted` y respuesta web.
- Login y navegación en español mediante Chromium.
- Verificación de la API autenticada cuando el cambio modifica el contrato.
- Captura de errores del navegador, requests fallidos, respuestas HTTP y tiempos de `dispatch`.
- Ejecución con salida externa bloqueada cuando se evalúa la continuidad offline; distinguirla de los smokes que habilitan Internet para dependencias o integraciones simuladas.
- Crear un paquete PostgreSQL, verificar checksums y restaurarlo en una base nueva sin modificar la base activa.
- Rechazar paquetes alterados, bases destino existentes y restauraciones parciales; comprobar que la limpieza sólo retire la base nueva creada por esa operación.

Los tests unitarios del supervisor no sustituyen las pruebas de runtime, y el inicio de sesión no sustituye la prueba de una API de dominio.

## Flujos POS obligatorios

Venta en efectivo con vuelto; venta con medios mixtos; descuentos por línea, carrito, cupón, combo y horario; reglas de acumulación; excepción autorizada; devolución parcial y total; anulación; productos pesables; caja compartida; apertura, arqueo, cierre y diferencia; impresión y recuperación ante impresora desconectada.

## Integridad y auditoría

- El operador no aprueba su propia excepción cuando la política exige separación.
- Los registros de auditoría no se editan ni borran desde la aplicación.
- Cada devolución remite al original.
- Repetir solicitud no duplica venta ni pago.
- Cambiar un precio no modifica ventas anteriores.
- Una salida interna no se cuenta como venta.
- Los perfiles sin permiso no acceden a operaciones restringidas.
- Un usuario no accede a otro negocio alterando identificadores.

## Offline y sincronización

Probar desconexión antes/durante/después de confirmar; cierre y reapertura con pendientes; reinicio; interrupción y repetición de sincronización; mensajes externos repetidos; cambios concurrentes; ventas desde cajas desconectadas; conflictos de stock; restauración de backup.

Criterios: una operación confirmada no se pierde; no se procesa dos veces; el usuario ve qué está pendiente; no se simula autorización fiscal o pago sin confirmación; los conflictos relevantes siguen reglas explícitas.

## Fiscalidad e integraciones

Homologación ARCA; factura y nota de crédito; integración de facturación externa y propia; no doble emisión; webhooks repetidos/tardíos/fuera de orden; pago autorizado, rechazado, pendiente y reembolsado; caída de proveedor; conciliación con liquidaciones.

## Inteligencia y datos

Cálculos financieros con casos conocidos; ventas netas, costo, margen y contribución; períodos incompletos y días sin stock; estacionalidad con datos sintéticos e históricos; no inferir causalidad de correlaciones; pronósticos fuera de muestra; error, sesgo e intervalos; promociones con contribución incremental; datos faltantes reducen confianza y se declaran.

## Seguridad

Pruebas de roles y permisos en servidor; aislamiento de negocios y sucursales; sesión; límites de solicitudes; secretos fuera del código; logs sin datos sensibles; validación de entradas/salidas; dependencias y secretos analizados en CI; revisión de cambios de autenticación, autorización y auditoría.

## Experiencia y rendimiento

Venta habitual con pocos pasos; teclado, lector y pantalla táctil; errores accionables; contraste, foco y semántica; pantallas pequeñas y grandes; latencia de búsqueda y confirmación; informes no bloquean caja.

## Evidencia

Cada entrega registra qué se probó, entorno y versión, resultado, evidencia, limitaciones y riesgos pendientes. No se informa "aprobado" sin ejecutar las pruebas correspondientes. Los datos de prueba son sintéticos.


## Marcos de calidad y accesibilidad

- **ISO/IEC 25010:2023** como modelo de calidad de producto: adecuación funcional, eficiencia de desempeño, compatibilidad, capacidad de interacción, fiabilidad, seguridad, mantenibilidad, flexibilidad y seguridad operacional según el modelo vigente. Traducir las características aplicables en métricas y pruebas: https://www.iso.org/standard/78176.html.
- **WCAG 2.2 nivel AA** como objetivo de accesibilidad para las interfaces web y administrativas. Validar teclado, foco, contraste, tamaño de objetivos, etiquetas, mensajes y compatibilidad con tecnologías de asistencia: https://www.w3.org/TR/wcag/.
- **OWASP ASVS 5.0** para requisitos verificables de seguridad: https://asvs.owasp.org/.
- **NIST SSDF SP 800-218 v1.1** como guía de prácticas de desarrollo seguro. La revisión 1.2 figuraba como borrador en la consulta del 19/11/2026 y se volverá a verificar antes de adoptar sus identificadores: https://csrc.nist.gov/Projects/ssdf/publications.
- **PCI DSS v4.0.1** cuando el alcance de pagos lo requiera. Se busca reducir dicho alcance mediante terminales y proveedores certificados: https://www.pcisecuritystandards.org/es/document_library/.

Estos marcos guían requisitos y pruebas. No se afirmará cumplimiento o certificación sin una evaluación formal y evidencia suficiente.


## Código de terceros y licencias

Toda dependencia, plugin, fragmento de código, plantilla, fuente, icono o recurso externo debe pasar una revisión antes de incorporarse.

La revisión registra:

- Repositorio y URL de origen.
- Versión, etiqueta o commit exacto.
- Licencia efectiva del archivo y del proyecto, más avisos y excepciones.
- Licencias de dependencias transitivas y recursos incluidos.
- Partes comerciales, Enterprise, duales o con condiciones especiales.
- Archivos modificados, avisos que deben conservarse y obligaciones de distribución.
- Mantenimiento, vulnerabilidades conocidas, cobertura de pruebas y compatibilidad.

Reglas de aceptación:

1. Preferir MIT, ISC, BSD y Apache 2.0 cuando el componente cubra la necesidad y su calidad sea suficiente.
2. Revisar LGPL con detalle antes de combinar, modificar o distribuir.
3. No incorporar GPL o AGPL al núcleo sin una decisión explícita sobre la licencia y el modelo de distribución del producto.
4. No usar código sin licencia identificable ni asumir que un repositorio público concede permiso de reutilización.
5. No incorporar código o recursos de una edición Enterprise/comercial sin contrato válido.
6. Conservar avisos, archivos LICENSE y NOTICE, atribuciones y fuentes de origen según las condiciones aplicables.
7. Fijar versiones; no depender de ramas flotantes para software de producción.
8. Mantener un SBOM en SPDX o CycloneDX y analizar dependencias, vulnerabilidades y licencias en CI.
9. Un cambio de versión obliga a revisar cambios de licencia y dependencias transitivas.

La guía completa y las licencias de los candidatos están en [Estrategia de reutilización de código abierto](OPEN_SOURCE_STRATEGY.md).

Para el protocolo de respaldo portable, migración de equipo, cifrado y restauración en Windows limpio, ver [Copias de seguridad y recuperación](BACKUP_AND_MIGRATION_STRATEGY.md).

La aprobación legal de una licencia no reemplaza la revisión técnica; una biblioteca permisiva también puede ser insegura, estar abandonada o no cumplir nuestras invariantes.


## Continuidad y recuperación

Además de las pruebas funcionales P01–P26, la aceptación de confiabilidad debe ejecutar P27–P48. Simulan terminación abrupta del proceso (sin apagar físicamente el equipo), comandos y webhooks duplicados, conflicto de clave, concurrencia CAS, cuotas offline, restauración, migraciones, despliegue independiente, Outbox y Sagas. El guion completo está en [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md).

## Arquitectura distribuida y aislamiento de servicios

- Cada servicio tiene almacenamiento/credenciales privados; se prueba que otros servicios no puedan leer ni escribir tablas ajenas.
- APIs y eventos con esquema/versionado, autenticación y pruebas de compatibilidad entre versiones coexistentes.
- Outbox/Inbox durables, idempotencia atómica y claves estables; reintentos concurrentes producen un solo efecto.
- Correlation ID de extremo a extremo, métricas y trazas que permiten reconstruir el recorrido de una operación.
- Reiniciar o actualizar un servicio no debe obligar a reiniciar o desplegar todos los demás.
- Un servicio nuevo o caído debe degradar sólo capacidades dependientes; los estados quedan visibles.
- Las transacciones distribuidas se prueban mediante Sagas y compensaciones idempotentes.
- Las copias de varios servicios se restauran con un manifiesto coherente de versiones y offsets de eventos.

## Contratos entre módulos externos

- Prueba de contrato de cada puerto/API con ejemplos válidos, inválidos y esquemas versionados.
- Reintentos repetidos con la misma clave no duplican venta, pago, movimiento, cupón ni factura.
- Webhooks duplicados o fuera de orden se deduplican y no retroceden estados finales.
- Un módulo no puede leer ni modificar el agregado de otro módulo por acceso directo a tablas.
- Aislamiento por negocio, sucursal, caja, dispositivo y permiso.
- Caída del servicio externo, timeout, respuesta parcial y recuperación.
- Outbox/inbox durables, dead-letter, replay autorizado y conciliación.
- Sustitución de adaptador sin modificar la lógica de negocio.
- Compatibilidad y build de cada puente en Windows, Linux y macOS por separado.

## Pruebas de checkout y terminal

- Retirar un producto del carrito antes del pago: total, descuentos e impuestos recalculados; sin venta ni salida de stock para esa línea.
- No permitir cambios silenciosos del importe una vez enviada la orden a terminal.
- Efectivo exacto, exceso y faltante: vuelto y neto de caja correctos al centavo.
- Pago mixto: suma de asignaciones igual al total; cada medio conserva su importe y estado.
- Terminal creada/en terminal/no confirmada: nunca se marca pagada.
- Aprobación, rechazo, cancelación, expiración, acción requerida y reembolso.
- Timeout después de que el cliente pudo haber pagado: consulta de estado antes de otro intento.
- Repetición de webhook y request: un único efecto.
- Voucher de terminal, ticket de venta y documento fiscal se concilian por separado.


---

Fin del manual técnico canónico. Toda nueva evidencia, contrato, decisión, investigación y actualización del roadmap técnico debe agregarse aquí.
