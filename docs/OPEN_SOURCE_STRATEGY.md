# Estrategia de reutilización de código abierto

**Revisión:** 19 de noviembre de 2026  
**Estado:** evaluación técnica y de licencias; todavía no se incorporó código de terceros.

## Conclusión ejecutiva

Sí: reutilizar proyectos y bibliotecas de código abierto puede reducir mucho el tiempo de desarrollo. No conviene, sin embargo, convertir el producto en una colección de sistemas pegados entre sí ni copiar un ERP entero para después luchar contra su modelo interno.

La estrategia recomendada es **reutilizar componentes y capacidades bien delimitadas, conservar un único núcleo transaccional y desarrollar las reglas diferenciales del negocio**. La licencia es una condición de entrada, no una revisión que se hace al final.

Los candidatos más útiles encontrados son:

1. **Medusa** como candidato principal para una prueba técnica de reutilización del núcleo de comercio. Su código central es MIT y ofrece módulos de catálogo, pedidos, precios, promociones, pagos e inventario, además de workflows y contratos de extensión.
2. **Odoo Community 19** como referencia funcional de primer nivel para POS completo, descuentos, caja, offline y hardware. También podría ser una base integral si se decidiera adoptar deliberadamente el ecosistema Odoo; su licencia es LGPLv3 y hay que distinguir Community de Enterprise.
3. **Apache OFBiz** como fuente de patrones y procesos ERP bajo Apache 2.0, pero no como base preferida: su amplitud y arquitectura Java elevan mucho el costo de adaptación.
4. **TastyIgniter** como referencia y posible fuente de componentes acotados para pedidos, reservas y gastronomía; no cubre nuestro núcleo comercial completo.

No recomiendo incorporar directamente al producto, por defecto, código GPL/AGPL de ERPNext, Vendure, uniCenta o NexoPOS. Se puede hacer legalmente bajo las condiciones de esas licencias, pero puede afectar la obligación de entregar el código fuente de partes derivadas cuando distribuimos el programa. Como el producto contempla instalación local y offline, conviene preservar esa decisión comercial hasta que se tome expresamente.

Esta evaluación no sustituye asesoramiento jurídico. Antes de distribuir software que incorpore código de terceros, se debe revisar el caso concreto con un profesional de propiedad intelectual y software.

## Qué significa reutilizar código

Hay cuatro formas distintas de aprovechar un proyecto externo:

| Forma | Qué hacemos | Cuándo conviene |
|---|---|---|
| Dependencia | Incorporamos una biblioteca o paquete mantenido por terceros | Utilidad técnica acotada y API estable |
| Extensión | Usamos un framework y agregamos módulos propios sin modificar su núcleo | El modelo del framework encaja con el producto |
| Adaptación de componente | Copiamos o extraemos una parte identificable, conservando licencia y avisos | La pieza resuelve un problema concreto y puede mantenerse aislada |
| Fork | Adoptamos el proyecto completo y mantenemos nuestra propia variante | El producto externo ya resuelve la mayor parte del negocio y el costo de adaptación es menor que construir |

La preferencia será **dependencia o extensión**, luego adaptación de una pieza aislada y, solamente con evidencia, un fork. No se copiará código por parecer útil sin identificar su origen, licencia, dependencias y pruebas.

## Comparación de candidatos

### Medusa — candidato principal para la prueba técnica

- **Licencia:** MIT para el núcleo, con materiales de Enterprise Edition expresamente separados y sujetos a licencia comercial. No todo lo que aparece en el repositorio tiene automáticamente licencia MIT.
- **Tecnología y estructura:** TypeScript/Node.js, API, PostgreSQL, módulos de comercio e infraestructura, workflows, eventos y panel administrativo extensible.
- **Qué puede acelerar:** catálogo, variantes, carritos, pedidos, precios, promociones, pagos, inventario, canales, integraciones y la infraestructura para extender esos conceptos.
- **Qué no resuelve por sí solo:** caja y turnos de cajeros, arqueo y diferencias, libro de movimientos comerciales completo, reglas de descuentos auditables específicas, offline resistente a cierres/reinicios, fiscalidad argentina, compras y recepción avanzada, costos/contabilidad, producción y recetas.
- **Riesgo de adaptación:** su modelo está orientado a comercio y pedidos. Debemos comprobar que ventas POS, pagos parciales/mixtos, devoluciones, stock y movimientos contables se puedan integrar sin forzar sus entidades ni mantener un fork del núcleo.
- **Evaluación:** es el candidato con mejor equilibrio inicial entre código reutilizable, licencia permisiva y arquitectura modular. No queda aprobado como base hasta superar la prueba vertical definida más abajo.

