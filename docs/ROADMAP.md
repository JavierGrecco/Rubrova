# Plan de trabajo

## Estado actual

**Fase 0 — selección técnica basada primero en reutilización.** Rubrova tiene definición funcional, modelos de dominio, arquitectura y un laboratorio de fixtures sintéticos; todavía no tiene una aplicación funcional ni código externo incorporado. La prioridad no es comenzar con servicios propios: es encontrar la mejor combinación de aplicaciones, módulos, plugins y bibliotecas existentes que podamos mantener y adaptar.

La decisión vigente y las puertas de selección están en [Estrategia de implementación basada primero en reutilización](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md). La comparación reproducible está en [Evaluación de plataformas](PLATFORM_EVALUATION.md). Los módulos y SDKs que pueden acelerar las integraciones están en [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md).

## Fase 0 — evaluar antes de construir

1. **Base ERP/gestión:** comparar MyCompany/lsFusion 6.2, Tryton serie 7.8 y Dolibarr 24.0.3. Mantener ERPNext 16.60.0 en el filtro comparativo.
2. **POS:** probar el POS incluido en cada plataforma, incluido Tryton `sale_point`; comparar Posnic 1.9.2 como candidato dedicado. No aprobar uniCenta 5.5.2 hasta verificar acceso a fuente, release y licencias.
3. **Componentes especializados:** revisar hardware/tickets, ARCA, WMS, tracking, contabilidad, importación, BI y automatización sólo cuando haya una necesidad concreta y un contrato compatible.
4. Fijar tag/commit, licencias, dependencias, instalación, APIs, extensiones, exportación, respaldo y restauración de cada candidato.
5. Probar los mismos datos sintéticos y flujos esenciales para evitar decidir por demos o promesas.
6. Elegir como máximo dos finalistas para el protocolo completo P01–P44; la prueba de cada producto se limita a los dominios que podría asumir.
7. Medir costo de adaptación y de actualización: módulos propios externos, cantidad de parches al core, dependencias, pasos manuales, conflictos y tiempo de recuperación.
8. Definir autoridad por dominio antes de conectar aplicaciones. No duplicar ventas, pagos, caja, inventario, comprobantes o contabilidad en sistemas paralelos.
9. Recién entonces elegir runtime, almacenamiento, broker, gateway y método de despliegue para las piezas propias que hagan falta.

**Criterio de salida:** una solución o composición aprobada con evidencia de cobertura, licencias, integridad, API, extensión, portabilidad, backup/restore y esfuerzo de mantenimiento. Si ninguna plataforma cubre un dominio, se reutilizan sus componentes compatibles y se implementa sólo esa brecha como servicio independiente. No se cambia automáticamente a un monolito propio.

## Fase 1 — primera entrega funcional basada en la selección

La primera entrega será un flujo vertical completo sobre la plataforma o combinación que supere la Fase 0. Su alcance exacto depende de los resultados, pero debe demostrar:

- Un recorrido operativo de extremo a extremo con datos persistentes y autoridad única.
- Extensiones propias separadas del núcleo cuando el producto lo permita.
- Integración mediante API/eventos versionados y adaptadores, sin acceso SQL cruzado.
- Idempotencia, concurrencia, permisos, auditoría y estados inciertos.
- Backup/restauración y actualización reproducibles.
- Pruebas de uso real y una ruta clara para reemplazar un componente sin perder datos.

Sólo si las plataformas candidatas fallan las puertas obligatorias se diseña el conjunto mínimo de servicios Rubrova para cubrir la brecha. En ese escenario se mantiene la arquitectura distribuida por dominio, se reutilizan SDK/bibliotecas y no se decide por anticipado un lenguaje, base o broker.

La secuencia anterior de construir directamente Gateway + Ventas + Inventario queda **condicionada**, no aprobada como inicio. Si finalmente hace falta, será una implementación propia justificada por evidencia y usará idempotencia, reservas/CAS, Outbox/Inbox y recuperación desde el primer flujo.

## Fase 2 — continuidad y gestión

Persistencia local; Outbox/Inbox; idempotencia; sincronización y conciliación; recuperación tras cierre/reinicio; compras y proveedores; clientes y cuentas corrientes; devoluciones y reembolsos; importación masiva y calidad de datos; hardware inicial validado.

