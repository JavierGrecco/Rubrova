# Estrategia de reutilización de código abierto

**Revisión:** 19 de noviembre de 2026  
**Estado:** evaluación técnica y de licencias; todavía no se incorporó código de terceros.

## Contexto de uso y criterio de licencias (actualización)

**El sistema se desarrollará para uso interno y privado del negocio. No está previsto distribuirlo, revenderlo, ofrecerlo como producto ni dar acceso remoto a terceros como servicio.** Esta condición cambia la estrategia de reutilización: no debemos descartar automáticamente GPL, AGPL ni otros proyectos copyleft por el solo hecho de que sus licencias no sean permisivas.

La guía de la Free Software Foundation confirma que una organización puede modificar y usar internamente software GPL sin publicar esas modificaciones ni entregar el código a terceros. La AGPL agrega una condición específica: si se modifica un programa AGPL y usuarios interactúan con esa versión remotamente a través de una red, debe ofrecerse el código fuente correspondiente a esos usuarios. Por eso, el uso interno no elimina la necesidad de leer y cumplir cada licencia.

**Nuevo criterio:** evaluar proyectos GPL, AGPL, LGPL, MIT, BSD, Apache y licencias duales según su utilidad técnica real para nuestro escenario. La licencia deja de ser un filtro automático de descarte y pasa a ser una condición de uso que se documenta y cumple. Si en el futuro cambiara el alcance —distribución, instalación en equipos de terceros, acceso de terceros por red o comercialización— se revisará la arquitectura y las obligaciones antes de ese cambio.

Esto no es asesoramiento jurídico. Las licencias pueden variar por versión, archivos, dependencias y excepciones; se conservarán avisos, textos de licencia y atribuciones aplicables, y se consultará a un profesional ante dudas sobre obras derivadas, integración de componentes o alcance de usuarios remotos.

Fuentes primarias:
- GNU GPL FAQ en español: https://www.gnu.org/licenses/gpl-faq.es.html
- GNU AGPLv3, sección 13: https://www.gnu.org/licenses/agpl-3.0.html
- Política de licencias Frappe: https://docs.frappe.io/legal/others/license-and-trademark

## Conclusión ejecutiva

Sí: reutilizar proyectos y bibliotecas de código abierto puede acelerar mucho el desarrollo. La comparación encontró dos candidatos que merecen una prueba real, pero por razones distintas:

1. **Odoo Community 20.0 — candidato de mayor cobertura funcional inmediata.** Su código Community incluye POS, inventario, compras, fabricación, contabilidad y programas de fidelización. Los manifiestos de los módulos principales revisados declaran LGPL-3. Puede ahorrar una gran cantidad de implementación si adoptamos Odoo como plataforma y construimos módulos propios encima. No conviene copiar su POS de forma aislada: sus modelos, permisos, extensiones y procesos forman parte de un ecosistema integrado. Sus límites offline son importantes y la licencia/edición de la integración electrónica completa con ARCA todavía debe verificarse.
2. **Medusa v2 — candidato de mayor control tecnológico y licencia permisiva.** Su núcleo es MIT, usa TypeScript y ofrece módulos de catálogo, pedidos, precios, promociones, pagos e inventario. Está mejor alineado con una aplicación propia y modular, pero deja más trabajo de POS, caja, compras, producción, auditoría, offline y fiscalidad.
3. **Monolito modular propio en TypeScript + PostgreSQL — alternativa de salida.** Evita dependencia de un framework comercial/ERP y permite que el modelo de negocio sea completamente nuestro, pero exige construir más capacidades desde cero.

Odoo 20.0 figura como versión principal lanzada en septiembre de 2026, con fin de soporte estándar previsto para septiembre de 2029. No vamos a usar Odoo 19 como base nueva si el objetivo es evaluar la versión vigente.

La decisión no se puede cerrar por cantidad de funciones en una ficha comercial. Hay que medir cuánto del producto real podemos conservar sin forzar el modelo, depender de componentes Enterprise, alterar el núcleo o incumplir las exigencias de continuidad offline.

**Recomendación actual:** hacer una comparación técnica acotada entre Odoo Community 20 y Medusa v2 con exactamente el mismo flujo de POS. No adoptar aún ninguno. El criterio será el costo total de llegar a una operación confiable y mantenible, no la cantidad de pantallas que ya traiga cada uno.

Ahora sí debemos evaluar la incorporación real de código GPL/AGPL de ERPNext, Vendure, uniCenta, OCA y módulos externos de ARCA. Para el uso privado previsto, esas licencias no son motivo automático de descarte. Pueden ser candidatos valiosos para adoptar, modificar o integrar, siempre que se determine si la solución es un programa independiente, una obra derivada o una interacción de red alcanzada por AGPL, y se cumplan los avisos y demás condiciones aplicables.

