# Plan de trabajo

## Estado actual

**Fase 0 — decisión técnica basada en evidencia.** Rubrova contiene definición de producto, arquitectura e investigación, pero todavía no tiene una aplicación funcional ni código externo incorporado. El paso inmediato es consolidar el modelo multiárea y ejecutar una evaluación local reproducible de las plataformas integrales y módulos especializados. Rubrova debe cubrir comercio minorista, online, mayorista/distribución y servicios B2B sobre datos compartidos, con rentabilidad por unidad y consolidada.

La prueba común, versiones fijadas, conjunto sintético y criterios de aprobación están en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

La investigación de mercado y los nuevos proyectos candidatos están en [Investigación de mercado y oportunidades](MARKET_RESEARCH_AND_ADDITIONAL_OPPORTUNITIES.md). La arquitectura objetivo de servicios independientes está en [Arquitectura modular distribuida](DISTRIBUTED_MODULAR_ARCHITECTURE.md). Los escenarios de continuidad, recuperación y backup/restauración están en [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md).

## Fase 0 — decidir la base

- Consolidar reglas comerciales, modelo de dominio, estados y contratos.
- Comparar Posnic 1.9.2, ERPNext 16.60.0/Frappe 16 y MyCompany/lsFusion 6.2 como plataformas integrales con pruebas equivalentes.
- Evaluar módulos dedicados de WMS/TMS, integraciones, promociones, servicios de campo, analítica, automatización y archivo documental detrás de contratos.
- Evaluar Dolibarr 24.0.3 como cuarto candidato integral sólo si puede ejecutarse con los mismos escenarios y puertas críticas; comparar InvenTree 1.7.3 como componente de inventario/producción, no como ERP ni autoridad paralela.
- Convertir los hallazgos de adopción digital y necesidades PyME en criterios medibles: conciliación entre canales, datos importables, margen real, cuentas corrientes y visibilidad de errores.
- Ejecutar escenarios de continuidad P27–P44: terminación abrupta de procesos (sin apagar el equipo), pagos inciertos, webhooks y comandos repetidos, conflictos CAS, cuotas offline, restauración, migraciones, Sagas y rollback por servicio.
- Definir adaptadores para Andreani, PAQ.AR, OCA e-Pak, Vía Cargo y agregadores; Kangu queda pendiente de confirmar en Argentina.
- Diseñar perfiles contables para Tango, Catedral, Bejerman, Xubio y Colppy, con lotes idempotentes y conciliación.
- Incorporar mejoras derivadas de necesidades PyME: recuperación de sincronizaciones, importación asistida, costo de reposición, cobranza/flujo de caja y WMS por ubicación.
- Definir y validar unidades de negocio, centros de beneficio/costo y dimensiones de canal, sucursal, territorio, proyecto y contrato.
- Probar mínimos y escalas mayoristas, crédito B2B, despachos parciales y tracking agregado después de la venta.
- Probar contratos de servicio, SLA, agenda, órdenes de trabajo, evidencia, aceptación y facturación.
- Probar consumo interárea de stock/servicios y su eliminación en el resultado consolidado.
- Completar la especificación del checkout: línea removible antes de pagar, efectivo recibido/vuelto y pago integrado con terminales locales.
- Probar caja, ventas, pagos mixtos, descuentos, devoluciones, inventario, compras y producción.
- Demostrar terminación abrupta/reinicio de un proceso, desconexión de red, reinicio de un servicio independiente, reintento idempotente, conflicto CAS, conciliación y restauración desde un punto registrado.
- Medir esfuerzo real de extensión, actualizaciones, dependencias y licencias.
- Verificar adaptación argentina, ARCA en homologación y hardware.
- Validar una plataforma distribuida de servicios por dominio: almacenamiento propio, APIs/eventos versionados, Outbox/Inbox, observabilidad y despliegue/rollback por servicio. Las plataformas integrales candidatas sólo se adoptan si pueden cubrir dominios sin fusionar sus autoridades ni imponer una base compartida.

