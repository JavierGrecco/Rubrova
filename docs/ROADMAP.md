# Plan de trabajo

## Estado actual

**Fase 0 — definición del producto y fundamentos.** El repositorio contiene documentación inicial. No existe todavía implementación funcional ni pruebas de una aplicación. Las fechas se definirán después de pruebas técnicas; no se inventan estimaciones.

## Fase 0 — definición y fundamentos

- Visión y alcance acordados.
- Flujos POS y reglas de descuentos.
- Modelo de dominio y estados.
- Límites y contratos entre módulos.
- Reglas de auditoría, roles y privacidad.
- Estrategia de canales y facturación.
- Riesgos y pruebas de aceptación.
- Decisiones técnicas registradas.
- Revisión de código abierto, licencias y dependencias.
- Odoo Community 20 y Medusa v2 como finalistas, sin aprobación anticipada.
- Prueba vertical equivalente para comparar POS, caja, inventario, descuentos, recuperación offline, extensibilidad y esfuerzo de adaptación.
- Verificación de licencias y disponibilidad real de los módulos argentinos para ARCA.

Criterio de salida: el equipo puede explicar alcance, arquitectura y flujos principales sin depender de conversaciones previas; la plataforma elegida supera la prueba comparativa sin alterar su núcleo, duplicar fuentes de verdad ni incumplir los requisitos offline. Si ninguna alternativa lo logra, se aprueba el monolito modular propio.

## Fase 1 — núcleo transaccional

1. Organización, sucursales, usuarios y permisos.
2. Catálogo, variantes, códigos y unidades.
3. Precios y listas.
4. Carrito y POS.
5. Descuentos y promociones trazables.
6. Pagos, medios mixtos y caja.
7. Movimientos de inventario.
8. Auditoría y turnos.
9. Pruebas automatizadas de flujos críticos.

Criterio de salida: una venta se registra, cobra, audita y reconcilia con caja e inventario en un entorno de prueba.

## Fase 2 — continuidad y gestión

Almacenamiento local; Outbox/Inbox, idempotencia y sincronización; recuperación tras reinicio; compras y proveedores; clientes y cuentas corrientes; devoluciones y reembolsos; importación masiva y calidad de datos; hardware inicial validado.

Criterio de salida: los flujos definidos sobreviven cortes y reintentos sin pérdida ni duplicación.

## Fase 3 — canales e integraciones

Tienda online y pedidos; WhatsApp y pedidos asistidos; Mercado Libre; pagos; ARCA en homologación; conciliación fiscal y de liquidaciones; envíos, retiros y reservas de stock.

Criterio de salida: pedidos y documentos externos se integran sin duplicar venta, pago o factura.

## Fase 4 — perfiles sectoriales

Supermercado y autoservicio; panadería y pastelería; rotisería y comidas preparadas; gastronomía y cafetería; recetas, producción, mermas, lotes, vencimientos, balanzas, comandas y cocina.

Criterio de salida: cada perfil completa sus flujos usando el núcleo común.

## Fase 5 — inteligencia del negocio

Definiciones financieras y analíticas; tableros globales, por sucursal y canal; rentabilidad por categoría/marca/producto; rotación, ABC-XYZ, GMROI y reposición; estacionalidad y pronósticos; radar de cambios de demanda y precios; promociones y medición incremental; contexto externo; asistente y escenarios.

Criterio de salida: informes conciliados con operaciones y pronósticos evaluados contra resultados reales.

## Fase 6 — escalabilidad y madurez

Multi-sucursal avanzada; servicio local si las pruebas lo justifican; automatizaciones; observabilidad; recuperación; revisión de seguridad independiente; preparación de despliegue y soporte.

## Reglas de priorización

Integridad antes que cantidad de funciones; POS y caja antes que tableros sofisticados; datos correctos antes que IA; sincronización verificada antes de prometer offline; homologación fiscal antes de producción; priorizar por beneficio, riesgo, dependencia y costo de mantenimiento.
