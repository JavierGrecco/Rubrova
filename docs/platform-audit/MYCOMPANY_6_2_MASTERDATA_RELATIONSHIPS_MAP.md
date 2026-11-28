# MyCompany 6.2 — datos maestros y relaciones transversales

**Estado: 84 módulos inventariados; lectura de fuentes principales realizada. Pruebas de runtime, revisión de extensiones y adecuación argentina pendientes.**

Este dominio alimenta compras, ventas, inventario, fabricación, facturación, CRM, RR. HH. y flota. Incluye entidades, jerarquías, atributos, unidades, contratos, historial, APIs e importadores.

## 1. Inventario de los 84 módulos

| Área | Módulos |
|---|---|
| Raíz y parámetros | `MasterDataP` (archivo `MasterData.lsf`), `MasterDataSettings` |
| Actividades | `Activity`, `ActivityType` |
| Contratos | `Contract`, `ContractCost`, `ContractImport`, `ContractPartner`, `ContractType` |
| Países | `CountryP`, `CountryImport` |
| Monedas/cotizaciones | `Currency`, `CurrencyImport`, `ExchangeRate` |
| Departamentos/sucursales | `Department`, `DepartmentPartner`, `DepartmentPartnerGeo` |
| Artículos | `Item`, `ItemAPI`, `ItemCost`, `ItemCostImport`, `ItemHistory`, `ItemImage`, `ItemImageImport`, `ItemPurchase`, `ItemSales`, `ItemUom`, `ItemUomImport`, `ItemVariant` |
| Atributos | `ItemAttribute`, `ItemAttributeAPI`, `ItemAttributeImport` |
| Códigos de barras | `BarCode`, `BarCodeHistory`, `BarCodeImport`, `BarCodePack`, `BarCodeUom`, `BarCodeMobile` |
| Categorías | `Category`, `CategoryAPI`, `CategoryImage`, `CategoryImport`, `CategoryLot`, `CategoryMobile` |
| Imágenes móviles | `ItemImageMobile` |
| Packs | `ItemPack`, `ItemPurchasePack`, `ItemSalesPack` |
| Impresión de artículos | `ItemPrint`, `ItemPrintInitial`, `ItemPrintType` |
| Productos | `Product`, `ProductGtin`, `ProductImport`, `ProductLot` |
| Servicios | `ServiceP`, `ServiceImport` |
| Socios | `Partner`, `PartnerAttribute`, `PartnerCall`, `PartnerCommunication`, `PartnerGeo`, `PartnerHistory`, `PartnerPurchase`, `PartnerSales`, `PartnerTag`, `PartnerUom` |
| Empresas/entidades legales | `Company`, `CompanyInitial`, `LegalEntity`, `LegalEntityImport` |
| Personas | `Individual`, `IndividualCall`, `IndividualImport`, `IndividualInitial` |
| Empleados | `Employee`, `EmployeeCall`, `EmployeeImport`, `EmployeePrint`, `EmployeePrintInitial`, `EmployeePrintType` |
| Puestos | `Position` |
| Unidades de medida | `Uom`, `UomImport` |

**Nota:** el archivo `MasterData.lsf` declara `MODULE MasterDataP`. El identificador de módulo se toma de la fuente, no del nombre del archivo. Varios archivos extienden entidades ya definidas; no representan 84 entidades de negocio independientes.

## 2. Socios y sus especializaciones

Fuente base: `partners/Partner.lsf`. La clase abstracta `Partner` centraliza ID, nombre/nombre completo, dirección, ciudad, provincia/estado, código postal, país, teléfono, correo, logotipo, tipo y archivado.

El correo tiene validación de formato. La búsqueda telefónica normaliza signos habituales (+, espacios, guiones y paréntesis); el correo se compara en minúsculas. Esto ayuda a encontrar coincidencias, pero no garantiza deduplicación.

| Especialización | Fuente | Uso |
|---|---|---|
| `LegalEntity` | `partners/LegalEntity.lsf` | Organización externa: cliente, proveedor, banco, transportista, contratista |
| `Company` | `partners/Company.lsf` | Empresa propia que compra, vende, emite documentos y tiene cuentas |
| `Individual` | `partners/individuals/Individual.lsf` | Persona física o contacto de una entidad |
| `Employee` | `partners/employees/Employee.lsf` | Persona empleada y usuario del sistema |