El diseño de Medusa separa rutas/API, workflows, módulos y persistencia. También mantiene aislados los modelos entre módulos y utiliza vínculos explícitos para relacionarlos. Sus workflows pueden registrar pasos y compensar operaciones ante fallos; para producción, su documentación recomienda un motor de workflows con persistencia y Redis en lugar del motor en memoria. Son capacidades útiles, pero no equivalen automáticamente a nuestra idempotencia, libro de stock ni sincronización offline: habrá que verificarlas.

Fuentes:
- https://github.com/medusajs/medusa
- https://github.com/medusajs/medusa/blob/develop/LICENSE
- https://github.com/medusajs/medusa/blob/develop/ENTERPRISE-LICENSE.md
- https://docs.medusajs.com/learn/introduction/architecture
- https://docs.medusajs.com/learn/fundamentals/module-links
- https://docs.medusajs.com/resources/architectural-modules/workflow-engine

### Odoo Community 19 — referencia POS/ERP y alternativa de adopción integral

- **Licencia:** LGPLv3 para Community. Enterprise es una edición distinta, con licencia comercial; no se debe confundir código visible con código reutilizable bajo LGPL.
- **Qué aporta:** un POS de comercio y gastronomía, sesiones de caja, ventas, devoluciones, descuentos por línea y globales, programas promocionales, listas de precios, redondeo, inventario, dispositivos y flujos de restaurante.
- **Offline:** el POS puede continuar creando y administrando pedidos con datos previamente cargados en caché del navegador y sincronizarlos al volver la conexión. La documentación advierte que no se debe cerrar ni recargar el navegador ni limpiar la caché antes de sincronizar. Durante la desconexión no están disponibles todas las funciones: por ejemplo, terminales de pago, sincronización de stock en tiempo real, carga bajo demanda y determinadas acciones de clientes o facturación.
- **Hardware:** contempla impresoras, cajones conectados a impresoras, lectores, balanzas, pantallas de cliente y terminales, directamente o mediante una pasarela IoT. La compatibilidad real depende del dispositivo, sistema operativo y conexión.
- **Costo de adopción:** Odoo tiene un modelo, ORM, permisos, vistas y ciclo de módulos propios. Extenderlo es razonable si se adopta el ecosistema; extraer piezas internas para un sistema distinto puede dejar dependencias difíciles de mantener. Además, hay funciones que pertenecen a Enterprise y no se deben presuponer disponibles en Community.
- **Evaluación:** excelente referencia de cobertura funcional y opción seria si se decide construir sobre Odoo Community. No recomiendo copiar su POS y mezclarlo informalmente con otro backend. Si se lo adopta como base, se debe aceptar su arquitectura y cumplir LGPLv3 para el código cubierto.

Fuentes:
- https://github.com/odoo/odoo/blob/19.0/LICENSE
- https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/use.html
- https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing.html
- https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/hardware_network.html
- https://www.odoo.com/documentation/19.0/es/administration.html
- https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/01_architecture.html

### Frappe Framework y ERPNext — separar el framework de la aplicación ERP

- **Licencias:** Frappe Framework es MIT; ERPNext es GPLv3. La licencia MIT del framework no convierte el código de ERPNext en MIT.
- **Qué aporta:** framework Python/JavaScript con modelos de documentos, usuarios, roles, permisos, API REST/RPC, trabajos de fondo, eventos en tiempo real, formularios y aplicaciones extensibles. ERPNext aporta compras, inventario, cuentas, fabricación y procesos comerciales.
- **Base de datos:** la documentación consultada describe MariaDB como predeterminada y PostgreSQL como soporte beta. Esto debe pesar en la decisión porque PostgreSQL es nuestro candidato para el núcleo.
- **Offline:** existen antecedentes de POS que almacena datos localmente y sincroniza operaciones. Sin embargo, una solicitud abierta en ERPNext fechada el 24 de junio de 2026 pide precisamente fortalecer su POS nativo para conectividad inestable. No debemos tomar documentación antigua de offline como prueba de que hoy resuelve nuestra exigencia de continuidad.
- **Evaluación:** Frappe podría ser un framework MIT independiente, pero usar ERPNext como fuente de código tiene implicaciones GPLv3. No lo elijo como base inicial por la combinación de licencia del ERP, dependencia del framework y estado de PostgreSQL/offline.

