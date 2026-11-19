# Arquitectura

## Dirección técnica

La dirección sigue siendo un **monolito modular con límites claros**, una base transaccional central y capacidad local para operar durante interrupciones de conectividad. No se dividirá en microservicios sin una necesidad medida.

La estructura del negocio y las invariantes son propias. Los frameworks y módulos externos se evalúan como herramientas reemplazables: no deben decidir qué significa una venta, un pago, un movimiento de caja o un movimiento de inventario.

## Candidato tecnológico para validar

La investigación de reutilización priorizó **Medusa v2 con TypeScript, React y PostgreSQL** como primer candidato para una prueba vertical. El núcleo de Medusa está bajo MIT, pero el repositorio separa materiales Enterprise sujetos a licencia comercial. Solo se considerarían módulos y archivos expresamente cubiertos por la licencia abierta.

El motivo para probarlo es que ofrece una arquitectura modular y código reutilizable para catálogo, precios, promociones, pedidos, pagos, inventario, canales, workflows y eventos. No incluye por sí solo las reglas críticas del producto: caja y turnos, arqueo, descuentos auditables según nuestras políticas, libro de stock y costos, producción, fiscalidad argentina ni continuidad offline robusta.

**Medusa no está aprobado todavía como framework.** La prueba debe demostrar que las funciones propias se pueden implementar mediante módulos y contratos, sin modificar su núcleo ni duplicar las fuentes de verdad.

Si no supera esa prueba, la alternativa preferida es un monolito modular propio en TypeScript sobre PostgreSQL, reutilizando únicamente bibliotecas permisivas aprobadas. Odoo Community 19 se mantiene como referencia funcional y alternativa de adopción integral, pero adoptarlo implicaría aceptar su framework, su modelo de datos y las obligaciones LGPLv3. La evaluación legal y técnica completa está en [Estrategia de reutilización de código abierto](OPEN_SOURCE_STRATEGY.md).

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
- [x] PostgreSQL definido como candidato para el almacenamiento central.
- [x] Estrategia de reutilización y revisión de licencias documentada.
- [ ] Aprobar o descartar Medusa mediante la prueba vertical completa.
- [ ] Cerrar interfaz React/PWA, persistencia local y eventual servicio local.
- [ ] Definir motor de workflows/eventos durable según la plataforma elegida.
- [ ] Elegir hosting, observabilidad y hardware inicial con pruebas.
- [ ] Confirmar el modelo de despliegue: nube, local por sucursal o híbrido.

Ninguna de estas decisiones pendientes se considera implementada o validada por estar escrita en este documento.