`Company` extiende `LegalEntity`, que extiende `Partner`. `Individual` también extiende `Partner` y registra entidad legal, departamento y puesto. Se valida que el departamento pertenezca a la misma entidad legal. `Employee` extiende `Individual` y `CustomUser`; exige que su entidad legal sea una empresa y puede usar la empresa predeterminada.

`PartnerSales` y `PartnerPurchase` agregan las marcas `isCustomer` y `isVendor`. Cliente/proveedor son roles comerciales configurables, distintos del tipo legal. Un socio puede cumplir ambos roles. El cliente puede tener vendedor asignado; el proveedor, condiciones y preferencias de compra.

Otras extensiones:
- `PartnerTag`: etiquetas de socios, también utilizadas en condiciones de descuentos.
- `PartnerAttribute`: atributos propios y valores, con marca de obligatorio.
- `PartnerCommunication`: canales de contacto adicionales configurables.
- `PartnerCall`: acción telefónica si hay un conector disponible.
- `PartnerGeo`: coordenadas/mapa; la fuente documenta dependencia de APIs de Google para geocodificación, mapas y lugares.
- `PartnerHistory`: historial de altas/modificaciones.
- `PartnerUom`: marca si el socio trabaja con unidades alternativas.

Los socios utilizados por documentos se archivan, no se borran. Pendiente: deduplicación, permisos, privacidad, retención, telefonía y geolocalización.

## 3. Empresas, personas, empleados y sucursales

`Company` tiene empresa predeterminada explícita; si sólo hay una empresa propia, puede seleccionarse automáticamente. Este titular se utiliza en compras, ventas, pagos, cuentas y contratos.

`Employee` sincroniza datos de contacto y nombre con la identidad de usuario. Incluye login, roles, foto, puesto, departamento, archivos e historial. Hay que probar la sincronización en ambas direcciones y frente a importaciones masivas.

`Department` pertenece a un socio y puede guardar dirección y ubicación. Los documentos validan que el departamento pertenezca al mismo socio; si cambia el socio, el vínculo puede limpiarse. No asumir que un departamento es un almacén, centro de costo, sucursal fiscal o punto de venta: esas relaciones deben buscarse en otros módulos.

`Position` provee catálogo de puestos. `Activity` y `ActivityType` ofrecen entidades que otros dominios pueden consumir; falta completar la trazabilidad de cada consumidor.

## 4. Artículos, productos y servicios

Fuente base: `items/Item.lsf`. La clase abstracta `Item` centraliza ID, categoría obligatoria, nombre, nombre completo calculado, referencia, descripción, unidad, archivado/activo, copia y comentarios.

El nombre completo se compone con prefijo de categoría, prefijo/sufijo del artículo y nombre. Está materializado, indexado y habilitado para búsqueda. La categoría puede proponer unidad por defecto mediante herencia. No se puede borrar una unidad utilizada por un artículo.

- `Product` extiende `Item` y agrega peso, volumen y país de origen.
- `Service` extiende `Item` y representa trabajos/servicios que no deben crear movimientos de inventario.
- `ItemPurchase` y `ItemSales` controlan si se puede comprar/vender.
- `ProductLot` y `CategoryLot` habilitan lotes/series.
- `ProductGtin` agrega GTIN, pero debe evaluarse por separado porque está fuera del cierre actual.

La distinción producto/servicio afecta recepción, despacho, stock, picking, costos y facturación; no es sólo visual.

## 5. Categorías, atributos y variantes

`Category` mantiene jerarquía padre/hijo, un único nodo raíz, nombre canónico y niveles materializados hasta seis. Se pueden heredar prefijos, unidades, atributos, lotes y packs. Algunas categorías referenciadas no se pueden borrar y deben archivarse.

`ItemAttribute` define atributos con ID, nombre, orden, obligatoriedad y categorías admitidas. Sus valores también pueden limitarse a categorías. Cada artículo guarda el vínculo atributo/valor. Se valida que:
- el valor pertenezca al atributo;
- el valor sea válido para la categoría del artículo;
- los atributos obligatorios aplicables no queden vacíos.

