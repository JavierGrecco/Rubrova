# Evaluación comparativa de plataformas

**Revisión:** 19 de noviembre de 2026  
**Estado:** laboratorio preparado; validación automática del dataset aprobada; ejecución local de plataformas pendiente.  
**Alcance:** uso interno, personal y privado. No se prevé distribuir, revender ni ofrecer el sistema como servicio a terceros.

Este documento convierte la investigación en una prueba repetible. No elige una plataforma por su README, una demo o la cantidad de módulos anunciados. La elección depende de ejecutar los mismos flujos, con datos sintéticos, y comprobar integridad, recuperación, esfuerzo de adaptación y mantenimiento.

## Decisión de evaluación

La ronda integral se amplía a tres candidatos porque la inspección de código encontró una plataforma adicional con POS, cobertura ERP amplia y extensibilidad explícita por módulos:

1. **MyCompany/lsFusion 6.2**, para comprobar POS, CRM, compras, multi-depósito, facturación, producción y la composición de módulos.
2. **Posnic 1.9.2**, para comprobar cuánto resuelve de POS local, caja, ventas e inventario y qué tan real es su continuidad offline.
3. **ERPNext 16.60.0 + Frappe Framework 16**, para comprobar cuánto adelanta de compras, inventario, producción, costos y contabilidad, sin asumir que su POS satisface nuestro requisito offline.

No se adoptan varias como fuentes de verdad paralelas. Los módulos especializados se evalúan aparte y se conectan por contratos explícitos. Odoo Community 20 y Medusa v2 dejan de ser finalistas de esta ronda; pueden reabrirse si aparece evidencia que cambie la comparación.

**Resultado actual: ninguna plataforma está aprobada.** No se ha instalado ni ejecutado localmente MyCompany, Posnic o ERPNext para Rubrova; no se ha incorporado código externo y no hay una aplicación de Rubrova implementada.

## Versiones y procedencia que se deben fijar

| Proyecto | Referencia de prueba | Procedencia comprobada | Precaución |
| MyCompany | Tag 6.2 | Commit del tag d21ca6978717b98b6300d90267f9767db7414008 | Aplicación Apache-2.0; plataforma lsFusion LGPL v3. No mezclar tag 6.2 con documentación online 7.0/master. |
|---|---|---|---|
| Posnic | Tag `v1.9.2` | Commit `4096126edb1ff4fd337069697776254215dc2680`; release publicada el 16/11/2026 | No probar desde una rama móvil sin registrar commit. |
| Posnic, revisión adicional | Rama `main` | HEAD consultado: `bf97ab2e2cdfba88121d369cacf48dd877ac8b55`, seis commits posterior al tag | Comparar diferencias con el tag antes de decidir si un arreglo posterior cambia la evaluación. |
| ERPNext | Release `v16.60.0` | Tag asociado al commit `886ab6ae187244e7f1b852393384ab6019d56264`; publicada el 17/11/2026 | Mantener fija la versión durante la prueba. |
| Frappe Framework | Incluido en la imagen ERPNext fijada | Versión efectiva registrada con `bench version` dentro del contenedor | No combinar una rama independiente del framework con una imagen ERPNext ya construida. |
| Frappe Docker | Configuración de demo | Commit `ef24ebc0a411b6237694765f0b51d8f8f8dd13ce`; su `pwd.yml` fija `frappe/erpnext:v16.60.0` | Demo desechable, no instalación de producción. Mantener el archivo local separado y limitar el puerto a localhost. |

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
| P10 | Dos puestos en la misma LAN | Permisos, concurrencia y consistencia sobre una única base local | Doble numeración, saldo o stock inconsistente |
| P11 | Corte de internet | Venta local guardada y estado de servicios externos visible | Bloquear o perder una venta local ya confirmada |
| P12 | Cierre forzado/reinicio | Reiniciar con operaciones pendientes y verificar recuperación | Pérdida, duplicación o corrupción |
| P13 | Reintento y sincronización repetida | Repetir el envío tres veces y conservar una única operación | Doble venta, pago, factura o movimiento |
| P14 | Conflicto de precio/stock | Conflicto explícito y conciliación con registro de decisión | Sobrescritura silenciosa o último cambio gana en dinero/stock |
| P15 | Backup y restauración | Restaurar en una instancia limpia y conciliar conteos/saldos | Backup ilegible o restauración incompleta |
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

