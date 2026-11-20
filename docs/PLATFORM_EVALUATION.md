# Evaluación comparativa de plataformas

**Revisión:** 20 de noviembre de 2026  
**Estado:** laboratorio preparado; dataset de evaluación 27/27 y benchmark mensual de demanda aprobados en CI; ejecución local de plataformas pendiente.  
**Alcance:** uso interno, personal y privado. No se prevé distribuir, revender ni ofrecer el sistema como servicio a terceros.

Este documento convierte la investigación en una prueba repetible. No elige una plataforma por su README, una demo o la cantidad de módulos anunciados. La elección depende de ejecutar los mismos flujos, con datos sintéticos, y comprobar integridad, recuperación, esfuerzo de adaptación y mantenimiento.

## Decisión de evaluación

**Objetivo principal:** evaluar la capacidad de completar una operación POS y de gestión completa, no empezar por integraciones periféricas. El primer circuito de prueba es catálogo → carrito editable → venta → pago/vuelto → caja → inventario → devolución → reporte y recuperación.

**Orden de la primera ronda:**
1. **ERPNext 16 / Frappe 16:** primera prueba funcional por su POS integrado con inventario, pagos, caja, perfiles y reportes/dimensiones.
2. **MyCompany 6.2 / lsFusion:** primera prueba funcional por su Retail POS y cobertura CRM, ventas, compras, inventario, fabricación y facturación.
3. **Tryton 8.0 + tryton-ar 8.0:** evaluación POS/ERP con localización argentina alineada; se deben instalar las ocho ramas coordinadas, ejecutar sus tests y homologar. Tryton 8.2 queda como actualización posterior.
4. **Dolibarr 24.0.3:** filtro corto como alternativa de menor complejidad.
5. **Posnic 1.9.2:** referencia POS secundaria, no ERP principal. Se prueba sólo si puede aportar algo que no cubre el POS de las plataformas anteriores.

No se amplía la lista sin una razón funcional. uniCenta queda fuera de la primera ronda hasta tener el código fuente exacto y licencias verificables.

**MyCompany:** su amplitud y POS justifican la prueba, pero todos los módulos de la instalación comparten una base. Esto es una restricción arquitectónica que se debe medir; no se presenta como microservicios independientes.

**ERPNext:** su POS Profile configura empresa, almacén, métodos de pago, listas, impuestos y cuentas; la operación afecta inventario y contabilidad, con reportes y dimensiones. Hay que comprobar velocidad real de caja, experiencia táctil, hardware, offline y localización argentina. Un site/bench es una unidad de operación y persistencia, no módulos desplegables como microservicios independientes.

**Tryton:** la alternativa argentina más directa que encontramos es Tryton 8.0 con el [conjunto de módulos fijado por commit](TRYTON_ARGENTINA_8_0_LOCK.md). Se verificaron manifiestos: account_invoice_ar 8.0.1; account_ar, party_ar, bank_ar, account_voucher_ar, account_check_ar y sale_pos_ar 8.0.0; account_report_ar 8.0.1. Los ocho repositorios contienen pruebas. account_invoice_ar incluye escenarios WSFE, FCE, WSFEX y recuperación; party_ar cubre CUIT/padrón mediante pyafipws. El módulo oficial sale_point también tiene release 8.0.0. La prueba debe instalar el conjunto completo desde cero, fijar cada commit, ejecutar los tests y homologar ARCA. Tryton 8.2 es más reciente, pero requiere adaptar y volver a validar los módulos argentinos; se trata como actualización posterior, no como inicio.

**Dolibarr:** su API REST, triggers, hooks y TakePOS justifican un filtro corto. Medir la profundidad del flujo de caja y gestión, la localización argentina, los costos y la recuperación.

**Posnic:** mantenerlo acotado a POS. Revisar código AGPL-3.0-only, MongoDB SSPL-1.0 y amCharts comercial por separado, además de la adaptación argentina y los límites offline publicados.

**Regla de arquitectura:** hay dos resultados válidos. (A) Una suite POS+ERP se adopta como núcleo operativo integrado y autoridad única para los dominios que cubra; sus módulos comparten base/runtime y no se llaman microservicios. (B) Los dominios se resuelven con servicios independientes cuando exista una ventaja comprobable y contratos soportados. La base compartida se registra como coste de acoplamiento, actualización y salida, pero no descarta automáticamente una suite. En ambos casos, los componentes externos acceden mediante APIs/eventos/exportaciones soportadas; no por SQL cruzado ni replicando ventas, pagos, stock o costos.