Los valores de atributos pueden incorporarse al nombre del artículo como prefijos o sufijos ordenados. Hay API e importador Excel.

`ItemVariant` relaciona una variante con el artículo principal mediante `variantOf` y resuelve `primary`. La variante hereda/sincroniza atributos, nombre base, categoría, unidad y archivado. Los atributos heredados quedan de sólo lectura.

Pendiente: cambios de categoría o principal, variantes de varios niveles, efectos sobre stock/precios/documentos y GTIN por variante.

## 6. Unidades, packs y códigos de barras

`Uom` mantiene unidades. `ItemUom` registra ratios por artículo y unidad alternativa. Los documentos convierten cantidades y precios a unidad base; no se puede seleccionar una unidad alternativa sin ratio.

`ItemPack` es metacódigo que agrega unidad y cantidad por paquete. `ItemPurchasePack` y `ItemSalesPack` lo aplican a compras y ventas. Los documentos muestran número de paquetes y convierten a cantidad base usando el ratio.

`BarCode` relaciona códigos con artículos, permite múltiples códigos y uno predeterminado. `BarCodeUom` asocia unidad y ratio; `BarCodePack` amplía el escaneo para sumar la cantidad contenida en el paquete y fijar la unidad correspondiente. La macro de lectura puede sumar unidades y posicionar el formulario.

Pendiente: unicidad, EAN/UPC/GTIN y dígito de control, códigos de balanza, lotes, precisión de conversiones y compatibilidad de dispositivos.

## 7. Costos, imágenes, historial e impresión

- `ItemCost` mantiene costos planificados con fecha; toma el último valor con vigencia menor o igual a la fecha consultada.
- `ItemCostImport` importa/exporta artículo, costo y fecha por Excel.
- `ItemImage` permite cargar, abrir, restablecer y copiar imágenes; existen variantes móviles e importador.
- `ItemHistory` usa macros de historial; `BarCodeHistory` registra altas/cambios/bajas de códigos.
- `ItemPrint`, `ItemPrintInitial` y `ItemPrintType` mantienen tipos/plantillas de impresión.

El costo planificado del maestro no equivale al costo contable FIFO/promedio ni al costo real de despacho. Cada consumidor debe quedar identificado.

## 8. Monedas, cotizaciones y países

`Currency` mantiene ID de tres caracteres, nombre y moneda predeterminada. `ExchangeRate` guarda series con moneda, fecha y tasa. Para una fecha se toma la última línea cuya fecha sea menor o igual; `rate1` puede usar 1.0 como alternativa si no hay cotización.

`Country` guarda ID, nombre, Alpha-2 y Alpha-3. Hay importadores de monedas y países.

Argentina: que se pueda cargar ARS o una cotización no demuestra integración con fuentes oficiales, reglas contables, diferencias de cambio ni tratamiento impositivo local.

## 9. Contratos

`Contract` guarda ID/número/nombre, tipo, fecha, vencimiento, empresa propia, socio, texto, adjuntos y comentarios. La macro de asociación a documentos valida que el contrato corresponda a la misma empresa y socio; si cambian los titulares, puede limpiar el vínculo.

`ContractType` configura tipos; `ContractCost` agrega costos; `ContractPartner` facilita crear contratos desde el socio; `ContractImport` importa/exporta. Otros módulos, como flota, agregan restricciones sobre la vinculación de vehículos.

Pendiente: vencimientos, renovaciones, costos, firma electrónica, versiones, permisos y uso real por dominio.

## 10. Importadores, exportadores y APIs

### 10.1 Familias Excel localizadas

Hay importadores/exportadores para entidades legales, empleados, personas, productos, servicios, categorías, unidades, atributos/valores, ratios de UOM, códigos de barras, costos fechados, monedas, países, contratos e imágenes.

Varios importadores verifican referencias a categorías, unidades, países, socios, atributos u otros IDs antes de crear datos. Si falta una referencia, algunos muestran un error y cancelan; otros tienen lógica propia. No asumir una garantía uniforme de rollback, deduplicación o transacción de lote sin leer cada archivo y probarlo.

