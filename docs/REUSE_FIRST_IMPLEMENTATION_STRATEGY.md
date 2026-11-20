# Estrategia de implementación basada primero en reutilización

**Revisión:** 20 de noviembre de 2026  
**Estado de la decisión:** aprobada como criterio de trabajo. Ninguna plataforma quedó elegida y todavía no se incorporó código externo.

## Decisión ejecutiva

Rubrova debe aprovechar primero software existente, probado y mantenido. No vamos a reconstruir un ERP, un POS, un WMS, un motor fiscal, conectores de hardware ni herramientas de analítica si existe una solución que podamos adoptar, extender o integrar con un costo y un riesgo razonables.

La estrategia queda definida así:

1. **Buscar y evaluar soluciones completas antes de programar el dominio.**
2. **Preferir configuración y módulos oficiales** antes que modificaciones del núcleo.
3. **Integrar aplicaciones especializadas como unidades de dominio independientes** cuando tengan una API, persistencia, ciclo de actualización y autoridad de datos claros.
4. **Reutilizar bibliotecas, SDK y adaptadores** para capacidades acotadas.
5. **Mantener un fork únicamente cuando la adaptación sea demostrablemente más económica que reemplazarlo** y podamos absorber sus actualizaciones.
6. **Escribir código propio sólo para brechas concretas**, reglas particulares de nuestra operación, integraciones argentinas o experiencia de uso que ninguna solución cubra bien.

Por lo tanto, queda en pausa la idea de comenzar directamente implementando Gateway, Ventas e Inventario propios. Esa prueba sólo se hará si la evaluación demuestra que las plataformas y los componentes disponibles no resuelven las capacidades necesarias sin comprometer la arquitectura.

## Qué entendemos por modularidad

La arquitectura objetivo sigue siendo una composición de aplicaciones y servicios de dominio independientes. No queremos una aplicación propia enorme, ni una colección de microservicios diminutos que multiplique el mantenimiento.

Una unidad de dominio debe tener una responsabilidad clara, una autoridad única sobre sus datos, una interfaz de integración documentada, pruebas, backup/restore y un ciclo de actualización controlable.

Un producto existente puede tener módulos internos que comparten runtime o base de datos. Podemos evaluarlo como **una aplicación de dominio completa**, aislada del resto por API y con su propia persistencia. En ese caso no afirmaremos que sus módulos internos son microservicios. Sólo se acepta si el conjunto que administra forma un límite de negocio razonable y Rubrova no duplica esas mismas autoridades. Si la aplicación mezcla responsabilidades que necesitamos desplegar, recuperar o sustituir por separado, y no se puede encapsular sin modificarla profundamente, no será la base de esos dominios.

Reglas que no cambian:

- Ningún servicio escribe en tablas privadas de otro.
- Un solo dueño transaccional por venta, pago, caja, stock, documento fiscal y asiento.
- Los sistemas externos se conectan mediante API, eventos o adaptadores; no por acceso directo a sus bases.
- No se agrega un gateway, broker, base de datos o framework por anticipado. Primero se prueba lo que ofrece el componente seleccionado y se incorpora infraestructura sólo cuando exista una necesidad concreta.
- Un ERP/POS externo puede resolver varias funciones dentro de su propio límite, pero Rubrova no ejecutará dos motores paralelos que mantengan el mismo stock, venta o pago.

La diferencia entre aplicación modular, servicio independiente y biblioteca está documentada en [Composición de módulos](MODULE_COMPOSITION.md) y [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md). Los componentes técnicos están en [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md).

## Orden de reutilización