**Criterio de salida:** los flujos definidos sobreviven cortes y reintentos sin pérdida, corrupción ni duplicación.

## Fase 3 — canales e integraciones

Tienda online y pedidos; WhatsApp y pedidos asistidos; Mercado Libre; pagos; ARCA en homologación; conciliación fiscal y de liquidaciones; envíos, retiros y reservas de stock.

**Criterio de salida:** pedidos y documentos externos se integran sin duplicar venta, pago o factura. Los servicios externos que requieren conexión mantienen estados explícitos cuando están caídos.

## Fase 4 — perfiles sectoriales

Supermercado y autoservicio; panadería y pastelería; rotisería y comidas preparadas; gastronomía y cafetería; recetas, producción, mermas, lotes, vencimientos, balanzas, comandas y cocina.

**Criterio de salida:** cada perfil completa sus flujos usando el núcleo común y conserva trazabilidad.

## Fase 5 — inteligencia del negocio

Definiciones financieras y analíticas; tableros globales, por sucursal y canal; rentabilidad por categoría/marca/producto; rotación, ABC-XYZ, GMROI y reposición; estacionalidad y pronósticos; radar de cambios de demanda y precios; promociones y medición incremental; contexto externo; asistente y escenarios.

**Criterio de salida:** informes conciliados con operaciones y pronósticos evaluados contra resultados reales. La inteligencia explica fuentes, supuestos y confianza.

## Fase 6 — madurez

Multi-sucursal avanzada; servicio local si las pruebas lo justifican; automatizaciones; observabilidad; recuperación; revisión de seguridad independiente; backup/restauración verificados y operación estable.

## Reglas de priorización

Integridad antes que cantidad de funciones; POS y caja antes que tableros sofisticados; datos correctos antes que IA; sincronización probada antes de prometer offline; homologación fiscal antes de producción; una sola fuente de verdad; y cada dependencia externa debe ahorrar más trabajo del que agrega en actualización y mantenimiento.

## Entregables actuales de Fase 0

