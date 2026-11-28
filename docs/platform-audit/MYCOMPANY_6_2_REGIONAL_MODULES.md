# Inventario de módulos regionales de MyCompany 6.2

**Estado: inventariados; auditoría funcional módulo por módulo pendiente.**

Este documento identifica los 96 módulos ubicados bajo `vendor/mycompany/src/main/lsfusion/region` que no forman parte del cierre actual de `RubrovaCustom`. No se los descarta ni se los considera activables para Argentina por el solo hecho de existir.

## Conteo por región

| Región | Módulos |
|---|---:|
| Bulgaria | 7 |
| Polonia | 26 |
| Rusia | 63 |
| **Total** | **96** |

## Cómo leer las descripciones

- **Fuente leída parcialmente:** se abrió el archivo y se identificó parte de su contrato/implementación, pero falta seguir dependencias, acciones, efectos, errores y pruebas.
- **Solo inventariado:** la descripción inicial se infiere de la ruta y el nombre del módulo. No equivale a una revisión funcional.
- Las descripciones son de orientación para organizar la auditoría. No certifican cumplimiento normativo, integración operativa, disponibilidad de credenciales ni compatibilidad con servicios actuales.

## Inventario completo

| Región | Módulo | Área inicial | Capacidad identificada o inferida | Estado de fuente | Ruta |
|---|---|---|---|---|---|
| Bulgaria | `Zadarma` | Telefonía SIP | Autenticación, configuración y llamadas vía Zadarma | Fuente leída parcialmente | `region/bg/utils/sip/zadarma/Zadarma.lsf` |
| Bulgaria | `ZadarmaPBX` | Telefonía SIP | Consulta y registro de números/extensiones PBX | Fuente leída parcialmente | `region/bg/utils/sip/zadarma/ZadarmaPBX.lsf` |
| Bulgaria | `ZadarmaRecord` | Telefonía SIP | Grabaciones de llamadas | Solo inventariado | `region/bg/utils/sip/zadarma/ZadarmaRecord.lsf` |
| Bulgaria | `ZadarmaEmployee` | Telefonía SIP / RR. HH. | Vinculación de internos/usuarios con empleados | Solo inventariado | `region/bg/utils/sip/zadarma/masterdata/partners/ZadarmaEmployee.lsf` |
| Bulgaria | `ZadarmaEmployeeCall` | Telefonía SIP / RR. HH. | Relación entre llamadas y empleados | Solo inventariado | `region/bg/utils/sip/zadarma/masterdata/partners/ZadarmaEmployeeCall.lsf` |
| Bulgaria | `ZadarmaNotify` | Telefonía SIP | Notificaciones de eventos de llamada | Solo inventariado | `region/bg/utils/sip/zadarma/masterdata/partners/ZadarmaNotify.lsf` |
| Bulgaria | `ZadarmaWebRTC` | Telefonía SIP | Comunicaciones desde navegador mediante WebRTC | Solo inventariado | `region/bg/utils/sip/zadarma/ZadarmaWebRTC.lsf` |
| Polonia | `MyCompanyPl` | Regionalización | Configuración/ajustes generales para Polonia | Solo inventariado | `region/pl/MyCompanyPl.lsf` |
| Polonia | `InvoicePrintInitialPl` | Impresión fiscal/documental | Plantilla inicial de factura para Polonia | Solo inventariado | `region/pl/invoicing/invoices/print/InvoicePrintInitialPl.lsf` |
| Polonia | `InvoicePrintPl` | Impresión fiscal/documental | Formato polaco de factura | Solo inventariado | `region/pl/invoicing/invoices/print/InvoicePrintPl.lsf` |
| Polonia | `KSeF` | Facturación electrónica / KSeF | Configuración de API, autenticación y tokens de acceso KSeF | Fuente leída parcialmente | `region/pl/invoicing/ksef/KSeF.lsf` |
| Polonia | `KSeFCertificate` | Facturación electrónica / certificados | Certificados usados para autenticación/cifrado KSeF | Solo inventariado | `region/pl/invoicing/ksef/KSeFCertificate.lsf` |
| Polonia | `KSeFScheduler` | Facturación electrónica / planificación | Automatización de tareas KSeF | Solo inventariado | `region/pl/invoicing/ksef/KSeFScheduler.lsf` |
| Polonia | `KSeFSession` | Facturación electrónica / sesiones | Apertura y gestión de sesiones KSeF; cifrado de clave y datos de sesión | Fuente leída parcialmente | `region/pl/invoicing/ksef/KSeFSession.lsf` |
| Polonia | `KSeFToken` | Facturación electrónica / credenciales | Autorizaciones, permisos y tokens KSeF; renovación/consulta de estado | Fuente leída parcialmente | `region/pl/invoicing/ksef/KSeFToken.lsf` |
| Polonia | `KSeFBill` | Facturación electrónica / compras | Integración de facturas de proveedor con KSeF | Solo inventariado | `region/pl/invoicing/ksef/bills/KSeFBill.lsf` |
| Polonia | `KSeFFaktura` | Facturación electrónica / facturas | Modelo de datos de factura KSeF | Solo inventariado | `region/pl/invoicing/ksef/faktury/KSeFFaktura.lsf` |
| Polonia | `KSeFFakturaFA3` | Facturación electrónica / esquema FA(3) | Versión de estructura de factura FA(3) | Solo inventariado | `region/pl/invoicing/ksef/faktury/KSeFFakturaFA3.lsf` |
| Polonia | `KSeFFakturaQuery` | Facturación electrónica / consulta | Consulta/descarga de facturas KSeF | Solo inventariado | `region/pl/invoicing/ksef/faktury/KSeFFakturaQuery.lsf` |
| Polonia | `KSeFFakturaSend` | Facturación electrónica / envío | Envío de facturas al servicio KSeF | Solo inventariado | `region/pl/invoicing/ksef/faktury/KSeFFakturaSend.lsf` |
| Polonia | `KSeFInvoice` | Facturación electrónica / ventas | Relación de facturas de venta con KSeF | Solo inventariado | `region/pl/invoicing/ksef/invoices/KSeFInvoice.lsf` |
| Polonia | `KSeFInvoiceSend` | Facturación electrónica / envío | Envío de facturas de venta a KSeF | Solo inventariado | `region/pl/invoicing/ksef/invoices/KSeFInvoiceSend.lsf` |
| Polonia | `TaxInitialPl` | Impuestos | Datos iniciales de impuestos para Polonia | Solo inventariado | `region/pl/invoicing/taxes/TaxInitialPl.lsf` |
| Polonia | `LegalEntityImportPl` | Datos maestros / entidades | Importación de datos de entidades legales polacas | Solo inventariado | `region/pl/masterdata/partners/LegalEntityImportPl.lsf` |
| Polonia | `LegalEntityPl` | Datos maestros / entidades | Datos y validaciones de entidades legales polacas | Solo inventariado | `region/pl/masterdata/partners/LegalEntityPl.lsf` |
| Polonia | `PartnerPl` | Datos maestros / socios | Extensión regional de socios | Solo inventariado | `region/pl/masterdata/partners/PartnerPl.lsf` |
| Polonia | `RegonDaneSzukajPodmity` | Registro REGON | Búsqueda de entidades mediante REGON | Solo inventariado | `region/pl/masterdata/partners/regon/RegonDaneSzukajPodmity.lsf` |
| Polonia | `RegonZaloguj` | Registro REGON | Autenticación SOAP al servicio REGON; endpoint fuente identificado | Fuente leída parcialmente | `region/pl/masterdata/partners/regon/RegonZaloguj.lsf` |
| Polonia | `PurchaseOrderPrintInitialPl` | Impresión de compras | Plantilla inicial de pedido de compra | Solo inventariado | `region/pl/purchase/orders/print/PurchaseOrderPrintInitialPl.lsf` |
| Polonia | `PurchaseOrderPrintPl` | Impresión de compras | Formato polaco de pedido de compra | Solo inventariado | `region/pl/purchase/orders/print/PurchaseOrderPrintPl.lsf` |
| Polonia | `SalesOrderPrintInitialPl` | Impresión de ventas | Plantilla inicial de pedido de venta | Solo inventariado | `region/pl/sales/orders/print/SalesOrderPrintInitialPl.lsf` |
| Polonia | `SalesOrderPrintPl` | Impresión de ventas | Formato polaco de pedido de venta | Solo inventariado | `region/pl/sales/orders/print/SalesOrderPrintPl.lsf` |
| Polonia | `UtilsPl` | Utilidades regionales | Funciones auxiliares para configuración regional polaca | Solo inventariado | `region/pl/utils/UtilsPl.lsf` |
| Rusia | `MyCompanyRu` | Regionalización | Configuración/ajustes generales para Rusia | Solo inventariado | `region/ru/MyCompanyRu.lsf` |
| Rusia | `EnterpriseData` | Intercambio de datos | Integración con EnterpriseData | Solo inventariado | `region/ru/integration/enterprisedata/EnterpriseData.lsf` |
| Rusia | `EnterpriseDataSend` | Intercambio de datos | Exportación de datos hacia EnterpriseData | Solo inventariado | `region/ru/integration/enterprisedata/EnterpriseDataExport.lsf` |
| Rusia | `EnterpriseDataReceive` | Intercambio de datos | Importación de datos desde EnterpriseData | Solo inventariado | `region/ru/integration/enterprisedata/EnterpriseDataImport.lsf` |
| Rusia | `EnterpriseDataBankAccount` | Intercambio de datos / bancos | Intercambio de cuentas bancarias | Solo inventariado | `region/ru/integration/enterprisedata/invoicing/accounts/bank/EnterpriseDataBankAccount.lsf` |
| Rusia | `EnterpriseDataBank` | Intercambio de datos / bancos | Intercambio de entidades bancarias | Solo inventariado | `region/ru/integration/enterprisedata/invoicing/banks/EnterpriseDataBank.lsf` |
| Rusia | `EnterpriseDataIncomingPayment` | Intercambio de datos / cobranzas | Intercambio de pagos entrantes | Solo inventariado | `region/ru/integration/enterprisedata/invoicing/payments/incoming/EnterpriseDataIncomingPayment.lsf` |
| Rusia | `EnterpriseDataOutgoingPayment` | Intercambio de datos / pagos | Intercambio de pagos salientes | Solo inventariado | `region/ru/integration/enterprisedata/invoicing/payments/outgoing/EnterpriseDataOutgoingPayment.lsf` |
| Rusia | `EnterpriseDataOutgoingPaymentInterpay` | Intercambio de datos / pagos | Adaptación de pagos a Interpay | Solo inventariado | `region/ru/integration/enterprisedata/invoicing/payments/outgoing/EnterpriseDataOutgoingPaymentInterpay.lsf` |
| Rusia | `EnterpriseDataPartner` | Intercambio de datos / socios | Intercambio de socios | Solo inventariado | `region/ru/integration/enterprisedata/masterdata/partners/EnterpriseDataPartner.lsf` |
| Rusia | `FusionWMS` | Depósito / WMS | Interfaz de integración con FusionWMS para datos de socios, unidades, categorías, productos, códigos de barras, recepciones y despachos | Fuente leída parcialmente | `region/ru/integration/fusionWMS/FusionWMS.lsf` |
| Rusia | `InventoryRu` | Inventario / regionalización | Ajustes regionales de inventario | Solo inventariado | `region/ru/inventory/InventoryRu.lsf` |
| Rusia | `LocationEmployeeRu` | Inventario / ubicaciones | Relación de empleados con ubicaciones | Solo inventariado | `region/ru/inventory/locations/LocationEmployeeRu.lsf` |
| Rusia | `ReceiptPrintInitialRu` | Impresión de inventario | Plantilla inicial de recepción | Solo inventariado | `region/ru/inventory/receipts/print/ReceiptPrintInitialRu.lsf` |
| Rusia | `ReceiptPrintRu` | Impresión de inventario | Formato de recepción para Rusia | Solo inventariado | `region/ru/inventory/receipts/print/ReceiptPrintRu.lsf` |
| Rusia | `ShipmentPrintInitialRu` | Impresión de inventario | Plantilla inicial de despacho | Solo inventariado | `region/ru/inventory/shipments/print/ShipmentPrintInitialRu.lsf` |
| Rusia | `ShipmentPrintRu` | Impresión de inventario | Formato de despacho para Rusia | Solo inventariado | `region/ru/inventory/shipments/print/ShipmentPrintRu.lsf` |
| Rusia | `InvoicingRu` | Facturación / regionalización | Ajustes regionales de facturación | Solo inventariado | `region/ru/invoicing/InvoicingRu.lsf` |
| Rusia | `BankRu` | Bancos | Datos y configuración bancaria regional | Solo inventariado | `region/ru/invoicing/banks/BankRu.lsf` |
| Rusia | `BillReceiptPrintRu` | Documentación / recepción | Impresión de factura asociada a recepción | Solo inventariado | `region/ru/invoicing/inventory/receipts/BillReceiptPrintRu.lsf` |
| Rusia | `InvoicePrintInitialRu` | Impresión de facturación | Plantilla inicial de factura | Solo inventariado | `region/ru/invoicing/invoices/print/InvoicePrintInitialRu.lsf` |
| Rusia | `InvoicePrintRu` | Impresión de facturación | Formato regional de factura | Solo inventariado | `region/ru/invoicing/invoices/print/InvoicePrintRu.lsf` |
| Rusia | `IncomingPaymentPrintInitialRu` | Impresión de cobranzas | Plantilla inicial de pago entrante | Solo inventariado | `region/ru/invoicing/payments/incoming/print/IncomingPaymentPrintInitialRu.lsf` |
| Rusia | `IncomingPaymentPrintRu` | Impresión de cobranzas | Formato regional de pago entrante | Solo inventariado | `region/ru/invoicing/payments/incoming/print/IncomingPaymentPrintRu.lsf` |
| Rusia | `OutgoingPaymentPrintInitialRu` | Impresión de pagos | Plantilla inicial de pago saliente | Solo inventariado | `region/ru/invoicing/payments/outgoing/print/OutgoingPaymentPrintInitialRu.lsf` |
| Rusia | `OutgoingPaymentPrintRu` | Impresión de pagos | Formato regional de pago saliente | Solo inventariado | `region/ru/invoicing/payments/outgoing/print/OutgoingPaymentPrintRu.lsf` |
| Rusia | `TaxInitialRu` | Impuestos | Datos iniciales de impuestos para Rusia | Solo inventariado | `region/ru/invoicing/taxes/TaxInitialRu.lsf` |
| Rusia | `ItemMarkRu` | Datos maestros / marcado | Extensión de artículo para identificación/marcado obligatorio | Solo inventariado | `region/ru/masterdata/items/ItemMarkRu.lsf` |
| Rusia | `ItemTnved` | Datos maestros / clasificación | Clasificación TN VED de mercancías | Solo inventariado | `region/ru/masterdata/items/ItemTnved.lsf` |
| Rusia | `IndividualRu` | Datos maestros / personas | Datos regionales de personas físicas | Solo inventariado | `region/ru/masterdata/partners/IndividualRu.lsf` |
| Rusia | `LegalEntityImportRu` | Datos maestros / entidades | Importación de entidades legales rusas | Solo inventariado | `region/ru/masterdata/partners/LegalEntityImportRu.lsf` |
| Rusia | `LegalEntityRu` | Datos maestros / entidades | Datos regionales de entidades legales | Solo inventariado | `region/ru/masterdata/partners/LegalEntityRu.lsf` |
| Rusia | `PartnerRu` | Datos maestros / socios | Extensión regional de socios | Solo inventariado | `region/ru/masterdata/partners/PartnerRu.lsf` |
| Rusia | `DaDataAuthentication` | Datos maestros / DaData | Autenticación con servicio DaData | Solo inventariado | `region/ru/masterdata/partners/dadata/DaDataAuthentication.lsf` |
| Rusia | `DaDataLegalEntityFind` | Datos maestros / DaData | Búsqueda de entidades legales mediante DaData | Solo inventariado | `region/ru/masterdata/partners/dadata/DaDataLegalEntityFind.lsf` |
| Rusia | `UomRu` | Datos maestros / unidades | Unidades de medida regionales | Solo inventariado | `region/ru/masterdata/uom/UomRu.lsf` |
| Rusia | `PurchaseRu` | Compras / regionalización | Ajustes regionales de compras | Solo inventariado | `region/ru/purchase/PurchaseRu.lsf` |
| Rusia | `PurchaseOrderReceiptPrintRu` | Impresión de compras/recepciones | Formato de recepción vinculada a pedido de compra | Solo inventariado | `region/ru/purchase/inventory/receipts/orders/PurchaseOrderReceiptPrintRu.lsf` |
| Rusia | `PurchaseOrderPrintInitialRu` | Impresión de compras | Plantilla inicial de pedido de compra | Solo inventariado | `region/ru/purchase/orders/print/PurchaseOrderPrintInitialRu.lsf` |
| Rusia | `PurchaseOrderPrintRu` | Impresión de compras | Formato de pedido de compra | Solo inventariado | `region/ru/purchase/orders/print/PurchaseOrderPrintRu.lsf` |
| Rusia | `PosDashboardCRPT` | POS / marcado | Flujo POS vinculado a CRPT y control de productos marcados | Solo inventariado | `region/ru/retail/pos/PosDashboardCRPT.lsf` |
| Rusia | `PosDashboardRu` | POS / regionalización | Ajustes regionales del POS | Solo inventariado | `region/ru/retail/pos/PosDashboardRu.lsf` |
| Rusia | `CashRegisterAtol` | Controlador fiscal ATOL | Driver concreto: apertura/cierre de turno, report X, ingreso/egreso de efectivo, venta y devolución vía API | Fuente leída parcialmente | `region/ru/retail/pos/cashregister/CashRegisterAtol.lsf` |
| Rusia | `SalesRu` | Ventas / regionalización | Ajustes regionales de ventas | Solo inventariado | `region/ru/sales/SalesRu.lsf` |
| Rusia | `SalesOrderShipmentPrintRu` | Impresión de ventas/despachos | Formato de despacho vinculado a pedido de venta | Solo inventariado | `region/ru/sales/inventory/shipments/orders/SalesOrderShipmentPrintRu.lsf` |
| Rusia | `SalesOrderPrintInitialRu` | Impresión de ventas | Plantilla inicial de pedido de venta | Solo inventariado | `region/ru/sales/orders/print/SalesOrderPrintInitialRu.lsf` |
| Rusia | `SalesOrderPrintRu` | Impresión de ventas | Formato de pedido de venta | Solo inventariado | `region/ru/sales/orders/print/SalesOrderPrintRu.lsf` |
| Rusia | `SalesPricelistPrintInitialRu` | Impresión de ventas | Plantilla inicial de lista de precios | Solo inventariado | `region/ru/sales/pricelists/print/SalesPricelistPrintInitialRu.lsf` |
| Rusia | `CRPT` | Marcado y trazabilidad | Cliente base para servicios CRPT / Честный знак y CDN; verificación de nodos | Fuente leída parcialmente | `region/ru/utils/gov/crpt/CRPT.lsf` |
| Rusia | `CRPTCodesOffline` | Marcado y trazabilidad | Gestión/verificación offline de códigos CRPT | Solo inventariado | `region/ru/utils/gov/crpt/CRPTCodesOffline.lsf` |
| Rusia | `CRPTCodesOnline` | Marcado y trazabilidad | Consulta online de estado/validez/venta/bloqueo/vencimiento de códigos | Fuente leída parcialmente | `region/ru/utils/gov/crpt/CRPTCodesOnline.lsf` |
| Rusia | `Wazzup` | Mensajería | Configuración y autenticación API Wazzup | Solo inventariado | `region/ru/utils/messenger/wazzup/Wazzup.lsf` |
| Rusia | `WazzupChat` | Mensajería | Canal/chat Wazzup | Solo inventariado | `region/ru/utils/messenger/wazzup/WazzupChat.lsf` |
| Rusia | `WazzupLead` | CRM / mensajería | Asociación de conversaciones Wazzup con leads | Solo inventariado | `region/ru/utils/messenger/wazzup/crm/leads/WazzupLead.lsf` |
| Rusia | `WazzupWebhook` | CRM / mensajería | Recepción de eventos webhook Wazzup | Solo inventariado | `region/ru/utils/messenger/wazzup/crm/leads/WazzupWebhook.lsf` |
| Rusia | `WazzupPartner` | Datos maestros / mensajería | Asociación de conversaciones Wazzup con socios | Solo inventariado | `region/ru/utils/messenger/wazzup/masterdata/partners/WazzupPartner.lsf` |
| Rusia | `CryptoPro` | Certificados y firma | Consulta de certificados CryptoPro, metadatos y firma | Fuente leída parcialmente | `region/ru/utils/security/cryptopro/CryptoPro.lsf` |
| Rusia | `Mango` | Telefonía SIP | Configuración y API Mango; firma/hash de solicitud | Fuente leída parcialmente | `region/ru/utils/sip/mango/Mango.lsf` |
| Rusia | `MangoPBX` | Telefonía SIP | Extensión de PBX Mango | Solo inventariado | `region/ru/utils/sip/mango/MangoPBX.lsf` |
| Rusia | `MangoRecord` | Telefonía SIP | Registro/grabación de llamadas | Solo inventariado | `region/ru/utils/sip/mango/MangoRecord.lsf` |
| Rusia | `MangoEmployee` | Telefonía SIP / RR. HH. | Vinculación de empleados con internos Mango | Solo inventariado | `region/ru/utils/sip/mango/masterdata/partners/MangoEmployee.lsf` |
| Rusia | `MangoEmployeeCall` | Telefonía SIP / RR. HH. | Relación entre llamadas y empleados | Solo inventariado | `region/ru/utils/sip/mango/masterdata/partners/MangoEmployeeCall.lsf` |
| Rusia | `MangoEventsCall` | Telefonía SIP | Eventos de llamadas Mango | Solo inventariado | `region/ru/utils/sip/mango/masterdata/partners/MangoEventsCall.lsf` |