Fuentes:
- https://github.com/frappe/frappe
- https://github.com/frappe/erpnext/blob/develop/license.txt
- https://docs.frappe.io/framework/user/en/basics
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api
- https://docs.frappe.io/framework/user/en/api/background_jobs
- https://github.com/frappe/erpnext/issues/56438

### Apache OFBiz — ERP amplio con licencia permisiva

- **Licencia:** Apache License 2.0.
- **Qué aporta:** catálogo, pedidos, promociones, pagos, almacenes, inventario, contabilidad, CRM, abastecimiento y fabricación. Su arquitectura incluye un motor de entidades, un motor de servicios y una interfaz basada en widgets.
- **Ventaja:** una base empresarial muy completa y una licencia que permite uso, modificación y distribución, cumpliendo avisos y condiciones.
- **Costo:** es una suite grande, basada en Java y con convenciones propias. Adaptarla a una experiencia de caja simple, local-first y moderna puede demandar más trabajo que implementar un núcleo acotado. La serie 24.09 está congelada en funciones desde septiembre de 2024 y recibe correcciones; la versión 24.09.08 se publicó en noviembre de 2026.
- **Evaluación:** estudiar procesos, entidades e invariantes; no adoptarlo como base preferida.

Fuentes:
- https://github.com/apache/ofbiz-framework/blob/trunk/LICENSE
- https://ofbiz.apache.org/
- https://ofbiz.apache.org/release-notes/24.09.08.html

### Otros proyectos relevantes

| Proyecto | Licencia verificada o declarada | Aporte y decisión |
|---|---|---|
| Vendure | GPLv3 por defecto; alternativa comercial VCL y excepción para plugins | Muy buen diseño de comercio extensible en TypeScript. No usar su núcleo como base si no aceptamos GPLv3 o licencia comercial. Estudiar patrones y contratos. |
| Saleor | BSD 3-Clause | Comercio electrónico en Python, catálogo, pedidos y canales. Referencia si evaluamos una plataforma Python, pero no trae el POS operativo que necesitamos. |
| uniCenta oPOS | GPLv3 | POS Java con experiencia de periféricos y releases recientes; útil como referencia de operación/hardware. La arquitectura y licencia no justifican incorporarlo por defecto. |
| NexoPOS | GPL-3.0 según el repositorio revisado | POS web en Laravel/Vue con ventas, inventario, compras y reportes. Buen material para estudiar flujos, pero no copiar sin aceptar GPL y revisar el repositorio/versiones exactas. |
| Open Source Point of Sale (OSPOS) | MIT con condiciones adicionales en su propio archivo LICENSE | Tiene POS, stock, clientes, proveedores, recepciones y reportes. Su licencia exige mantener visible e inalterable la firma y atribución del producto en cada pantalla. No sirve para una interfaz completamente rebrandeada bajo nuestros criterios. |
| TastyIgniter | MIT | Laravel/Bootstrap para pedidos online, reservas y gestión gastronómica. Puede aportar patrones o componentes de ese sector, no un núcleo comercial común. |

Fuentes:
- Vendure: https://github.com/vendurehq/vendure/blob/master/LICENSE.md
- Saleor: https://github.com/saleor/saleor/blob/main/LICENSE
- uniCenta: https://unicenta.com/faqs/ y https://unicenta.com/changelog-unicenta-opos/
- NexoPOS: https://github.com/Blair2004/NexoPOS
- OSPOS: https://github.com/opensourcepos/opensourcepos/blob/master/LICENSE
- TastyIgniter: https://tastyigniter.com/license

## Criterio de licencias

La licencia del proyecto principal no basta. Hay que revisar cada dependencia, paquete, plugin, recurso visual, fuente, plantilla, ejemplo y componente que llegue al producto.

