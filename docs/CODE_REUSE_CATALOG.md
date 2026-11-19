# Catálogo de código reutilizable

**Revisión:** 19 de noviembre de 2026.  
**Propósito:** identificar proyectos y componentes concretos que podamos adoptar, extender, adaptar o usar como base para el sistema de gestión de uso interno.

Este catálogo no declara componentes aprobados para producción. Distingue evidencia documental, hipótesis de reutilización y validaciones pendientes. Antes de incorporar código se debe fijar un commit o release, revisar licencias y dependencias, ejecutar pruebas y conservar procedencia.

## Resumen ejecutivo

| Prioridad | Proyecto | Qué puede adelantarnos | Estado |
|---|---|---|---|
| Muy alta | [Posnic](https://github.com/Posnic/POS) | POS local/offline, retail y gastronomía, ventas, inventario, compras y devoluciones | Evaluar como base integral |
| Muy alta | [ERPNext](https://github.com/frappe/erpnext) + [Frappe](https://github.com/frappe/frappe) | ERP, contabilidad, compras, stock, fabricación, pedidos y POS | Evaluar como base integral |
| Alta | [NexoPOS](https://github.com/Blair2004/NexoPOS) | POS, caja, ventas, compras, stock, clientes, permisos y módulos | Evaluar; licencia contradictoria |
| Muy alta | [pos-toolkit](https://github.com/narisolutions/pos-toolkit) | ESC/POS, impresoras, cajón, scanners seriales, balanzas HID y tickets | Candidato modular |
| Muy alta | [arca-sdks](https://github.com/ramiidv/arca-sdks) | WSAA, WSFEv1, WSFEX, CAEA, padrón, QR y otros servicios ARCA | Candidato fiscal principal |
| Alta | [emupos](https://github.com/ahmedalrifai/emupos) | Simulación de impresoras, cajón, balanzas y lectores | Herramienta de pruebas |
| Alta | [ESCPost](https://github.com/receiptful/escpost) | Renderizado, perfiles, diagnóstico y pruebas ESC/POS | Herramienta de pruebas |
| Media-alta | [PowerSync](https://github.com/powersync-ja/powersync-js) | SQLite local sincronizado con backend, cliente web y servicio self-hosted | Evaluar offline |
| Media | [Dexie.js](https://github.com/dexie/Dexie.js) | Persistencia IndexedDB y consultas reactivas | Candidato PWA |
| Media | [TastyIgniter](https://github.com/tastyigniter/TastyIgniter) | Pedidos online, reservas y gestión gastronómica | Reutilización sectorial |
| Exploratoria | [OCA/l10n-argentina](https://github.com/OCA/l10n-argentina) | Localización argentina para Odoo | Revisar módulos individuales |
| Exploratoria | [l10n_ar_arca_edi](https://github.com/leonobitech/l10n_ar_arca_edi) | Integración Odoo 19 con WSAA/WSFE | Referencia; beta declarada |
| Exploratoria | [DearPOS](https://github.com/engindearing-projects/dearpos) | Perfiles, terminal local, SQLite y cola de sincronización | Proyecto temprano |
| Exploratoria | [ElitaleRestro](https://github.com/tirforge/restro) | KDS, mesas, recetas, modificadores, stock por receta y PIN | AGPL; evaluar partes |

## 1. Plataformas integrales

### Posnic — primer candidato para prueba local

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

**Recomendación:** priorizar una prueba integral en VM compatible, pero no aprobar todavía como base. Medir si la adaptación argentina y la recuperación offline pasan los controles sin un fork profundo. Los instaladores y sus hashes se documentan en [Laboratorio de evaluación](PLATFORM_LAB_SETUP.md); los resultados se registran con [Evaluación de plataformas](PLATFORM_EVALUATION.md).
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

**Prueba requerida:** ejecutar P01–P17 del protocolo común, incluyendo venta rápida, arqueo, pagos mixtos, compra/recepción, costo, producción y recuperación offline.

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

1. **Posnic 1.9.2** es el primer candidato a prueba por su POS local. No está aprobado: la evidencia offline es limitada, la sincronización entre bases independientes es un servicio aparte y el paquete contiene MongoDB SSPL-1.0 y amCharts comercial.
2. **ERPNext 16.60.0/Frappe 16** es la alternativa integral por la profundidad de compras, inventario, producción y contabilidad; su POS y continuidad offline deben probarse.
3. La ronda integral queda limitada a esos dos candidatos. Odoo Community 20 y Medusa v2 quedan fuera de la ronda activa; NexoPOS continúa bloqueado por discrepancia de licencia.
4. **pos-toolkit** aporta código concreto para hardware y tickets. La parte de hardware requiere Tauri v2; `register-core` está planificado.
5. **emupos + ESCPost** pueden reducir la compra temprana de periféricos y hacer reproducibles las pruebas de hardware.
6. **arca-sdks** es el adaptador fiscal candidato para TypeScript; el paquete de facturación 7.1.0 declara MIT y requiere Node >=22.12. La homologación y la recuperación de estados inciertos siguen siendo responsabilidad de nuestra integración.
7. **PowerSync** se evalúa como motor de sincronización, distinguiendo Open Edition de Enterprise/Cloud; **Dexie** es almacenamiento IndexedDB, no sincronizador completo.
8. No integrar varios ERP/POS como fuentes de verdad. El sistema elegido será dueño de ventas, pagos, caja y stock; el resto aporta herramientas o módulos aislados.
9. El uso privado permite considerar GPL/AGPL, pero no elimina obligaciones ni licencias separadas de dependencias, fuentes, recursos comerciales y servicios.
10. La evaluación completa, con versiones fijadas, datos sintéticos y escenarios P01–P17, está en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

Ninguno de estos candidatos está incorporado ni ejecutado dentro de Rubrova.
## 7. Prueba técnica siguiente

Seguir el protocolo único de [Evaluación de plataformas](PLATFORM_EVALUATION.md). No duplicar guiones ni comenzar a copiar módulos antes de ejecutar las dos plataformas.

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