| Orden | Alternativa | Criterio |
|---|---|---|
| 1 | Adoptar una aplicación existente | Cubre el flujo completo, se opera localmente y puede convertirse en autoridad de un dominio |
| 2 | Extender con módulos o plugins oficiales | El punto de extensión está soportado y sobrevive a actualizaciones |
| 3 | Integrar una aplicación especializada | Resuelve un dominio concreto con API, persistencia y ciclo de vida propios |
| 4 | Incorporar una biblioteca o SDK | Resuelve una función técnica acotada sin llevarse reglas de negocio ajenas |
| 5 | Mantener un fork o extraer un módulo | El costo total, incluyendo actualizaciones, es menor y está probado |
| 6 | Implementar la brecha | No hay solución adecuada o la adaptación implica más riesgo y costo que desarrollar sólo esa parte |

No se debe confundir "reutilizar código" con conectar proyectos indiscriminadamente. Cada adopción necesita un dueño de datos, un contrato y una estrategia de actualización. Copiar archivos sin comprender su dependencia del framework o del modelo de datos suele trasladar el costo en lugar de reducirlo.

## Candidatos para la primera evaluación

La selección se divide por tipo de responsabilidad. Las versiones siguientes son referencias de laboratorio observadas el 20/11/2026; antes de ejecutar una prueba se volverán a verificar el tag, el commit, las dependencias y la licencia efectiva.

### Base ERP / gestión administrativa

