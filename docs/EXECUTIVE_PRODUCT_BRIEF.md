# Brief ejecutivo de producto — Rubrova

**Revisión:** 26 de noviembre de 2026  
**Etapa:** piloto integrado POS + ERP; no es una versión productiva.

## 1. Qué es Rubrova

Rubrova es una plataforma de operación y gestión comercial orientada a negocios que necesitan unificar su punto de venta, inventario, compras, proveedores, clientes, caja y análisis de gestión.

La ambición de producto no es sumar pantallas administrativas. Es ofrecer una única secuencia operativa verificable: una venta impacta en el cobro, la caja, el inventario y el comprobante correspondiente; una compra y su recepción actualizan el abastecimiento; y los reportes se construyen sobre los movimientos reales que originaron cada indicador.

**Idea central:** simplificar la operación diaria y mejorar la calidad de las decisiones sin perder control sobre el dato.

## 2. Problema y oportunidad

En comercios y empresas de distribución, la información suele quedar separada entre caja, planillas, sistemas administrativos, marketplaces, mensajería, terminales de pago y transportistas. Esa separación dificulta:

- conocer el disponible real después de reservas y compromisos;
- conciliar ventas, pagos, efectivo, comprobantes e inventario;
- medir margen real por artículo, marca, canal, área y sucursal;
- distinguir una caída de demanda de un período sin stock;
- reponer con anticipación sin duplicar compromisos ni generar compras a ciegas;
- conservar trazabilidad cuando una integración externa falla.

Rubrova aborda estos problemas desde un núcleo transaccional común y una arquitectura que permite incorporar capacidades de forma progresiva.

## 3. Usuarios y segmentos objetivo

El diseño contempla distintos perfiles sobre un núcleo compartido:

| Perfil | Necesidad principal |
|---|---|
| Kioscos, almacenes y autoservicios | Cobro rápido, caja, catálogo, stock y reposición |
| Supermercados y comercios minoristas | Sucursales, depósitos, precios, promociones y control de margen |
| Panaderías, rotiserías y gastronomía | Productos, recetas, producción, mermas, costos y turnos |
| Mayoristas y distribuidores | Escalas de precio, mínimos, crédito, compras y entregas |
| Servicios B2B | Clientes empresariales, contratos, SLA, agenda y seguimiento |
| Administración y dirección | Caja, compras, costos, rentabilidad, riesgos y rendimiento por área/canal |

Estos son segmentos previstos por el diseño; todavía no representan instalaciones ni clientes comerciales validados.

## 4. Propuesta de valor prevista

1. **Operación integrada:** POS y gestión trabajan sobre una única autoridad de inventario, ventas, pagos y caja.
2. **Continuidad local:** el núcleo debe seguir operando en la red local aunque un proveedor externo o Internet no esté disponible.
3. **Trazabilidad:** anulaciones y devoluciones generan movimientos auditables; no se corrige historia mediante borrado silencioso.
4. **Reposición responsable:** el planificador distingue existencia física, disponibilidad, reservas, compromisos y recepciones previstas; sus recomendaciones no crean órdenes automáticamente.
5. **Inteligencia explicable:** cada métrica y recomendación debe poder rastrearse a los hechos, reglas y supuestos que la produjeron.
6. **Extensibilidad controlada:** los canales, adquirentes y proveedores se incorporan con contratos, idempotencia, límites y recuperación.

No se presentan estas capacidades como resultados comerciales medidos: son objetivos de producto y criterios de aceptación.

## 5. Diferenciadores que se están construyendo

### Control del inventario y abastecimiento

MyCompany mantiene separados el stock físico y el disponible. Rubrova trabaja sobre esa semántica: el disponible descuenta reservas que participan en la disponibilidad, mientras que los compromisos de salida y las recepciones previstas se concilian por identidad de línea para evitar dobles conteos.

La primera integración del planificador es estrictamente de lectura. Necesita políticas explícitas de demanda, lead time, stock de seguridad, MOQ y múltiplos; no inventa esos valores.

### Operación local con resiliencia

La ruta prioritaria de desarrollo es Java 21, PostgreSQL 18 y Tomcat 9 ejecutándose de forma nativa. Docker se mantiene como diagnóstico y empaquetado, no como dependencia obligatoria de la operación local prevista.

### Rentabilidad y demanda con historia

El modelo contempla vigencias de precios y costos, disponibilidad, quiebres de stock, devoluciones, promociones, canales, marca y unidad de negocio. El objetivo es distinguir demanda observada, demanda censurada y pronósticos, evitando presentar estimaciones como ventas reales.