**Regla de selección:** filtro documental/código para todos; prueba corta POS+ERP de los candidatos iniciales; como máximo dos finalistas a P01–P57. Se debe demostrar instalación local, caja rápida, integridad transaccional, permisos, exportación completa, backup cifrado y restauración en equipo distinto, interfaces soportadas, extensibilidad, operación en español y camino fiscal argentino. Una demo o un README no cuentan como aprobación. La arquitectura se puntúa por el control real de datos y la posibilidad de evolución/salida, no por cantidad de procesos separados.

**Estado actual:** ninguna plataforma está aprobada, instalada y aceptada para producción. El repositorio todavía no contiene la aplicación funcional de Rubrova ni código externo incorporado. La validación de fixtures no prueba un POS ni un ERP.

## Versiones y procedencia que se deben fijar

| Proyecto | Referencia para laboratorio | Licencia declarada / dato relevante | Precaución |
|---|---|---|---|
| MyCompany | Tag 6.2, commit `d21ca6978717b98b6300d90267f9767db7414008` | Aplicación Apache-2.0; lsFusion LGPL-3.0 | La documentación online puede referirse a otra versión. Los módulos comparten una base de datos. |
| Tryton | Serie 8.0 con ocho ramas tryton-ar 8.0; fijar servidor, cliente y módulo por commit | GPL-3.0 en módulos argentinos; pyafipws LGPL-3.0 | `sale_point` 8.0.0; manifiestos argentinos 8.0.0/8.0.1. Tryton 8.2 requeriría port y homologación posterior. |
| Dolibarr | 24.0.3, release estable consultada | Proyecto GPL-3.0; verificar módulos externos individualmente | API REST y hooks/triggers; probar autenticación y límites de API. |
| ERPNext | Release 16.60.0, tag/commit fijados en el laboratorio existente | ERPNext GPL-3.0; Frappe Framework MIT | Registrar la versión efectiva del framework y no mezclar tags. |
| Posnic | Tag `v1.9.2`, commit `4096126edb1ff4fd337069697776254215dc2680` | Código AGPL-3.0-only | Verificar MongoDB SSPL-1.0, amCharts comercial y todas las dependencias del instalador. |
| uniCenta oPOS | Release 5.5.2 publicada el 29/10/2026 | No aprobar hasta obtener el código actual y revisar sus avisos | La descarga del código requiere login; mirrors antiguos no fijan el paquete actual. |
| Apache OFBiz | Release 24.09.08, noviembre de 2026 | Apache-2.0 | Serie 24.09 congelada en funciones desde septiembre de 2024; mantener en observación salvo necesidad concreta. |

Los hashes de artefactos descargados, las instrucciones exactas y los resultados del laboratorio se registran en [Laboratorio de evaluación](PLATFORM_LAB_SETUP.md). Una versión citada en esta tabla no implica que haya sido instalada, ejecutada o aprobada.

El repositorio Posnic declara `develop` como rama predeterminada, pero en la consulta del 19/11/2026 esa rama estaba divergida respecto del tag estable: dos commits por delante y 27 por detrás. La rama `main` tenía seis commits por delante del tag. Por reproducibilidad, la primera prueba debe usar el tag estable `v1.9.2`; las diferencias de `main` se revisan aparte. No usar `develop` como sustituto silencioso del release.

**Compatibilidad del paquete Posnic 1.9.2:** la release publica instalador firmado para Windows x64 y AppImage/paquete Debian para Linux x86_64, pero no un instalador macOS. El manual oficial señala que la notarización del binario nativo seguía en corrección. Si el equipo principal es Mac, la prueba de escritorio debe hacerse en una VM Ubuntu Desktop x86_64 con el AppImage; no instalar un paquete no notarizado. Los hashes de los instaladores y los comandos de validación están en [Laboratorio de evaluación](PLATFORM_LAB_SETUP.md).