| Candidato | Qué reutiliza | Encaje y límite arquitectónico | Prioridad |
|---|---|---|---|
| [ERPNext + Frappe](https://github.com/frappe/erpnext) 16 / Frappe 16 | POS, ventas, compras, inventario, fabricación, costos, contabilidad, administración y reportes | POS Profile integra empresa, depósito, precios, impuestos, medios y cuentas. Sus apps comparten site/bench y persistencia: aplicación integrada, no microservicios independientes. ERPNext GPL-3.0; Frappe MIT. | Primera prueba |
| [MyCompany / lsFusion](https://github.com/lsfusion-solutions/mycompany) 6.2 | CRM, ventas, compras, multi-depósito, facturación, fabricación, POS y RR. HH. | Módulos propios y API HTTP. Todos los módulos de la instalación comparten base de datos; evaluarlo como aplicación acotada, no como microservicios independientes. MyCompany Apache-2.0 y lsFusion LGPL-3.0. | Primera prueba |
| [Tryton](https://www.tryton.org/) 8.2 | Ventas, compras, inventario, contabilidad, fabricación y POS oficial sale_point | Arquitectura cliente-servidor con PostgreSQL. sale_point 8.2 documenta ventas, devoluciones, pagos, vuelto, sesiones, movimientos de stock y asientos. Los módulos comparten servidor/base. Las ramas principales de tryton-ar inspeccionadas declaran versiones 7.1 y 8.1 en módulos distintos; verificar un conjunto compatible de tags para 8.2 antes de portarlo. | Primera ronda condicionada |
| [Dolibarr](https://www.dolibarr.org/) 24.0.3 | CRM, pedidos, compras, inventario, envíos, fabricación, facturación, pagos, POS y contabilidad | API REST, hooks y triggers; módulos dentro de una aplicación integrada. Se evalúa como filtro corto de menor complejidad y se mide TakePOS. | Filtro corto |
| [Posnic](https://github.com/Posnic/POS) 1.9.2 | POS retail/gastronómico, ventas, devoluciones, pagos, compras, catálogo e inventario | Aplicación POS dedicada, pero el paquete revisado combina AGPL-3.0-only con MongoDB SSPL-1.0 y componente comercial; reglas fiscales orientadas a India y soporte macOS limitado. | Referencia POS secundaria |

ERPNext y MyCompany son las primeras pruebas de cobertura porque permiten medir un POS integrado con catálogo, pagos, stock y administración. Ninguno se aprueba por tener muchos módulos: ambos deben demostrar que su límite de datos y despliegue es compatible con Rubrova. Tryton 8.2 se evalúa en paralelo por su POS oficial y su base PostgreSQL. La localización argentina merece atención especial: las ramas principales inspeccionadas declaran series diferentes; hay que verificar tags/versiones alineados y, sólo si no existen, estimar el port a 8.2. Dolibarr pasa por un filtro corto para comprobar si su menor complejidad compensa sus límites funcionales. El ganador no está predeterminado.

### POS y operación de caja

| Candidato | Qué reutiliza | Riesgos / condición | Prioridad |
|---|---|---|---|
| [Posnic](https://github.com/Posnic/POS) 1.9.2 | POS retail/gastronómico, ventas, devoluciones, pagos, compras, catálogo e inventario | Fuente AGPL-3.0-only; el paquete revisado identifica MongoDB Community bajo SSPL-1.0 y amCharts comercial. El modo self-hosted usa una base común y no resuelve por sí solo la sincronización de bases independientes. Hay que validar fiscalidad argentina, proceso offline y componentes empaquetados. | Prueba POS |
| [uniCenta oPOS](https://unicenta.com/) 5.5.2 | POS maduro, periféricos y operación en varios sistemas | El sitio publica binarios para Windows, macOS Intel y Linux, pero la descarga del código 5.5.2 exige iniciar sesión. No se aprueba reutilización de fuente hasta obtener el código exacto, licencia y avisos de terceros. | En espera de fuente verificable |
| POS de MyCompany, Tryton, Dolibarr y ERPNext | Evita mantener un segundo sistema de ventas cuando la plataforma ERP ya cubre el flujo | Comparar velocidad real de caja, escáner, pesables, pagos mixtos, vuelto, turnos, devoluciones y recuperación tras cierre/reinicio. | Se prueba junto a cada ERP |

Posnic se evalúa como candidato específico para la responsabilidad POS. No se debe instalar como segundo dueño de stock si otra plataforma ya administra las existencias. uniCenta sólo sube de prioridad cuando podamos revisar el código de la versión actual, no un espejo antiguo de una release diferente.

### Componentes y aplicaciones especializadas

| Proyecto | Uso potencial | Condición |
|---|---|---|
| [pos-toolkit](https://github.com/narisolutions/pos-toolkit) | Tickets ESC/POS, impresoras, cajón, lectores seriales y balanzas HID | Separar constructor TypeScript de tickets del plugin nativo Rust/Tauri. Probar hardware y sistema operativo exactos. |
| [arca-sdks](https://github.com/ramiidv/arca-sdks) | WSAA, WSFE, WSFEX, CAEA y servicios relacionados | SDK comunitario; homologación, versión fijada, revisión de licencia y manejo propio de estados inciertos/idempotencia. |
| [Odoo `l10n_ar`](https://github.com/odoo/odoo/tree/19.0/addons/l10n_ar) + `l10n_ar_edi` | Localización contable base y facturación electrónica argentina | `l10n_ar` público LGPL-3, disponible en ramas 19/20. La documentación oficial lista `l10n_ar_edi` para WSFE/CAE, pero el código no aparece en Community; obtener código/licencia exactos antes de considerar su reutilización. |
| [leonobitech/l10n_ar_arca_edi](https://github.com/leonobitech/l10n_ar_arca_edi) | Addon comunitario WSAA/WSFEv1 para Odoo 19 | AGPL-3, versión 19.0.1.0.0, Beta y último push observado 17/03/2026; sólo candidato de laboratorio con homologación. |
| [InvenTree](https://github.com/inventree/InvenTree) | Inventario técnico, ubicaciones, trazabilidad, BOM, compras y fabricación ligera | Tiene API y arquitectura de plugins. No asumir que su modelo de partes sustituye el catálogo minorista o el POS. |
| [OpenBoxes](https://github.com/openboxes/openboxes) | WMS, recepción, picking, lotes, vencimientos, conteos y despacho | Evaluar sólo si la profundidad logística justifica la instalación y puede asumir una autoridad de stock claramente delimitada. |
| [Apache OFBiz](https://ofbiz.apache.org/) 24.09.08 | Referencia de servicios de negocio, ERP, pedidos y contabilidad | Posee un Service Engine orientado a SOA, pero la serie 24.09 está congelada en funciones y recibe correcciones. Mantener como referencia y candidato de segunda etapa por su complejidad. |

PowerSync, Dexie, Spree/Saleor, InvenTree, Bigcapital, DuckDB/Superset/Metabase, Keycloak, OpenTelemetry, Prometheus/Grafana, pgBackRest y restic/Kopia siguen siendo candidatos, no decisiones de tecnología. La localización Odoo `l10n_ar` y el addon Beta `l10n_ar_arca_edi` sólo se prueban si Odoo queda en la composición; la rama OCA Argentina 19.0 revisada no contiene addons. Spree/Saleor sólo se evaluarían como canales online conectados a la autoridad comercial elegida; PowerSync como capa offline para lecturas/tareas no conflictivas; InvenTree sólo si la trazabilidad técnica y BOM justifican un dueño acotado; Bigcapital sólo si puede ser la autoridad financiera sin duplicar el ledger del ERP; DuckDB/BI para datos analíticos de sólo lectura; y pgBackRest/restic para respaldos según el motor y tipo de datos. Primero se elige quién posee cada dato y se comprueba si su mecanismo nativo alcanza. Después se incorpora la pieza mínima que resuelva una brecha demostrada.

## Cómo se decide

### Puertas obligatorias

Un candidato queda descartado para una responsabilidad si no supera cualquiera de estas puertas:

1. El código fuente, la versión y la licencia de los componentes necesarios no se pueden verificar.
2. No se puede instalar desde una referencia reproducible o no hay una ruta de actualización mantenible.
3. No permite exportar los datos propios en un formato utilizable o recuperar un backup en una instalación limpia.
4. No expone una API, exportación o mecanismo soportado que permita integrarlo sin leer/escribir tablas privadas.
5. No puede asignársele una autoridad única sobre los datos del dominio.
6. No supera los flujos críticos de concurrencia, reintentos, duplicados y recuperación que le correspondan.
7. La adaptación requiere modificar tantas partes del núcleo que el costo de mantener el fork supera el de implementar una alternativa acotada.

Una limitación no crítica puede registrarse como brecha y resolverse con un adaptador; no se convierte en aprobado sin una prueba.

### Puntuación después de las puertas

| Criterio | Peso |
|---|---:|
| Cobertura funcional y calidad de los flujos reales | 25 |
| Separación de responsabilidades, API y extensibilidad | 20 |
| Integridad transaccional, concurrencia, offline y recuperación | 20 |
| Adaptación a Argentina: fiscalidad, moneda, idioma, pagos y operación | 15 |
| Instalación, Windows/macOS, backup, actualización y soporte | 10 |
| Licencia, procedencia, seguridad y mantenimiento | 10 |
| **Total** | **100** |

La puntuación no reemplaza las puertas obligatorias. Se guarda evidencia de cada nota: pantalla/resultado, log, prueba, archivo, commit o limitación observada. No se asigna una nota alta por una función anunciada en el README.

## Protocolo de trabajo

### Etapa A — filtro documental y de código

Para cada candidato: fijar tag/commit, identificar runtime y base de datos, leer licencias raíz y de dependencias, verificar extensiones/APIs, comprobar instalación limpia, identificar datos exportables y listar las áreas funcionales realmente implementadas. Las demos sirven para orientar; no cuentan como prueba de persistencia, recuperación o licencia.

### Etapa B — laboratorio corto y comparable

Usar el mismo conjunto de datos sintéticos y el mismo guion para las aplicaciones candidatas. Se empieza por ERPNext y MyCompany como candidatos de cobertura; Tryton 8.2 se evalúa en paralelo con la compatibilidad de la localización argentina; Dolibarr recibe un filtro corto. Posnic se prueba sólo como referencia POS secundaria. No se obliga a todos a ejecutar escenarios fuera de su responsabilidad.

La prueba mínima cubre:

- Artículos, variantes, códigos, unidades, pesables, clientes y proveedores.
- Pedido/venta, descuentos, pagos mixtos, vuelto, caja y devolución.
- Compra, recepción parcial, costo, reserva y movimiento de stock.
- Producción/BOM, consumo, merma y trazabilidad cuando corresponda.
- Dos puestos en LAN, caída de internet, cierre abrupto del proceso y reinicio.
- Exportación, backup y restauración en una instalación limpia.
- API de lectura/escritura controlada, eventos, autenticación y conciliación.
- Impresora, escáner, balanza y cajón con simulador antes de hardware real.

### Etapa C — finalistas

Sólo los dos candidatos con mejor evidencia pasan al protocolo profundo P01–P44. Se prueban conflictos de stock por operaciones distintas, idempotencia concurrente, webhooks repetidos/fuera de orden, pagos inciertos, migraciones, backup distribuido y recuperación.

### Etapa D — prueba de extensión y actualización

Antes de aprobar un producto, desarrollar una extensión pequeña y representativa sin editar el núcleo, actualizar entre versiones fijadas y volver a ejecutar las pruebas. Registrar líneas/archivos modificados, dependencias nuevas, pasos manuales y conflictos de actualización. Si el único modo de adaptar es un fork grande, contabilizar su mantenimiento real.

### Etapa E — composición de Rubrova

Definir qué aplicación o servicio será dueño de cada dominio. Crear adaptadores versionados para conectar interfaces y servicios. No implementar una segunda versión propia del mismo proceso hasta decidir que se reemplazará formalmente al dueño existente y planificar migración y conciliación.

## Qué se construye en Rubrova

El código original se concentra donde puede generar una ventaja real y donde no haya una opción madura adecuada:

- Experiencia de usuario unificada y flujos particulares de nuestras actividades.
- Adaptación argentina que no esté cubierta por los módulos seleccionados.
- Integraciones propias con ARCA, medios de pago, transportistas y sistemas contables, reutilizando SDK y conectores verificables.
- Orquestación, conciliación y recuperación entre aplicaciones.
- Indicadores, rentabilidad multiárea y automatizaciones basadas en datos confiables.
- Brechas puntuales demostradas en POS, inventario, producción o servicios B2B.

No se empieza por escribir un motor de stock, contabilidad, CRM o compras si un producto evaluado ya resuelve esas reglas de forma mantenible.

## Primer paso y criterio de salida

**Primera prueba:** ERPNext 16/Frappe 16 y MyCompany/lsFusion 6.2; Tryton 8.2 entra condicionado por el conjunto de módulos argentinos; Dolibarr 24.0.3 recibe un filtro corto. Posnic 1.9.2 se compara como referencia POS, no como ERP paralelo. No hay un ganador documental.

La primera entrega de software se elegirá después de esa comparación: será un flujo vertical que use las capacidades reutilizadas y agregue sólo los adaptadores o reglas faltantes. No se aprueba aún una implementación propia de Gateway, Ventas e Inventario.

**Criterio de salida:** seleccionar una base o combinación de aplicaciones con evidencia de cobertura, integración, licencias y recuperación; definir el dueño de cada dato; registrar brechas y costo de adaptación; y recién entonces abrir la implementación funcional.

## Estado real del repositorio

- La documentación, los modelos de prueba y el validador del dataset están en Rubrova.
- El workflow existente valida la consistencia de fixtures sintéticos; no ejecuta ni aprueba MyCompany, Tryton, Dolibarr, ERPNext o Posnic.
- No se incorporó código de terceros ni existe todavía una aplicación funcional de Rubrova.
- No se decidió lenguaje, base de datos o broker para servicios propios. Esa decisión depende de los candidatos que superen el laboratorio.

La estrategia de licencias y uso privado está en [Estrategia de código abierto](OPEN_SOURCE_STRATEGY.md); la pauta reproducible está en [Evaluación de plataformas](PLATFORM_EVALUATION.md); la lista de proyectos está en [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md).