**Criterio de salida:** los servicios cumplen aislamiento de datos, contratos compatibles, idempotencia, recuperación y despliegue independiente. Se demuestran operaciones sin pérdida/duplicación, restauración verificable y ruta fiscal viable. Si una plataforma candidata no respeta estos límites, se descarta como base aunque tenga muchas funciones; sólo se reutilizan componentes que pasen sus pruebas.

## Fase 1 — núcleo transaccional

Se implementa como servicios independientes. Un componente ERP/POS externo puede cubrir un dominio si respeta contratos, aislamiento, idempotencia, versionado y despliegue independiente; no se fusiona toda la plataforma en un único runtime.

1. Organización, sucursales, usuarios y permisos.
2. Catálogo, variantes, códigos, unidades y reglas de precio.
3. Carrito y venta POS.
4. Descuentos, promociones y autorizaciones trazables.
5. Pagos, medios mixtos, movimientos de caja y arqueo.
6. Libro de movimientos de inventario.
7. Auditoría, turnos y devoluciones.
8. Pruebas automatizadas de los flujos críticos.

**Criterio de salida:** una venta se registra, cobra, audita y reconcilia con caja e inventario en un entorno repetible.

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
- [x] Especificación de continuidad operativa, recuperación, backups, estados inciertos y pruebas P27–P44.
- [x] Decisión de arquitectura distribuida: servicios de dominio independientes, contrato/API/eventos, propiedad de datos, gateway local y coordinación de stock por CAS/cuotas offline.
- [x] Especificación detallada de checkout, vuelto, terminales y documentos separados.
- [x] Contratos de composición modular y estrategia de adaptadores por OS documentados.
- [x] Nueva investigación de MyCompany/lsFusion, Simple WMS, OpenLinker, OfferKit, DuckDB, Superset y Node-RED.
- [x] Alcance multiárea, mayorista/distribución, servicios B2B y rentabilidad por unidad documentados.
- [x] Investigación de Dolibarr, OCA Field Service, OpenFieldPro y Open TMS para los nuevos dominios.
- [ ] Instalar/evaluar Dolibarr 24.0.3 de forma comparable o documentar por qué no supera el costo de evaluación.
- [ ] Instalar/evaluar InvenTree 1.7.3 para ubicaciones, código, trazabilidad, BOM y API.
- [ ] Instalar/evaluar MyCompany 6.2 en entorno aislado.
- [ ] Instalar/evaluar MyCompany/lsFusion 6.2, Posnic 1.9.2 y ERPNext/Frappe en entornos aislados.
- [ ] Inspección dirigida de InvenTree, OpenBoxes y componentes públicos de OpenWMS; fijar módulos/commits y límites de licencia.
- [ ] Solicitar credenciales de QA a Andreani, PAQ.AR y OCA; comparar Envíopack, AfterShip y 17TRACK para tracking multioperador.
- [ ] Confirmar si existe una API/operativa Kangu aplicable a Argentina; no asumir disponibilidad.
- [ ] Solicitar layouts de importación/exportación de Catedral y licencias/versiones de Tango, Bejerman, Xubio y Colppy.
- [ ] Probar importación/migración, exportación contable balanceada, conciliación y recuperación de lotes.
- [ ] Solicitar/obtener documentación y terminales de prueba para Mercado Pago Point, Getnet, Fiserv Posnet y Payway.
- [ ] Ejecutar escenarios P20–P26: multiárea, mínimos/tier pricing, despacho posterior, contratos/servicios, rentabilidad y transferencias internas.
- [ ] Inspección dirigida de Dolibarr 24.0.3 y decidir si entra a la comparación integral.
- [ ] Ejecutar P27–P36 y validar backup/restauración, RPO/RTO y recuperación real.
- [ ] Ejecución y evidencia de todos los escenarios.
- [ ] Decisión de base y plan de adaptación.

No se marca una prueba como aprobada por haber leído documentación, ejecutar una demo o completar un formulario. Se necesita evidencia reproducible.