- [x] Catálogo de código reutilizable.
- [x] Estrategia de uso interno privado y revisión de licencias.
- [x] Posnic fijado en tag v1.9.2 para una prueba reproducible.
- [x] ERPNext v16.60.0 y Frappe Framework 16 identificados como alternativa integral.
- [x] Protocolo común P01–P26 con datos sintéticos y puertas críticas.
- [x] Laboratorio de instalación para MyCompany 6.2, Posnic 1.9.2 y ERPNext 16.60.0.
- [x] Validador automático del dataset y workflow de GitHub Actions; última ejecución confirmada: 21/21 pruebas aprobadas y dataset válido.
- [x] Auditoría de cobertura y mapa integral de capacidades recuperado/documentado.
- [x] Investigación nacional de adopción digital y testimonios de necesidades PyME con límites de representatividad documentados.
- [x] Evaluación documental adicional de Dolibarr 24.0.3, InvenTree 1.7.3, OpenBoxes, OpenWMS y localización argentina Odoo/OCA.
- [x] Verificación de localización argentina Odoo 19/20: addon `l10n_ar` público LGPL-3, `l10n_ar_edi` documentado pero no localizado en Community, addon comunitario WSAA/WSFE Beta y rama OCA 19 sin módulos instalables.
- [x] Especificación de continuidad operativa, recuperación, backups, estados inciertos y pruebas P27–P44.
- [x] Decisión de arquitectura distribuida: servicios de dominio independientes, contrato/API/eventos, propiedad de datos, gateway local y coordinación de stock por CAS/cuotas offline.
- [x] Especificación detallada de checkout, vuelto, terminales y documentos separados.
- [x] Contratos de composición modular y estrategia de adaptadores por OS documentados.
- [x] Nueva investigación de MyCompany/lsFusion, Simple WMS, OpenLinker, OfferKit, DuckDB, Superset y Node-RED.
- [x] Shortlist transversal ampliada: PowerSync, Spree, Saleor, InvenTree, addons OCA, Bigcapital, DuckDB, Metabase, Superset, Keycloak, OpenTelemetry, Prometheus, Grafana, pgBackRest, restic y Kopia; versiones y licencias registradas.
- [x] Alcance multiárea, mayorista/distribución, servicios B2B y rentabilidad por unidad documentados.
- [x] Investigación de Dolibarr, OCA Field Service, OpenFieldPro y Open TMS para los nuevos dominios.
- [ ] Instalar/evaluar Dolibarr 24.0.3 de forma comparable o documentar por qué no supera el costo de evaluación.
- [ ] Instalar/evaluar InvenTree 1.7.3 para ubicaciones, código, trazabilidad, BOM y API.
- [ ] Instalar/evaluar MyCompany 6.2 en entorno aislado.
- [ ] Instalar/evaluar MyCompany/lsFusion 6.2, Tryton serie 7.8 (incluido `sale_point`), Dolibarr 24.0.3, ERPNext/Frappe 16 y Posnic 1.9.2 en entornos aislados y según la responsabilidad que cada uno pueda asumir.
- [ ] Inspección dirigida de InvenTree, OpenBoxes y componentes públicos de OpenWMS; fijar módulos/commits y límites de licencia.
- [ ] Solicitar credenciales de QA a Andreani, PAQ.AR y OCA; comparar Envíopack, AfterShip y 17TRACK para tracking multioperador.
- [ ] Confirmar si existe una API/operativa Kangu aplicable a Argentina; no asumir disponibilidad.
- [ ] Solicitar layouts de importación/exportación de Catedral y licencias/versiones de Tango, Bejerman, Xubio y Colppy.
- [ ] Probar importación/migración, exportación contable balanceada, conciliación y recuperación de lotes.
- [ ] Solicitar/obtener documentación y terminales de prueba para Mercado Pago Point, Getnet, Fiserv Posnet y Payway.
- [ ] Si Odoo supera la evaluación de plataforma, probar el addon oficial `l10n_ar` y obtener/verificar el código/licencia de `l10n_ar_edi`; comparar con `leonobitech/l10n_ar_arca_edi` Beta en homologación. No asumir que OCA/l10n-argentina 19.0 contiene módulos instalables.
- [ ] Ejecutar escenarios P20–P26: multiárea, mínimos/tier pricing, despacho posterior, contratos/servicios, rentabilidad y transferencias internas.
- [ ] Inspección dirigida de Dolibarr 24.0.3 y decidir si entra a la comparación integral.
- [ ] Ejecutar P27–P44 y validar backup/restauración, idempotencia concurrente, CAS, cuotas offline y rollback individual de servicios.
- [ ] Ejecución y evidencia de todos los escenarios.
- [ ] Probar PowerSync como caché offline de catálogo y tareas de dispositivo; comprobar desconexión, reinicio, reintentos y dos terminales en conflicto sin delegarle la autoridad del stock.
- [ ] Comparar Spree v6.0.5 y Saleor 3.23.50 como canal online/B2B; seleccionar como máximo uno y probar pedidos, cancelaciones, reservas, webhooks duplicados y conciliación con la autoridad comercial central.
- [ ] Evaluar InvenTree para componentes/BOM y addons OCA Manufacturing sólo si Odoo entra en la composición; revisar cada addon por licencia y dependencias.
- [ ] Probar DuckDB con exports Parquet/CSV canónicos y conciliar los resultados analíticos contra los reportes transaccionales; evaluar Superset sólo si se necesita un servicio BI multiusuario.
- [ ] Comparar Bigcapital v0.25.46 con la contabilidad nativa de los ERP finalistas; medir API, balance de comprobación, estados financieros, bancos, multimoneda, impuestos, ARCA, licencias, dependencias y backup/restore antes de decidir si puede ser la única autoridad financiera.
- [ ] Probar pgBackRest (si PostgreSQL forma parte de la solución) con recuperación PITR a instancia alternativa; probar restic/Kopia para documentos/archivos y restauración verificada.
- [ ] Diferir Keycloak y la pila OpenTelemetry/Prometheus/Grafana hasta que haya varias aplicaciones/servicios o una necesidad de SSO/observabilidad que el sistema elegido no cubra.
- [ ] Decisión de tecnología y almacenamiento por servicio, despliegue local y plan de adaptación de plataformas reutilizadas.

No se marca una prueba como aprobada por haber leído documentación, ejecutar una demo o completar un formulario. Se necesita evidencia reproducible.
