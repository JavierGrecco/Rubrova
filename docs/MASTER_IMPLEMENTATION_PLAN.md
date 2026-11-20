# Plan maestro de implementación de Rubrova

**Revisión:** 20 de noviembre de 2026  
**Estado:** dirección de producto y secuencia de trabajo propuestas; pendientes las pruebas funcionales comparables de plataformas.  
**Estado real del software:** todavía no existe una aplicación funcional de Rubrova ni se incorporó código de terceros. El repositorio contiene definición, arquitectura, investigación y un validador de datos sintéticos.

## 1. Decisión ejecutiva

Rubrova no se debe desarrollar alrededor del seguimiento de envíos ni como una colección de integraciones. El centro es la **operación y gestión del negocio**.

La experiencia empieza en el POS, pero el POS tiene que usar desde el primer día datos y reglas del sistema de gestión: catálogo, precios, clientes, stock, pagos, caja, devoluciones y estado fiscal. Después se completa el ERP administrativo, se consolida contabilidad y costos, y recién entonces se construyen los análisis de gestión con resultados confiables.

La secuencia aprobada para dirigir el trabajo es:

1. **Operación comercial y POS:** vender, cobrar, devolver, abrir/cerrar caja y dejar el stock correcto.
2. **ERP de gestión:** productos, clientes, proveedores, compras, recepción, inventario, costos, cuentas corrientes, depósitos y sucursales.
3. **Contabilidad y fiscalidad argentina:** libro contable, impuestos, ARCA, comprobantes, conciliación, bancos, cuentas por cobrar/pagar y cierres.
4. **Reportes y control de gestión:** ventas, costos, márgenes, rentabilidad por producto/marca/canal/área, compras, stock, caja y finanzas.
5. **Capacidades sectoriales y crecimiento:** producción, recetas, lotes, vencimientos, mayorista, distribución, servicios B2B y contratos.
6. **Canales externos:** ecommerce, Mercado Libre, WhatsApp, delivery y otras fuentes de pedidos.
7. **Logística avanzada:** fulfillment, agregadores, transportistas, etiquetas y seguimiento unificado.

No significa postergar toda la administración hasta terminar el POS: las dimensiones de negocio, centros de costo, sucursal, canal, cliente, depósito, trazabilidad y reglas de precios deben estar en el modelo inicial. Lo que se posterga es la profundidad funcional de cada área, no los cimientos que después serían caros de corregir.

## 2. Qué tiene que ser la primera entrega

La primera entrega no es una demo de caja ni un CRUD de artículos. Es un **circuito comercial completo y repetible**, inicialmente en una sucursal y con datos sintéticos:

1. Alta/importación de un producto con código de barras, unidad, variante y precio.
2. Consulta del artículo por código o búsqueda desde el POS.
3. Carrito editable: agregar, quitar y cambiar cantidades antes de iniciar el cobro.
4. Recalcular descuentos, promociones, impuestos y total sin modificar ventas anteriores.
5. Asociar un cliente cuando corresponda, sin forzar una ficha para cada consumidor de mostrador.
6. Comprobar disponibilidad y reservar o confirmar el movimiento de stock con la autoridad del inventario.
7. Cobrar en efectivo, calcular vuelto exacto y admitir más de un medio de pago.
8. Confirmar el turno de caja, el movimiento de efectivo y el resultado de cada pago.
9. Registrar la venta y conservar ticket, voucher y documento fiscal como documentos diferentes.
   - Política de impresión: efectivo y transferencia verificada en impresora térmica de caja; QR/tarjeta preferentemente en terminal inteligente con ticket detallado generado por Rubrova y voucher; impresora de caja como respaldo si el modelo no admite impresión personalizada. Evitar duplicados y permitir reimpresión auditada.
10. Cerrar o reiniciar el POS/servicio y demostrar que la operación confirmada no se pierde ni se duplica.
11. Devolver parcial o totalmente una venta, vinculando la operación original y dejando los movimientos compensatorios.
12. Consultar un cierre básico: ventas netas, devoluciones, medios de pago, efectivo esperado, diferencia de caja y unidades vendidas.

**Para dar por terminada esta entrega:** cada total debe poder reproducirse; ventas, pagos, caja, inventario y fiscalidad deben conciliar; los errores y estados pendientes deben ser visibles; y la caja debe poder usarse con teclado, lector y pantalla táctil. No se declara una venta cobrada porque el POS haya mostrado una pantalla de éxito o porque el cliente presente una captura.