| Familia | Qué permite en términos generales | Regla para este proyecto |
|---|---|---|
| MIT, ISC, BSD-2/3 | Uso, modificación y distribución; normalmente exigen conservar avisos y cumplir condiciones de atribución | Preferidas para componentes acotados |
| Apache 2.0 | Uso, modificación y distribución; exige conservar avisos/licencia y atender condiciones de patentes y archivos NOTICE cuando correspondan | Preferida; registrar NOTICE y modificaciones |
| LGPL | Permite determinados usos combinados bajo condiciones; las modificaciones a la biblioteca cubierta y la forma de enlazar/distribuir tienen obligaciones específicas | Aceptable solo con revisión de cómo se integra, avisos, fuente y posibilidad de reemplazo/re-enlace |
| GPL | Permite uso comercial, pero al distribuir una obra cubierta o derivada pueden existir obligaciones de entregar el código fuente correspondiente bajo GPL | No incorporar al núcleo por defecto |
| AGPL | Añade obligaciones para ciertos usos de versiones modificadas a través de una red | No incorporar al núcleo por defecto |
| Licencias comerciales, duales o personalizadas | Dependen del contrato o de condiciones adicionales | No usar sin permiso y alcance documentados |
| Sin licencia | El código público no concede automáticamente permiso para copiar, modificar o distribuir | No reutilizar |

Dos precisiones importantes:

- GPL no significa que no se pueda cobrar ni usar comercialmente. El punto crítico es qué se distribuye y qué obligaciones se activan al entregar copias de un programa cubierto. GPLv3 define que la mera interacción con un usuario a través de una red, sin transferencia de una copia, no es por sí sola una distribución; AGPL trata específicamente la interacción de red con versiones modificadas. Nuestro producto contempla instalaciones locales, por lo que no debemos basar una decisión en la expectativa de que todo será solo SaaS.
- LGPL no equivale a MIT. En obras combinadas hay requisitos sobre avisos, licencia, fuente de la parte cubierta y posibilidad de modificar/reemplazar la biblioteca. Copiar y modificar internamente un módulo de Odoo no debe tratarse como si fuera una dependencia MIT.

Textos oficiales:
- GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html
- LGPLv3: https://www.gnu.org/licenses/lgpl-3.0.en.html
- Apache 2.0: https://www.apache.org/licenses/LICENSE-2.0

## Estrategia de integración recomendada

1. **Mantener un solo dueño de cada dato y movimiento.** No ejecutar dos ERPs ni dos motores de stock como fuentes de verdad. Las piezas externas se conectan al núcleo mediante contratos explícitos.
2. **No copiar el núcleo de un ERP para aprovechar unas pocas funciones.** Primero evaluar paquete, extensión o módulo aislado. Si una pieza requiere arrastrar todo el framework, medir ese costo antes.
3. **No alterar el núcleo de una dependencia por comodidad.** Extender por API, plugin o estrategia pública. Un parche upstream solo se acepta si se puede mantener y probar.
4. **Adaptar el modelo, no replicar entidades ciegamente.** En particular, una orden ecommerce, una venta POS, un pago, una liquidación, un movimiento de caja, un movimiento de inventario y un comprobante fiscal no son el mismo objeto.
5. **Aislar proveedores.** Catálogo, pagos, fiscalidad, mensajería, impresoras, balanzas y marketplaces entran por adaptadores. La indisponibilidad de uno no debe invalidar una venta ya persistida.
6. **Conservar las reglas diferenciales propias.** Libro de movimientos, precios históricos, descuentos auditables, autorización, márgenes, pagos mixtos, devoluciones, costos por canal, offline y conciliación fiscal se definen bajo nuestros contratos.
7. **Aprovechar pruebas y patrones solo después de revisar su licencia.** Los casos de prueba externos ayudan a descubrir escenarios, pero no sustituyen nuestros criterios ni demuestran que nuestra implementación sea correcta.

## Dirección técnica recomendada para validar

La evaluación favorece una solución web modular, con interfaz propia para POS y administración, un núcleo transaccional único y almacenamiento local duradero para operar sin conexión.

Como primer candidato se propone validar **Medusa v2 (núcleo MIT) + TypeScript + React + PostgreSQL**, extendiendo con módulos propios para POS, caja, libro de inventario, compras, producción, fiscalidad, auditoría y sincronización. La interfaz POS no debe depender del panel administrativo de Medusa. No se usarán materiales Enterprise sin contrato.

La parte local debe diseñarse por separado del servidor: aplicación instalable, almacenamiento transaccional local, cola persistente de operaciones, identificadores globales, idempotencia y conciliación. El prototipo tiene que sobrevivir a desconexión, cierre y reapertura del navegador o aplicación; no basta con mantener una pestaña abierta. IndexedDB es una alternativa inicial para PWA, pero si no garantiza la recuperación requerida en equipos objetivo, se evaluará un agente local con SQLite. La elección final se basará en pruebas de recuperación, no en preferencia tecnológica.

