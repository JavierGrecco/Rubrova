# Ficha de integración — Partner

**Fuente fijada:** MyCompany 6.2 · commit `d21ca6978717b98b6300d90267f9767db7414008`  
**Composición:** incluido en el cierre actual de `RubrovaCustom`, según el catálogo estructural.  
**Evidencia:** revisión estática de fuente; runtime, conciliación y aceptación deben probarse aparte.

**Identificador:** `MODULE Partner` · **Namespace:** `MasterData`  
**Fuente:** [Partner.lsf](../../../vendor/mycompany/src/main/lsfusion/masterdata/partners/Partner.lsf#L1-L202)  
**Dossier:** [Datos maestros y relaciones transversales](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§2–3, 9–12.

## 1. Lectura de 2 minutos

`Partner` es la clase abstracta de identidad común para socios/personas/organizaciones que participan del negocio. Centraliza nombre, datos de contacto, dirección, país, clasificación genérica y archivado. Cliente/proveedor son roles comerciales agregados por extensiones; no son el tipo legal.

**REQUIRE directos:** Utils, MetaNumerator, Input, Icon, Comments, CountryP.

**Consumidores directos:** InvLedger, PickingTask, Receipt, Shipment, Account, BankAccountImport, CashAccountImport, BillType, InvoiceType, Debt, DebtPartner, IncomingPayment, OutgoingPayment, PaymentCalendar, Department, LegalEntity, PartnerAttribute, PartnerCall, PartnerCommunication, PartnerGeo, PartnerHistory, PartnerPurchase, PartnerTag, PartnerUom, Individual, KSeFBill (regional polaco), PartnerPl (regional polaco), FusionWMS (regional ruso), PartnerRu (regional ruso), DiscountCard, DiscountCardPartner, SalesSettings, SalesLedger, SalesPricelist y SalesPriceType.

## 2. Entidad y datos

Clase `Partner` abstracta. Incluye ID generado, nombre/nombre completo, dirección, ciudad, provincia/estado, código postal, país, teléfono, email, tipo, archivado/activo y logo.

Reglas observadas:
- email tiene expresión regular de validación.
- comparación telefónica elimina +, paréntesis, espacios y guiones.
- comparación de email usa minúsculas.
- archived es bandera de archivo; active es NOT archived.
- nombre materializado e indexado.
- Los socios usados por documentos se deben archivar, no borrar, para conservar referencias históricas.

La normalización de búsqueda ayuda a localizar coincidencias, pero **no demuestra deduplicación ni una identidad universal**.

## 3. Especializaciones y roles

| Especialización | Módulo | Uso |
|---|---|---|
| Entidad legal | LegalEntity | Organización externa |
| Empresa propia | Company | Empresa que compra, vende, emite documentos y es titular de cuentas |
| Persona | Individual | Persona/contacto asociado a entidad legal |
| Empleado | Employee | Individual vinculado a usuario/roles |
| Cliente/proveedor | PartnerSales / PartnerPurchase | Roles comerciales configurables sobre Partner |

Company hereda de LegalEntity y Partner; Individual hereda de Partner; Employee hereda de Individual y CustomUser. Un socio puede tener ambos roles comerciales. No crear distintos registros de cliente/proveedor para la misma entidad sin una decisión explícita de identidad.

## 4. Relaciones y módulos consumidores

- Documentos Receipt, Shipment, Invoice, Bill, PurchaseOrder y SalesOrder leen el socio según el rol esperado.
- Debt, IncomingPayment, OutgoingPayment y Account usan socio/empresa para cuentas, saldos e imputaciones.
- PartnerPurchase y PartnerSales agregan condición de proveedor/cliente y sus parámetros.
- PartnerAttribute/Tag/Communication/Geo/History/Uom extienden la ficha maestra.
- Individual/Company/LegalEntity establecen especialización legal y organizativa.
- Departamentos y empleados se conectan a socios/empresa; el departamento no debe asumirse almacén o sucursal fiscal.

## 5. Interfaz, APIs y utilidades

La fuente define formularios `partner`, `partners`, `dialogPartners` y navegación bajo Master Data. Los listados filtran activos/archivados; el diálogo selecciona por nombre y soporta filtro de búsqueda. `showPartner(LONG id)` está anotado `@@api`; no tratarlo como API pública estable sin revisar publicación, autenticación, autorización, esquema y pruebas.

Se extiende mecanismo de comentarios. PartnerGeo depende de capacidades de geocodificación/mapas externas que deben ser revisadas por separado.

## 6. Privacidad, seguridad y ciclo de vida

- Partner puede contener datos personales y de contacto: definir acceso, visibilidad, retención y exportación.
- Archivar no equivale a anonimizar ni a borrar datos.
- Probar permisos de lectura/escritura en formularios, acciones y API.
- Las relaciones históricas con documentos, cuentas, pagos, deuda y contratos se deben preservar.
- Revisar política de deduplicación con coincidencias parciales, teléfonos compartidos, personas de múltiples empresas y cambios de razón social.
- No enviar datos personales a servicios de geolocalización/telefonía sin validar consentimiento, minimización y configuración.

## 7. Pruebas mínimas

1. Alta de entidad legal/persona/empresa y especializaciones.
2. Cliente, proveedor y ambos roles; validación en documentos.
3. Email válido/incorrecto, teléfono normalizado y coincidencias ambiguas.
4. Archivo de socio referenciado; comprobar histórico de documentos.
5. Cambio de titular, empresa, departamento y cuentas.
6. Permisos por rol/empresa/ubicación y API showPartner.
7. Exportación/importación y deduplicación bajo regla definida.
8. Datos personales, retención, privacidad y uso de mapas/telefonía.
9. Integraciones regionales no habilitadas sin aprobación/localización.

**Aceptación:** dossier declara fuentes principales leídas; deduplicación, privacidad, runtime, importadores y adecuación argentina pendientes.

## 8. Lecturas siguientes

- [Product](Product.md), [PurchaseOrder](PurchaseOrder.md), [Invoice](Invoice.md), [Bill](Bill.md), [Pos](Pos.md).
- [Datos maestros](../MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) §§2–3, 9–12.
- [Facturación/deuda/pagos](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) y [Retail/POS](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md).
- [Seguridad y auditoría](../../SECURITY_AND_AUDIT.md), [postura de seguridad](../../SECURITY_POSTURE.md), [resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md).

**Regla de integración:** Partner es la identidad común; LegalEntity/Company/Individual/Employee y roles cliente/proveedor especializan esa identidad. No duplicarla por flujo.