## 3. Fundaciones que se incorporan desde el primer día

Aunque se implementen progresivamente, estas dimensiones deben existir desde el comienzo para evitar migraciones destructivas:

- Organización y entidad legal; sucursal, caja, depósito, ubicación, usuario, rol y dispositivo.
- Producto/servicio, variante, código, unidad de medida, conversión, precio, costo, impuesto y proveedor.
- Cliente y proveedor; persona/empresa, CUIT cuando corresponda, condiciones comerciales, crédito y cuenta corriente.
- Unidad de negocio, canal, sucursal, centro de costo y proyecto como dimensiones distintas.
- Pedido, venta, pago, movimiento de stock, sesión de caja, comprobante fiscal y despacho como hechos distintos.
- Identificador externo, correlation ID, clave de idempotencia, auditoría y estado de sincronización.
- Fecha/hora, moneda, tipo de cambio, política de redondeo y fotografía de las condiciones aplicadas a la operación.

Una venta puede incluir líneas de áreas diferentes. La dimensión económica debe guardarse a nivel de línea cuando corresponda; el consolidado no debe duplicar ingresos, stock ni costos internos.

## 4. Arquitectura objetivo y límites de reutilización

Rubrova debe ser una **composición de módulos y servicios de dominio con responsabilidades reales**, no una aplicación propia gigante ni un conjunto de microservicios diminutos.

Los límites que se deben respetar son:

| Dominio | Qué posee | Prioridad de construcción |
|---|---|---|
| Identidad y organización | Usuarios, roles, permisos, entidades, sucursales, cajas y dispositivos | Fundación |
| Catálogo y precios | Productos, variantes, códigos, unidades, listas, reglas y vigencias | Fundación |
| Clientes y proveedores | Maestros, contactos, condiciones, crédito y cuentas de relación | Inicial |
| POS, pedidos y ventas | Carrito, pedido, venta, devoluciones, estados comerciales y ticket | Primera entrega |
| Inventario y almacenes | Ledger de stock, reservas, ubicaciones, lotes, conteos y disponibilidad | Primera entrega |
| Pagos y caja | Intentos, asignaciones, efectivo, vuelto, turnos, arqueos, reembolsos y liquidaciones | Primera entrega |
| Compras y abastecimiento | Órdenes, recepción, costos de compra, proveedores y reposición | Segunda entrega |
| Contabilidad y fiscal | Asientos, períodos, cuentas, impuestos, ARCA, comprobantes y conciliación | Segunda entrega; homologación antes de operar fiscalmente |
| Inteligencia y reportes | Métricas, proyecciones de lectura, dashboards y pronósticos | Reportes básicos iniciales; BI avanzado después de validar costos |
| Producción y servicios | Recetas/BOM, órdenes, consumos, rendimiento, mermas, contratos y SLA | Expansión sectorial |
| Canales e integraciones | Adaptadores, webhooks, importación/exportación y bandejas Inbox/Outbox | Según necesidad; ecommerce después del núcleo |
| Logística y fulfillment | Preparación, bultos, entrega, booking, guías, operadores y tracking | Modelo básico temprano; conectores y tracking al final |

Los servicios se comunican por API/eventos versionados, tienen datos y credenciales propios y se pueden desplegar/actualizar/recuperar sin actualizar todo Rubrova. Se permite que varios procesos se ejecuten en la misma computadora local; no se permite que eso se convierta en tablas compartidas o accesos SQL cruzados.

**No se exige un proceso por cada tabla o pantalla.** Se definen límites por consistencia y propiedad del dato. Las operaciones que deben ser inmediatas (por ejemplo, confirmar una reserva de stock) se resuelven en el servicio propietario. Las tareas asíncronas se implementan con Outbox/Inbox, mensajes durables e idempotencia. El número de tecnologías se mantiene pequeño.

Un ERP existente puede evaluarse como aplicación externa acotada, pero sus módulos internos no se describen como microservicios si comparten servidor, base o migraciones. Sólo se adopta si el límite que administra es deliberado, tiene API, datos propios, backup/restore, actualizaciones controlables y no absorbe autoridades que deban ser independientes. Si no pasa esa puerta, se reutilizan piezas realmente separables o se descarta.

