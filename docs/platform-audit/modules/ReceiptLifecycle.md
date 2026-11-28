# Pasaporte de integración — ciclo de recepción de compras

**Grupo funcional:** Receipt / purchase-order receipt lifecycle  
**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Plataforma:** lsFusion 6.2 · commit dd4dbe5bf9b136e73e18fe25d741253929324350  
**Composición:** módulos incluidos en el cierre estático de RubrovaCustom; verificar el registro estructural al cambiar los locks.  
**Nivel de evidencia:** fuentes revisadas, compilación aprobada y escenarios sintéticos parcial/completo aceptados en runtime; permisos exhaustivos, WMS y conciliación comercial/contable real siguen pendientes.

Este pasaporte agrupa módulos que implementan una única secuencia transaccional. No convierte todos sus archivos en una ficha individual independiente: conserva las fronteras de responsabilidad y las relaciones entre módulos. Complementa [Receipt](Receipt.md), [PurchaseOrder](PurchaseOrder.md), el [mapa de compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) y el [mapa de inventario y ledgers](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md).

## 0. Resumen de integración — lectura de 2 minutos

| Pregunta | Respuesta |
|---|---|
| Módulos exactos del circuito | Receipt, ReceiptType, ReceiptSelection, ReceiptReady, ReceiptDone, ReceiptCanceled, ReceiptRes, ReceiptInv, ReceiptPutAway, ReceiptCost, PurchaseOrderReceipt, PurchaseOrderReceiptCost, PurchaseOrderReceiptInitial y PurchaseOrderReceiptStatus |
| Dominio y dueños | Inventory posee Receipt/ReceiptLine, estado de recepción y productores de ledgers; Purchase conserva Order/OrderLine y su relación con cada recepción |
| Caso cubierto | Pedido de compra confirmado → recepción prevista Ready → recepción efectiva parcial/completa → ubicación interna opcional → costo → cancelación y reposición de la cantidad pendiente |
| Punto de entrada | order / orders, confirmación del pedido, formulario receipt y acciones Ready, Done, Put away y Cancel |
| Lectura principal | Recepciones relacionadas al pedido; cantidades done / toReceive; ledgers InvLedger, ResLedger y CostLedger |
| Datos que posee | Receipt, ReceiptLine, ReceiptType y detalle ReceiptPutAway; PurchaseOrderReceipt relaciona el documento de compra con sus recepciones |
| Efectos transversales | Esperado/reserva, inventario físico por ubicación, ubicación hija, costo/valuación y cantidad pendiente de compra |
| APIs | Estos módulos no declaran una API HTTP propia. La comunicación interna es lógica lsFusion. La exportación propia de reposición es otra frontera de sólo lectura |
| Riesgo clave | No confundir demanda inicial, cantidad recibida, cantidad ubicada, reserva esperada y costo; no duplicar cantidades al distribuirlas entre ubicaciones |
| Decisión reuse-first | Reutilizar el circuito nativo. No crear otra entidad de recepción, motor de stock ni ledger propio |
| Prueba que desbloqueó | Run #613: recepción parcial con put-away y completa sin put-away, cancelación y lectura persistida tras reinicio |

### Ruta inmediata para quien trabaje en el circuito

1. Leer esta ficha, Receipt, PurchaseOrder, ResLedger, InvLedger y CostLedger.
2. Verificar el snapshot en platform/source-lock.json y el parche versionado de ReceiptRes.lsf.
3. Seguir la línea de compra hasta ReceiptLine y los tres ledgers; no sustituir el vínculo documental por un saldo agregado.
4. Antes de modificar, registrar qué dato posee cada módulo y qué efecto queda activo/inactivo al cancelar.
5. Repetir el smoke nativo cuando se altere la fuente, la composición o el comportamiento.

## 1. Identidad, versión y composición

### 1.1 Módulos del grupo y fuente

