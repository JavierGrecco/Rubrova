# Inicio de implementación: POS + ERP

**Revisión:** 20 de noviembre de 2026.  
**Estado:** MyCompany 6.2 fijado como primer piloto integrado. No está instalado ni aprobado para uso diario. Tryton 8.0 + tryton-ar 8.0 queda como contraste fiscal argentino.

## Decisión de partida

Vamos a comenzar reutilizando una suite POS+ERP madura, no construyendo una caja aislada ni una arquitectura propia enorme. La primera candidata para el laboratorio es MyCompany 6.2 sobre lsFusion. Su código ya reúne Retail POS, ventas, sesiones, pagos, devoluciones, inventario, costos, compras, facturación y fabricación.

La referencia queda fijada por el tag 6.2 y el commit de origen d21ca6978717b98b6300d90267f9767db7414008. MyCompany declara Apache-2.0 y lsFusion declara LGPL-3.0: son licencias distintas y ambas forman parte del inventario de dependencias. La suite comparte base y runtime entre módulos. La adoptaremos como una aplicación integrada si supera las pruebas; no vamos a describirla como microservicios.

**Tryton 8.0 + tryton-ar 8.0** se conserva para contrastar localización y circuito fiscal argentino. No vamos a mezclar sus módulos GPL con los módulos lsFusion: tienen frameworks, modelos y ciclos diferentes. **ERPNext 16** pasa a reserva y sólo se vuelve a instalar si aparece una brecha concreta que justifique compararlo. Dolibarr queda como filtro corto; Posnic, como referencia de interfaz POS, no como segundo dueño de inventario.

## Módulos fuente concretos que vamos a reutilizar

Los siguientes archivos existen en el tag MyCompany 6.2. La decisión es consumirlos como módulos upstream de la suite, no copiarlos a Rubrova ni mantener una bifurcación de todo el ERP.

| Bloque | Módulos upstream inspeccionados | Responsabilidad aprovechada |
|---|---|---|
| POS | retail/pos/Pos.lsf, retail/pos/dashboard/PosDashboard.lsf | Puesto de venta, carrito, líneas, selección de caja y flujo de mostrador |
| Búsqueda y táctil | PosDashboardSearch.lsf, PosDashboardTouch.lsf | Búsqueda por artículo/código, agregado de productos y navegación por categorías |
| Pagos | PosDashboardPayment.lsf, retail/payments/PaymentMethod.lsf | Métodos configurables, división del pago, cálculo de vuelto y asociación de pagos con la venta |
| Turnos y caja | retail/sessions/Session.lsf, SessionPayment.lsf, PosDashboardCash.lsf | Apertura/cierre, resumen por medio, ingresos y retiros de efectivo asociados al turno |
| Devoluciones | PosDashboardReturn.lsf | Documento de devolución enlazado con la venta de origen |
| Existencias | inventory/ledgers/inv/InvLedger.lsf y módulos de recepción/movimientos | Ledger de entradas/salidas, existencias por ubicación y política de stock negativo |
| Costos | inventory/ledgers/cost/CostLedger.lsf | Ledger y métodos de costeo que deben contrastarse contra casos calculados |
| Compras | purchase/orders/PurchaseOrder.lsf y módulos de Purchase | Proveedores, órdenes, líneas, cantidades, precios e impuestos |
| Ventas y documentos | sales, invoicing/invoices/Invoice.lsf y módulos de pagos | Venta, factura, deuda y pagos como conceptos vinculados pero diferenciados |
| Expansión ERP | CRM, Manufacturing, ProjectManagement, HumanResources y Fleet | Capacidades que se activarán cuando el circuito operativo y el caso de uso estén validados |

La lectura del código del POS muestra que se pueden configurar varios medios de pago en una misma venta; el vuelto se calcula contra el importe entregado y el sobrepago sólo se admite para efectivo. También existen movimientos de ingreso/retiro de efectivo vinculados al turno y un flujo de devolución que parte de la factura original. Es evidencia del código de la versión fijada, **no evidencia de que hayamos ejecutado y aceptado estos flujos**.

## Arquitectura de integración