**Regla excluyente para no introducir un monolito:** ERPNext, MyCompany, Tryton o Dolibarr pueden probarse como referencias funcionales y para identificar módulos reutilizables. No se adopta una suite completa como núcleo único de Rubrova si hace que POS/Ventas, Inventario, Pagos/Caja y Contabilidad compartan una base o un ciclo de despliegue. Un componente sólo se adopta si puede actuar como una unidad de dominio con contrato soportado, datos/credenciales propios, backup/restore, actualización y rollback independientes y sin convertirse en autoridad duplicada. Si el producto no permite ese límite, se descarta como plataforma base aunque su cobertura funcional sea excelente; se reutiliza sólo el código separable o se construyen los servicios propios detrás de contratos versionados.


### Primera composición desplegable

El primer conjunto de procesos de Rubrova debe ser pequeño, pero mantener límites reales:

| Unidad desplegable | Autoridad | Incluye al inicio |
|---|---|---|
| Gateway local | Entrada y enrutamiento, sin ser dueño de ventas/stock/dinero | Autenticación de dispositivo, routing, permisos de acceso, rate limits y correlation ID |
| Identidad y organización | Usuarios, roles, entidad, sucursal, caja, depósito y dispositivos | Administración básica de usuarios y contexto operativo |
| Catálogo y precios | Artículos, variantes, códigos, unidades, listas y reglas vigentes | Importación básica, búsqueda y snapshot de precios |
| POS / Ventas | Carrito, pedido, venta, líneas, descuentos y devoluciones | Interfaz de caja y estados comerciales |
| Inventario | Ledger, reservas, disponibilidad, movimientos y conteos | Reserva atómica, salida de venta y devolución |
| Pagos y Caja | Intentos de pago, medios, efectivo, vuelto, turnos, arqueos y reembolsos | Efectivo, medios manuales y un adaptador de terminal sólo cuando esté probado |
| Fiscal | Numeración fiscal, comprobantes, ARCA, notas y estados inciertos | Contrato y homologación; no se considera productivo hasta superar las pruebas fiscales |

Clientes/proveedores pueden comenzar dentro de una unidad de Maestros/Relaciones si la plataforma elegida lo exige; deben conservar identificadores y contratos propios para separarlos después sin migración destructiva. Compras, contabilidad general y BI se incorporan en las siguientes entregas, sin crear procesos vacíos sólo para completar un diagrama.

**Flujo coordinado de una venta:**

1. El POS consulta Catálogo/Precios y conserva la fotografía de artículo, precio, impuesto y promoción aplicada.
2. Ventas registra un carrito/operación con clave idempotente y solicita a Inventario una reserva con cantidad y versión esperada.
3. Si la reserva no se confirma, el checkout ofrece alternativas; no inicia el cobro por una unidad no reservada según la política.
4. Pagos procesa cada medio. Una respuesta incierta queda pendiente de consulta/conciliación y no permite enviar otro cobro a ciegas.
5. Cuando se cumplen las reglas comerciales y de pago, Ventas confirma la operación; Inventario transforma la reserva en movimiento definitivo mediante una operación idempotente.
6. Fiscal recibe el evento y emite/consulta el comprobante según la obligación fiscal; un fallo de ARCA no borra la venta ni genera doble factura.
7. Caja cierra el turno con cobros, vuelto, retiros, ajustes autorizados y diferencias conciliadas.

Cada unidad tiene almacenamiento y migraciones propios. En instalaciones pequeñas se pueden co-alojar en una misma máquina/instancia física, pero con bases o esquemas, roles, credenciales y despliegues separados. La comunicación es por APIs versionadas y eventos Outbox/Inbox, no por SQL cruzado.



## 5. Selección de plataformas: qué probar y qué no asumir

Las plataformas se comparan por el circuito POS + gestión que realmente necesitamos, no por la cantidad de módulos de su página de inicio. La prueba debe medir instalación, caja, inventario, reportes, localización argentina, APIs, extensión, portabilidad, recuperación, experiencia y costo de mantenimiento.

### Candidatos de primera evaluación