Esta evaluación no sustituye asesoramiento jurídico. Antes de distribuir software que incorpore código de terceros, se debe revisar el caso concreto con un profesional de propiedad intelectual y software.

## Qué significa reutilizar código

Hay cuatro formas distintas de aprovechar un proyecto externo:

| Forma | Qué hacemos | Cuándo conviene |
|---|---|---|
| Dependencia | Incorporamos una biblioteca o paquete mantenido por terceros | Utilidad técnica acotada y API estable |
| Extensión | Usamos un framework y agregamos módulos propios sin modificar su núcleo | El modelo del framework encaja con el producto |
| Adaptación de componente | Copiamos o extraemos una parte identificable, conservando licencia y avisos | La pieza resuelve un problema concreto y puede mantenerse aislada |
| Fork | Adoptamos el proyecto completo y mantenemos nuestra propia variante | El producto externo ya resuelve la mayor parte del negocio y el costo de adaptación es menor que construir |

La preferencia será **reutilizar el máximo de funcionalidad que encaje**, empezando por adopción/extensión de un proyecto completo cuando ahorre más trabajo, luego módulos y componentes, y finalmente bibliotecas aisladas. Un fork también es válido si resulta la ruta más eficiente y mantenible para el uso interno. No se copiará código por parecer útil sin identificar origen, versión, licencia, dependencias, avisos, pruebas y condiciones de uso.

## Comparación de candidatos

### Medusa — finalista para una plataforma propia

- **Licencia:** MIT para el núcleo, con materiales de Enterprise Edition expresamente separados y sujetos a licencia comercial. No todo lo que aparece en el repositorio tiene automáticamente licencia MIT.
- **Tecnología y estructura:** TypeScript/Node.js, API, PostgreSQL, módulos de comercio e infraestructura, workflows, eventos y panel administrativo extensible.
- **Qué puede acelerar:** catálogo, variantes, carritos, pedidos, precios, promociones, pagos, inventario, canales, integraciones y la infraestructura para extender esos conceptos.
- **Qué no resuelve por sí solo:** caja y turnos de cajeros, arqueo y diferencias, libro de movimientos comerciales completo, reglas de descuentos auditables específicas, offline resistente a cierres/reinicios, fiscalidad argentina, compras y recepción avanzada, costos/contabilidad, producción y recetas.
- **Riesgo de adaptación:** su modelo está orientado a comercio y pedidos. Debemos comprobar que ventas POS, pagos parciales/mixtos, devoluciones, stock y movimientos contables se puedan integrar sin forzar sus entidades ni mantener un fork del núcleo.
- **Evaluación:** es el finalista más atractivo si se prioriza una plataforma propia en TypeScript y se quiere minimizar el riesgo de licencia copyleft. Su ventaja de licencia no significa que incluya más producto listo: la mayor parte de la gestión comercial y la experiencia POS seguirán siendo trabajo nuestro.

El diseño de Medusa separa rutas/API, workflows, módulos y persistencia. También mantiene aislados los modelos entre módulos y utiliza vínculos explícitos para relacionarlos. Sus workflows pueden registrar pasos y compensar operaciones ante fallos; para producción, su documentación recomienda un motor de workflows con persistencia y Redis en lugar del motor en memoria. Son capacidades útiles, pero no equivalen automáticamente a nuestra idempotencia, libro de stock ni sincronización offline: habrá que verificarlas.

Fuentes:
- https://github.com/medusajs/medusa
- https://github.com/medusajs/medusa/blob/develop/LICENSE
- https://github.com/medusajs/medusa/blob/develop/ENTERPRISE-LICENSE.md
- https://docs.medusajs.com/learn/introduction/architecture
- https://docs.medusajs.com/learn/fundamentals/module-links
- https://docs.medusajs.com/resources/architectural-modules/workflow-engine

### Odoo Community 20.0 — finalista para acelerar la cobertura funcional