| Módulo | Fuente | Responsabilidad principal | REQUIRE directo relevante |
|---|---|---|---|
| Receipt | [Receipt.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf#L1-L253) | Documento base, líneas, ubicación, proveedor, demanda inicial, historial y acceso por ubicación | System, Time, DateUtils, FileUtils, InventorySettings, Location, Partner, Product, ReceiptType, ItemPurchase, PartnerPurchase, BarCode, Doc, ResLedger |
| ReceiptType | [ReceiptType.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptType.lsf#L1-L82) | Configuración del tipo, numerador, ubicación por defecto y máximo | Numerator, Location |
| ReceiptSelection | [ReceiptSelection.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptSelection.lsf#L1-L13) | Selección/listado, copia de fecha y borrado mediante macros genéricas | Receipt |
| ReceiptReady | [ReceiptReady.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptReady.lsf#L1-L46) | Transición a Ready y habilitación del esperado | Receipt, ResLedger, ReceiptSelection |
| ReceiptDone | [ReceiptDone.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptDone.lsf#L1-L87) | Cantidad efectivamente recibida, validación y fecha/hora | ReceiptReady |
| ReceiptCanceled | [ReceiptCanceled.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptCanceled.lsf#L1-L47) | Cancelación y definición de recepción activa | ReceiptDone |
| ReceiptRes | [ReceiptRes.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptRes.lsf#L1-L28) | Esperado negativo y política de impacto en disponible | ReceiptDone, ReceiptCanceled |
| ReceiptInv | [ReceiptInv.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptInv.lsf#L1-L25) | Entrada física por lo recibido aún no ubicado | ReceiptCanceled, InvLedger |
| ReceiptPutAway | [ReceiptPutAway.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptPutAway.lsf#L1-L143) | Distribución a ubicaciones descendientes y ledger de movimiento interno | ReceiptDone, ReceiptInv, LocationProduct, Input |
| ReceiptCost | [ReceiptCost.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptCost.lsf#L1-L40) | Entrada de costo por recepción activa | ReceiptCanceled, CostLedger, CostLocation |
| PurchaseOrderReceipt | [PurchaseOrderReceipt.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/inventory/receipts/orders/PurchaseOrderReceipt.lsf#L1-L122) | Relación pedido↔recepción, cantidades pendientes y regeneración | PurchaseOrder, PurchaseOrderConfirmed, PurchaseOrderCanceled, PurchaseOrderLocked, ReceiptCanceled, ProductSku |
| PurchaseOrderReceiptCost | [PurchaseOrderReceiptCost.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/inventory/receipts/orders/PurchaseOrderReceiptCost.lsf#L1-L7) | Derivar costo de recepción desde el precio del pedido | PurchaseOrderReceipt, ReceiptCost |
| PurchaseOrderReceiptInitial | [PurchaseOrderReceiptInitial.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/inventory/receipts/orders/PurchaseOrderReceiptInitial.lsf#L1-L9) | Tipo de recepción inicial para el tipo de pedido estándar | PurchaseOrderInitial, PurchaseOrderReceipt |
| PurchaseOrderReceiptStatus | [PurchaseOrderReceiptStatus.lsf](../../../vendor/mycompany/src/main/lsfusion/purchase/inventory/receipts/orders/PurchaseOrderReceiptStatus.lsf#L1-L18) | Estado agregado de las recepciones relacionadas al pedido | PurchaseOrderReceipt |

Las dependencias de ledger que deben seguirse como autoridad externa al grupo son ResLedger, InvLedger, CostLedger, Location/LocationProduct y los maestros de producto, proveedor y empresa.

### 1.2 Dependencia local protegida

ReceiptRes.lsf tiene un parche pequeño y versionado de Rubrova. El archivo local exige ReceiptCanceled además de ReceiptDone y filtra NOT canceled(receipt(line)). La implementación se aplica con scripts/platform/apply-rubrova-source-patches.py, con anclas exactas, rechazo ante drift/estado parcial y prueba de idempotencia. La razón es impedir que una recepción Ready cancelada siga sumando una reserva esperada negativa.

No se sustituye por active(receipt): en la fuente active(Receipt) significa done AND NOT canceled, y usarlo en ReceiptRes excluiría también las recepciones Ready no completadas, que sí deben representar entradas futuras activas.

## 2. Responsabilidad, autoridad y límites

| Dato / entidad | Dueño | Este circuito crea/lee/modifica | Fuente de verdad |
|---|---|---|---|
| Pedido y línea | PurchaseOrder | Lee y conserva referencia desde recepción | Order / OrderLine |
| Recepción y línea | Receipt | Crea/actualiza documentos y líneas; mantiene número, tipo, proveedor, ubicación y demanda inicial | Receipt / ReceiptLine |
| Configuración | ReceiptType + extensiones | Lee defaults/políticas y permite administrarlas | ReceiptType |
| Cantidad recibida | ReceiptDone | Registra cantidad efectiva por línea y fecha/hora | done(ReceiptLine) / done(Receipt) |
| Cantidad ubicada | ReceiptPutAway | Registra asignación por detalle y destino descendiente | ReceiptPutAway |
| Esperado/reserva | ReceiptRes | Proyecta cantidad esperada como reserva negativa | ReceiptResLedger sobre ResLedger |
| Movimiento físico | ReceiptInv / ReceiptPutAway | Proyecta entrada pendiente a ubicación principal y entrada a ubicaciones hijas | InvLedger y productores específicos |
| Costo | ReceiptCost + PurchaseOrderReceiptCost | Calcula importe por recepción activa y ubicación de costo | CostLedger / InCostLedger |
| Estado resumido del pedido | PurchaseOrderReceiptStatus | Lee recepciones asociadas y excluye las canceladas del agregado | Status(Receipt) y relación documental |

**No es dueño de:** factura de proveedor, deuda, pago, libro contable, lote/serie, autorización WMS ni liquidación fiscal. Debe conservar sus enlaces nativos con PurchaseOrderBill/Bill, módulos de lotes y cualquier integración habilitada, pero no reemplazarlos.

## 3. Casos de uso y secuencia operativa

| Caso | Actor/rol | Entrada/acción | Resultado | Excepciones relevantes |
|---|---|---|---|---|
| Recepción prevista desde pedido | Compras | Confirmar pedido con tipo/ubicación de recepción configurados | Se crea o actualiza Receipt Ready con líneas ligadas al pedido | Sin ubicación/tipo o pedido no confirmado no se activa el trigger |
| Recepción manual inmediata | Depósito | Acción immediateReceipt() desde receipts | Receipt no planificada en sesión nueva; permite recepción directa | No tiene reserva previa del pedido |
| Completar recepción | Depósito | Capturar done(ReceiptLine) y validate(Receipt) | Documento Done, fecha/hora efectiva y ledgers físicos/costo | Cantidad fuera de rango, salvo que el tipo desactive el control |
| Recepción parcial | Depósito | Recibir menos que initialDemand | Pedido conserva cantidad pendiente; otra recepción puede cubrirla | No confundir recibido con pedido total |
| Put-away | Depósito | Agregar detalle con ubicación hija y cantidad; marcar Put away | Cantidad ubicada se registra en hija; saldo restante sigue en ubicación principal | Destino no descendiente o suma ubicada mayor a recibida |
| Cancelación prevista | Supervisor autorizado | cancel(Receipt) antes de Done | Se excluye el esperado por ReceiptRes y el pedido vuelve a calcular el remanente | La reserva sólo se libera correctamente si el filtro contempla cancelación |
| Cancelación posterior a Done | Supervisor autorizado | cancel(Receipt) sobre recepción efectiva | Receipt queda cancelada/inactiva para stock/costo; pedido puede generar otra Ready | Verificar inventario por ubicación, costo y regeneración sin duplicar |
| Factura vinculada | Cuentas a pagar | Política ordered/delivered en PurchaseOrderBill | Factura mantiene referencia a pedido y, si delivered, a recepción activa | No facturar dos veces una recepción |

**Secuencia nativa revisada:** Order confirmado → PurchaseOrderReceipt WHEN → Receipt/ReceiptLine Ready → ReceiptResLedger negativo → ReceiptDone.validate → ReceiptInvLedger + ReceiptPutAwayLedger opcional + ReceiptCostLedger → ReceiptCanceled.cancel → ledger físico/costo inactivo, reserva futura excluida y Purchase.toReceive recalculado → nueva Receipt Ready distinta cuando corresponde.

El diagrama representa el contrato y la ruta revisada; los efectos aceptados por runtime se delimitan en §11.

## 4. Modelo de datos, cardinalidades y semántica

### 4.1 Entidades y relaciones

- Order 1:N OrderLine; una línea de pedido puede vincularse con varias recepciones parciales a lo largo del tiempo.
- Receipt 1:N ReceiptLine; cada línea de recepción puede guardar su referencia orderLine.
- ReceiptType 1:N Receipt; determina numeración, ubicación por defecto y políticas agregadas desde módulos de estado/ledger.
- ReceiptLine 1:N ReceiptPutAway; cada detalle apunta a una línea recibida y a una ubicación destino.
- Receipt produce proyecciones en ledgers distintos; no existe una única fila genérica que represente simultáneamente reserva, movimiento físico y valoración.

### 4.2 Propiedades críticas

| Propiedad | Firma / tipo | Semántica |
|---|---|---|
| initialDemand | NUMERIC[16,3] (ReceiptLine) | Cantidad prevista en la línea de recepción |
| done | NUMERIC[16,3] (ReceiptLine) | Cantidad físicamente recibida y validada por línea |
| done | BOOLEAN (Receipt) | Estado/indicador de recepción completada |
| put | GROUP SUM quantity(ReceiptPutAway) por ReceiptLine | Total distribuido a ubicaciones hijas |
| ledgerDone | ABSTRACT; extendida por ReceiptPutAway con put | Cantidad ya transferida a ubicación hija |
| toDo | done - ledgerDone | Cantidad que ReceiptInv mantiene en ubicación principal |
| toReceive | max(receivedQuantity - suma done de recepciones activas, 0) | Cantidad de pedido aún no recibida |
| reserveReceipt | DATA Receipt (Order) | Referencia del pedido a su recepción Ready prevista |
| reserved | ReceiptResLedger | Cantidad negativa, -initialDemand |
| skipAvailable | ReceiptResLedger | Excluye esperado del disponible cuando increaseAvailableStock es falso |
| cost | ABSTRACT CASE NUMERIC[14,2] (ReceiptLine) | Costo de línea resuelto por datos manuales o extensiones |
| costAmount | SUM por Receipt | Importe de costos ledger asociado al documento |

Conversión de unidad: receivedQuantity(OrderLine) multiplica la cantidad del pedido por skuCoeff(item(orderLine)); receivedProduct resuelve el SKU. PurchaseOrderReceiptCost incorpora el precio del pedido prorrateado por el mismo coeficiente. No comparar unidades antes de normalizarlas.

### 4.3 Configuración funcional del tipo

| Propiedad | Módulo productor | Efecto |
|---|---|---|
| defaultLocation, maxQuantity, numerador | ReceiptType | Defaults, límite de demanda y numeración |
| increaseAvailableStock | ReceiptRes | Decide si el esperado negativo participa en disponible |
| putAway | ReceiptPutAway | Habilita el proceso de distribución interna |
| showCost | ReceiptCost | Muestra costo manual por línea |
| doNotCheckDone | ReceiptDone | Desactiva el constraint de rango de cantidad recibida |

La última opción requiere especial cuidado: la expresión fuente agrupa done < 0 y done > initialDemand bajo NOT doNotCheckDone. Por lo tanto, activarla no sólo permite excedentes; también desactiva el control inferior de cantidad negativa. Mantenerla desactivada salvo que una política de tipo y una prueba específica justifiquen lo contrario.

## 5. Formularios, navegación y experiencia de uso

| Elemento | Módulo | Uso |
|---|---|---|
| Navegación operations → receipts | Receipt | Listado principal |
| receipt | Receipt | Cabecera, proveedor, ubicación, líneas, demanda inicial, historial, adjuntos y comentarios |
| receipts | Receipt + extensiones | Grilla de documentos con estados/filtros |
| receiptType / receiptTypes | ReceiptType + extensiones | Configuración por tipo |
| markAsToDo | ReceiptReady | Pasar de Draft a Ready |
| validate / setDone | ReceiptDone | Confirmar cantidad efectiva |
| markAsPutAway y grilla ReceiptPutAway | ReceiptPutAway | Distribuir cantidad a ubicaciones descendientes |
| cancel | ReceiptCanceled | Cancelar y retirar efectos activos |
| relación de documentos rc en order | PurchaseOrderReceipt | Ver/editar recepciones relacionadas al pedido |
| orderReceiptShow | PurchaseOrderReceipt | Ver cantidad recibida por línea y documento |

La pantalla no es la autoridad de seguridad. El acceso por ubicación se agrega en Receipt mediante @defineDocLocationAccess; permisos de cada acción y lecturas por API deben comprobarse en servidor.

## 6. Contratos de integración y comunicación

### 6.1 Dentro de lsFusion

Las fronteras son módulos/propiedades/acciones sobre las mismas clases y sesión; no requieren HTTP, colas ni una segunda base. El flujo interno usa:
- REQUIRE y extensiones de clases/propiedades;
- WHEN al cambiar toReceive, confirmar, desbloquear o modificar proveedor/fecha/ubicación/número;
- APPLY, CANCEL y NEWSESSION en acciones de estado;
- relaciones de documento y línea para mantener trazabilidad;
- agregaciones nativas para formar ledgers.

### 6.2 Recalculación del pedido

PurchaseOrderReceipt crea/actualiza la recepción prevista cuando cambian eventos relevantes del pedido. Si la recepción guardada ya no está en estado Ready, el módulo limpia reserveReceipt(Order); luego busca otra recepción Ready ligada al pedido y, si no existe y toReceive > 0, crea una nueva Receipt Ready. Actualiza proveedor, fecha y ubicación; crea líneas sólo cuando corresponde y asigna initialDemand desde toReceive.

La cancelación de una recepción Done cambia active(receipt) (definida como done AND NOT canceled), por lo que la cantidad de la recepción cancelada deja de restarse de la cantidad pedida. Esto permite que el trigger de toReceive restituya la cantidad pendiente y que se genere otra recepción. La prueba #613 confirmó ese comportamiento en los dos casos sintéticos documentados.

### 6.3 APIs y sistemas externos

Estos módulos no declaran endpoints HTTP propios. RubrovaReplenishmentExport expone una API de sólo lectura para exportar datos nativos; su contrato y adaptación son otra capa. FusionWMS aparece como consumidor regional en el dossier de Receipt, pero su presencia no demuestra que esté activo, que sea compatible con esta composición ni que esté homologado para Argentina.

## 7. Estados, transacciones y efectos secundarios

### 7.1 Estados

| Indicador / estado | Productor | Efecto |
|---|---|---|
| Draft | Receipt | Documento editable |
| Ready | ReceiptReady | Reserva esperada mientras no Done/cancelado |
| Done | ReceiptDone | Cantidad efectiva y fecha/hora |
| Put away | ReceiptPutAway | Indicador de proceso de ubicación interna |
| Canceled | ReceiptCanceled | Marca de cancelación y desactiva efectos que filtran por activo |

Los indicadores no son mutuamente excluyentes. En el runtime probado, una recepción cancelada después de completarse conservó ready=true y done=true junto con canceled=true. No inferir que canceled borra cantidades o reescribe el historial; los ledgers determinan si el hecho sigue activo.

### 7.2 Ledgers y signo

| Efecto | Productor | Regla |
|---|---|---|
| Esperado / reserva | ReceiptResLedger | -initialDemand; sólo Ready, cantidad positiva, no Done y no cancelado |
| Disponible | ResLedger | El esperado participa según skipAvailable, inverso de increaseAvailableStock |
| Ingreso físico principal | ReceiptInvLedger | done - ledgerDone; sólo suma al saldo cuando active(receipt) |
| Ingreso físico hijo | ReceiptPutAwayLedger | Cantidad de cada detalle en ubicación hija; activo según recepción |
| Valuación | ReceiptCostLedger | Cantidad Done y costo de línea, ubicación de costo derivada de ubicación del documento |

El movimiento principal no duplica el detalle en las hijas: ReceiptInv descuenta del ingreso principal lo que ReceiptPutAway ya distribuyó. El costo del documento se registra en la ubicación de costo resuelta por CostLocation; no asumir que el importe se divide automáticamente por cada ubicación hija.

### 7.3 Frontera de cancelación

- ReceiptCanceled.cancel aplica la sesión actual, verifica cancelación previa y marca el flag en una nueva sesión.
- active(Receipt) es done AND NOT canceled.
- ReceiptInv y ReceiptPutAwayLedger heredan esa condición para el saldo físico.
- ReceiptCostLedger filtra done AND active(receipt).
- ReceiptRes requiere además NOT canceled por el parche local descrito en §1.2; no puede usar simplemente active porque una Ready sin Done debe seguir proyectando esperado.

## 8. Seguridad, permisos y auditoría

Controles detectados en fuente:
- proveedor debe cumplir isVendor;
- producto debe cumplir canBePurchased;
- la ubicación del documento no puede ser internalUse;
- Receipt incluye @defineDocLocationAccess;
- cada detalle de put-away debe referir a una ubicación descendiente de la recepción y activa en el selector.

Pendiente de comprobar con perfiles runtime:
- lectura/edición/cancelación con usuario sin acceso a ubicación;
- acceso a ubicación hija sin acceso a raíz y viceversa;
- autorización real de la acción, no sólo su visibilidad;
- acceso por API y selección múltiple;
- auditoría de usuario/fecha/hora en cancelación y edición;
- comportamiento ante cambio de ubicación luego de generar la recepción.

No asignar roles ni dar por resueltas autorizaciones a partir de macros o botones ocultos solamente.

## 9. Configuración y prerrequisitos

- empresa y ubicación válidas;
- proveedor habilitado y producto comprable;
- ReceiptType y numerador configurados;
- ubicación no interna para la recepción;
- tipo de pedido con ReceiptType asignado;
- política increaseAvailableStock;
- política putAway;
- costo manual (showCost) o fuente del costo resuelta por módulos de producto/pedido;
- unidades y coeficientes SKU consistentes;
- ubicación CostLocation definida según la política de valuación.

PurchaseOrderReceiptInitial asigna receiptType('receipt') al tipo de pedido cuyo ID es order; no asumir que todos los tipos de pedido comparten ese default.

## 10. Excepciones y límites conocidos

| Situación | Comportamiento de fuente/evidencia | Riesgo / siguiente prueba |
|---|---|---|
| Recepción excedida | Constraint compara Done con initialDemand y permite control por tipo | Verificar doNotCheckDone y evitar negativos/excedentes no autorizados |
| Recepción parcial | toReceive descuenta sólo recepciones activas; probado pedido 3, recibido 2 | Probar múltiples recepciones parciales sucesivas |
| Ubicación parcial | El saldo principal conserva lo no ubicado; medido 11 en principal y 1 en hija | Probar 2+ ubicaciones hijas y cambios/eliminación de detalles |
| Destino no descendiente | Constraint rechaza ubicación fuera de jerarquía | Añadir prueba negativa del servidor |
| Cantidad put-away negativa | El diálogo sólo crea si q>0, pero el extracto no muestra un constraint explícito quantity >= 0 | Probar escritura directa/servidor; no confiar sólo en UI |
| Marcar Put away incompleto | Acción pone flag; no aparece constraint de igualdad put = done | Aclarar significado operativo y probar faltantes de ubicación |
| Cancelación Done | Ledgers físicos/costo se vuelven inactivos; aceptado en #613 | Conservar historial; probar repetición concurrente/cancelación doble |
| Reserva cancelada Ready | Patcher local añade filtro explícito NOT canceled; aceptado en #609 | Reaplicar patcher en toda actualización de snapshot |
| FIFO / fecha de costo | CostLedger contiene otras reglas temporales críticas | Probar fecha, recálculo y movimientos fuera de orden en dossier CostLedger |
| WMS | Consumidor regional identificado, no aceptación | Auditar país, servicio, credenciales, datos y contrato |
| Permisos y recuperación | Cobertura no exhaustiva | Pruebas con usuarios/ubicaciones y corte/reintento |

## 11. Matriz de pruebas y evidencia

| Prueba | Nivel | Resultado observado | Evidencia |
|---|---|---|---|
| Lectura de módulos y composición | Fuente | Revisados los módulos de §1 y sus propietarios | Snapshot MyCompany 6.2 fijado |
| Compilación completa | Build | Aprobada | [Workflow #613](https://github.com/JavierGrecco/Rubrova/actions/runs/46119691078) |
| Cancelar Ready/no Done | Runtime + persistencia | Expected/planned/available conciliados y reemplazo Ready distinto | [Run #609](https://github.com/JavierGrecco/Rubrova/actions/runs/46113654320) |
| Pedido de 3, recibir 2, ubicar 1, cancelar | Runtime + persistencia | Principal/hija/costo/pendiente: 11/1/2.000/1 → 10/0/0/3 | [Run #613](https://github.com/JavierGrecco/Rubrova/actions/runs/46119691078); Receipt PIC/000002 → PIC/000005 |
| Pedido de 4, recibir 4 sin put-away, cancelar | Runtime + persistencia | 14/0/4.000/0 → 10/0/0/4 | [Run #613](https://github.com/JavierGrecco/Rubrova/actions/runs/46119691078); Receipt PIC/000003 → PIC/000006 |
| Lectura después del reinicio | Runtime | Principal 10, hija 0 y costo activo 0; la sonda no repitió operaciones | Marcador de conciliación emitido en ambas lecturas |
| Permisos, ubicación no descendiente, cantidades negativas, put-away múltiple, WMS, recepción inmediata, corte/reintento | Pendiente | No aceptado | Próxima matriz E2E |

La aceptación #613 se ejecutó con fixtures sintéticas sobre macOS ARM64 nativo. Linux/Docker fueron omitidos; Windows sólo tuvo validación sintáctica. No equivale a prueba contra base comercial real ni autorización productiva.

## 12. Decisión reuse-first y plan de integración

| Alternativa | Decisión | Motivo |
|---|---|---|
| Nativo configurable | **Usar** | Receipt, PurchaseOrderReceipt, estado, reservas, ledgers, put-away y costo ya resuelven el circuito |
| Extensión nativa | Sólo si una regla local o permiso concreto requiere ampliar el contrato | Aprovechar propiedades, eventos y formularios existentes |
| Adaptador externo | Para WMS/proveedor u otro ERP externo | Mantener la autoridad interna en MyCompany |
| Módulo Rubrova nuevo | No para duplicar Receipt/stock/costo | No hay brecha demostrada para reemplazar el motor nativo |
| Parche upstream | Mantener sólo el parche estrecho de ReceiptRes y sus pruebas | El ledger de reserva requería excluir cancelaciones y no había hook equivalente suficiente |
| Dependencia de terceros | No necesaria para el circuito base | Todo el flujo está dentro de MyCompany/lsFusion |

**Cambios prohibidos:** escribir SQL sobre tablas de ledgers; crear un segundo saldo de inventario; registrar a mano movimiento/costo al cancelar; usar active(Receipt) para filtrar la reserva Ready; tratar pedido, esperado, recibido, ubicado y costo como una sola cantidad.

**Pendientes que bloquean aceptación más amplia:** pruebas negativas de permisos y cantidades, múltiples ubicaciones hijas, recibos sucesivos parciales, recepción inmediata, conciliación con factura/deuda/pago, WMS y recuperación ante interrupciones.

## 13. Relaciones y rutas de lectura

- [Receipt](Receipt.md) y [PurchaseOrder](PurchaseOrder.md).
- [ResLedger](ResLedger.md), [InvLedger](InvLedger.md), [CostLedger](CostLedger.md).
- [Mapa de compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md).
- [Mapa de inventario, reservas y costos](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md).
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md).
- [Directorio de módulos](../MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md).
- [Parche de ReceiptRes](../../../patches/lsfusion/README.md) y [patcher](../../../scripts/platform/apply-rubrova-source-patches.py).
- [Manual técnico](../../ENGINEERING_MASTER.md), [resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) y [seguridad](../../SECURITY_POSTURE.md).

**Definición de terminado:** una persona puede modificar una parte de este ciclo identificando el módulo dueño, la frontera documental, el ledger productor, la configuración que lo condiciona y la prueba que debe volver a pasar; ningún dato/ledger se duplica por desconocer la capacidad nativa.