| Candidato | Por qué merece prueba | Riesgo/condición | Prioridad |
|---|---|---|---|
| **ERPNext 16 / Frappe 16** | Cobertura amplia de ERP, compras, inventario, manufactura, contabilidad, dimensiones y POS con perfiles, depósitos, impuestos y pagos | El POS debe medirse con una jornada real y hardware; stack y operación más pesados; localización argentina y adaptación fiscal deben probarse. Sus apps comparten el site/bench y persistencia: no equivale a microservicios. | Primera ronda |
| **MyCompany 6.2 / lsFusion** | Cobertura integrada de Retail POS, ventas, CRM, compras, inventario, fabricación, facturación y RR. HH.; módulos extensibles | Todos los módulos de una instalación comparten base. Verificar API, usabilidad real de caja, Argentina/ARCA, instalación y recuperación. No considerarlo arquitectura distribuida por ser modular. | Primera ronda |
| **Tryton 8.0 + tryton-ar 8.0** | ERP/POS con PostgreSQL; la localización cubre plan contable, CUIT/padrón, facturación WSFE/WSFEX, bancos, vouchers, cheques y reportes | Hay ocho ramas argentinas coordinadas con manifiestos 8.0.0/8.0.1 y tests. `sale_point` 8.0 cubre la operación minorista. Los módulos comparten servidor/base; no son microservicios independientes. Tryton 8.2 queda como actualización posterior, condicionada al port. | Primera ronda condicionada a instalación y pruebas |
| **Dolibarr 24.0.3** | CRM/ERP, API REST, hooks y triggers; TakePOS y módulos extensibles; posible camino de instalación más sencillo | Medir profundidad del POS, gestión de costos, producción y la localización argentina. Sus módulos también comparten una aplicación/base. | Filtro corto / alternativa |
| **Posnic 1.9.2** | POS dedicado, ventas, compras, clientes, caja, catálogo e inventario | No cubre el ERP integral; revisar AGPL, MongoDB SSPL y componente comercial de gráficos; orientado a reglas fiscales de India, no Argentina; su prueba offline pública es limitada y el paquete macOS no está resuelto. | Referencia POS, no base principal |

No se declara un ganador antes de instalar y recorrer la misma prueba. El filtro documental reduce candidatos; las pruebas reproducibles deciden.

### Hallazgos específicos que cambian la evaluación

- **ERPNext:** su POS Profile configura empresa, depósito, medios de pago, lista de precios, impuestos y cuentas. Su POS puede actualizar stock y alimentar contabilidad, admite varios medios de pago y ofrece reportes/dimensiones. Esto lo hace un candidato fuerte para demostrar rápido el circuito completo; no prueba por sí solo velocidad, experiencia de caja, terminales ni fiscalidad argentina.
- **MyCompany:** su cobertura funcional es muy amplia y el POS retail forma parte de la distribución. La base compartida es una restricción de arquitectura, no un detalle menor.
- **Tryton:** probar primero la serie 8.0 junto con las ramas argentinas 8.0 coordinadas. El POS oficial `sale_point` cubre ventas minoristas, pagos, vuelto, sesiones y efectos de stock/contabilidad. La localización 8.0 aporta plan contable, CUIT/padrón, WSAA/WSFE, comprobantes, bancos, pagos/cheques y reportes. Tryton 8.2 es más reciente, pero requiere adaptar y revalidar ese conjunto; no actualizar antes de completar una prueba funcional y fiscal en 8.0.
- **ARCA para Tryton:** ver el [lock reproducible del conjunto tryton-ar 8.0](TRYTON_ARGENTINA_8_0_LOCK.md). Incluye `account_invoice_ar` 8.0.1, `account_ar`, `party_ar`, `bank_ar`, vouchers, cheques, reportes y `sale_pos_ar` 8.0.0/8.0.1. `account_invoice_ar` incluye escenarios WSFE, FCE, WSFEX y recuperación; `party_ar` depende de `pyafipws` (LGPL-3). Instalar las ocho ramas juntas, fijar commits, ejecutar sus tests y homologar antes de confiarle emisión. La documentación histórica de instalación contiene referencias antiguas, por lo que mandan los manifiestos, dependencias y pruebas del código 8.0.
- **Odoo argentino:** el addon público l10n_ar cubre la localización contable base; no es el emisor WSFE por sí solo. La documentación menciona l10n_ar_edi, pero su código no apareció en el repositorio Community inspeccionado. El addon comunitario disponible para WSAA/WSFE se declara Beta. OCA l10n-argentina 19.0, al momento de la revisión, no contenía addons instalables.
- **Bigcapital:** conservar como candidato contable especializado sólo si la contabilidad nativa de los finalistas no alcanza. No sumar un segundo libro mayor ni otro inventario.