Durante el piloto MyCompany será una sola suite operativa y, si resulta aprobada, la autoridad única de ventas, pagos, caja, stock, compras y costos que habilitemos. No se instalará otro POS o WMS que mantenga saldos paralelos.

Las personalizaciones de Rubrova quedarán fuera del código upstream:
- Punto de entrada propio `RubrovaCustom`, que requiere MyCompany y módulos de personalización Rubrova.
- Módulo `RubrovaPOSLocalization`, separado, que aplica captions es_AR al primer flujo POS sin editar el código upstream.
- ResourceBundle propio `es_AR`, inicialmente parcial.

Este será el patrón de composición de los próximos bloques: un punto de entrada pequeño y módulos Rubrova separados por responsabilidad. Si una brecha se demuestra, podrán sumarse `RubrovaArgentina`, `RubrovaReporting` o conectores especializados, cada uno con sus dependencias, pruebas y límites. No agregaremos módulos por anticipado.
- Adaptadores e integraciones futuras mediante las APIs, mecanismos de extensión o exportaciones soportadas.
- Sin acceso SQL externo a tablas privadas, sin parches manuales al núcleo y sin duplicación del ledger.

No agregamos un gateway, broker, una segunda base, microservicios ni un framework web propio de forma preventiva. Primero se prueba lo que resuelve la suite y se añade únicamente la pieza mínima que cubra una brecha demostrada.

## Progreso real del Bloque 0 (20/11/2026)

