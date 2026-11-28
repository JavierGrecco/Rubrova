# Ficha de integración — Receipt


**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Composición:** dentro del cierre actual de RubrovaCustom, según el catálogo estructural.  
**Evidencia:** lectura de fuente estática; no equivale a runtime, conciliación ni aceptación.

**Identificador real:** MODULE Receipt · **Namespace:** Inventory  
**Fuente:** [Receipt.lsf](../../../vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf#L1-L253)  
**Dossiers:** [Inventario](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) §2; [compras y reposición](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §3.

## 1. Resumen de 2 minutos

Receipt define el **documento base de recepción** y sus líneas. No concentra por sí solo las transiciones ni los ledgers: la preparación, recepción efectiva, reserva, movimiento físico, costo y put-away están distribuidos en módulos relacionados.

**REQUIRE directos:** System, Time, DateUtils, FileUtils, InventorySettings, Location, Partner, Product, LocationEmployee, ReceiptType, ItemPurchase, PartnerPurchase, BarCode, Doc, ResLedger.

**Consumidores directos:** Inventory, ReceiptFilter, ReceiptReady, ReceiptSelection, ReceiptPackage, ShipmentAcceptanceReceipt, FusionWMS (regional) y SalesPricelistPrintReceipt.

## 2. Responsabilidad y entidades

- Receipt: tipo, indicador immediate, fecha programada, numeración, ubicación, proveedor, referencia del proveedor y nota.
- ReceiptLine: documento propietario, producto, unidad derivada del producto, índice y demanda inicial.
- La empresa del documento se deriva de la empresa asociada a la ubicación.
- El tipo propone configuración por defecto, incluyendo ubicación y comportamiento.
- Usa utilidades de documento, historia, comentarios, archivos y acceso por ubicación.

No crear una segunda entidad de recepción para resolver un canal externo sin demostrar primero que el contrato nativo no puede extenderse.

## 3. Validaciones y configuración

- El socio seleccionado debe cumplir rol de proveedor (isVendor).
- El producto debe permitir compra (canBePurchased).
- La ubicación no puede ser de uso interno.
- initialDemand no puede ser negativo y debe respetar maxQuantity(type(receipt)) cuando el tipo define un máximo.
- type, location y vendor tienen defaults controlados.
- La recepción inmediata se crea mediante immediateReceipt(), abre una sesión nueva, marca immediate y muestra el formulario de edición.

## 4. Interfaz y operaciones

El formulario receipt muestra cabecera y líneas; la edición depende de readonly(r). El listado receipts permite alta/edición/eliminación sujetas al mismo control. Hay navegación receipts, historial de documento/línea, comentarios, archivos y control de acceso por ubicación.

La acción copy ejecuta APPLY, comprueba cancelación y crea una nueva sesión/documento copiando tipo, ubicación, proveedor, nota, modo inmediato y líneas. No modifica el documento original.

## 5. Ciclo de vida y módulos relacionados

| Aspecto | Módulo relacionado | Responsabilidad |
|---|---|---|
| Tipo/configuración | ReceiptType | Defaults y política |
| Listo | ReceiptReady | Transición a listo y efecto de esperado |
| Reserva/esperado | ReceiptRes | Registro en ResLedger; signo negativo |
| Recepción efectiva | ReceiptDone | Cantidad real y fecha/hora |
| Movimiento físico | ReceiptInv | Entrada real a InvLedger |
| Costo | ReceiptCost | Entrada a CostLedger |
| Ubicación interna | ReceiptPutAway y módulos asociados | Distribución entre ubicación principal y descendientes |
| Cancelación | ReceiptCanceled | Estado y retiro del efecto activo según el circuito |

Demanda inicial, cantidad esperada, cantidad recibida, cantidad ubicada y cantidad valorizada son datos distintos. La distribución interna debe evitar doble conteo.

## 6. Integraciones y contratos

- Compras integra mediante PurchaseOrderReceipt y conserva la relación con pedido/líneas.
- Facturación de proveedor se vincula mediante PurchaseOrderBill/Bill; la política depende del pedido.
- FusionWMS aparece como consumidor regional, pero eso no demuestra compatibilidad ni adecuación argentina. Revisarlo individualmente y no asumirlo activo.
- Receipt requiere ResLedger, no InvLedger ni CostLedger directamente. ReceiptInv y ReceiptCost son productores específicos de esos efectos.
- No se declara aquí una API externa propia; no inferir HTTP a partir de un consumidor WMS.

## 7. Permisos y datos maestros

La ubicación participa del control de acceso por ubicación; proveedor y producto se validan por rol/capacidad; historia y archivos usan mecanismos comunes. Comprobar permisos de acción, empresa, ubicación y líneas en runtime, no sólo la presencia del formulario.

## 8. Pruebas mínimas

1. Recepción planificada con demanda, estado listo y esperado.
2. Recepción inmediata sin reserva previa.
3. Proveedor no habilitado, producto no comprable y ubicación interna: rechazo de servidor.
4. Recepción parcial y múltiples recepciones contra un pedido.
5. Recepción efectiva, movimiento físico y costo conciliados por línea.
6. Put-away parcial en varias ubicaciones, sin duplicar saldos.
7. Cancelación, copia, edición y usuario sin acceso a la ubicación.
8. Corte/reintento entre confirmación y registro de ledgers.

**Estado de aceptación:** pendiente de runtime, WMS y conciliación E2E.

## 9. Lecturas siguientes

- [InvLedger](InvLedger.md), [ResLedger](ResLedger.md) y [CostLedger](CostLedger.md).
- [Compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) §§3–4 y [facturación](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md).
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) para Product, Partner, Company, Location y unidades.
- [Utilidades](../MYCOMPANY_6_2_UTILITY_MODULES.md) para Doc, FileUtils, BarCode y numeración.
- [Resiliencia de integraciones](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) para WMS, idempotencia y estados inciertos.

**Definición de terminado:** reconstruir cada línea desde pedido proveedor hasta recepción, stock físico, costo y factura, con parciales, cancelaciones y permisos probados.


## 8.1 Aceptación runtime de cancelación posterior a Done (#17)

La fixture efímera de CI crea dos órdenes independientes sobre un depósito aislado con saldo inicial de 10 unidades y una ubicación hija vacía. El primer pedido es de 3 unidades: se reciben 2 y queda 1 pendiente; el segundo pedido de 4 unidades se recibe completo. Ambos usan precio de compra de $1.000 por unidad y las acciones nativas de recepción.

| Escenario | Momento | Depósito principal | Ubicación hija | Costo de la recepción |
|---|---|---:|---:|---:|
| Recibir 2 y ubicar 1 en hija | Después de Done/put-away | 11 | 1 | 2.000 |
| Mismo escenario | Después de cancelar | 10 | 0 | 0 |
| Recibir 4 sin put-away | Después de Done | 14 | 0 | 4.000 |
| Mismo escenario | Después de cancelar | 10 | 0 | 0 |

Estos saldos e importes son **objetivos de aceptación**, todavía no resultados medidos. El inspector exige tolerancia máxima de 0,001, comprueba que la cantidad ubicada no se duplique entre origen y destino y exige una recepción Ready distinta por la cantidad que vuelve a quedar pendiente. La misma sonda se ejecuta durante el arranque inicial y, en modo de consulta, después de reiniciar el servidor.

La fixture crea documentos de compra, registra cantidades recibidas, crea el detalle nativo de put-away y ejecuta las acciones nativas de validar, ubicar y cancelar. No inserta, elimina ni modifica manualmente registros de los ledgers físicos, de ubicación interna o de costo.

La aprobación sólo acepta el circuito sintético de recepción física/costo en MyCompany 6.2; no equivale a conciliación con una base comercial real ni a homologación productiva.