## 6. Cómo decidir: pruebas comparables y puertas obligatorias

Antes de ejecutar el protocolo completo, hacer un filtro rápido. ERPNext, MyCompany y Tryton 8.0 + tryton-ar 8.0 pasan por el mismo circuito corto; como máximo dos finalistas pasan a la evaluación profunda. Tryton 8.0 debe superar instalación conjunta, tests de los ocho módulos y homologación fiscal.

**Puertas obligatorias** (no compensables con puntaje):
1. Fuente, versión y licencia verificables de todos los componentes necesarios.
2. Instalación reproducible y operación local sin depender de un servicio cloud propietario.
3. Exportación de datos, backup y restauración en una instancia limpia.
4. APIs/contratos o mecanismos soportados; nada de integrarse escribiendo tablas privadas.
5. Una autoridad única por dato; sin duplicar ventas, pagos, stock, comprobantes o ledger.
6. POS completo: carrito editable, venta por código/peso, pagos, vuelto, turnos, devolución y auditoría.
7. Recuperación tras desconexión y terminación abrupta del proceso.
8. Camino argentino concreto: impuestos, CUIT, tipo de comprobante, punto de venta, ARCA/homologación y conciliación.
9. Interfaz en español, permisos por rol y experiencia viable para cajero y administrador.

**Ponderación después de superar las puertas:**

| Criterio | Peso |
|---|---:|
| POS y flujo de ventas/caja: velocidad, facilidad, devoluciones, pagos y hardware | 25% |
| ERP diario: catálogo, clientes/proveedores, compras, stock y costos | 20% |
| Contabilidad, fiscalidad y adaptación argentina | 15% |
| Arquitectura, APIs, extensibilidad y separación de datos | 15% |
| Reportes, dimensiones de negocio y trazabilidad hasta el movimiento | 10% |
| Confiabilidad, offline, backup, restore y actualización | 10% |
| Usabilidad administrativa y mantenimiento de la instalación | 5% |
| **Total** | **100%** |

El puntaje es evidencia de una prueba, no una preferencia subjetiva. Una plataforma que no supere una puerta se descarta para esa responsabilidad aunque tenga buen promedio.

### Circuito común de evaluación

- Catálogo: importación, variantes, códigos, unidad y peso.
- POS: escaneo, búsqueda, carrito editable, descuentos, impuestos, efectivo, vuelto y pago mixto.
- Caja: apertura, fondo inicial, movimientos, arqueo, cierre y diferencia.
- Ventas: contado, cuenta corriente, cancelación, devolución parcial/total y nota de crédito.
- Stock: reserva, salida, devolución, compra, recepción parcial, costo y conteo.
- ERP: proveedor, cliente, lista de precio, crédito, cuenta corriente y permisos.
- Finanzas: diarios, asiento, cuenta por cobrar/pagar, bancos y reportes.
- Argentina: CUIT, condiciones IVA, comprobantes A/B/C/E cuando correspondan y homologación ARCA.
- Robustez: proceso terminado abruptamente, red caída, reintento, webhook duplicado y restauración.
- Gestión: ventas por día/caja/operador/producto/área, stock, costo, margen y conciliación.

Los escenarios P01–P44 existentes siguen vigentes; la prioridad de ejecución se organiza por este circuito, no por el orden numérico ni por la facilidad de una integración.

## 7. Construcción e integración por entregas

### Entrega 0 — Seleccionar el núcleo (ahora)

- Fijar referencias: ERPNext 16, MyCompany 6.2, Tryton 8.0 + ocho módulos tryton-ar 8.0 y Dolibarr 24.0.3. Mantener Tryton 8.2 como objetivo de actualización posterior.
- Preparar laboratorio reproducible para cada candidato, sin datos reales ni credenciales productivas.
- Reutilizar el dataset sintético existente y ampliar los casos POS, inventario, caja y contabilidad.
- Probar ERPNext, MyCompany y Tryton 8.0 + localización argentina alineada con el mismo circuito POS+ERP; usar Dolibarr como filtro de menor complejidad. Sólo dos finalistas pasan a la evaluación profunda.
- Registrar capturas, tiempos, pasos, errores, salida exportada, licencias, hashes y resultados.
- Decidir qué capacidades del núcleo serán plataforma externa encapsulada, qué componentes se integran como servicios independientes y qué brechas requieren código propio.

