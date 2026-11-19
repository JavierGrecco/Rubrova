# Arquitectura

## Dirección técnica

La dirección sigue siendo un **monolito modular con límites claros**, una base transaccional central y capacidad local para operar durante interrupciones de conectividad. No se dividirá en microservicios sin una necesidad medida.

La estructura del negocio y las invariantes son propias. Los frameworks y módulos externos se evalúan como herramientas reemplazables: no deben decidir qué significa una venta, un pago, un movimiento de caja o un movimiento de inventario.

## Plataformas candidatas para validar

La arquitectura base sigue siendo un **monolito modular con límites claros**, pero la implementación se está comparando entre dos plataformas:

- **Odoo Community 20.0:** candidato para acelerar la cobertura funcional. El repositorio público contiene bajo LGPL-3 módulos de POS, inventario, compras, fabricación, contabilidad base, fidelización y localización fiscal argentina base. Permite extender el sistema mediante módulos propios. Su adopción implica aceptar el framework, ORM, modelo de datos y ciclo de actualizaciones de Odoo. El offline documentado del POS se apoya en la caché del navegador y advierte no cerrar ni recargar antes de sincronizar; no cumple por sí solo la recuperación fuerte que requerimos. La licencia y disponibilidad Community de los módulos de facturación electrónica y reportes de Argentina deben confirmarse antes de contar con ellos.
- **Medusa v2:** candidato para una plataforma propia en TypeScript. El núcleo comercial es MIT, con materiales Enterprise separados. Ofrece módulos para catálogo, precios, promociones, pedidos, pagos, inventario y workflows; no ofrece el POS/ERP completo que necesitamos, por lo que caja, arqueos, compras avanzadas, producción, fiscalidad, auditoría y offline serán módulos propios.

La elección no se va a basar solo en la velocidad de mostrar una primera pantalla. Se ejecutará una prueba vertical equivalente sobre ambas alternativas, midiendo cuánta lógica se puede extender sin parches al núcleo, qué limitaciones de offline quedan, qué licencias aplican y cuánto esfuerzo real demanda cumplir los flujos críticos.

Si Odoo requiere sobrescribir grandes partes de su POS o no permite recuperación offline duradera sin un fork profundo, pierde su ventaja de velocidad. Si Medusa obliga a construir casi todo el núcleo comercial o a duplicar sus conceptos de pedidos/stock, también pierde su ventaja modular.

**Alternativa de salida:** si ninguna plataforma supera la evaluación sin comprometer la integridad, se construye un monolito modular propio en TypeScript sobre PostgreSQL y se reutilizan únicamente bibliotecas y componentes permisivos que hayan superado la revisión. No se ejecutarán Odoo y Medusa como dos fuentes de verdad ni se mezclará el código interno de sus POS.

## Principios

- Los módulos representan responsabilidades del negocio.
- Cada módulo es dueño de sus reglas y datos.
- Otros módulos usan contratos públicos, no leen tablas internas ajenas.
- No existen dependencias circulares.
- Los eventos describen hechos ocurridos; no sustituyen transacciones necesarias.
- Operaciones financieras y de inventario usan transacciones explícitas.
- Servicios externos quedan detrás de adaptadores.
- La lógica de negocio no depende de una interfaz específica.
- El modo local no depende de que una tarea del navegador siempre esté disponible.
- El código externo no se incorpora sin revisión de licencia, mantenimiento, seguridad y compatibilidad.
- Cada dato transaccional tiene un único sistema responsable; no se ejecutan dos motores de stock o ventas como fuentes de verdad.

## Módulos

| Módulo | Responsabilidad |
|---|---|
| Identidad y acceso | Usuarios, sesiones, roles, permisos |
| Organización | Negocios, sucursales, cajas y ubicaciones |
| Catálogo | Productos, variantes, marcas, categorías y unidades |
| Precios y descuentos | Listas, vigencias, promociones y cupones |
| Ventas POS | Carrito, venta, líneas y tickets |
| Pedidos y canales | Pedidos propios y externos, atribución y entrega |
| Pagos y caja | Cobros, conciliación, caja, turnos y reembolsos |
| Inventario | Existencias, reservas, lotes, movimientos y conteos |
| Compras | Proveedores, cotizaciones, órdenes, recepciones y costos |
| Clientes | Perfil, cuenta corriente, beneficios y consentimiento |
| Producción | Recetas, órdenes, lotes, consumos, rendimientos y mermas |
| Fiscal | Comprobantes, autorizaciones, notas de crédito y conciliación |
| Promociones | Campañas, combos y medición de resultados |
| Inteligencia | Métricas, modelos, pronósticos, alertas y recomendaciones |
| Auditoría | Eventos, autorizaciones y consultas sensibles |
| Integraciones | Adaptadores externos y webhooks |
| Plataforma | Sincronización, notificaciones, archivos, backups y observabilidad |

