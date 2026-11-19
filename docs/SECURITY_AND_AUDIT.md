# Seguridad, permisos y auditoría

## Objetivo

Proteger dinero, inventario, datos personales, información fiscal y continuidad. El sistema debe permitir saber qué ocurrió, quién intervino y qué autorización existió.

## Identidad individual

- Cada persona opera con su propio usuario.
- Se permite PIN rápido después de identificar al usuario, sin reemplazar autenticación apropiada.
- No se comparten credenciales de caja.
- Sesiones bloqueadas por inactividad según riesgo.
- Autenticación reforzada para propietarios y administradores.
- Recuperación de cuenta controlada y auditada.

## Roles y permisos

Roles iniciales: propietario, administrador, encargado, cajero, vendedor, depósito/compras, preparación/cocina, contador y auditor.

Los roles son configurables. El permiso se evalúa por acción, negocio, sucursal, caja, importe y contexto.

Acciones sensibles:
- Cambiar precios.
- Aplicar descuentos fuera de límite.
- Anular ventas.
- Devolver dinero.
- Reabrir turnos.
- Ajustar stock.
- Dar de baja productos.
- Registrar retiros y gastos.
- Crear salidas internas.
- Exportar datos.
- Ver información financiera o fiscal.
- Consultar auditorías.

Puede exigirse aprobación de un usuario distinto al operador. Los límites se configuran por comercio.

## Registro de auditoría

Registrar:
- Inicio/cierre de sesión e intentos fallidos.
- Cambios de roles y permisos.
- Descuentos manuales y excepciones.
- Anulaciones, devoluciones y reembolsos.
- Ajustes y salidas de inventario.
- Modificaciones de precio y costo.
- Cierres, diferencias y reaperturas de caja.
- Cambios de configuración e integración.
- Exportaciones y consultas sensibles.

Cada evento incluye id, fecha, actor, negocio, sucursal, dispositivo, turno, acción, entidad afectada, valores relevantes, motivo, autorización y resultado.

Los logs no almacenan contraseñas, tokens, CVV ni datos personales innecesarios.

## Protección de registros

- Eventos append-only desde la aplicación.
- Sin edición o borrado de auditoría desde la interfaz.
- Controles de integridad y detección de alteración.
- Acceso restringido y registrado.
- Retención definida por tipo de dato y obligación legal.
- Backups separados y restauración probada.
- Protección contra inyección de logs.
- Exportaciones con alcance, fecha y responsable.

La inmutabilidad lógica no sustituye backups ni controles de acceso.

## Cajas, turnos y arqueos

Asignar operador, caja, sucursal y período. Registrar fondo inicial, medios de pago, entradas, retiros, gastos y reembolsos. Permitir arqueo ciego, diferencia explicada y autorización para reapertura o ajuste.

Los indicadores de desempeño deben contextualizar volumen, horas, función y permisos. Una mayor cantidad de anulaciones no prueba por sí sola una conducta incorrecta.

## Anulaciones y devoluciones

La operación original se conserva. Se genera un movimiento compensatorio relacionado. Se actualizan stock, pagos, cuentas y documentación fiscal según reglas. Una devolución no implica necesariamente que el artículo vuelva a stock vendible. El reembolso es un movimiento separado y debe prevenirse la duplicación.

## Movimientos internos no comerciales

Clasificaciones:
- Consumo propio o de personal.
- Muestra o degustación.
- Compensación autorizada a cliente.
- Promoción sin cargo.
- Donación.
- Uso interno o producción.
- Rotura, pérdida o vencimiento.
- Devolución a proveedor.

Se excluyen de reportes de ventas y demanda cuando no representan venta. Sí aparecen en movimientos de stock, costo, control administrativo, auditoría y documentación fiscal que corresponda.

Puede existir un menú restringido a administración para mantener la caja simple. La restricción de visibilidad no elimina registros ni impide el acceso de auditoría autorizado. No se implementan ventas no declaradas ni mecanismos para ocultar ingresos u operaciones.

El tratamiento documental y fiscal de cada salida debe configurarse con asesoramiento contable y conforme a normativa vigente.

## Privacidad y aislamiento

- Separación estricta por negocio.
- Acceso mínimo necesario.
- Cifrado en tránsito y protección de secretos.
- Cifrado de datos almacenados cuando corresponda.
- Minimización y retención definida.
- Consentimiento y preferencias de comunicación.
- Acceso a datos sensibles auditado.
- Datos sintéticos para pruebas.
- No mostrar datos comerciales de un negocio a otro sin base legal, anonimización robusta y controles aprobados.

## Estándares

Usar OWASP ASVS 5.0 como catálogo verificable de controles. La adopción se registra con requisitos, pruebas y evidencias; no se declara certificación por el solo hecho de consultar el estándar.

Para pagos con tarjeta se priorizan terminales y proveedores externos, minimizando el alcance de datos de tarjeta. El alcance PCI aplicable debe ser revisado por especialistas antes de procesar o almacenar datos.