PostgreSQL se mantiene como candidato para el registro central. Redis no se incorpora hasta confirmar su necesidad; si se adopta Medusa en producción, se deberá configurar el motor durable que recomienda su documentación para workflows y eventos. Los cálculos estadísticos iniciales se resolverán con SQL y procesos del mismo sistema; no se introducirá un segundo backend Python hasta que exista una necesidad medida.

**Alternativa de salida:** si la prueba muestra que Medusa obliga a forzar entidades, parchear el núcleo o duplicar el libro transaccional, no se lo adopta. En ese caso se construye un monolito modular propio en TypeScript sobre PostgreSQL y se conservan únicamente las bibliotecas permisivas que hayan superado la revisión.

Esto es una dirección de evaluación, no una decisión irrevocable: el framework se aprueba únicamente con evidencia.

## Prueba única de compatibilidad antes de cerrar el framework

No vamos a encadenar pruebas sueltas. Se define una prueba vertical de punta a punta que resuelva una vez los riesgos más importantes:

1. Cargar producto, variante, código de barras, unidad y lista de precios.
2. Abrir turno/caja, iniciar carrito y registrar artículos.
3. Aplicar una promoción automática y un descuento manual que requiera autorización; conservar precio base, regla, importe, operador y aprobador.
4. Cobrar con dos medios, calcular vuelto y guardar los movimientos correspondientes.
5. Registrar venta e inventario con transacciones e identificadores idempotentes.
6. Cortar la red antes y después de confirmar; continuar vendiendo con las reglas offline permitidas.
7. Cerrar inesperadamente y reabrir la aplicación sin perder ventas pendientes.
8. Restaurar conexión y sincronizar varias veces; no duplicar venta, pago ni salida de stock.
9. Provocar conflicto de precio/stock y mostrar una conciliación explícita, sin sobrescribir silenciosamente.
10. Comprobar permisos, auditoría, aislamiento entre negocios y trazabilidad de las operaciones.
11. Ejecutar la misma suite con base limpia y datos sintéticos repetibles; registrar versión, tiempos y resultados.
12. Revisar que no se haya modificado el código central de la dependencia y que el inventario de licencias esté completo.

**Criterio para aprobar Medusa:** completar el flujo sin modificar su núcleo, sin crear una segunda fuente de verdad para ventas/pagos/stock, con recuperación durable y sincronización idempotente; las limitaciones deben quedar dentro de módulos propios y mantenibles. Si no cumple, se descarta como base y se adopta la alternativa modular propia.

No se considerará aprobada la compatibilidad de hardware por una simulación: luego se necesitará una matriz de pruebas con modelos físicos concretos de impresora, lector, balanza, cajón y terminal.

## Control permanente de código de terceros

Antes de incorporar una dependencia o fragmento:

- Registrar proyecto, URL, autor, versión/tag/commit exacto, fecha de consulta y archivos utilizados.
- Guardar el texto de licencia y los avisos de copyright correspondientes.
- Revisar licencias de dependencias transitivas, plugins, fuentes, iconos, imágenes y otros recursos.
- Identificar partes comerciales, enterprise, duales o sujetas a términos adicionales.
- Registrar qué se modificó y mantener el archivo de origen o el aviso en el lugar correspondiente.
- Generar un SBOM en formato SPDX o CycloneDX para las versiones distribuidas.
- Ejecutar análisis de vulnerabilidades, dependencias abandonadas y licencias en CI.
- Bloquear dependencias sin licencia identificable, con licencia incompatible o con condiciones no aprobadas.
- Volver a revisar el inventario al actualizar una versión o agregar un plugin.

Una biblioteca no se aprueba solo porque sea popular o tenga muchas estrellas. También se evalúan mantenimiento, actividad real, seguridad, cobertura de pruebas, documentación, compatibilidad, tamaño, dependencias, rendimiento y facilidad de reemplazo.

## Estado de la decisión

- [x] Se identificaron candidatos con código y licencia comprobables.
- [x] Se separaron licencias permisivas, copyleft, comerciales y condiciones personalizadas.
- [x] Se definió una estrategia para conservar un único núcleo transaccional.
- [x] Se priorizó Medusa como primer candidato para validar.
- [ ] No se incorporó código de terceros.
- [ ] No se eligió ni fijó todavía una versión de framework.
- [ ] Falta ejecutar la prueba vertical de compatibilidad.
- [ ] Falta generar el primer inventario/SBOM del software propio y sus dependencias.

