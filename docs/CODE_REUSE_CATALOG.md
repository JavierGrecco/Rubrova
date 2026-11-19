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

### Posnic — candidato principal para prueba vertical

Repositorio: https://github.com/Posnic/POS  
Licencia del código propio: AGPL-3.0-only.  
Tecnología observada: Electron, Node.js y frontend/API local; el paquete revisado declara MongoDB.

El proyecto se presenta como POS offline-first para retail y restaurantes, con API y base de datos ejecutándose en el equipo de caja o servidor propio. Incluye ventas, devoluciones, pagos parciales, productos, variantes, compras, inventario, cuentas de clientes, permisos, reportes y flujos gastronómicos. Distingue la edición local de servicios cloud opcionales.

**Por qué importa:** coincide con nuestra necesidad de uso local, caja rápida y continuidad sin internet. Puede permitir partir de un sistema operativo real en lugar de construir la caja completa.

**Riesgos y límites:**
- La licencia del código propio es AGPL-3.0-only. Si usuarios interactúan remotamente con una versión modificada por red, revisar la obligación de ofrecer el código fuente de esa versión a esos usuarios.
- Los instaladores incluyen MongoDB Community Server bajo SSPL-1.0, licencia distinta y no aprobada por OSI. La licencia del POS no describe por sí sola todo el instalador.
- La evidencia publicada de operación offline está acotada a flujos y versiones concretos; no prueba todos los medios de pago, cortes de energía, sincronización multi-sucursal ni todos los periféricos.
- La edición self-hosted descrita no equivale a sincronización entre varias bases/cajas; esa función se documenta como servicio separado.
- Debemos comprobar si el modelo de datos y los puntos de extensión permiten nuestras reglas de descuentos, fiscalidad argentina, trazabilidad y analítica sin reescribir el núcleo.

**Prueba requerida:** fijar una versión, levantarla localmente y ejecutar venta, descuento, pago mixto, cierre de caja, devolución parcial, movimiento de inventario, corte de red, cierre forzado, reinicio y recuperación. Inspeccionar ventas, stock, pagos, caja, migraciones, roles y sincronización.

**Recomendación:** máxima prioridad de evaluación; no aprobado todavía como base definitiva.

### ERPNext + Frappe

Repositorios: https://github.com/frappe/erpnext y https://github.com/frappe/frappe  
Licencias: ERPNext GPL-3.0; Frappe Framework MIT.

ERPNext declara cobertura de contabilidad, pedidos, inventario, abastecimiento, fabricación, activos y otras áreas. Frappe proporciona framework, autenticación, API, base de datos y estructura de aplicaciones.

**Valor:** candidato fuerte para reutilizar procesos ERP profundos: compras, proveedores, inventario, costos, órdenes de producción, recetas/BOM, contabilidad y reportes. Frappe permite crear aplicaciones propias y extender documentos y flujos.

**Riesgos:** Python/MariaDB y modelo de aplicación propio; adaptar el POS, experiencia de caja, offline-first fuerte e integración fiscal argentina puede requerir trabajo considerable. No asumir que el POS resuelve hardware ni recuperación tras apagado.

**Prueba requerida:** recorrido equivalente al de Posnic y además recepción parcial de compras, costo de inventario y producción con receta/lote. Verificar qué funciones POS están incluidas en Community.

**Recomendación:** máxima prioridad como alternativa integral, especialmente si gestión, producción y contabilidad listas reducen más trabajo que el costo de adaptar.

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

### pos-toolkit — candidato directo

Repositorio: https://github.com/narisolutions/pos-toolkit  
Licencia: Apache-2.0.

El repositorio contiene:
- Plugin Tauri v2 y librería Rust para ESC/POS por red, USB y Windows spooler.
- Apertura de cajón de dinero y enumeración de impresoras USB.
- Lectores seriales Virtual COM.
- Balanzas POS USB HID.
- Constructor de tickets de ancho fijo para papel de 80 mm y 57 mm.

El paquete register-core aparece como **planned**, no disponible terminado. El README indica que los paquetes no incorporan dependencias específicas del producto y que el plugin expone funciones de librería además de comandos Tauri.

**Valor:** coincidencia directa con nuestra capa de hardware. Evita escribir desde cero protocolos de impresora, lectura serial y soporte HID.

**Límites:** soporte y compromiso de mantenimiento declarados modestos; validar modelos, sistemas operativos, reconexión, permisos USB y balanzas reales. Un protocolo genérico no equivale a compatibilidad con todas las marcas.

**Recomendación:** evaluar primero pos-hardware y receipt-builder; no contar register-core como existente hasta verificar su código.

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

1. **Posnic pasa a ser el primer candidato a prueba integral**, por su enfoque local/offline y cobertura POS retail/restaurante.
2. **ERPNext queda como segundo candidato integral**, especialmente por gestión, inventario, compras, fabricación y contabilidad.
3. **NexoPOS queda como tercer candidato**, pero no se aprueba hasta resolver la contradicción GPLv3 vs MIT entre LICENSE y composer.json.
4. **pos-toolkit** es el candidato más concreto para acelerar hardware.
5. **emupos + ESCPost** forman una posible caja de herramientas para probar hardware sin depender siempre de dispositivos físicos.
6. **arca-sdks** es el candidato principal para ARCA si la plataforma termina en TypeScript; afip.py es alternativa para Python.
7. **PowerSync** merece prueba como motor de sincronización; **Dexie** como opción de almacenamiento browser, no como sincronizador.
8. No integrar varios ERP/POS como fuentes de verdad. Si adoptamos una plataforma integral, los demás proyectos aportan módulos aislados, herramientas de prueba o conocimiento, no una segunda contabilidad o inventario paralelo.
9. No copiar componentes sin revisar dependencias transitivas, archivos de licencia, marcas, fuentes de datos, avisos y scripts de instalación.
10. El uso previsto es privado e interno. GPL/AGPL no son descartes automáticos; para AGPL evaluar expresamente interacción remota de usuarios por red. SSPL y licencias source-available se revisan por separado: no se deben llamar open source ni asumir equivalencia con GPL.

## 7. Prueba técnica siguiente

No construir aún una aplicación definitiva ni copiar módulos de manera aislada. Primero comparar Posnic y ERPNext (y NexoPOS cuando se resuelva su licencia) con el mismo guion:

- Alta/importación de producto con código, variante y unidad.
- Venta con lector simulado, descuentos por línea y carrito, autorización y registro de impacto.
- Pago mixto, vuelto, apertura/cierre y arqueo.
- Salida de inventario, devolución parcial, reembolso y disposición del producto.
- Impresión y apertura de cajón con emupos; vista previa de ticket con ESCPost.
- Desconexión, cierre forzado, reinicio y reconciliación sin pérdida ni duplicación.
- Compra, recepción parcial, actualización de costo y producción por receta/lote.
- Emisión ARCA en homologación desde adaptador separado; estado incierto sin reintento ciego.

Medir porcentaje de flujo resuelto sin tocar el core, módulos que hay que modificar, complejidad de actualización, cobertura real de tests, tiempo de adaptación, offline, compatibilidad física y claridad de datos.

**Criterio de decisión:** gana la plataforma que reduzca más trabajo total y riesgo operativo, no la que tenga más pantallas ni la demo más vistosa. Si ninguna supera el guion, tomar solo módulos y componentes y construir el monolito modular propio.

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

La revisión es documental y de manifiestos/repositorios; todavía no se clonaron, ejecutaron ni auditaron estos proyectos. Ninguno se considera incorporado al producto por aparecer en este catálogo.