- **Versión:** Odoo 20.0 fue lanzado en septiembre de 2026. El soporte estándar está previsto hasta septiembre de 2029.
- **Licencia:** LGPL-3 para Community. Verificamos los manifiestos de `point_of_sale`, `stock`, `purchase`, `mrp`, `account`, `loyalty` y `l10n_ar` en la rama pública `20.0`; todos declaran LGPL-3. Enterprise es una edición diferente bajo licencia comercial. No se debe copiar material Enterprise ni asumir que un módulo documentado está disponible bajo LGPL.
- **Qué puede acelerar:** un POS integrado con productos, pedidos, sesiones, pagos y caja; inventario; compras; fabricación; contabilidad; listas de precios; descuentos por línea y globales; promociones, cupones y fidelización. Es el candidato con mayor cobertura de procesos comerciales ya implementados.
- **Offline del POS:** el POS guarda pedidos sin conexión en la caché del navegador y los sincroniza al volver internet. La documentación advierte expresamente que no se debe cerrar ni recargar el navegador ni borrar la caché antes de sincronizar. Sin conexión también quedan limitadas acciones como registrar clientes, ver detalles de producto, sincronizar stock en tiempo real, usar terminales de pago y cargar datos bajo demanda. El modo offline general de Odoo también tiene límites de caché y no equivale a una base transaccional local duradera.
- **Hardware:** la documentación de Odoo describe integración con impresoras, básculas, lectores, cajones, pantallas y terminales, a menudo mediante IoT o acceso a red local. Hay dependencias de edición, conexión y modelo físico. No se debe suponer que todas las funciones IoT o todos los periféricos están disponibles en Community. Cada modelo concreto necesita prueba.
- **Argentina y ARCA:** el módulo base `l10n_ar` está en el repositorio público Community y declara LGPL-3. Odoo 20 documenta también `l10n_ar_edi` para emitir por web service y `l10n_ar_reports` para reportes; sin embargo, esos dos módulos no aparecen en las rutas públicas correspondientes de `odoo/odoo` 20.0 que revisamos. No se pudo confirmar que su código esté incluido en Community ni su licencia. Por lo tanto, **no contamos todavía la facturación electrónica ARCA como código abierto reutilizable de Odoo Community**.
- **Costo de adopción:** Odoo tiene su propio framework, ORM, permisos, vistas y ciclo de módulos. Extenderlo es razonable si se adopta el ecosistema; extraer el POS para mezclarlo con otro backend arrastra dependencias difíciles de mantener. La ventaja se pierde si para diferenciar el producto debemos sobrescribir gran parte del núcleo.
- **Evaluación:** es el finalista con más funcionalidad existente y puede ser la ruta de menor tiempo para un ERP/POS. Solo es conveniente si aceptamos que la base técnica sea Odoo y podemos resolver las exigencias offline y de identidad del producto mediante extensiones limpias, sin un fork profundo. No se aprueba todavía.

Fuentes:
- Versiones y soporte: https://www.odoo.com/documentation/20.0/es/administration/supported_versions.html
- POS y operación offline: https://www.odoo.com/documentation/20.0/es_419/applications/sales/point_of_sale/use.html
- Descuentos y promociones: https://www.odoo.com/documentation/20.0/es_419/applications/sales/point_of_sale/extra/pricing.html
- Hardware y básculas: https://www.odoo.com/documentation/20.0/applications/sales/point_of_sale/hardware_network/scale.html
- Impresoras: https://www.odoo.com/documentation/20.0/applications/sales/point_of_sale/configuration/epos_printers.html
- Ediciones y licencias: https://www.odoo.com/documentation/20.0/legal/licenses/licenses.html
- Manifiestos LGPL-3: https://github.com/odoo/odoo/blob/20.0/addons/point_of_sale/__manifest__.py, https://github.com/odoo/odoo/blob/20.0/addons/stock/__manifest__.py, https://github.com/odoo/odoo/blob/20.0/addons/purchase/__manifest__.py, https://github.com/odoo/odoo/blob/20.0/addons/mrp/__manifest__.py, https://github.com/odoo/odoo/blob/20.0/addons/account/__manifest__.py, https://github.com/odoo/odoo/blob/20.0/addons/loyalty/__manifest__.py y https://github.com/odoo/odoo/blob/20.0/addons/l10n_ar/__manifest__.py
- Localización argentina y módulos documentados: https://www.odoo.com/documentation/20.0/es_419/applications/finance/fiscal_localizations/argentina.html

### Código abierto argentino para ARCA — referencia, no incorporación aprobada

Encontramos `leonobitech/l10n_ar_arca_edi`, un módulo de facturación electrónica para Odoo Community que declara integración WSAA/WSFEv1, generación de CAE y pruebas para documentos y WSFE. La revisión de su manifiesto es más importante que una etiqueta del buscador: declara **AGPL-3**, versión Odoo 19 y estado de desarrollo Beta. Su README también contiene una inconsistencia sobre la licencia, por lo que debe prevalecer el manifiesto y el archivo LICENSE, no los badges o resúmenes.