Fuentes de versión:
- [MyCompany 6.2](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [MyCompany code tag](https://github.com/lsfusion-solutions/mycompany/tree/6.2)
- [Posnic v1.9.2](https://github.com/Posnic/POS/releases/tag/v1.9.2)
- [Posnic main](https://github.com/Posnic/POS/tree/main)
- [ERPNext v16.60.0](https://github.com/frappe/erpnext/releases/tag/v16.60.0)
- [Configuración oficial Frappe Docker fijada](https://github.com/frappe/frappe_docker/blob/ef24ebc0a411b6237694765f0b51d8f8f8dd13ce/pwd.yml)

## Perfil técnico y riesgos conocidos

### MyCompany / lsFusion 6.2

La aplicación MyCompany tiene licencia Apache-2.0 y utiliza la plataforma lsFusion, que tiene licencia independiente LGPL v3. La release 6.2 incluye CRM, ventas, compras, inventario, fabricación, facturación, RR. HH., proyectos y Retail POS. La documentación de desarrollo describe cómo añadir módulos propios y seleccionar módulos existentes mediante dependencias declaradas.

**Ventajas:** cobertura funcional extensa; módulos seleccionables; web client accesible desde los tres OS de escritorio; instalación Windows y Linux; posibilidad de Docker. Es un candidato importante para reutilizar capacidades ERP en vez de reconstruirlas.

**Riesgos:** no se demostró adaptación argentina, ARCA ni terminales locales; el POS y módulos fiscales pueden depender de configuraciones regionales. El release etiquetado es 6.2 (commit d21ca6978717b98b6300d90267f9767db7414008), mientras la documentación online consultada se identifica como 7.0 y master declara 7.0-SNAPSHOT. No tomar instrucciones de 7.0 como prueba de funciones en 6.2.

**Prueba requerida:** ejecutar POS, sesiones, pagos mixtos/vuelto, inventario, compras y producción; añadir un módulo custom mínimo sin parchear el core; comprobar comportamiento al actualizar.

### Posnic

La aplicación de escritorio usa Electron y Node.js; la API local usa Express/Mongoose y MongoDB. El propio repositorio se identifica como AGPL-3.0-only y el paquete revisado exige Node.js >=22.12.

**Encaje potencial**
- POS para comercio minorista y gastronomía, catálogo, variantes, ventas, devoluciones, pagos parciales, compras, inventario, clientes, permisos y reportes.
- La edición de escritorio puede mantener API y base principal en el equipo de caja.
- La instalación self-hosted permite que varios equipos de una misma red local usen una base común.

**Límites que debemos probar**
- Self-hosted con varios clientes no significa varias bases independientes sincronizadas. La documentación del proyecto dice que sincronizar cajas o sucursales separadas corresponde a Posnic Cloud, un servicio aparte.
- La prueba offline publicada que acompaña al producto está acotada: una venta sintética en efectivo completada y reabierta en una versión anterior, dentro de Electron, con ciertos hosts bloqueados. No demuestra una jornada completa, corte de energía, recuperación tras matar el proceso, terminales de pago ni todos los flujos.
- El outbox local de sincronización es un acelerador opcional; el propio código aclara que no es el mecanismo de registro de la venta y que el escaneo periódico sigue siendo el respaldo.
- El modelo contiene campos y reglas orientados a India, incluidos datos GST. Hay que medir el trabajo para reemplazarlos o aislarlos frente a IVA, tipos de comprobante, CUIT, puntos de venta y ARCA.
- La dependencia de MongoDB/Mongoose y la arquitectura propia tienen costo de migración y mantenimiento; no asumir que se pueden extraer módulos sueltos sin arrastrar parte del sistema.

**Licencias y paquete**
- Código propio: AGPL-3.0-only. Para nuestro uso privado, GPL/AGPL no son descartes automáticos; sí debemos mantener avisos y revisar las condiciones si usuarios acceden remotamente a una versión modificada por red o si cambia el uso previsto.
- El paquete de escritorio revisado incorpora MongoDB Community Server 7.0.14 bajo SSPL-1.0, una licencia separada de la del POS. No describir el instalador entero como AGPL.
- El aviso de terceros identifica amCharts 4 como comercialmente licenciado. No reutilizar ese componente sin confirmar que la licencia permite nuestro uso; la opción segura puede ser reemplazarlo por una biblioteca compatible o no usar esa parte.
- Deben inspeccionarse los avisos y licencias de las dependencias transitivas del paquete exacto que se ejecute.

### ERPNext + Frappe

ERPNext aporta procesos ERP profundos: inventario, abastecimiento, compras, fabricación, contabilidad y administración. Frappe Framework proporciona el entorno de aplicaciones, documentos, permisos, API, formularios y tareas de fondo.

**Encaje potencial**
- Puede adelantar mucho trabajo de compras, proveedores, recepciones, costos, stock, producción, cuentas e informes.
- Los perfiles de POS configuran empresa, almacén, medios de pago, listas de precios, impuestos, terminal y comportamiento de la caja.
- Frappe Framework tiene licencia MIT; ERPNext tiene GPL-3.0. No confundir ambas licencias.

**Límites que debemos probar**
- La cobertura de ERP no garantiza una caja de alta velocidad ni una experiencia táctil simple.
- No damos por demostrado el offline duradero de la versión 16. Hay que cortar internet, cerrar el navegador o matar el proceso y recuperar las operaciones sin pérdidas ni duplicados.
- El stack habitual de Frappe/ERPNext gira alrededor de Python y MariaDB; PostgreSQL no se debe asumir como una opción equivalente o estable para esta evaluación.
- La prueba local usa la configuración oficial desechable `frappe_docker/pwd.yml`, fijada al commit `ef24ebc0a411b6237694765f0b51d8f8f8dd13ce` y a la imagen `frappe/erpnext:v16.60.0`. No admite instalar aplicaciones propias en esta modalidad. Registrar la versión exacta de Frappe con `bench version`.
- La adaptación del POS, localización argentina, hardware y experiencia de uso puede exigir extensiones considerables.

### Tryton 8.0, POS y localización argentina

Tryton 8.0 ofrece arquitectura cliente-servidor con PostgreSQL y un módulo oficial sale_point 8.0.0 para ventas minoristas, pagos, vuelto, sesiones y efectos de stock/contabilidad. El conjunto de localización argentina en ramas 8.0 cubre: account_ar (plan de cuentas/impuestos), party_ar (entidades, CUIT/padrón), bank_ar, account_invoice_ar (WSFE/WSFEX, FCE, recuperación), account_voucher_ar (cobros/pagos), account_check_ar, account_report_ar (subdiarios/CITI y reportes) y sale_pos_ar. Todos los manifiestos declaran 8.0.0/8.0.1. Los repositorios contienen tests de módulo y escenarios; account_invoice_ar cubre WSFE, FCE, WSFEX y recuperación. Fuentes: [sale_point 8.0](https://docs.tryton.org/8.0/modules-sale-point/design.html), [account_invoice_ar 8.0](https://github.com/tryton-ar/account_invoice_ar/tree/8.0), [account_ar 8.0](https://github.com/tryton-ar/account_ar/tree/8.0), [party_ar 8.0](https://github.com/tryton-ar/party_ar/tree/8.0), [bank_ar 8.0](https://github.com/tryton-ar/bank_ar/tree/8.0), [account_voucher_ar 8.0](https://github.com/tryton-ar/account_voucher_ar/tree/8.0), [account_check_ar 8.0](https://github.com/tryton-ar/account_check_ar/tree/8.0), [account_report_ar 8.0](https://github.com/tryton-ar/account_report_ar/tree/8.0) y [sale_pos_ar 8.0](https://github.com/tryton-ar/sale_pos_ar/tree/8.0). No confundir sale_pos_ar (lleva el punto de venta fiscal a la venta/factura) con sale_point (interfaz POS minorista oficial).

**Ventaja de reutilización:** existe código oficial real de POS, con reglas de caja, pagos y efectos transaccionales, no sólo una pantalla o demo.

**Riesgos:** Tryton y sus módulos comparten servidor/base, por lo que la suite no equivale a microservicios separados. La documentación de instalación histórica de tryton-ar todavía contiene referencias antiguas a Tryton 3.0; la prueba se debe basar en los manifiestos, dependencias, commits y tests de las ramas 8.0, no en copiar ciegamente esas instrucciones. Hay que comprobar que las ocho ramas se instalan juntas sin resolver dependencias hacia `master`, ejecutar sus suites y probar emisión/recuperación en homologación. El salto a Tryton 8.2 exigiría volver a adaptar y probar.

**Prueba específica:** venta al contado y pago mixto, vuelto, devolución, sesión de caja, asiento, movimientos de stock, lector simulado, API, exportación y restauración. Añadir cierre abrupto del servidor y recuperación después de reiniciarlo.

## Reglas de prueba comunes

- Usar instalaciones aisladas y bases nuevas. No cargar ventas reales, datos personales, certificados privados ni credenciales de producción.
- Usar el mismo conjunto de datos sintéticos, zona horaria, moneda, catálogo, flujo y casos de error.
- Registrar versiones, commits, sistema operativo, configuración, comandos, duración, resultados y capturas de evidencia.
- No modificar el núcleo de los candidatos durante la primera vuelta. Registrar cada extensión, parche o workaround por separado.
- Repetir cada escenario crítico al menos tres veces y repetir sincronizaciones o reintentos cuando corresponda.
- Mantener deshabilitadas las integraciones que generen cargos o efectos externos. ARCA se prueba únicamente en homologación, nunca con certificados de producción durante esta evaluación.
- Un escenario no probado se marca **pendiente**, no aprobado. Un flujo que solo funciona con la ventana abierta no pasa la recuperación.

## Datos sintéticos compartidos

La prueba debe representar una operación argentina sencilla, sin utilizar información real. Los datos canónicos, con importes en unidades menores enteras y resultados esperados, están en [dataset sintético](fixtures/platform-evaluation.json):

| Dato | Valor de prueba |
|---|---|
| Idioma y zona | Español (Argentina), `America/Argentina/Cordoba` |
| Moneda | ARS |
| Artículo por unidad | `SKU-UNIT-001`, precio de ejemplo $10.000 |
| Artículo por peso | `SKU-WEIGHT-001`, venta en kg, precisión de 0,001 kg |
| Variante | `SKU-VAR-001`, dos variantes con códigos distintos |
| Proveedor | `PROV-TEST-001` |
| Cliente | `CLI-TEST-001`, identidad ficticia |
| Caja inicial | $20.000 |
| Venta de prueba | Dos artículos; total de ejemplo $10.000 |
| Pago mixto | $6.000 efectivo + $4.000 transferencia simulada |
| Descuento | 10% en una línea, con motivo y operador registrados |

Los importes son datos didácticos y no representan precios de mercado ni reglas fiscales. La prueba debe incluir además una venta por peso de 0,325 kg y comprobar redondeos, cantidades, importe por línea y total.

## Guion de aceptación común

| ID | Escenario | Evidencia exigida | Falla crítica |
|---|---|---|---|
| P01 | Alta e importación de artículos, variantes, códigos y unidades | Datos conservados, búsqueda por código y errores de importación identificados | Artículo duplicado o unidad mal interpretada |
| P02 | Venta rápida con lector simulado | Carrito, precio aplicado, cantidad y ticket coinciden | Venta o línea perdida/duplicada |
| P03 | Descuento manual y promoción | Regla, valor previo, importe, motivo, operador y autorización auditables | Descuento silencioso o no trazable |
| P04 | Venta por peso | 0,325 kg, precisión y redondeo coherentes | Diferencia inexplicable entre balanza, línea y total |
| P05 | Pago mixto y vuelto | $6.000 + $4.000 para total $10.000; movimientos y medios separados | Pago duplicado, suma incorrecta o caja descuadrada |
| P06 | Apertura, cierre y arqueo | Saldo esperado, efectivo contado, diferencia y responsable | No poder reconstruir el saldo |
| P07 | Devolución parcial | Línea devuelta, motivo, reintegro y destino del stock diferenciados | Borrar o sobrescribir la venta original |
| P08 | Compra y recepción parcial | Proveedor, orden, cantidades recibidas, costo y stock | Stock o costo actualizado sin documento trazable |
| P09 | Producción básica | Receta/BOM, consumo, rendimiento y merma | Consumo de insumos sin trazabilidad |
| P10 | Dos puestos en la misma LAN a través de APIs de servicios | Gateway, contratos, autoridad de Inventario/Pagos, correlación y aislamiento entre servicios | Acceso SQL cruzado, doble numeración o saldo/stock inconsistente |
| P11 | Corte de internet | Venta local guardada y estado de servicios externos visible | Bloquear o perder una venta local ya confirmada |
| P12 | Terminación abrupta del proceso POS/servicio y reinicio | Reiniciar sólo el proceso afectado y verificar operaciones/Outbox/Inbox | Pérdida, duplicación o corrupción |
| P13 | Reintento con la misma clave idempotente | Repetir el comando tres veces y devolver el mismo resultado registrado | Doble venta, pago, factura o movimiento |
| P14 | Conflicto de precio/stock | Precio versionado y reserva/CAS con expected_version; conciliación auditada | Sobrescritura silenciosa o último cambio gana en dinero/stock |
| P15 | Backup y restauración distribuida | Restaurar manifiesto de servicios, bases y offsets/eventos en una instancia limpia | Backup ilegible, corte inconsistente o restauración incompleta |
| P16 | Hardware | Ticket de 80/57 mm, lector, balanza y cajón; primero simulado, luego físico | Confirmar compatibilidad por marca sin prueba |
| P17 | Fiscalidad argentina | Adaptador separado, comprobantes en homologación y recuperación de estado incierto | Emisión duplicada o reintento ciego |
| P18 | Retiro de productos antes del pago | Eliminar una línea y comprobar total, descuentos/impuestos, reserva y ausencia de venta/salida/pago para el artículo retirado | La línea retirada queda cobrada o descuenta stock |
| P19 | Terminal integrada e impresión desde el dispositivo | Enviar importe, detectar estado final, procesar webhook repetido, conciliar voucher e imprimir desde la terminal el ticket detallado de Rubrova | Marcar cobrado antes de confirmación, duplicar transacción o no poder imprimir el ticket requerido |
| P20 | Separación multiárea | Mismo cliente en retail, wholesale y servicios; ventas/costos quedan en su área y se consolidan sin duplicados | Duplicar cuenta o mezclar ingresos/costos de áreas |
| P21 | Mínimos y escalas mayoristas | Validar mínimo por SKU, pack multiple, mínimo cesta, lista cliente y tier por cantidad/importe | Aplicar regla equivocada, precio inconsistente o excepción no auditada |
| P22 | Acuerdo B2B y crédito | Cotización/pedido empresarial con condiciones, límite, plazo y vigencia congelados | Aceptar sobre límite sin autorización o cambiar precio histórico |
| P23 | Despacho posterior a la venta | Venta confirmada sin tracking; crear envíos parciales y agregar carrier/guía después; pickup/own fleet/carrier | Exigir guía antes de vender, duplicar salida o perder enlace pedido-envío |
| P24 | Contrato y cumplimiento de servicios | Contrato versionado, agenda recurrente, SLA, orden, horas/materiales, evidencia y facturación | Trabajo sin obligación/contrato o factura duplicada |
| P25 | Rentabilidad por área y consolidado | Ingresos, costo directo, gastos compartidos y allocation suman correctamente; P&L por área y global | Doble conteo, costo no asignado oculto o total no conciliado |
| P26 | Consumo y transferencias internas entre áreas | Un área consume stock/servicio de otra; costo y movimiento se registran una vez; cargos internos se eliminan en el consolidado de la misma entidad legal | Venta ficticia, movimiento duplicado, costo duplicado o eliminación incorrecta |
| P49 | Fundación de datos para inteligencia comercial y demanda | Producto con marca/segmento por categoría y vigencia; unidad comparable; precio/costo histórico; promociones; ventas mensuales por SKU, sucursal, canal y área; disponibilidad y días sin stock; exportación/API soportada | El ERP sólo conserva valores actuales, no puede reconstruir el estado histórico, confunde faltantes con caída de demanda o no permite extraer esos datos sin SQL privado |

### P50–P57 — trazabilidad comercial, datos analíticos y exportación

| ID | Escenario | Evidencia exigida | Falla crítica |
|---|---|---|---|
| P50 | Dimensiones sin confusión | Área, canal, formato, sucursal, depósito y fulfillment separados; venta mayorista por WhatsApp y minorista local/digital clasificadas correctamente | Mezclar canal con área o formato y distorsionar reportes |
| P51 | Historial de catálogo | Reconstruir marca/segmento, presentación, unidad, precio y costo vigentes al vender, incluso tras cambios posteriores | Reescribir el pasado con valores actuales |
| P52 | Tiempo y disponibilidad | Fecha de recepción/movimiento, ocurrido/registrado/efectivo y quiebre por ubicación; stockout no se interpreta como demanda cero | Perder temporalidad o censurar incorrectamente demanda |
| P53 | Pagos, referencias y conciliación | Pagos mixtos, intentos fallidos, referencias externas, idempotencia, comisiones, liquidación, reintegro y conciliación | Marcar como cobrado un intento incierto o duplicar cobros |
| P54 | Cajeros, cajas y turnos | Responsable, supervisor, caja, turno, dispositivo, apertura, egresos, arqueo y diferencias reconstruibles | No poder atribuir un movimiento de efectivo |
| P55 | Promociones y descuentos | Regla/versiones, elegibilidad, descuentos distribuidos por línea y autorización del precio manual | Descuento no reproducible o sin responsable |
| P56 | Reclamos, devoluciones y envíos | Diferenciar reclamo, devolución física, disposición, reintegro, nota de crédito y una o varias entregas; referencias cruzadas conservadas | Resolver reclamo con movimiento incorrecto o duplicar stock/reintegro |
| P57 | Exportación analítica portable | Mismo informe filtrado en CSV, XLSX y Parquet con manifiesto/diccionario; reproducir totales fuera del ERP usando DuckDB u otra herramienta compatible | Exportar sólo PDF, perder relaciones/unidades o no reproducir indicadores |

Los P50–P57 extienden P49: no reemplazan las pruebas existentes. La matriz completa, los atributos temporales y el diseño de exportación están en [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md). Las herramientas propuestas son candidatas; la prueba debe poder realizarse aunque no se instalen todas.

En P11 se debe distinguir pérdida de internet de pérdida de red local. En un servidor local compartido, los otros puestos pueden seguir conectados por LAN; una caja con su propia base desconectada es un caso distinto y debe documentarse como tal.

En P17 no se emitirán comprobantes reales. Una respuesta incierta de ARCA debe pasar por consulta/recuperación antes de cualquier nuevo intento; nunca asumir que un timeout significa que no se emitió.

P49 se evalúa dentro del circuito POS+ERP, aunque el motor de forecasting no se instale en la plataforma candidata. El objetivo es probar que los hechos comerciales necesarios quedan guardados desde el día uno y se pueden extraer mediante una interfaz soportada. El fixture ampliado está en [inteligencia de demanda, rentabilidad y marcas](DEMAND_AND_MARGIN_INTELLIGENCE.md) y [historial mensual sintético](fixtures/demand-monthly-history.json).

## Medición y decisión

Cada criterio se califica de 0 a 5 únicamente después de ejecutar la prueba:

| Nota | Interpretación |
|---:|---|
| 0 | No existe o no se pudo demostrar |
| 1 | Solo funciona con un workaround manual frágil |
| 2 | Requiere personalización invasiva o cambios del núcleo |
| 3 | Funciona mediante una extensión propia con esfuerzo apreciable |
| 4 | Funciona mediante extensión/configuración limpia y mantenible |
| 5 | Función nativa demostrada con pruebas repetibles y evidencia |

Ponderación propuesta después de superar las puertas obligatorias:

| Área | Peso |
|---|---:|
| POS y flujo de ventas/caja: velocidad, facilidad, devoluciones, pagos y hardware | 25% |
| ERP diario: catálogo, clientes/proveedores, compras, stock y costos | 20% |
| Contabilidad, fiscalidad y adaptación argentina | 15% |
| Arquitectura, APIs, extensibilidad, autoridad única y coste de acoplamiento/salida | 15% |
| Reportes, dimensiones de negocio y trazabilidad hasta el movimiento | 10% |
| Confiabilidad, offline, backup, restore y actualización | 10% |
| Usabilidad administrativa y mantenimiento de la instalación | 5% |
| **Total** | **100%** |

La matriz y los escenarios detallados están en [Plan maestro de implementación](MASTER_IMPLEMENTATION_PLAN.md). No se calcula un ganador ponderado si falla una puerta excluyente. Para pasar a la fase siguiente deben demostrarse: venta y efectos asociados exactamente una vez; caja y stock conciliados; recuperación tras terminación abrupta; backup restaurable; roles correctos; API soportada y ruta fiscal argentina viable.

**Comprobación fiscal argentina adicional (si Odoo entra en la composición):** el código público de Odoo Community incluye `l10n_ar` en ramas 19.0 y 20.0 (manifiesto 3.7, LGPL-3), que aporta localización contable, impuestos, tipos documentales y datos ARCA. La documentación oficial enumera separadamente `l10n_ar_edi` para emitir comprobantes por web service, pero esa ruta no aparece en el repositorio Community público inspeccionado. El addon comunitario `leonobitech/l10n_ar_arca_edi` sí contiene código WSAA/WSFEv1 y tests, aunque su manifiesto lo declara Beta (AGPL-3, Odoo 19.0.1.0.0; último push observado 17/03/2026). La rama OCA `l10n-argentina` 19.0 consultada no contiene addons instalables. Ninguno de estos hallazgos constituye una prueba de homologación ni habilita producción; ver [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md).

No se calculará un ganador ponderado si falla una condición excluyente. Para pasar la prueba, cada candidato debe demostrar: una venta confirmada y sus efectos asociados exactamente una vez; recuperación tras cierre forzado; backup restaurable; auditoría; roles correctos; y una ruta fiscal argentina viable. Si no supera esos mínimos, no compensa tener más pantallas o módulos.

La decisión final debe incluir también el costo de actualización, la cantidad de código que habría que mantener, la compatibilidad con nuestros perfiles sectoriales y qué partes conviene tomar como módulos separados.

## Componentes especializados: evaluar aparte

Estos componentes no convierten por sí solos a una plataforma en la base del producto:

- **pos-toolkit** (Apache-2.0): tiene código real para impresoras ESC/POS, cajón, scanners seriales, balanzas HID y constructor de tickets. El plugin de hardware es Rust/Tauri v2, por lo que requiere que esa arquitectura de escritorio tenga sentido; no es un plugin universal de navegador. `register-core` figura como planificado, no implementado.
- **emupos** y **ESCPost** (Apache-2.0): herramientas para simular periféricos y probar tickets. No certifican compatibilidad física.
- **arca-sdks**: el paquete `@ramiidv/arca-facturacion` 7.1.0 declara MIT y Node >=22.12; contiene WSAA/WSFE/WSFEX/CAEA y pruebas de homologación configurables. Es un adaptador candidato, no un motor contable ni una garantía de cumplimiento fiscal. Se probará solo en homologación.
- **PowerSync Open Edition** (Apache-2.0): candidato de sincronización SQLite/PostgreSQL, con funciones Enterprise/Cloud separadas. Debe medirse frente al requisito concreto; no resuelve por sí solo las invariantes de caja, stock o emisión fiscal.
- **Dexie.js** (Apache-2.0): persistencia IndexedDB, no sincronización distribuida completa.

La revisión de licencias se hace para la versión y los archivos que realmente se incorporen. El uso privado permite considerar código GPL/AGPL, pero no elimina las licencias separadas de dependencias, fuentes, imágenes, servicios o componentes comerciales.

El validador del dataset comprueba importes, descuentos, pagos mixtos, caja, inventario, devoluciones, recepción parcial, retiro de líneas, vuelto e invariantes de la secuencia de estados de una terminal. La ejecución de CI del 20/11/2026 terminó correctamente: 27 pruebas aprobadas y dataset canónico válido. El benchmark mensual de demanda (48 meses por serie, modelos regulares e intermitentes) también pasó su workflow; es una prueba matemática con datos sintéticos, no valida una plataforma. Esto valida las reglas aritméticas y las invariantes modeladas de multiárea, mayorista, envíos, servicios, costos internos y rentabilidad; no valida todavía el comportamiento funcional de MyCompany, Posnic o ERPNext.

## Estado de ejecución

| Actividad | Estado |
|---|---|
| Inspección documental y licencias iniciales de MyCompany/lsFusion 6.2 | Hecha; prueba funcional pendiente |
| Fijación de release, instalador y JAR MyCompany 6.2 | Preparada mediante hashes; runtime debe registrarse |
| Inspección documental y manifiestos de Posnic | Hecha |
| Fijación de release/commit para Posnic | Hecha |
| Inspección documental de ERPNext/Frappe v16 | Hecha parcialmente |
| Protocolo común y dataset sintético | Preparados |
| Laboratorio de instalación para los tres candidatos | Preparado |
| Validador y CI del dataset | Aprobados: 27/27 tests y dataset válido (20/11/2026) |
| Instalación/evaluación de MyCompany 6.2 y módulo custom | Pendiente |
| Instalación local de Posnic en VM compatible | Pendiente |
| Instalación local de ERPNext/Frappe con Docker | Pendiente |
| Ejecución P01–P26 (POS/ERP) | Pendiente |
| Ejecución P27–P48 (resiliencia/arquitectura) | Pendiente |
| Ejecución P49–P56 (fundación de datos e historial) | Pendiente |
| Ejecución P57 (exportación analítica portable) | Pendiente |
| Pruebas físicas de terminales y hardware | Pendiente |
| Revisión completa de dependencias y seguridad | Pendiente |
| Decisión de plataforma | Pendiente |
| Incorporación de código externo | No iniciada |

**Próximo paso técnico:** comparar ERPNext 16, MyCompany 6.2 y Tryton 8.0 + módulos argentinos 8.0 con el mismo circuito POS+ERP; filtrar Dolibarr 24.0.3 y usar Posnic sólo como referencia POS. Sólo dos candidatos pasan a P01–P57. En Tryton, instalar las ocho ramas 8.0 juntas, ejecutar las suites y probar WSFE/WSFEX en homologación. Tryton 8.2 se evalúa después como upgrade, con port y homologación. La frontera de servicio, actualización, exportación y restauración debe demostrarse antes de aprobar una adopción. En MyCompany, comprobar además un módulo de extensión mediante REQUIRE; en ERPNext, registrar `bench version`; en las pruebas de terminal, usar sandbox y terminal física habilitada. No marcar offline, impresiones ni compatibilidad como aprobadas sin evidencia por modelo y sistema operativo. La CI cubre el validador y las reglas aritméticas, no simula una instalación real de las plataformas. Después de medir, definiremos qué servicios se construyen y qué componente existente puede cubrir uno o varios dominios detrás de APIs/eventos, conservando almacenamiento, despliegue y rollback independientes.


## Extensión del protocolo: varias áreas y operación B2B (P20–P25)

Los seis escenarios nuevos usan un mismo CustomerAccount empresarial relacionado con más de una unidad de negocio. Las unidades se distinguen de canales, sucursales y centros de costo.

El despacho se ejecuta después de confirmar la venta. El tracking/guía puede estar vacío al registrar la venta y asociarse al Shipment después; la prueba incluye entregas parciales y handoff a transportista. Los acuerdos de servicio generan obligaciones y órdenes de trabajo, mientras los ingresos/costos se imputan al contrato y unidad de negocio.

La prueba de rentabilidad distingue devengado, facturado y cobrado, y compara costos directos, compartidos sin asignar y compartidos distribuidos mediante una regla versionada. Las asignaciones deben sumar el costo de origen sin contarlo dos veces.


## P26 — consumo interno y resultado consolidado

El caso utiliza áreas dentro de la misma entidad legal. El módulo de inventario registra un único movimiento de salida del depósito; el área consumidora recibe la imputación del costo real. Si existe una tarifa interna para medir desempeño, queda identificada como cargo/abono gerencial y se elimina al consolidar. No se emite factura fiscal ni se genera cobro externo por el mero traspaso interno.

La variante multi-entidad legal se prueba aparte: debe utilizar documentos intercompany reales y una eliminación de consolidación, sin borrar libros fiscales de cada entidad.