**Salida:** decisión sustentada sobre el primer núcleo operativo; no se construyen todavía más módulos sobre una plataforma no seleccionada.

### Entrega 1 — POS operativo con el mínimo de gestión real

El primer despliegue implementa el flujo sobre las unidades del apartado anterior. Si un candidato externo cubre una parte completa, se encapsula detrás de su API y se mantiene su propia autoridad; no se convierte su base compartida en una base global de Rubrova.

- Identidad, roles, organización, sucursal, caja y depósito básicos.
- Catálogo, precios, variantes, códigos, unidades y clientes.
- Carrito y checkout de mostrador; efectivo, vuelto y medios mixtos.
- Pagos/caja, turnos, arqueos, devoluciones y anulaciones.
- Inventario con reservas y ledger; compras/recepción inicial para que exista costo de stock.
- Ticket propio, comprobante fiscal por estado separado y auditoría.
- Adaptador inicial para lector/impresora; terminal física sólo después del sandbox del adquirente.
- Panel operativo de cierre, venta neta y conciliación.

**Salida:** una jornada de prueba repetible, sin duplicados ni diferencias inexplicadas, con recuperación probada.

### Entrega 2 — ERP administrativo y control de inventario

- Artículos, listas, proveedores, clientes empresariales, condiciones y cuentas corrientes.
- Solicitud/orden de compra, recepción total/parcial, devoluciones a proveedor y costos accesorios.
- Múltiples depósitos, transferencias, conteos, ajustes autorizados, lotes y vencimientos según perfil.
- Métodos de valuación de inventario y costo histórico/reposición.
- Presupuestos, límites de crédito, aprobaciones, documentos y vencimientos.
- Importación masiva y validación de datos, sin fusionar automáticamente coincidencias dudosas.

**Salida:** compras, recepciones, stock, costo y ventas reconcilian; los reportes pueden explicar de dónde viene cada saldo.

### Entrega 3 — Contabilidad y Argentina

- Libro mayor y submayores; cuentas por cobrar/pagar; bancos y conciliaciones.
- Períodos, cierre, centros de costo y dimensiones por unidad de negocio, sucursal y canal.
- Impuestos, tipos de comprobante, numeración y punto de venta.
- ARCA en homologación con consulta/recuperación ante timeout y estados inciertos.
- Facturas, notas de crédito/débito, pagos, retenciones/percepciones según la operatoria real.
- Exportación al estudio/ERP que se use (Tango, Catedral, Bejerman, Xubio, Colppy u otros), con lotes idempotentes y conciliación.

**Salida:** ventas, stock, pagos, impuestos y ledger cuadran; no hay doble emisión ni asientos sin origen.

### Entrega 4 — Reportes de gestión y analítica

Primero reportes nativos y métricas definidas con fórmulas conocidas. Después, si la plataforma elegida no alcanza, construir un modelo analítico de sólo lectura; DuckDB es candidato para análisis/exports y Metabase o Superset se comparan sólo si hay necesidad de BI multiusuario.

Requisitos obligatorios de inteligencia comercial:

- Seguimiento diario, semanal, mensual, trimestral y por estación del hemisferio sur.
- Alertas tempranas de crecimiento, aceleración, desaceleración, estancamiento y caída por SKU, familia, marca, sucursal y canal.
- Pronóstico previo a cada trimestre/estación, con rangos, confianza, historial disponible, calendario y factores relevantes.
- Ajuste por quiebres de stock, disponibilidad, promociones, precios y surtido.
- Rentabilidad por producto/marca: ganancia absoluta, margen porcentual, contribución neta de costos variables, costo de reposición, GMROI y capital inmovilizado.
- Matriz de alta/baja venta versus alta/baja rentabilidad.
- Clasificación configurable de primeras marcas, segundas, económicas, propias y alternativas; medir participación por unidades, tickets, ventas y ganancia.
- Detección de sustitución y cambios de preferencia entre segmentos.
- Simulación de compras, precios y promociones; toda ejecución requiere aprobación.
- Backtesting y medición de error/sesgo de pronósticos.

Orden de informes:

1. Cierre diario: ventas netas, cantidad de tickets, ticket promedio, descuentos, devoluciones, medios de pago y diferencias de caja.
2. Ventas: producto, variante, marca, categoría, cajero, cliente, sucursal, canal y área.
3. Inventario: disponible, reservado, en tránsito, rotación, cobertura, quiebre, excedente, vencimiento y antigüedad.
4. Costos y rentabilidad: costo vendido, margen bruto, contribución después de comisiones/envíos, precio de reposición y GMROI.
5. Compras/proveedores: plazo, cumplimiento, costo, diferencias y propuestas de reposición.
6. Finanzas: caja, bancos, cuentas por cobrar/pagar, mora, flujo de caja y resultados.
7. Áreas: minorista, ecommerce, mayorista/distribución y servicios, además del consolidado.

Cada métrica documenta fórmula, fuente, filtros, fecha de actualización, manejo de datos faltantes y posibilidad de navegar al documento/movimiento de origen. No publicar margen si el costo está ausente o desactualizado sin mostrar esa limitación.

**Salida:** indicadores que concilian con el sistema transaccional y no bloquean el POS.

### Entrega 5 — Perfiles sectoriales y expansión comercial

- Gastronomía/panadería/rotisería: recetas, BOM, rendimiento, merma, producción por tandas, comandas, cocina y vencimientos.
- Mayorista/distribución: mínimos, múltiplos, escalas, listas por cliente, crédito, entregas parciales y costo de servir.
- Servicios B2B: cotización, contratos versionados, recurrencia, SLA, agenda, órdenes de trabajo, materiales, horas y rentabilidad.
- Multiárea: reglas y permisos por unidad, reportes por línea y consolidación sin ingresos internos ficticios.

**Salida:** los perfiles reutilizan los mismos contratos y datos base, sin duplicar POS, clientes o inventario.

### Entrega 6 — Omnicanalidad e integraciones

- Ecommerce, pedidos por WhatsApp, marketplaces y delivery.
- Integrar un canal por vez, empezando por el que tenga demanda real y documentación/sandbox.
- Importar pedido/pago/devolución/comisión con IDs externos e idempotencia.
- Evitar doble emisión fiscal y sobreventa; preservar quién es la autoridad del pedido, pago y stock.

Spree y Saleor quedan como candidatos para canal ecommerce, no como ERP/POS principal. PowerSync se prueba para lectura/tareas offline no conflictivas, no para decidir quién vende la última unidad.

**Salida:** los pedidos externos se concilian con ventas, pagos, impuestos y stock sin duplicados.

### Entrega 7 — Logística avanzada

- Fulfillment independiente de la venta desde el modelo inicial.
- Primero retiro y entrega propia/manual.
- Después Andreani, Correo Argentino PAQ.AR y OCA según credenciales y pruebas de QA.
- Vía Cargo mediante tracking externo hasta confirmar API operativa; Kangu sólo si se verifica servicio argentino.
- Agregadores, tarifas, etiquetas, webhooks, seguimiento, reclamos e indicadores logísticos.

**Salida:** ningún transportista controla la venta ni el inventario maestro; cada guía y evento conserva el vínculo al pedido y a la entrega.

## 8. Estrategia de reutilización según la fase

| Necesidad | Candidato | Momento | Qué no delegar |
|---|---|---|---|
| POS + ERP base | ERPNext, MyCompany, Tryton, Dolibarr | Entrega 0 | Decisión de arquitectura y prueba de caja |
| POS específico | POS incluido; Posnic sólo referencia | Entrega 0–1 | Fuente única de stock, pagos y venta |
| Hardware | QZ Tray / pos-toolkit | Entrega 1 | Reglas comerciales y autorización del pago |
| Fiscal argentina | Addons Tryton/Odoo verificados; arca-sdks / LaPyme / pyafipws según stack | Entrega 0–3 | Idempotencia, conciliación y estado fiscal final |
| Importación/normalización | OpenRefine, Frictionless, RapidFuzz, python-stdnum, Pint | Entrega 1–2 | Aprobación/fusión humana de registros ambiguos |
| Contabilidad especializada | Nativa del ERP; Bigcapital sólo como alternativa completa | Entrega 0–3 | Dos libros mayores simultáneos |
| Analítica | Reportes nativos; DuckDB; Metabase/Superset | Entrega 4 | Escrituras sobre ledgers operativos |
| Producción | Módulos de fabricación del núcleo; InvenTree/OCA sólo si encajan | Entrega 5 | Segundo dueño de stock |
| Ecommerce | Spree o Saleor, uno como máximo | Entrega 6 | Autoridad del catálogo, precio e inventario |
| Offline | Capacidades nativas, después PowerSync si aporta valor | Entrega 1–6 | Reservas/stock sin coordinación |
| Logística | Adaptadores directos, Karrio/agregador si conviene | Entrega 7 | Venta, cobro y stock maestro |
| Observabilidad/SSO | Logs nativos primero; OpenTelemetry/Grafana/Keycloak si la escala lo exige | Cuando haya varios servicios | Operación básica y permisos del dominio |

