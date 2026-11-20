# Catálogo de código reutilizable

**Revisión:** 20 de noviembre de 2026.  
**Propósito:** identificar proyectos y componentes concretos que podamos adoptar, extender, adaptar o usar como base para el sistema de gestión de uso interno.

Este catálogo no declara componentes aprobados para producción. Distingue evidencia documental, hipótesis de reutilización y validaciones pendientes. Antes de incorporar código se debe fijar un commit o release, revisar licencias y dependencias, ejecutar pruebas y conservar procedencia.

**Orden de selección actualizado (20/11/2026):** adoptar/extender primero una aplicación existente; comparar MyCompany/lsFusion, Tryton, Dolibarr y ERPNext como base ERP/gestión; evaluar Posnic como candidato POS. uniCenta no pasa a reutilización de fuente hasta disponer de la release actual y sus avisos. La regla vigente y los límites para no convertir una aplicación modular en falsos microservicios están en [Estrategia reuse-first](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md).

## Resumen ejecutivo

| Prioridad | Proyecto | Qué puede adelantarnos | Estado |
|---|---|---|---|
| Muy alta | [MyCompany/lsFusion](https://github.com/lsfusion-solutions/mycompany) | ERP/POS modular, CRM, compras, inventario, producción, RR. HH. y proyectos | Nuevo candidato integral; evaluar release 6.2 |
| Alta | [Posnic](https://github.com/Posnic/POS) | POS local/offline, retail y gastronomía, ventas y devoluciones | Candidato POS especializado; revisar separación respecto del stock y compras |
| Muy alta | [Tryton](https://www.tryton.org/) | ERP modular de tres capas, PostgreSQL y POS oficial `sale_point` | Primera ronda; probar POS y separación respecto de stock/contabilidad |
| Alta | [Dolibarr](https://www.dolibarr.org/) | ERP/CRM modular con REST API, hooks y triggers | Reincorporado a la primera ronda |
| Media-alta | [Apache OFBiz](https://ofbiz.apache.org/) | ERP y Service Engine orientado a SOA | Referencia de segunda etapa; complejidad y serie 24.09 feature-frozen |
| Condicionada | [uniCenta oPOS](https://unicenta.com/) | POS multiplataforma, periféricos y caja | Fuente 5.5.2 requiere login; no aprobar reutilización hasta revisar código y licencia |
| Muy alta | [ERPNext](https://github.com/frappe/erpnext) + [Frappe](https://github.com/frappe/frappe) | ERP, contabilidad, compras, stock, fabricación, pedidos y POS | Evaluar como base integral |
| Alta | [NexoPOS](https://github.com/Blair2004/NexoPOS) | POS, caja, ventas, compras, stock, clientes, permisos y módulos | Evaluar; licencia contradictoria |
| Muy alta | [pos-toolkit](https://github.com/narisolutions/pos-toolkit) | ESC/POS, impresoras, cajón, scanners seriales, balanzas HID y tickets | Candidato modular |
| Muy alta | [arca-sdks](https://github.com/ramiidv/arca-sdks) | WSAA, WSFEv1, WSFEX, CAEA, padrón, QR y otros servicios ARCA | Candidato fiscal principal |
| Alta | [emupos](https://github.com/ahmedalrifai/emupos) | Simulación de impresoras, cajón, balanzas y lectores | Herramienta de pruebas |
| Alta | [ESCPost](https://github.com/receiptful/escpost) | Renderizado, perfiles, diagnóstico y pruebas ESC/POS | Herramienta de pruebas |
| Media-alta | [PowerSync](https://github.com/powersync-ja/powersync-service) | Motor self-hosted para sincronizar SQLite local con backend y clientes web/móvil/escritorio | Evaluar lectura offline; no resuelve por sí solo concurrencia de stock |
| Media | [Dexie.js](https://github.com/dexie/Dexie.js) | Persistencia IndexedDB y consultas reactivas | Candidato PWA |
| Media | [TastyIgniter](https://github.com/tastyigniter/TastyIgniter) | Pedidos online, reservas y gestión gastronómica | Reutilización sectorial |
| Exploratoria | [OCA/l10n-argentina](https://github.com/OCA/l10n-argentina) | Localización argentina para Odoo | Revisar módulos individuales |
| Exploratoria | [l10n_ar_arca_edi](https://github.com/leonobitech/l10n_ar_arca_edi) | Integración Odoo 19 con WSAA/WSFE | Referencia; beta declarada |
| Exploratoria | [DearPOS](https://github.com/engindearing-projects/dearpos) | Perfiles, terminal local, SQLite y cola de sincronización | Proyecto temprano |
| Exploratoria | [ElitaleRestro](https://github.com/tirforge/restro) | KDS, mesas, recetas, modificadores, stock por receta y PIN | AGPL; evaluar partes |
| Alta | [QZ Tray](https://github.com/qzind/tray) | Puente local para impresoras, ESC/POS, USB, serie, HID y sockets | Comparar con pos-toolkit; impresión silenciosa exige firma |
| Alta | [Mercado Pago SDK Node](https://github.com/mercadopago/sdk-nodejs) | SDK oficial TypeScript para APIs de Mercado Pago | MIT; probar Point físico/webhooks por separado |
| Alta | [Karrio](https://github.com/karrioapi/karrio) | API multi-carrier para tarifas, etiquetas y tracking | LGPL-3.0 en componentes comunitarios; no aparecen conectores argentinos en el árbol revisado |
| Alta | [OpenRefine](https://github.com/OpenRefine/OpenRefine) | Limpieza asistida, clustering y reconciliación de datos sucios | BSD-3-Clause; herramienta de preparación, no autoridad |
| Alta | [Frictionless](https://github.com/frictionlessdata/frictionless-py) | Validación estructural y transformación de CSV/XLS/JSON | MIT; candidato para importador |
| Alta | [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | Coincidencias aproximadas y sugerencias de deduplicación | MIT; nunca fusionar automáticamente por score |
| Alta | [python-stdnum](https://github.com/arthurdejong/python-stdnum) | Validación de formatos CUIT, CBU y DNI | LGPL-2.1; no sustituye el padrón ARCA |
| Media-alta | [Docling](https://github.com/docling-project/docling) | Extracción estructurada de PDF, tablas y documentos ofimáticos | MIT; medir rendimiento y precisión |
| Media-alta | [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) | Archivo documental OCR local con API | GPL-3.0; no es libro contable |
| Media | [Node-RED](https://github.com/node-red/node-red) | Automatización de eventos, webhooks y dispositivos | Apache-2.0; sólo flujos periféricos |
| Exploratoria | [Simple WMS](https://github.com/q7-technology/simple-wms) | Ledger append-only, scanner PWA y tareas de depósito | MIT; sin release estable, referencia en vigilancia |
| Alta | [Spree](https://github.com/spree/spree) | Ecommerce headless, B2B/mayorista, listas de precios, canales y marketplace | BSD-3-Clause; evaluar como canal externo, no autoridad de stock |
| Media-alta | [Saleor](https://github.com/saleor/saleor) | Comercio headless GraphQL, canales, monedas, precios y stock | BSD-3-Clause; alternativa a Spree, no evaluar ambos en profundidad |
| Media-alta | [InvenTree](https://github.com/inventree/InvenTree) | Inventario técnico, trazabilidad de partes, ubicaciones, BOM, API y plugins | MIT; evaluar para fabricación/repuestos, no como POS minorista |
| Condicionada | [OCA/manufacture](https://github.com/OCA/manufacture) | Addons Odoo para BOM, planificación multinivel y fabricación | Revisar licencia y dependencias por addon; sólo si se elige Odoo |
| Alta | [DuckDB](https://github.com/duckdb/duckdb) | Motor analítico local para CSV, Parquet, JSON, Excel y cálculos | MIT; analítica/read models, no OLTP |
| Media | [Apache Superset](https://github.com/apache/superset) | Dashboards y exploración BI sobre fuentes SQL | Apache-2.0; requiere servicio/operación propia y modelo analítico de sólo lectura |
| Media-alta | [Metabase](https://github.com/metabase/metabase) | BI y dashboards para usuarios de negocio | Community AGPL-3.0; Enterprise y embedding tienen licencias separadas |
| Condicionada | [OCA/stock-logistics-workflow](https://github.com/OCA/stock-logistics-workflow) | Addons Odoo para operaciones y flujos de depósito | Sólo si se elige Odoo; licencia individual por addon |
| Condicionada | [OCA/purchase-workflow](https://github.com/OCA/purchase-workflow) | Addons Odoo para procesos de compras | Sólo si se elige Odoo; licencia individual por addon |
| Media-alta | [pgBackRest](https://github.com/pgbackrest/pgbackrest) | Backup PostgreSQL, WAL, retención, verificación y restauración | MIT; sólo si la plataforma usa PostgreSQL |
| Alta | [restic](https://github.com/restic/restic) | Backup cifrado y multiplataforma de documentos y archivos | BSD-2-Clause; complementa, no reemplaza backup consistente de DB |
| Condicionada | [Keycloak](https://github.com/keycloak/keycloak) | Identidad y SSO central para múltiples aplicaciones | Apache-2.0; diferir si la plataforma elegida ya cubre autenticación |
| Condicionada | [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) | Recolección/exportación unificada de logs, métricas y trazas | Apache-2.0; incorporar cuando varias aplicaciones lo justifiquen |

## 1. Plataformas integrales

### Tryton, serie 7.8 — módulo oficial `sale_point`

Documentación: https://docs.tryton.org/7.8/modules-sale-point/design.html  
Paquetes: https://downloads.tryton.org/7.8/

Tryton mantiene un módulo oficial POS que registra ventas/devoluciones, métodos de pago y sesiones de caja; calcula el vuelto y, al contabilizar una venta, genera movimientos de stock y asientos. El módulo `sale_point` 7.8.4 se publicó el 16/04/2026; el cliente de escritorio tiene su propia secuencia de parches. Fijar la versión de servidor, cliente y cada módulo por separado.

**Límite:** el POS utiliza ventas, stock y contabilidad dentro del mismo servidor/base. Es código funcional reutilizable, pero no equivale a tres servicios independientes. Probar dependencias, puntos de extensión y autoridad de datos antes de adoptarlo. La documentación tampoco demuestra que la experiencia de caja sea suficientemente rápida para Rubrova.

### Posnic — candidato POS especializado (no aprobado)

Repositorio: https://github.com/Posnic/POS  
Release fijado: `v1.9.2`, commit `4096126edb1ff4fd337069697776254215dc2680` (16/11/2026).  
Licencia del código propio: AGPL-3.0-only.  
Tecnología observada: Electron, Node.js >=22.12, Express, Mongoose y MongoDB.

El código revisado cubre POS, ventas, devoluciones, pagos parciales, productos, variantes, compras, inventario, cuentas de clientes, permisos, reportes y gastronomía. La aplicación de escritorio mantiene API y base principal local; el modo self-hosted puede atender varios equipos de una LAN sobre una base compartida.

**Compatibilidad de ejecución:** la release 1.9.2 publica instalador firmado Windows x64 y paquetes Linux x86_64; no publica instalador macOS. El manual oficial indica que la notarización nativa seguía en corrección. Para evaluar desde Mac usaremos una VM Ubuntu Desktop y el AppImage verificado; no usaremos builds no notarizados.

**Hallazgos nuevos de la inspección del código y documentación:**
- El modo self-hosted no sincroniza varias bases de datos independientes. La documentación del proyecto reserva esa sincronización entre cajas o sucursales para Posnic Cloud.
- La prueba offline que el README publica está limitada a una venta sintética en efectivo que se completó y reabrió en Electron, en una versión anterior. No demuestra pérdida de energía, cierre forzado, jornada completa ni terminales de pago.
- `api/src/sync/outbox.js` describe una cola local opcional para acelerar la sincronización. El propio código aclara que no es el mecanismo de registro de la venta: el escaneo periódico de cambios sigue como respaldo.
- El modelo de venta incluye campos y reglas orientados a GST/India. La adaptación de IVA, CUIT, comprobantes y ARCA requiere evaluación real.
- El tag `v1.9.2` es más reproducible que usar ramas móviles. En la consulta del 19/11/2026, `main` tenía seis commits posteriores; `develop` estaba divergida respecto del tag (2 commits delante y 27 detrás). Se probará primero el tag y se revisarán por separado los cambios posteriores de `main`.

**Licencias del paquete:**
- La raíz declara AGPL-3.0-only.
- El aviso de terceros identifica MongoDB Community Server 7.0.14 bajo SSPL-1.0.
- El mismo aviso identifica amCharts 4 como comercialmente licenciado. No reutilizarlo sin confirmar permiso; contemplar reemplazo.
- Las dependencias npm y los recursos visuales/fuentes requieren inventario propio. La licencia raíz no cubre automáticamente todo el instalador.

**Recomendación:** priorizar una prueba acotada de POS, caja, operación multi-terminal y recuperación en VM compatible. No tratarlo como base ERP ni permitir que sea un segundo dueño de inventario; comprobar si POS y stock pueden delimitarse según la arquitectura. Los instaladores y sus hashes se documentan en [Laboratorio de evaluación](PLATFORM_LAB_SETUP.md); los resultados se registran con [Evaluación de plataformas](PLATFORM_EVALUATION.md).
### ERPNext + Frappe

Repositorios: https://github.com/frappe/erpnext y https://github.com/frappe/frappe  
Release evaluada: ERPNext `v16.60.0` (17/11/2026); framework de la línea 16.  
Licencias: ERPNext GPL-3.0; Frappe Framework MIT.

ERPNext aporta procesos de contabilidad, pedidos, inventario, abastecimiento, fabricación y administración. Frappe aporta framework de aplicaciones, modelos de documentos, autenticación, permisos, API, formularios y tareas en segundo plano.

**Valor:** fuerte candidato para reutilizar compras, proveedores, recepciones, costos, producción/recetas, stock, contabilidad y reportes. Sus perfiles POS configuran empresa, almacén, medios de pago, precios y comportamiento de caja.

**Riesgos y límites:**
- El POS debe evaluarse en una caja realista; una interfaz ERP funcional no garantiza velocidad ni claridad para el cajero.
- No se considera demostrado el offline duradero de v16. Debe sobrevivir al cierre del navegador o proceso, corte de red, reinicio y reintento.
- Frappe se utiliza habitualmente con MariaDB; PostgreSQL no debe asumirse como alternativa equivalente para esta evaluación.
- La localización argentina y ARCA deben verificarse módulo por módulo. No contar una integración por una pantalla documentada si no se encuentra el código, licencia y prueba correspondiente.
- ERPNext GPL-3 no se convierte en MIT por estar construido sobre Frappe Framework MIT.

**Prueba requerida:** ejecutar P01–P26 del protocolo común, incluyendo venta rápida, retiro de artículos, pagos mixtos/vuelto, terminal, arqueo, compra/recepción, costo, producción y recuperación offline.

**Recomendación:** segundo candidato integral. Puede ahorrar mucho trabajo de back-office, pero gana solo si el costo de adaptar caja, experiencia offline y operación argentina es menor que construir esas capacidades.
### NexoPOS

Repositorio: https://github.com/Blair2004/NexoPOS  
Tecnología observada: Laravel 12, PHP 8.2+, Vue, Tailwind y módulos.

Su README declara ventas POS, pedidos, pagos, recibos, devoluciones, cajas, inventario, compras, historial de stock, clientes, recompensas, cupones, roles, permisos, auditoría, códigos de barras y módulos.

**Alerta de licencia:** el archivo raíz LICENSE contiene GPLv3, pero composer.json declara MIT. Son señales contradictorias. No resolver la discrepancia por intuición ni asumir MIT por el campo del paquete. Hasta que el mantenedor aclare el alcance y los archivos bajo cada licencia, tratar el código como GPLv3 y no aprobar incorporación.

**Riesgos funcionales:** varias funciones sectoriales se distribuyen como módulos externos del marketplace; el README distingue explícitamente lo que no está incluido en el repositorio central.

**Recomendación:** candidato real para comparar, pero la discrepancia de licencia es un bloqueo de aprobación, no de investigación.

### Odoo Community

Se mantiene como candidato integral por su cobertura POS, inventario, compras, fabricación y contabilidad. Su POS offline no satisface por sí solo la recuperación duradera exigida. La localización ARCA debe verificarse módulo por módulo y no asumir que todo lo documentado pertenece a Community.

## 2. Hardware, tickets y periféricos

### pos-toolkit — candidato directo para hardware y tickets

Repositorio: https://github.com/narisolutions/pos-toolkit  
Licencia: Apache-2.0.  
Revisión de código: commit `a3fcd401b002d6112068667359f41d1438796e46` (03/11/2026).

El repositorio contiene:
- Plugin Tauri v2 y librería Rust para ESC/POS por red, USB y Windows spooler.
- Apertura de cajón y enumeración de impresoras USB.
- Lectores seriales Virtual COM.
- Balanzas POS USB HID.
- Constructor de tickets TypeScript de 80 mm/57 mm.

**Qué se puede reutilizar:** `packages/receipt-builder` es un paquete TypeScript Apache-2.0, versión 0.1.0, sin dependencias runtime declaradas. Recibe un documento ya compuesto por el host; Rubrova conserva el cálculo de IVA, totales, pagos, idioma y fechas. Admite formato de importes delegado al host y codificaciones ASCII/UTF-8/CP852/transliteración.

**Límites:** el plugin de hardware es Rust/Tauri v2, no un driver universal de navegador/PWA. Requiere comprobar el empaquetado y los permisos del sistema operativo. El mantenedor declara compromisos de soporte modestos. `packages/register-core` figura como **planned**, no implementado.

**Recomendación:** evaluar el constructor de tickets como componente aislado y el plugin solo si la arquitectura final elige una aplicación de escritorio Tauri o una pasarela compatible. Validar impresoras, lectores, balanzas y cajón físicos concretos.
### QZ Tray — puente local para impresión y periféricos

Repositorio: https://github.com/qzind/tray  
Release observada: `v2.3.0` (11/09/2026).  
Licencia del código fuente según `LICENSE.txt`: LGPL-2.1; ejemplos de API public domain y componentes de terceros con licencias propias.

QZ Tray conecta aplicaciones web con impresoras y dispositivos locales; documenta ESC/POS, USB, serie, HID, sockets y archivos. Ofrece paquetes para Windows, macOS y Linux.

**Condición:** imprimir silenciosamente requiere firmar las solicitudes; la documentación contempla adquirir un certificado de QZ o implementar una autoridad raíz propia. Esto exige proteger y distribuir correctamente las claves. Compararlo en laboratorio con [pos-toolkit](https://github.com/narisolutions/pos-toolkit). Probar impresoras, cajón, balanza y lector concretos.

### emupos — simulador de hardware

Repositorio: https://github.com/ahmedalrifai/emupos  
Licencia: Apache-2.0.

Simula a nivel de protocolo una impresora ESC/POS, cajón, balanza, lector de códigos, códigos EAN-13 con peso/precio y fallas físicas: papel agotado, tapa abierta, dispositivo offline, peso inestable, tara y sobrecarga.

**Valor:** permite probar software sin comprar todos los periféricos desde el primer día y automatizar escenarios de error realistas.

**Recomendación:** herramienta de pruebas; no driver de producción.

### ESCPost — laboratorio de impresión

Repositorio: https://github.com/receiptful/escpost  
Licencia: Apache-2.0.

Incluye renderer ESC/POS, perfiles de impresoras, salida PNG, diagnóstico, impresora virtual TCP y SDK JavaScript. Su documentación aclara que la impresora virtual y administración de dispositivos son funciones CLI, no APIs de librería. Windows y Linux tienen validación con impresoras físicas; macOS aún no figura verificado.

**Valor:** validar tickets, cortes, QR, códigos de barras, geometría, perfiles y regresiones visuales antes de imprimir en papel.

**Recomendación:** candidato para pruebas y herramientas internas; verificar compatibilidad con impresoras reales elegidas.

## 3. Integración fiscal argentina

### arca-sdks — candidato principal para TypeScript

Repositorio activo: https://github.com/ramiidv/arca-sdks  
Licencia del paquete de facturación revisado: MIT.  
Paquete: @ramiidv/arca-facturacion 7.1.0 en el manifiesto consultado; Node >=22.12, ESM.

El monorepo separa SDKs para WSAA y componentes comunes; WSFEv1, WSFEX, CAEA y QR; padrón A4/A10/A13/A100; constatación de comprobantes WSCDC; WSMTXCA; WSFECRED; agro; SIRE y empleados.

El README describe errores diferenciados para rechazo, error de servicio y respuesta incierta. Indica que las emisiones no se reintentan automáticamente, un detalle importante para evitar emitir dos veces ante un timeout ambiguo.

**Alerta operativa:** la versión anterior ramiidv/arca-facturacion fue archivada el 1/11/2026; el desarrollo se trasladó a arca-sdks. No integrar desde el repositorio archivado.

**Recomendación:** candidato fiscal prioritario si elegimos TypeScript. Revisar el código y changelog de la versión exacta, ejecutar pruebas de homologación, verificar normativa vigente y añadir nuestra propia capa de idempotencia, conciliación y bloqueo ante estado incierto. El SDK no resuelve por sí solo la prevención de doble factura con Mercado Libre.

### LaPyme/facturas — alternativa de SDK ARCA

Repositorio: https://github.com/LaPyme/facturas  
Release observada: `facturas@0.28.0` (17/11/2026). Licencia del paquete: Apache-2.0. Node.js >=22, ESM; estado pre-1.0.

Cubre facturación electrónica, notas de crédito/débito y consultas de padrón; incluye CLI y documentación en español. Expone estados `authorized`, `rejected`, `indeterminate` y `conflict`, claves idempotentes y recuperación/conciliación del número reservado.

**Recomendación:** comparar con `@ramiidv/arca-facturacion` en homologación. Fijar versión, revisar tests, certificados, concurrencia y recuperación. No ejecutar dos SDK emisores en producción.

### Afip.py

Repositorio: https://github.com/AfipSDK/afip.py  
Licencia: MIT.

Biblioteca Python para Web Services de ARCA/AFIP. Puede servir si elegimos ERPNext/Frappe o una capa de integración Python. No elegir dos SDK fiscales en producción sin necesidad: seleccionar uno según la plataforma principal y usar el otro, como máximo, para contrastar respuestas en pruebas.

### OCA y módulo externo Odoo

- https://github.com/OCA/l10n-argentina — licencia raíz AGPL-3.0; la licencia de cada addon se toma del __manifest__.py.
- https://github.com/leonobitech/l10n_ar_arca_edi — addon Odoo 19 para WSAA/WSFE; el manifiesto revisado declara AGPL-3 y el proyecto se describe como Beta.

**Recomendación:** reutilización potencial si gana Odoo; validar cada addon, rama, manifiesto, pruebas y mantenimiento. No usar una localización beta como única garantía fiscal.

## 4. Offline y sincronización

### PowerSync

Repositorio de SDK: https://github.com/powersync-ja/powersync-js  
Licencia de SDK y Open Edition del servicio: Apache-2.0. La documentación oficial distingue Open Edition autohospedada de funciones Enterprise cerradas y PowerSync Cloud.

El SDK mantiene SQLite en el cliente y sincroniza con backend PostgreSQL y otros motores soportados. Tiene clientes web, React, Node, React Native y Tauri.

**Valor:** posible acelerador para persistencia local y sincronización, en lugar de implementar desde cero transporte y réplica.

**Límites:** validar qué operaciones se pueden ejecutar offline, cómo se escriben cambios, conflictos, filtros por negocio/sucursal, latencia, retención y límites de la edición Open. No confiarle invariantes financieras ni asumir que resuelve por sí solo Outbox/Inbox, idempotencia fiscal o reservas de stock entre cajas.

**Recomendación:** prueba técnica comparativa; candidato serio si la app usa SQLite local y PostgreSQL central.

### Dexie.js

Repositorio: https://github.com/dexie/Dexie.js  
Licencia: Apache-2.0.

Wrapper para IndexedDB con consultas y hooks reactivos; funciona en navegadores, Electron y PWAs. Es almacenamiento local, no un motor de sincronización completo. Dexie Cloud es una opción aparte.

**Recomendación:** alternativa sencilla para persistencia PWA; no confundirla con sincronización confiable ni usarla como único almacenamiento si necesitamos transacciones complejas de caja y recuperación fuerte.

### Posnic como referencia offline

Además de candidato integral, estudiar su arquitectura de API/base local, cola y persistencia. La prueba publicada es acotada y no demuestra recuperación ante todos los cortes o fallas de energía.

## 5. Módulos sectoriales y gastronomía

### TastyIgniter

Repositorio: https://github.com/tastyigniter/TastyIgniter  
Licencia: MIT.

Plataforma Laravel para pedidos online y reservas de restaurantes. Puede acelerar menú digital, reservas y pedidos externos, pero no sustituye nuestro POS minorista ni el núcleo de stock/contabilidad.

### ElitaleRestro

Repositorio: https://github.com/tirforge/restro  
Licencia declarada en README: AGPLv3. Stack TypeScript/Next.js/Prisma/PostgreSQL.

Incluye KDS, mesas, modifiers, pedidos QR, inventario por receta, descuentos, pagos divididos y roles PIN. La orientación fiscal es GST/India y sus integraciones UPI no son directamente aplicables a Argentina.

**Recomendación:** estudiar el modelo de comandas, estados de cocina, modifiers y consumo por receta; no adoptar su fiscalidad ni su flujo de pagos.

### DearPOS

Repositorio: https://github.com/engindearing-projects/dearpos  
Licencia: Apache-2.0.

Stack Next.js/Expo/Prisma/PostgreSQL/SQLite. Declara diseño de perfiles sobre entidades comunes y una cola local. Sin embargo, el README reconoce que sigue en scaffold/active development y que no se recomienda producción; inventario y KDS aparecen en roadmap.

**Recomendación:** referencia arquitectónica, no base de producción.

## 6. Hallazgos y decisiones

1. **MyCompany/lsFusion 6.2:** candidato para reutilizar módulos ERP/POS y probar extensiones propias; su base compartida exige demostrar la separación por dominio.
2. **Tryton, serie 7.8:** incluye el módulo oficial `sale_point`, con ventas, pagos, caja y efectos en stock/contabilidad; debe comprobarse si puede respetar la propiedad independiente de esos dominios.
3. **Dolibarr 24.0.3:** entra al filtro inicial por su cobertura y REST API/hooks; la presencia de extensiones no demuestra despliegue independiente de cada módulo.
4. **ERPNext 16.60.0/Frappe 16:** se mantiene en comparación por su cobertura de compras, inventario, producción y contabilidad.
5. **Posnic 1.9.2:** se evalúa como candidato POS especializado, no como base ERP ni autoridad paralela de inventario. Su offline es limitado y el paquete incluye MongoDB SSPL-1.0 y amCharts comercial.
6. **uniCenta 5.5.2:** queda condicionado a disponer del código actual y avisos verificables.
7. **pos-toolkit / QZ Tray:** candidatos de puente de periféricos con arquitecturas y requisitos de firma diferentes; deben compararse con hardware real.
8. **SDK de ARCA:** LaPyme/facturas y arca-sdks son alternativas a probar en homologación; no usarlas como emisores simultáneos.
9. **Karrio:** puede acelerar la API multi-carrier, pero el repositorio inspeccionado no trae conectores para los operadores argentinos prioritarios.
10. **Calidad e importación:** OpenRefine, Frictionless, RapidFuzz y python-stdnum pueden reducir tareas repetitivas y errores de carga; no reemplazan las validaciones de dominio.
11. No integrar varios ERP/POS como fuentes de verdad. Cada dominio tendrá un dueño único de ventas, pagos, caja y stock; el resto aporta herramientas o módulos aislados.
12. El uso privado permite considerar GPL/AGPL, pero no elimina obligaciones ni licencias separadas de dependencias, recursos comerciales y servicios.
13. La investigación detallada y la priorización de componentes están en [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md).

Ningún candidato de esta investigación está incorporado ni aprobado para producción.

## 7. Prueba técnica siguiente

Seguir el protocolo único de [Evaluación de plataformas](PLATFORM_EVALUATION.md). No duplicar guiones ni comenzar a copiar módulos antes de ejecutar los tres candidatos integrales.

La prueba debe dejar evidencia de versiones, commits, entorno, escenarios, fallos, recuperación, licencias y esfuerzo de adaptación. La elección se hace con condiciones excluyentes: venta/pago/stock exactamente una vez, cierre forzado recuperable, backup restaurable, auditoría, permisos y ruta fiscal argentina viable.

Después de la evaluación integral, probar por separado los componentes especializados:
- pos-toolkit receipt-builder y, si la arquitectura lo permite, pos-hardware;
- emupos y ESCPost con escenarios físicos simulados;
- arca-sdks en homologación;
- PowerSync Open Edition frente a almacenamiento local más protocolo propio.

No se declara reutilizado un proyecto hasta fijar su versión, conservar avisos, revisar dependencias y ejecutar las pruebas pertinentes.
## Fuentes primarias consultadas

- Posnic: https://github.com/Posnic/POS y https://www.posnic.com/posnic-facts
- ERPNext: https://github.com/frappe/erpnext y https://github.com/frappe/frappe
- NexoPOS: https://github.com/Blair2004/NexoPOS
- pos-toolkit: https://github.com/narisolutions/pos-toolkit
- emupos: https://github.com/ahmedalrifai/emupos
- ESCPost: https://github.com/receiptful/escpost
- ARCA SDKs: https://github.com/ramiidv/arca-sdks
- Afip.py: https://github.com/AfipSDK/afip.py
- OCA Argentina: https://github.com/OCA/l10n-argentina
- PowerSync: https://github.com/powersync-ja/powersync-js y https://powersync.com/legal/licensing-terms
- Dexie.js: https://github.com/dexie/Dexie.js
- TastyIgniter: https://github.com/tastyigniter/TastyIgniter
- DearPOS: https://github.com/engindearing-projects/dearpos
- ElitaleRestro: https://github.com/tirforge/restro

La revisión de repositorios y código fuente es documental; todavía no se instalaron ni ejecutaron los candidatos localmente para Rubrova ni se completó una auditoría de seguridad. Ninguno se considera incorporado o aprobado por aparecer en este catálogo. La prueba reproducible y sus datos sintéticos están en [Evaluación de plataformas](PLATFORM_EVALUATION.md) y [fixtures/platform-evaluation.json](fixtures/platform-evaluation.json).


## 8. Módulos ampliados para un producto más grande que POS

La investigación detallada, versiones y límites están en [Investigación ampliada de módulos](MODULAR_COMPONENT_RESEARCH.md).

- **MyCompany/lsFusion 6.2:** Apache-2.0 para la aplicación, LGPL v3 para la plataforma; POS, CRM, compras, inventario multi-depósito, facturación, fabricación, proyectos y RR. HH. Nuevo candidato integral. Release commit d21ca6978717b98b6300d90267f9767db7414008. No está demostrado ARCA/offline argentino.
- **Simple WMS:** MIT; FastAPI/PostgreSQL, ledger append-only, recepción/putaway/pick/pack/ship, transferencias, pallets/SSCC y scanner PWA. Candidato WMS, con un recorrido de devolución SAP que necesita corrección.
- **OpenLinker v0.20.0:** Apache-2.0; ports/adapters, conectores ecommerce/marketplace/carrier, OAuth, webhooks, jobs durables y mapeo de IDs. Referencia y extracción selectiva.
- **OfferKit:** MIT; cupones, redenciones atómicas, gift cards, loyalty, referidos y segmentos. Candidato de promociones, madurez baja, imagen publicada linux/amd64.
- **DuckDB:** MIT; motor analítico local y multiplataforma, no OLTP.
- **Apache Superset:** Apache-2.0; BI self-hosted, solo lectura sobre modelos analíticos.
- **Node-RED:** Apache-2.0; automatización periférica, no autoridad de transacciones.
- **OpenOMS:** Elastic License 2.0, no aprobado como open source; solo referencia condicionada.

La estrategia de contratos, ownership y adaptadores está en [Composición de módulos](MODULE_COMPOSITION.md).


## 9. Áreas de negocio, mayorista, servicios y TMS

La investigación detallada está en [Investigación ampliada de módulos](MODULAR_COMPONENT_RESEARCH.md); los requisitos están en los documentos de áreas, mayorista, servicios y rentabilidad.

- **Dolibarr 24.0.3 (GPL-3.0):** nuevo candidato integral para estudiar. Combina CRM, contratos/suscripciones, intervenciones, agenda, proyectos, envíos, POS, stock, fabricación y contabilidad. Requiere verificar dimensiones de unidad de negocio, margen, mayorista y localización.
- **OCA Field Service 19.0 (AGPL-3.0):** addons de acuerdos, calendarios, recurrencia, timesheets, gastos, vehículos y stock. fieldservice_agreement figura Beta y depende del runtime Odoo; no es módulo independiente de Odoo.
- **OpenFieldPro (AGPL-3.0-only):** agenda, dispatch, work orders, estimaciones, facturas, service plans y app técnica móvil. Release-candidate hardening; fuente de código/patrones, no base integral aprobada.
- **Open TMS:** TMS TypeScript con pedidos, carriers, shipments, tracking posterior, división y consolidación. README/metadata indican MIT pero no se encontró LICENSE raíz; licencia pendiente antes de reutilizar.
- **ERPNext:** referencia fuerte para venta mayorista: price lists por cliente, Item Price con mínimos y packing units, Pricing Rules y Promotional Schemes por cantidad/importe; Sales Orders con entrega y facturación parciales; dimensiones contables para informes por unidad/centro.

La estrategia multiárea mantiene una sola cuenta de cliente y asigna la unidad de negocio a nivel de documento/línea. El despacho y tracking son objetos posteriores y separados de la venta. Ninguna referencia queda aprobada hasta ejecutar pruebas.


## 10. Logística, inventario, automatización y documentos

- **InvenTree (MIT):** backend Django con REST API y plugins; stock, partes, ubicaciones, trazabilidad y aplicaciones extensibles. Muy útil como referencia de inventario, ubicaciones, barcode y API; no adoptar como segundo dueño de stock sin una decisión explícita.
- **OpenBoxes (EPL-1.0):** WMS/inventario orientado a supply chain, lotes, transferencias, recepción y almacenes. Su aplicación completa es pesada para Rubrova; estudiar flujos y modelo, no duplicar el ledger de stock.
- **OpenWMS.org:** plataforma WMS/MFC Java/Spring y servicios distribuidos; el root publica Apache-2.0, pero el propio catálogo mezcla componentes públicos Apache-2.0 con módulos privados/GPLv3. Referencia arquitectónica de warehouse execution y flujos físicos; no copiar componentes sin verificar licencia y disponibilidad individuales.
- **Apache Superset (Apache-2.0):** BI de solo lectura para datasets/vistas analíticas; ya figura como candidato, conviene conservar la separación del OLTP.
- **Temporal (MIT):** ejecución durable de procesos largos, reintentos y recuperación con historial; candidato para workflows críticos de ARCA, conciliación y logística si la complejidad justifica operar su infraestructura.
- **Activepieces:** MIT para core fuera de directorios enterprise, con capacidades empresariales bajo licencia aparte; automatización periférica e integraciones no críticas, no propietario de pagos o stock.
- **n8n:** Sustainable Use License, source-available y no OSI open source; no es la base de una estrategia de código abierto aunque su licencia contemple determinados usos internos. Evitar incorporar carpetas .ee sin licencia empresarial.
- **Paperless-ngx (GPL-3.0):** archivo documental OCR con etiquetas y búsqueda; candidato de referencia o servicio local separado para facturas, remitos y documentos, no libro contable.
- **OpenBoxes / InvenTree / OpenWMS:** son aplicaciones/plataformas, no pequeñas bibliotecas neutrales. No ejecutar varias como autoridad de inventario a la vez.

La investigación de alcance, stack, licencias, madurez y recomendaciones está en [Investigación ampliada de módulos](MODULAR_COMPONENT_RESEARCH.md).

## 11. Logística argentina y seguimiento

- **Andreani:** API oficial y wrapper TypeScript MIT de la comunidad; revisar compatibilidad con la API actual.
- **Correo Argentino PAQ.AR:** API oficial y wrapper TypeScript MIT; endpoints publicados incluyen cotización, agencias y alta de envíos.
- **OCA e-Pak:** Web Services oficiales y wrappers MIT en Ruby/Python.
- **Vía Cargo:** AfterShip publica integración de tracking; 17TRACK también lista soporte. No encontramos API pública oficial de creación de envíos/cotización.
- **Envíopack:** agregador comercial con tracking normalizado y webhooks; confirmar operadores incluidos.
- **Kangu:** la información pública revisada sobre la adquisición por Mercado Libre menciona Brasil, Colombia y México; no demuestra disponibilidad API/servicio para Argentina.

**Karrio como motor multi-carrier:** https://github.com/karrioapi/karrio ofrece una API autohospedada para tarifas, etiquetas y tracking. El archivo raíz declara LGPL-3.0 fuera de `ee/`, con Enterprise bajo licencia separada. En el árbol de conectores de la rama principal consultado el 20/11/2026 no aparecen Andreani, PAQ.AR, OCA ni Vía Cargo. Puede acelerar el modelo multioperador, pero requiere conectores argentinos propios y credenciales de QA.

Ver [Logística argentina y seguimiento unificado](ARGENTINA_LOGISTICS_INTEGRATION.md).

## 12. Interoperabilidad administrativa/contable

- **Tango/Axoft:** TangoDeltaApi y APIeCommerce son repositorios oficiales de la organización verificada; ApiClientes expone JSON de comprobantes con CAE; Tango Contabilidad publica capacidades de API para asientos bajo condiciones de versión/abono.
- **Catedral:** exportación/importación de Excel y otros formatos, intercambio Empresa–Estudio; API pública de desarrollador no confirmada.
- **Bejerman:** API abierta y WebService como adicionales según plan.
- **Xubio:** API REST OAuth2, documentación de comprobantes, asientos, centros de costo, bancos, depósitos, impuestos y retenciones/percepciones.
- **Colppy:** API REST documentada en su portal; declara comprobantes, clientes/proveedores, asientos e inventario.
- **Asentia:** producto comercial de conciliación bancaria que acepta extractos y exporta asientos; referencia funcional, no código abierto.

La arquitectura y las pruebas de estos destinos están en [Interoperabilidad contable y administrativa](ACCOUNTING_INTEROPERABILITY.md). Los repositorios oficiales y manuales se consultan antes de cada implementación.


## 13. OCR, pronóstico, procesamiento analítico y contabilidad

- **invoice2data (MIT):** parser de facturas PDF basado en plantillas; candidato para extraer campos de proveedores. Necesita OCR previo para escaneos y revisión humana; no valida CAE ni reemplaza cuentas a pagar.
- **OCRmyPDF (MPL-2.0):** OCR local, PDF/A y búsqueda sobre escaneos; el README declara soporte Windows/Linux/macOS. Ver dependencias Tesseract y binarios de cada paquete.
- **skforecast (BSD-3-Clause):** forecasting estadístico/ML/foundation, backtesting, intervalos y explainability; usar como laboratorio/servicio analítico para demanda, no como módulo que compra automáticamente.
- **Polars (MIT):** motor DataFrame/SQL en Rust con bindings Python y Node; candidato para importaciones y pipelines analíticos, nunca para reemplazar OLTP.
- **Bigcapital (AGPL-3.0):** aplicación completa de contabilidad/inventario y API headless de doble partida. Útil para estudiar ledger y estados financieros; no está probada su adaptación argentina y no debe convertirse en otro libro contable paralelo.

Investigación de detalle y límites: [Investigación ampliada de módulos](MODULAR_COMPONENT_RESEARCH.md). Requisitos de integración contable: [Interoperabilidad contable](ACCOUNTING_INTEROPERABILITY.md).


## 14. Componentes transversales investigados (20/11/2026)

La [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md) reúne calidad/importación de datos, documentos, hardware, ARCA, logística multi-carrier, sincronización offline, ecommerce, inventario/fabricación, BI, identidad, observabilidad y backups. Incluye licencias, versiones observadas, límites y orden de prueba, incluidos los límites comerciales del embedding de Metabase y las licencias individuales de addons OCA.

Ninguno está aprobado ni incorporado. La shortlist distingue componentes candidatos a prueba controlada, proyectos de referencia y piezas que conviene diferir por complejidad, licencias o madurez.