## Hallazgos que cambian el análisis de reutilización

### Polonia: KSeF y REGON

La familia KSeF no es un simple formato de impresión: las fuentes revisadas contienen configuración del servicio, autenticación, certificados, tokens, permisos, sesiones y estructuras de facturas. Los nombres del código y los contratos muestran una integración de facturación electrónica dirigida al esquema polaco. También hay conexión SOAP a REGON para búsqueda/autenticación de entidades.

**Conclusión:** estudiar sus mecanismos técnicos reutilizables, pero no considerarlos una implementación de ARCA ni una adaptación argentina. Las reglas, certificados, esquemas y autoridades son diferentes.

### Rusia: ATOL, CRPT, CryptoPro, DaData, Mango y Wazzup

- `CashRegisterAtol` contiene un driver concreto con operaciones de apertura/cierre de turno, reporte X, ingreso/retiro de efectivo, venta y devolución. Esto demuestra que la extensión regional va más allá del contrato abstracto `CashRegisterFiscal` de la base, pero está vinculada a ATOL y su API rusa; no demuestra soporte de un controlador homologado en Argentina.
- `CRPT` y `CRPTCodesOnline` implementan acceso a servicios de marcado/consulta de códigos, verificando estados como validez, venta, bloqueo y vencimiento. Está relacionado con el régimen ruso de identificación/marcado, no debe confundirse con GTIN ni con un código fiscal argentino.
- `CryptoPro` gestiona certificados y metadatos de certificados regionales. Su uso, proveedor y compatibilidad criptográfica deben analizarse por separado del módulo genérico `Crypto`.
- `DaData` aporta autenticación y búsqueda de entidades legales rusas.
- `Mango` integra telefonía y PBX; `Wazzup` integra mensajería y webhooks con CRM/socios.
- `FusionWMS` expone una integración de depósito para maestros de socios, unidades, categorías, artículos/códigos de barras, recepciones y despachos.