## Capas por módulo

- Dominio: entidades, valores, reglas e invariantes.
- Aplicación: casos de uso y coordinación.
- Interfaces: API, tareas y entrada desde la interfaz.
- Infraestructura: base de datos, colas, proveedores y dispositivos.
- Pruebas: unitarias, integración, contrato y aceptación.

La estructura debe permitir encontrar responsabilidades sin imponer carpetas innecesarias.

## Datos y persistencia

- PostgreSQL es el candidato para la base central, sujeto a la prueba de compatibilidad.
- Almacenamiento local transaccional: IndexedDB para la primera prueba PWA; SQLite mediante un servicio local se evaluará si el navegador no ofrece la recuperación necesaria.
- Historial de movimientos para caja, pagos, inventario y cuentas corrientes.
- Fotografía de valores relevantes al momento de la venta.
- Identificadores globales para operaciones originadas sin conexión.
- Migraciones y esquemas versionados.
- Consultas analíticas separadas lógicamente del flujo de caja.

## Aislamiento de negocios

Toda entidad operativa pertenece a un negocio y, cuando corresponde, a sucursal o ubicación. El servidor valida el contexto del negocio; nunca confía en identificadores del cliente sin comprobar permisos. Se evaluará Row-Level Security como defensa adicional. Las pruebas deben intentar acceder a datos de otro negocio desde cada ruta.

## Operación sin conexión

- Persistir localmente antes de confirmar al usuario que la operación quedó guardada.
- Cola duradera de operaciones pendientes.
- UUID, dispositivo, negocio, secuencia local y versión de esquema.
- Envío repetible con idempotencia del servidor.
- Bandeja de entrada para deduplicar eventos.
- Reintentos con backoff y estado visible.
- Conflictos explícitos para stock, precios y datos maestros.
- Reconciliación y estado fiscal separado.
- Recuperación tras cierre, reinicio, pérdida de proceso y corte durante sincronización.

Dos dispositivos desconectados no pueden conocer cambios mutuos. Para varias cajas offline se evaluará un servicio local de sucursal o concentrador LAN. No usar "último cambio gana" para conflictos financieros o de stock.

No prometer offline total: ARCA, pagos externos y datos de otros dispositivos pueden requerir conexión. El offline POS debe ser probado incluso después de cerrar y volver a abrir la aplicación; mantener una pestaña abierta no alcanza.

## Eventos y sincronización

Usar Outbox/Inbox cuando una transacción deba producir un mensaje confiable. Cada evento incluye id, tipo, versión, fecha, negocio, origen y correlación. No incluir secretos ni datos personales innecesarios.

Si se adopta Medusa, su motor en memoria no se considerará suficiente para producción: se deberá configurar y probar un motor durable de workflows/eventos acorde con la documentación del framework. Redis solo se incorpora si forma parte de esa solución elegida y se justifica operativamente.

## Hardware

La interfaz POS se comunica con una capa de dispositivos independiente. Los protocolos y controladores de impresoras, lectores, balanzas, cajones, pantallas y terminales se aíslan detrás de adaptadores. Se prioriza una pasarela local cuando sea necesaria para acceso USB, serie o red y para mantener la caja desacoplada de los servicios externos.

No se afirma compatibilidad por marca genérica: cada modelo, conexión y sistema operativo se registra en una matriz de pruebas físicas.

## Observabilidad

Logs estructurados, correlación por operación, métricas de latencia y sincronización, trazas de flujos, alertas de fallos fiscales y de pago, estado visible para operaciones pendientes, backups automáticos y pruebas de restauración.

## Decisiones y validaciones pendientes

- [x] Dirección de monolito modular y propiedad de datos por módulo.
- [x] Estrategia de reutilización y revisión de licencias documentada.
- [x] Odoo Community 20 y Medusa v2 seleccionados como finalistas.
- [ ] Comparar ambas plataformas con la misma prueba vertical.
- [ ] Aprobar una plataforma o elegir el monolito propio.
- [ ] Confirmar las licencias y disponibilidad real de los módulos de Argentina que resuelvan ARCA.
- [ ] Cerrar interfaz React/PWA, persistencia local y eventual servicio local.
- [ ] Definir motor de workflows/eventos durable según la plataforma elegida.
- [ ] Elegir hosting, observabilidad y hardware inicial con pruebas.
- [ ] Confirmar el modelo de despliegue: nube, local por sucursal o híbrido.

Ninguna de estas decisiones pendientes se considera implementada o validada por estar escrita en este documento.