### 10.2 APIs JSON localizadas

| API | Entrada | Salida observada | Pendiente |
|---|---|---|---|
| `MasterData.getItems` | Categoría, bandera `extended` | ID, nombre, clase, referencia, barcode, categoría, UOM, país; imagen y descripción opcionales | Autenticación, paginación, filtros, variantes y datos privados |
| `MasterData.getItemAttributes` | Categoría | Artículo, atributo y valor | Permisos, valores inactivos y obligatoriedad |
| `MasterData.getCategories` | Sin parámetros | ID, nombre y padre | Archivadas, paginación, orden y permisos |

Los métodos usan la marca `@@api`. Esto identifica un punto de exposición, pero no demuestra por sí solo autenticación/autorización. Documentar ruta, método, permisos, validación, errores, límites y campos devueltos.

## 11. Relaciones transversales

| Dato maestro | Consumidores/efecto |
|---|---|
| Socio/cliente/proveedor | Pedidos, facturas, pagos, contratos, CRM y descuentos |
| Empresa propia | Titularidad de documentos, cuentas, pagos, contratos, inventario y RR. HH. |
| Departamento | Persona, documentos y asignaciones |
| Artículo | Compras, ventas, facturas, stock, reservas, lotes, costos, fabricación y POS |
| Categoría | Jerarquía y herencia de atributos, UOM, impuestos, packs y lotes |
| Atributos | Clasificación, filtros, descuentos y nombre compuesto |
| Variante/principal | Herencia de datos y barcode; efecto en stock pendiente |
| UOM/ratio/pack | Cantidades y precios de compras/ventas/recepciones/despachos/picking |
| Barcode | Búsqueda de artículos, unidades y paquetes |
| Costo planificado | Sugerencias de compra y precios; no equivale a ledger de costo físico |
| Moneda/cotización | Facturación, deuda, precios y pagos |
| Contrato | Documentos, cuentas y flota |
| Persona/empleado | CRM, RR. HH., usuarios, vendedores y responsables |
| Geolocalización | Socios/departamentos, CRM, asistencia y logística |

## 12. Pruebas y adecuación argentina

| Tema | Pruebas mínimas |
|---|---|
| Tipos de socio | Cliente/proveedor simultáneo; persona vs entidad; empresa propia; archivado |
| Titularidad | Documento/contrato/departamento de otro socio o empresa |
| Duplicados | Nombre, teléfono normalizado, correo, referencias y barcode |
| Jerarquía | Cambiar padre; herencia de unidad, prefijos, atributos, lotes y packs |
| Atributos | Obligatorios, valores inválidos, cambio de categoría y nombre |
| Variantes | Cambiar principal, herencia, GTIN/barcode y stock |
| Unidades/packs | Ratio faltante, conversiones, decimales y redondeos |
| Costos | Fechas, costo faltante, importación y comparación con ledger |
| Monedas | Cotización vigente/anterior, ausencia, fallback y cambio de fecha |
| Contratos | Vencidos, titulares diferentes, vínculo a vehículo/documentos |
| Importaciones | Duplicados, referencias faltantes, archivo parcial, rollback y permisos |
| APIs | Acceso anónimo, usuario sin permiso, archivados, volumen y datos sensibles |
| Privacidad | Geolocalización, imágenes, contactos y datos personales |

La fuente genérica no demuestra CUIT, condición frente a IVA, jurisdicción, padrón ARCA, IIBB ni convenio multilateral implementados adecuadamente para Argentina. Tener país/provincia/ID no resuelve la identificación fiscal. Tampoco asumir que monedas, unidades o cotizaciones están normalizadas para el uso local sin pruebas.

## 13. Estado

Las fuentes centrales de socios, empresas, personas, empleados, departamentos, artículos, productos/servicios, categorías, atributos, variantes, códigos, unidades, packs, costos, monedas, cotizaciones y contratos están identificadas y leídas en un primer nivel. Las familias de importación/exportación y tres APIs JSON están localizadas.

**No se declara cerrado:** faltan pruebas de runtime, revisión individual de todas las extensiones restantes, conciliación entre dominios y validación argentina.