### Bulgaria: Zadarma

La familia Zadarma abarca configuración, PBX, grabaciones, empleados, notificaciones y WebRTC. Debe revisarse como una integración de telefonía completa: autenticación, webhooks, llamadas entrantes/salientes, identificación de contacto, almacenamiento de grabaciones, estados y permisos.

## Decisiones bloqueadas hasta terminar el análisis

1. No activar ninguno de estos módulos en Rubrova por defecto.
2. No desarrollar adaptadores propios de fiscalidad, certificados, telefonía, mensajería, WMS o identidad sin haber leído primero el módulo upstream y sus dependencias.
3. No asumir que un conector funciona sólo porque compila: hace falta verificar versión del servicio externo, autenticación, contrato, errores, reintentos, idempotencia, logs, manejo de secretos y permisos.
4. Para Argentina, evaluar por separado la reutilización del patrón técnico y la validez normativa/operativa local.
5. Revisar los nueve documentos KSeF que sólo aparecen en la variante polaca y los dos documentos rusos adicionales de Mango y marcado; el paquete inglés no representa por sí solo toda la documentación regional.

## Siguientes tareas de auditoría

- Leer los 96 módulos, no sólo los que tienen una descripción conocida.
- Resolver las dependencias de cada módulo regional y su punto de entrada.
- Asociar cada módulo con sus páginas de documentación, APIs, servicios, credenciales, esquemas, licencias y proveedores.
- Identificar los datos que importa/exporta, efectos sobre documentos y ledgers, y comportamiento ante duplicados/errores.
- Registrar qué partes son genéricas y cuáles están acopladas a cada país/proveedor.
- Determinar mediante evidencia qué piezas técnicas son reutilizables en Argentina y cuáles deben quedar excluidas.

**Estado de puerta:** ABIERTA. El inventario de los 96 módulos no equivale al cierre de su análisis funcional.