Regla general: primero capacidades nativas y extensiones soportadas; luego aplicación de dominio externa; después biblioteca/SDK; por último desarrollo propio de la brecha. Registrar tag/commit, licencia de cada componente y dependencia, pruebas, backup, exportación y costo de actualizar.

## 9. Criterios de terminado por entrega

Ninguna entrega se cierra por tener pantallas o completar un README. Requiere:

- Flujo principal, errores y estados pendientes documentados.
- Pruebas unitarias, integración, contrato y end-to-end según alcance.
- Permisos, auditoría y aislamiento verificados.
- Idempotencia para comandos reintentables y webhooks.
- Concurrencia de stock y caja controlada.
- Backup y restauración probados; actualización y rollback definidos.
- Rendimiento medido en caja y reportes sin bloquear la operación.
- Textos y errores en español, experiencia accesible y documentación de uso.
- Dependencias, licencias, hashes y avisos inventariados.
- Evidencia de pruebas y limitaciones conocidas; nada se marca aprobado sin ejecutar.

## 10. Qué queda deliberadamente fuera del inicio

No construir primero tracking multioperador, ecommerce complejo, asistente con IA, pronósticos avanzados, dashboards sofisticados, WMS completo, nómina, infraestructura de Kubernetes/Kafka ni numerosos microservicios. Tampoco elegir Bigcapital, InvenTree, PowerSync, Metabase, Superset, Keycloak o Grafana sólo porque existan.

Cada uno podrá entrar cuando una brecha concreta y medible justifique su costo de instalación, integración, actualización y soporte.

## 11. Decisiones que necesitamos cerrar con evidencia

1. ¿Qué candidato permite la mejor experiencia POS y el circuito de ventas/caja/inventario sin parches invasivos?
2. ¿Cuál cubre el ERP diario y los cálculos de costos con menos adaptación?
3. ¿Qué límites de servicio se pueden mantener sin convertir un ERP integrado en la base de todos los dominios?
4. ¿Existe localización argentina mantenida y compatible con la versión exacta? ¿Qué parte requiere un servicio fiscal propio?
5. ¿Se puede exportar y restaurar sin dependencia del proveedor?
6. ¿Cuánto cuesta mantener las extensiones en cada actualización?

La decisión no se tomará por cantidad de funciones ni por estrellas de GitHub. Se elegirá la composición que complete mejor el circuito operativo, respete límites de datos, sea recuperable y tenga el menor costo total de adaptación y mantenimiento.

## Referencias principales

- [ERPNext — POS Profile](https://docs.frappe.io/erpnext/pos-profile)
- [ERPNext — Point of Sale](https://docs.frappe.io/erpnext/point-of-sale)
- [ERPNext — Accounting Introduction](https://docs.frappe.io/erpnext/accounting-introduction)
- [ERPNext — Accounting Dimensions](https://docs.frappe.io/erpnext/accounting-dimensions)
- [Tryton 8.0 — Sale Point](https://docs.tryton.org/8.0/modules-sale-point/design.html)
- [Tryton 8.2 — Sale Point, actualización posterior](https://docs.tryton.org/8.2/modules-sale-point/design.html)
- [Localización argentina Tryton — ramas 8.0](https://github.com/tryton-ar)
- [Tryton 8.2 — Accounting releases](https://docs.tryton.org/8.2/modules-account/releases.html)
- [MyCompany 6.2](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [Dolibarr — API, triggers and hooks](https://www.dolibarr.org/presentation-api.php)
- [Estrategia reuse-first](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md)
- [Evaluación de plataformas](PLATFORM_EVALUATION.md)
- [Requisitos del POS](POS_REQUIREMENTS.md)
- [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md)
- [Inteligencia del negocio](BUSINESS_INTELLIGENCE.md)
- [Continuidad y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md)