## 6. Arquitectura actual

Rubrova parte de MyCompany 6.2 y lsFusion 6.2, con fuentes vendorizadas y versiones fijadas. El núcleo funciona como una suite integrada; no se etiqueta como microservicios.

- **Servidor y lógica:** Java 21 / lsFusion 6.2.
- **Aplicación base:** MyCompany 6.2.
- **Cliente web:** GWT / Apache Tomcat 9.
- **Persistencia:** PostgreSQL 18.
- **Extensiones Rubrova:** módulos propios para localización POS, resiliencia, configuración de terminales de pago y exportación de reposición.
- **Análisis y herramientas:** adaptadores Python y pruebas reproducibles.

El código de la plataforma y de MyCompany está en vendor; las extensiones y los scripts propios permanecen en sus directorios del repositorio.

## 7. Estado verificable a la fecha

| Hito | Evidencia | Lectura correcta |
|---|---|---|
| Fuentes MyCompany/lsFusion y compilación propia | [CI 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) | Servidor, cliente GWT y lógica compilados desde fuentes vendorizadas |
| POS nativo macOS ARM64 | [CI 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) | Login, venta sintética, pago, stock, cierre y persistencia tras reinicio |
| Backup lógico PostgreSQL | [CI 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) | Creación, SHA-256, verificación `pg_restore --list` y restore en una base nueva |
| Planificador y adaptador de snapshots | CI de reposición | Suites sobre fixtures sintéticas; aún falta contrastar con una base MyCompany de negocio |
| Windows | CI 45855055565 | Comprobación de sintaxis PowerShell; no equivale a instalación funcional completa |
| Linux nativo y Docker/Linux | CI 45855055565 | Jobs omitidos; no se cuentan como aprobados |
| Terminales bancarias y ARCA | Diseño/documentación | Sin adquirente homologado ni conexión fiscal productiva |

La venta de CI fue por ARS 1.250: el pago en efectivo quedó vinculado a la factura, el stock bajó de 10 a 9 y el turno quedó cerrado con importes conciliados. Después del reinicio se recuperaron factura, pago, existencia, turno y ocho incidencias.

El respaldo de prueba se creó desde `rubrova_dev`, se verificó con SHA-256 y se restauró en `rubrova_restore_ci`. La base activa y la configuración del runtime no se modificaron. Su alcance es PostgreSQL únicamente: no contiene documentos externos, imágenes, adjuntos, certificados ni secretos.

**Límites de la evidencia:** la salida externa estuvo habilitada y `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`; Linux y Docker/Linux se omitieron; Windows fue sintáctico; las ventas son fixtures. No hay todavía una jornada de operación real ni aceptación física en el Mac del usuario.

## 8. Qué no está terminado

- Devoluciones, reintegros y conciliación completa con la operación original.
- Arqueo contado, diferencias, ingresos y retiros de caja.
- Vuelto, pagos mixtos y aceptación de pagos con terminal real.
- Homologación fiscal ARCA y flujos definitivos de facturación.
- Exportación nativa conciliada contra una base MyCompany real.
- Instalación limpia offline en Windows/macOS y actualización controlada.
- Backup, restauración y rollback demostrados en un equipo limpio.
- Pruebas prolongadas de rendimiento, estabilidad y recuperación.
- Piloto comercial con un negocio real y métricas de uso/resultado.

Hasta cerrar estas brechas, Rubrova se considera un proyecto de ingeniería en etapa de piloto; no una solución lista para venta o uso diario.

## 9. Próximos hitos

1. Aceptar la exportación nativa autenticada en macOS ARM64 y Linux.
2. Conciliar una exportación real con los ledgers de MyCompany en una base local aislada.
3. Probar el primer arranque en un MacBook Air de usuario y documentar el recorrido local.
4. Completar devoluciones, reintegros, arqueo y medios de pago del POS.
5. Demostrar backup, restauración, actualización y rollback.
6. Ampliar la base de datos histórica y recién entonces contrastar modelos de demanda con datos reales.

## 10. Mensaje de posicionamiento

**Rubrova busca ser el sistema operativo del negocio: una experiencia de venta sencilla respaldada por gestión, control y análisis de punta a punta.**

El mensaje público debe hablar de la dirección del producto y de la evidencia disponible. No debe prometer todavía operación offline comercial, integración fiscal, pagos reales, precisión predictiva ni disponibilidad productiva que aún no se hayan homologado.