En P11 se debe distinguir pérdida de internet de pérdida de red local. En un servidor local compartido, los otros puestos pueden seguir conectados por LAN; una caja con su propia base desconectada es un caso distinto y debe documentarse como tal.

En P17 no se emitirán comprobantes reales. Una respuesta incierta de ARCA debe pasar por consulta/recuperación antes de cualquier nuevo intento; nunca asumir que un timeout significa que no se emitió.

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

Ponderación propuesta:

| Área | Peso |
|---|---:|
| Integridad transaccional, offline, reinicio y restauración | 30% |
| POS, pagos, caja, devoluciones y operación del cajero | 20% |
| Inventario, compras, costos y producción | 15% |
| Extensibilidad, contratos, actualizaciones y esfuerzo de mantenimiento | 10% |
| Argentina, ARCA y adaptación fiscal | 10% |
| Hardware, terminales y compatibilidad de sistemas operativos | 10% |
| Simplicidad de operación y experiencia de uso | 5% |

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

El validador del dataset comprueba importes, descuentos, pagos mixtos, caja, inventario, devoluciones, recepción parcial, retiro de líneas, vuelto e invariantes de la secuencia de estados de una terminal. La ejecución de CI del 19/11/2026 terminó correctamente: seis pruebas aprobadas y dataset canónico válido. Esto valida el dataset y sus reglas aritméticas; no valida todavía el comportamiento funcional de MyCompany, Posnic o ERPNext.

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
| Validador y CI del dataset | Aprobados: 13/13 tests y dataset válido (19/11/2026) |
| Instalación/evaluación de MyCompany 6.2 y módulo custom | Pendiente |
| Instalación local de Posnic en VM compatible | Pendiente |
| Instalación local de ERPNext/Frappe con Docker | Pendiente |
| Ejecución P01–P26 | Pendiente |
| Pruebas físicas de terminales y hardware | Pendiente |
| Revisión completa de dependencias y seguridad | Pendiente |
| Decisión de plataforma | Pendiente |
| Incorporación de código externo | No iniciada |

**Próximo paso técnico:** instalar los tres candidatos en entornos aislados y ejecutar P01–P26 con datos sintéticos equivalentes. En MyCompany, comprobar además un módulo de extensión mediante REQUIRE; en ERPNext, registrar `bench version`; en las pruebas de terminal, usar sandbox y terminal física habilitada. No marcar offline, impresiones ni compatibilidad como aprobadas sin evidencia por modelo y sistema operativo. La CI cubre el validador y las reglas aritméticas, no simula una instalación real de las plataformas. Después de medir, decidiremos si adoptamos una base integral o construimos nuestro monolito modular tomando componentes especializados.


## Extensión del protocolo: varias áreas y operación B2B (P20–P25)

Los seis escenarios nuevos usan un mismo CustomerAccount empresarial relacionado con más de una unidad de negocio. Las unidades se distinguen de canales, sucursales y centros de costo.

El despacho se ejecuta después de confirmar la venta. El tracking/guía puede estar vacío al registrar la venta y asociarse al Shipment después; la prueba incluye entregas parciales y handoff a transportista. Los acuerdos de servicio generan obligaciones y órdenes de trabajo, mientras los ingresos/costos se imputan al contrato y unidad de negocio.

La prueba de rentabilidad distingue devengado, facturado y cobrado, y compara costos directos, compartidos sin asignar y compartidos distribuidos mediante una regla versionada. Las asignaciones deben sumar el costo de origen sin contarlo dos veces.


## P26 — consumo interno y resultado consolidado

El caso utiliza áreas dentro de la misma entidad legal. El módulo de inventario registra un único movimiento de salida del depósito; el área consumidora recibe la imputación del costo real. Si existe una tarifa interna para medir desempeño, queda identificada como cargo/abono gerencial y se elimina al consolidar. No se emite factura fiscal ni se genera cobro externo por el mero traspaso interno.

La variante multi-entidad legal se prueba aparte: debe utilizar documentos intercompany reales y una eliminación de consolidación, sin borrar libros fiscales de cada entidad.