- Puede servir para comprender el protocolo, descubrir casos de prueba y comparar cobertura.
- Puede ser candidato para adaptación interna. Antes de incorporarlo, validar versión, madurez, dependencias, avisos y obligaciones AGPL si usuarios interactúan remotamente con la versión modificada.
- No está validado para Odoo 20 ni para producción ARCA; sus propios metadatos indican Beta.
- El repositorio OCA `l10n-argentina` declara AGPL-3 en su nivel raíz y advierte que cada módulo puede tener licencia distinta. En la rama 19.0 observada encontramos la estructura de mantenimiento, pero no módulos listos para incorporar. No se lo considera hoy una base lista para integrar.

Fuentes:
- https://github.com/leonobitech/l10n_ar_arca_edi
- https://github.com/leonobitech/l10n_ar_arca_edi/blob/main/__manifest__.py
- https://github.com/leonobitech/l10n_ar_arca_edi/blob/main/LICENSE
- https://github.com/OCA/l10n-argentina

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
| GPL | Permite uso comercial, pero al distribuir una obra cubierta o derivada pueden existir obligaciones de entregar el código fuente correspondiente bajo GPL | Permitidas para evaluación e incorporación interna, con cumplimiento de condiciones |
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

La arquitectura general permanece como un **monolito modular con una fuente de verdad transaccional**. La decisión de plataforma todavía está abierta porque hay una disyuntiva real:

- **Elegir Odoo Community 20** si la prioridad es acelerar con POS, inventario, compras, fabricación y contabilidad existentes, y aceptamos construir el producto como un conjunto de módulos dentro del ecosistema Odoo. En ese caso no se reescribe el POS desde cero ni se extraen archivos sueltos; se extiende Odoo mediante sus módulos y APIs. Hay que resolver fuera de la caja la recuperación offline tras cierre/reinicio, confirmar qué módulos de Argentina son Community y evitar dependencia no planificada de Enterprise.
- **Elegir Medusa v2** si la prioridad es una base tecnológica propia en TypeScript, con núcleo MIT y límites modulares más cercanos a una plataforma que diseñamos nosotros. Se desarrollaría un POS propio y los módulos de caja, compras, producción, fiscalidad, auditoría y sincronización que Medusa no ofrece.
- **Construir un monolito propio en TypeScript + PostgreSQL** si Medusa no encaja sin forzar su modelo y Odoo exige demasiadas adaptaciones o no supera los requisitos offline. Esta opción mantiene mayor independencia, pero tiene el costo inicial más alto.

No se recomienda ejecutar Odoo y Medusa juntos como dos sistemas transaccionales, ni usar sus tablas como dos fuentes de verdad. Tampoco se recomienda combinar código del POS de Odoo dentro de una aplicación Medusa: ambos son frameworks completos con modelos, permisos, ciclo de vida y dependencias propias.

La comparación debe medir el producto que realmente necesitamos, no solo el arranque:

| Criterio | Odoo Community 20 | Medusa v2 |
|---|---|---|
| POS funcional inicial | Alto | Bajo; hay que construirlo |
| Inventario, compras y fabricación | Alto en módulos existentes | Parcial; exige extensiones |
| Catálogo, pedidos y promociones | Alto | Alto para comercio/pedidos |
| Arquitectura TypeScript propia | No; framework Python de Odoo | Sí; core TypeScript |
| Licencia del core revisado | LGPL-3 | MIT, excluyendo Enterprise |
| Offline resistente a cierre/reinicio | No demostrado; la guía advierte no cerrar el navegador antes de sincronizar | No viene resuelto; hay que diseñarlo |
| ARCA | Localización documentada; licencia de EDI/reportes por confirmar | Adaptador propio o componente externo aprobado |
| Dependencia de framework | Alta | Media/alta |
| Esfuerzo inicial esperado | Menor en funciones ERP; mayor donde se requiera alterar POS u offline | Mayor en POS/ERP; menor fricción para diseñar contratos propios |

La matriz es una hipótesis cualitativa basada en funcionalidades y arquitectura revisadas; no es el resultado de una prueba ejecutada. La elección final se hará con una prueba comparativa. PostgreSQL sigue siendo el candidato para el registro central si elegimos Medusa o el monolito propio; Odoo administra sus propios datos y motor de persistencia si gana la alternativa Odoo.

Para una app propia, la capa local debe tener almacenamiento transaccional y cola duradera, identificadores globales, idempotencia, reintentos y conciliación explícita. IndexedDB es una alternativa inicial de PWA; si no garantiza recuperación, se evaluará SQLite mediante un servicio local. No se prometerá offline total: ARCA, pagos externos y datos de otros dispositivos pueden requerir conexión.

