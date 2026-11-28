# Ficha de integración — Product

**Fuente fijada:** MyCompany 6.2 · commit `d21ca6978717b98b6300d90267f9767db7414008`  
**Composición:** incluido en el cierre actual de `RubrovaCustom`, según el catálogo estructural.  
**Evidencia:** revisión estática de fuente; runtime, conciliación y aceptación deben probarse aparte.

**Identificador:** `MODULE Product` · **Namespace:** `MasterData`  
**Fuente:** [Product.lsf](../../../vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf#L1-L124)  
**Dossier:** [Datos maestros y relaciones transversales](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§4–7.

## 1. Lectura de 2 minutos

`Product` es la especialización física de `Item`. Añade peso, volumen y país de origen; hereda de Item identidad, categoría, nombre, unidad, activo/archivado, referencia, atributos y comportamiento común. No crear un segundo catálogo de productos para inventario, ventas o compras.

**REQUIRE directos:** MasterData, Item, CountryP.

**Consumidores directos:** Adjustment, CostLedger, CostProduct, InvLedger, LocationProduct, Lot, ProductSku, Package, PickingTask, Receipt, Scrap, Shipment, Bill, Invoice, InvoicePrint, Bom, MasterDataP, ItemAPI, ItemCostImport, ItemVariant, BarCode, ProductGtin, ProductImport, ProductLot, PurchaseOrderBill y FusionWMS (regional).

## 2. Modelo y autoridad

- Clase `Product` extiende `Item`.
- Propiedades propias: `weight` NUMERIC[11,3], `volume` NUMERIC[11,3], `countryOrigin` Country.
- Product comparte identidad base, category, name, uom, archived/active, reference y demás propiedades de Item.
- La distinción Product/Service determina si puede generar movimiento de inventario; no es sólo una etiqueta.
- `ProductGtin` y `FusionWMS` aparecen como consumidores fuera de los flujos básicos; revisar composición antes de utilizarlos.

## 3. Interacción

La fuente extiende el formulario `item` con peso, volumen y país de origen y el listado `items` con propiedades de producto. Define formulario/listado `products`, con filtro por categoría en árbol, filtro de activos/archivados y alta/edición/eliminación. `newProduct` puede crear un producto desde categoría o nombre y muestra el editor item.

La acción `copy` ejecuta APPLY, crea una nueva sesión/entidad y copia las propiedades propias junto con la copia nativa de Item. No es una modificación del original.

## 4. Integración con Item y consumidores

| Tema | Módulo relacionado | Responsabilidad |
|---|---|---|
| Identidad/categoría/nombre/unidad | Item / Category | Propiedad maestra y reglas base |
| Compra/venta | ItemPurchase / ItemSales | Capacidad comercial; no inferirla por ser Product |
| Atributos/variantes | ItemAttribute / ItemVariant | Esquema y herencia de atributos |
| Código/pack/UoM | BarCode / ItemUom / ItemPack | Escaneo y conversión de unidades |
| Lote/serie | ProductLot / CategoryLot / Lot | Trazabilidad del inventario |
| Inventario | Receipt / Shipment / Adjustment / Scrap / InvLedger | Movimiento físico derivado |
| Costo | ItemCost / CostLedger / CostProduct | Costo planificado versus valoración de ledger |
| Venta/compra/factura | SalesOrder / PurchaseOrder / Invoice / Bill | Documentos comerciales consumen Product/Item |
| Fabricación | Bom | Lista de materiales y consumo |

Product requiere Item y CountryP; el módulo base Item es el dueño de buena parte del modelo y del comportamiento. Extender Item/Product según la responsabilidad, no replicar entidades o unidades.

## 5. Integración, importación y APIs

El mapa Master Data identifica ItemAPI, ItemAttributeAPI y ProductImport como mecanismos a revisar. Esta fuente Product no declara una API propia. No inferir que ProductGtin esté cargado ni que un GTIN sea clave única por el solo hecho de existir módulo consumidor.

Los imports deben respetar IDs/códigos externos, categoría, unidad, variantes, lotes y relaciones; definir política de duplicados y actualizaciones sin sobrescribir datos manuales sin regla explícita.

## 6. Riesgos

- tratar Product y Service como equivalentes;
- duplicar SKU, barcode, pack o unidad;
- cambiar categoría/unidad tras documentos o ledgers;
- archivar vs borrar entidades referenciadas;
- variantes múltiples o jerárquicas con atributos heredados;
- asumir GTIN/WMS/normalización internacional lista para Argentina;
- confundir ItemCost planificado con FIFO/AVCO del CostLedger.

## 7. Pruebas mínimas

1. Alta por categoría y alta por nombre; edición/copia/archivo.
2. Categoría requerida, unidad por defecto e herencia.
3. Atributos obligatorios y valores válidos para categoría.
4. Variante/primario y cambios de categoría/atributos.
5. UoM, ratios, packs, barcode y precisión.
6. Compra/venta habilitada y rechazada.
7. Producto referenciado por recepción, despacho, factura, lote y BOM; comprobar integridad al archivar.
8. Importación/API, claves externas, duplicados y reintentos.
9. WMS/GTIN sólo si se prueba el módulo y se acepta su uso.

**Aceptación:** dossier declara fuentes principales leídas para Master Data; runtime, importadores, extensiones y adecuación argentina pendientes.

## 8. Lecturas siguientes

- [Partner](Partner.md), [Receipt](Receipt.md), [SalesOrder](SalesOrder.md), [PurchaseOrder](PurchaseOrder.md), [Invoice](Invoice.md), [Bill](Bill.md).
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§4–7 y 10.
- [Inventario](../MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md), [ventas](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md), [compras](../MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) y [fabricación](../MYCOMPANY_6_2_FUNCTIONAL_MAP.md).
- [Utilities](../MYCOMPANY_6_2_UTILITY_MODULES.md) para barcode/imagen/historial; [seguridad](../../SECURITY_POSTURE.md).

**Regla de integración:** Item/Product es identidad maestra compartida; los documentos/ledgers son dueños de sus hechos transaccionales.
