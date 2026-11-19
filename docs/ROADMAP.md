# Plan de trabajo

## Estado actual

**Fase 0 — decisión técnica basada en evidencia.** Rubrova contiene definición de producto, arquitectura e investigación, pero todavía no tiene una aplicación funcional ni código externo incorporado. El paso inmediato es ejecutar una evaluación local reproducible de dos plataformas integrales, no sumar más referencias ni empezar pantallas aisladas.

La prueba común, versiones fijadas, conjunto sintético y criterios de aprobación están en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

## Fase 0 — decidir la base

- Consolidar reglas comerciales, modelo de dominio, estados y contratos.
- Evaluar Posnic 1.9.2 y ERPNext 16.60.0/Frappe 16 con el mismo conjunto de datos y flujo.
- Probar caja, ventas, pagos mixtos, descuentos, devoluciones, inventario, compras y producción.
- Demostrar corte de internet, cierre forzado, reinicio, reintento, conciliación y backup/restauración.
- Medir esfuerzo real de extensión, actualizaciones, dependencias y licencias.
- Verificar adaptación argentina, ARCA en homologación y hardware.
- Elegir una única plataforma transaccional o construir el monolito modular propio.

**Criterio de salida:** se completa la prueba sin pérdida ni duplicación de ventas, pagos o movimientos; la recuperación y restauración son demostrables; las extensiones son mantenibles; existe una ruta fiscal viable; y se documenta el costo de conservar la base elegida. Si ninguna opción supera los controles excluyentes, se descartan como base y se reutilizan solo los componentes que hayan pasado su revisión.

## Fase 1 — núcleo transaccional

Se ejecuta sobre la plataforma elegida. Si ninguna resulta adecuada, se implementa como monolito modular propio.

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
- [x] Protocolo común P01–P17 con datos sintéticos y puertas críticas.
- [x] Laboratorio de instalación reproducible para Posnic y ERPNext.
- [x] Validador automático del dataset y workflow de GitHub Actions; última ejecución confirmada: 6/6 pruebas aprobadas y dataset válido.
- [ ] Instalación local de Posnic.
- [ ] Instalación local de ERPNext/Frappe.
- [ ] Ejecución y evidencia de los escenarios.
- [ ] Decisión de base y plan de adaptación.

No se marca una prueba como aprobada por haber leído documentación, ejecutar una demo o completar un formulario. Se necesita evidencia reproducible.