En Medusa, el motor en memoria no se considerará suficiente para producción; se configurará el mecanismo durable recomendado por su documentación. Redis solo se incorpora si forma parte de la solución elegida y se justifica operativamente. En Odoo se debe demostrar cómo preservar las operaciones locales incluso si el proceso o el navegador se cierra abruptamente; no alcanza con la caché que documenta el POS.

## Prueba comparativa única antes de cerrar el framework

No vamos a encadenar pruebas sueltas ni construir dos productos. Se define una sola prueba vertical, pequeña y equivalente, ejecutada como dos pruebas de ajuste: un módulo/extensión mínima sobre Odoo Community 20 y un conjunto mínimo de módulos sobre Medusa. La implementación debe alcanzar el mismo resultado y registrar el esfuerzo y las dependencias de cada alternativa.

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
13. En Odoo, comprobar que el escenario funciona solo con código Community y módulos con licencia aprobada; verificar qué ocurre al cerrar el navegador durante el modo offline. En Medusa, comprobar que los módulos propios no alteran el núcleo y que cada dato tiene un solo dueño.
14. Registrar tiempo/esfuerzo real, cantidad de personalizaciones, puntos de extensión usados, dependencias, licencias, facilidad de actualización y deuda técnica introducida.

**Criterio para elegir:** comparar el esfuerzo real de completar el flujo en ambos candidatos, sin modificar núcleos y sin crear una segunda fuente de verdad para ventas/pagos/stock. La opción elegida debe preservar la recuperación tras cierre/reinicio, la sincronización idempotente, los permisos y la trazabilidad. Si ninguna cumple sin cambios invasivos, se construye el monolito modular propio.

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
- [x] Se seleccionaron Odoo Community 20 y Medusa v2 como finalistas de una comparación acotada.
- [x] Se identificó un módulo ARCA externo AGPL-3 que se mantiene como referencia, no como dependencia aprobada.
- [x] No se incorporó código de terceros.
- [ ] No se eligió ni fijó todavía una versión de framework.
- [ ] Falta ejecutar la prueba vertical de compatibilidad.
- [ ] Falta generar el primer inventario/SBOM del software propio y sus dependencias.

 

## Catálogo técnico ampliado — revisión 19/11/2026

Se creó [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md), con una evaluación por módulo y enlaces a repositorios y licencias verificadas. La búsqueda deja de limitarse a dos plataformas y ahora contempla:

- Plataformas integrales: Posnic, ERPNext/Frappe, NexoPOS y Odoo.
- Hardware: pos-toolkit para ESC/POS, impresoras, cajón, scanners seriales y balanzas HID.
- Pruebas físicas simuladas: emupos y ESCPost.
- Fiscalidad argentina: arca-sdks como primera opción para TypeScript; Afip.py como alternativa Python; OCA y módulos Odoo como candidatos condicionados.
- Offline: PowerSync Open Edition y Dexie.js, con responsabilidades y límites diferenciados.
- Gastronomía: TastyIgniter, ElitaleRestro y DearPOS para módulos o referencias concretas.

### Hallazgos que cambian la evaluación

1. Posnic pasa a ser el primer candidato para una prueba vertical integral por su arquitectura local/offline y cobertura POS retail/restaurante. No está aprobado: la evidencia offline publicada es acotada, el código propio es AGPL-3.0-only y los instaladores incluyen MongoDB bajo SSPL-1.0.
2. ERPNext/Frappe queda como segundo candidato integral por la cobertura de ERP, fabricación, compras, inventario y contabilidad.
3. NexoPOS es candidato, pero el LICENSE raíz declara GPLv3 y composer.json declara MIT. No aprobar incorporación hasta resolver la discrepancia con el mantenedor.
4. pos-toolkit es el componente más prometedor para hardware; register-core figura como planificado y no debe contarse como implementado.
5. arca-sdks reemplaza al repositorio arca-facturacion archivado. El paquete de facturación revisado declara MIT y requiere Node >=22.12.
6. PowerSync Open Edition es Apache-2.0; sus funciones Enterprise y Cloud tienen condiciones comerciales separadas. Dexie es almacenamiento IndexedDB, no sincronización completa.
7. emupos y ESCPost pueden reducir compras tempranas de periféricos y hacer reproducibles las pruebas de hardware.

La evaluación es documental. Todavía no se clonaron ni ejecutaron los proyectos y no se incorporó código externo. Las prioridades indican qué probar primero, no aprobación de producción.