- [x] Confirmar que el Compose específico de MyCompany 6.2 está publicado en el directorio oficial `solutions/mycompany-docker/6.2/`; no usar el Compose genérico de lsFusion.
- [x] Confirmar hashes SHA-256 del instalador y JAR contra la release 6.2.
- [x] Obtener desde la descarga oficial y fijar el SHA-256 del Compose MyCompany 6.2; el runner macOS verificó el mismo digest en descarga y segunda lectura desde caché.
- [x] Registrar las arquitecturas Docker: MyCompany 6.2 publica `linux/amd64`; las imágenes de servidor y cliente 6.2 publican `amd64` y `arm64`.
- [x] Preparar scripts de descarga y verificación para Windows y macOS/Linux.
- [x] Ejecutar el primer recorrido CI en Linux, Windows y macOS 26 Apple Silicon; los tres jobs aprobaron en el run [44785005509](https://github.com/JavierGrecco/Rubrova/actions/runs/44785005509). En macOS pasaron las pruebas Bash/BSD, staging y preparación del JAR con SHA-256.
- [x] Preparar scripts de despliegue modular de RubrovaCustom + RubrovaPOSLocalization para Windows nativo, Linux nativo y Docker, con backup de settings y de los archivos existentes.
- [x] Ejecutar un smoke test automatizado del staging Docker: confirma copia de los módulos y ResourceBundle, conservación de settings, backups y ausencia de invocaciones Docker.
- [x] Incorporar la primera capa de captions `es_AR` en RubrovaCustom para caja, cliente, carrito, turno, búsqueda, cobro, movimientos de efectivo y devoluciones.
- [x] Validar por CI que cada identificador `rubrova.*` utilizado en el módulo tiene traducción.
- [x] Definir comprobaciones de CI para lock, glosario, extensión y scripts.
- [ ] Descargar y ejecutar el instalador en Windows x64 o levantar el Compose en un equipo anfitrión compatible.
- [x] Ejecutar en CI el smoke test de runtime MyCompany 6.2 en Linux x86_64: cuatro servicios, cuatro digests fijados, HTTP 200 y carga de RubrovaPOSLocalization + RubrovaCustom (714/714 módulos) en unos 30 segundos.
- [ ] Confirmar que RubrovaCustom carga en el proceso real, que los captions `rubrova.*` se resuelven y que el idioma es_AR se reconoce.
- [ ] Recorrer los formularios de error y filtros heredados y traducir las cadenas que sigan apareciendo en inglés.
- [ ] Asegurar la cuenta admin y el firewall del equipo anfitrión.
- [ ] Crear backup y restaurarlo en una instalación limpia.

La validación estática pasó en Linux, Windows y macOS Apple Silicon. En el run [44791693036](https://github.com/JavierGrecco/Rubrova/actions/runs/44791693036), los cuatro jobs aprobaron. El runtime Linux x86_64 levantó PostgreSQL, MyCompany, lsFusion Server y el cliente web; verificó los cuatro digests fijados, confirmó que `-Dlogics.topModule=RubrovaCustom` llegó al proceso Java y registró `RubrovaPOSLocalization` como módulo 713 y `RubrovaCustom` como 714. El cliente respondió HTTP 200 y la inicialización terminó en unos 30 segundos. El job eliminó los contenedores, la red, los volúmenes y los archivos temporales. Este resultado demuestra carga de módulos y disponibilidad web; todavía no equivale a una aceptación funcional de ventas, pagos, devoluciones, localización visual, seguridad o backup/restore.

## Guía operativa del primer arranque

La guía específica está en [Instalación y carga de la extensión MyCompany 6.2](MYCOMPANY_RUNTIME_INSTALL.md). La guía [Compatibilidad con macOS](MACOS_SUPPORT.md) explica cómo validar desde una MacBook y qué limitación afecta a Apple Silicon. Para el primer runtime aceptado sigue siendo preferible un anfitrión x64 compatible; Docker en Apple Silicon queda como alternativa experimental hasta completar una prueba real.

## Bloques de implementación

### Bloque 0 — instalación reproducible y segura

1. Descargar artefactos oficiales de MyCompany 6.2 y validar SHA-256.
2. Instalar en entorno local aislado; no publicar puertos a Internet.
3. Cambiar la contraseña inicial del administrador antes de habilitar acceso desde otros equipos. La guía oficial advierte que el usuario inicial puede venir sin contraseña.
4. Fijar las versiones de lsFusion, Java, base de datos e imágenes de contenedor; revisar arquitectura de imagen especialmente en Apple Silicon.
5. Cargar RubrovaCustom sin tocar módulos upstream.
6. Completar la traducción española de los flujos críticos.
7. Hacer un backup y restaurarlo en una instancia limpia antes de introducir datos reales.

**Salida:** instalación repetible, autenticación protegida, extensión cargada, idioma crítico revisado y restauración verificada. Todavía no significa POS aceptado.

### Bloque 1 — POS conectado a la gestión

Aprovechar módulos nativos. Configurar y completar, sin duplicar reglas:
1. Empresa, sucursal, puesto, operador, permisos y depósito.
2. Productos, variantes, códigos de barras, unidades/conversiones, categorías, precios e impuestos.
3. Apertura de turno con fondo, operador y puesto; impedir sesiones simultáneas incompatibles.
4. Escaneo/búsqueda, carrito editable, cantidades, descuentos autorizados, impuestos y total.
5. Cliente opcional. Venta anónima permitida.
6. Efectivo, vuelto, tarjeta, QR y transferencia mediante estados verificados; más de un medio por venta.
7. Confirmación de venta, pagos, movimientos de efectivo, existencias y auditoría.
8. Ticket comercial separado del comprobante fiscal y del voucher del proveedor de pago.
9. Devolución parcial y total vinculada a la operación original, con movimientos de stock/reintegro auditables.
10. Arqueo y cierre por medio, diferencia, depósitos/retiros y reporte diario.
11. Prueba con dos cajas, fallos, reintentos, reinicio de proceso y restauración.

**Salida:** una jornada de mostrador repetible, en español, sin diferencias inexplicadas entre venta, pagos, caja y stock, con recuperación demostrada.

### Bloque 2 — ERP administrativo y abastecimiento

Completar compras, proveedores, recepción total/parcial, devoluciones a proveedor, listas, costos, depósitos, transferencias, conteos, ajustes autorizados, lotes y vencimientos cuando corresponda. Habilitar cuentas corrientes y condiciones comerciales.

**Salida:** compra → recepción → existencias → costo → deuda del proveedor conciliados.

### Bloque 3 — contabilidad y fiscalidad argentina

Contrastar la cobertura de MyCompany con el conjunto Tryton Argentina 8.0 y con documentación oficial ARCA. Definir plan contable, impuestos, CUIT, puntos de venta, comprobantes, notas, certificados, WSAA/WSFE/WSFEX cuando corresponda, CAE, reintentos y estados inciertos. Elegir SDK o adaptador fiscal sólo después de revisar su licencia, versión y tratamiento de errores.

**Salida:** homologación fiscal y conciliación completa desde la venta hasta el pago, stock, comprobante y asiento. No emitir comprobantes reales antes de homologar.

### Bloque 4 — reportes y control de gestión

Primero se validan los informes nativos contra los ledgers. Después se incorporan informes Rubrova de ventas, caja, compras, existencias, rotación, costo, margen y rentabilidad por producto, marca, segmento, categoría, unidad de negocio, canal, sucursal y cliente. Se preservan fotos históricas de costo, precio, promoción, marca/segmento y disponibilidad desde el primer registro.

DuckDB y StatsForecast se sumarán cuando la información transaccional esté conciliada y exista necesidad analítica demostrada. Nunca escribirán sobre ventas, pagos, inventario o contabilidad.

### Bloque 5 — clientes, mayorista y capacidades sectoriales

Ampliar CRM/ficha 360, fidelización voluntaria, listas y escalas B2B, cotizaciones, crédito, contratos, órdenes de trabajo, recetas, BOM, fabricación, mermas, lotes y vencimientos. Todos utilizan los maestros y ledgers ya existentes.

### Bloque 6 — canales y logística

Ecommerce, marketplaces, WhatsApp, delivery y, al final, integraciones de transportistas, etiquetas y seguimiento unificado. No se antepone logística a la operación comercial y administrativa.

## Puertas de aceptación obligatorias

- Pago mixto con efectivo y otro medio; vuelto sólo según reglas configuradas.
- Pago rechazado, pendiente, incierto y confirmado; nunca marcar la venta como cobrada por una pantalla de éxito o captura.
- Reintento de la misma operación sin duplicar venta, pago, movimiento de caja o salida de stock.
- Venta anónima y venta asociada voluntariamente a un cliente; un pagador tercero no crea ni fusiona clientes.
- Dos cajas que intentan vender la última unidad; el inventario debe resolver la concurrencia.
- Devolución parcial, total y repetida; impedir reintegros y retornos duplicados.
- Cierre/arqueo con diferencia explicable por medio.
- Corte de internet, cierre abrupto del proceso, reinicio y restauración en otro equipo.
- Exportación de productos, documentos, historial y adjuntos en formatos utilizables.
- Hardware real y sistema operativo real: lector, impresora, cajón, balanza y terminal.
- Interfaz crítica completa en español; no se habilita operación diaria con textos ingleses sin traducir.
- Homologación ARCA antes de habilitar emisión fiscal productiva.

## Estado honesto al iniciar

La lectura de código y la selección del candidato están realizadas. `RubrovaPOSLocalization` y `RubrovaCustom` ya compilaron y se inicializaron en el runtime MyCompany 6.2 de CI. La extensión incorpora ahora captions para la pantalla de reintegro por medio de pago, además del panel de devolución. Aún falta ingresar a la interfaz para comprobar que los captions `es_AR` se muestran correctamente y recorrer las operaciones reales del POS. **Todavía no instalamos el sistema en tu equipo, no tenemos un POS aceptado para uso diario y no probamos ARCA, hardware, modo offline ni restauración real.**

## Fuentes técnicas

- [MyCompany 6.2 fuente y licencia](https://github.com/lsfusion-solutions/mycompany/tree/6.2)
- [MyCompany 6.2 release](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [Extensiones lsFusion 6](https://docs.lsfusion.org/v6/Extensions/)
- [Internacionalización lsFusion 6](https://docs.lsfusion.org/v6/Internationalization/)
- [Instalación oficial MyCompany](https://mycompany-docs.lsfusion.org/administration/installation/)
- [Tryton 8.0 POS](https://docs.tryton.org/8.0/modules-sale-point/design.html)
- [Conjunto argentino Tryton 8.0 fijado](TRYTON_ARGENTINA_8_0_LOCK.md)
- [Decisión sobre identidad y conciliación de pagos](PAYMENT_IDENTITY_AND_RECONCILIATION.md)
