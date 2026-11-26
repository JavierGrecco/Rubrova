# Seguridad, permisos y auditoría

> **Estado de implementación:** este documento define requisitos y controles objetivo; no es una declaración de que todos estén implementados. Para distinguir las capacidades verificadas en CI de las diseñadas o pendientes, consultar [Postura de seguridad y confianza operacional](SECURITY_POSTURE.md). La vista previa actual es de desarrollo y no está aprobada para datos reales ni exposición a redes.

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

Los logs no almacenan contraseñas, tokens, PAN completo, CVV, PIN, track ni datos personales innecesarios.
- Los datos de pagador recibidos para conciliación permanecen separados del CustomerAccount y no se exponen a CRM, RFM ni campañas.
- Marca y últimos cuatro dígitos de tarjeta son referencias de conciliación, no identidad.
- CBU/CVU/alias, tokens e IDs de instrumentos no se utilizan como claves universales de persona.

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

Para pagos con tarjeta se priorizan terminales, tokenización y formularios hospedados por proveedores, minimizando el alcance de datos de tarjeta. Rubrova no almacena PAN completo, CVV/CVC, PIN/PIN block ni datos de banda/track. El alcance PCI aplicable debe ser revisado por especialistas antes de procesar o almacenar datos.

La identidad de comprador, pagador y titular del instrumento son conceptos distintos. Los datos de pagador limitados por el proveedor a conciliación no pueden usarse para identificar o perfilar clientes.


## Referencias y normativa a validar

- OWASP ASVS 5.0: catálogo de requisitos verificables para controles de aplicación. Se seleccionará el nivel de requisitos según riesgo y se mantendrá evidencia de pruebas: https://asvs.owasp.org/.
- NIST SSDF SP 800-218 v1.1 es la referencia final publicada. NIST SP 800-218 Rev. 1 / v1.2 seguía figurando como borrador en la consulta del 19/11/2026; no se tratará como versión final hasta su publicación: https://csrc.nist.gov/Projects/ssdf/publications.
- PCI DSS v4.0.1: revisar el alcance aplicable con un especialista y el adquirente. La primera estrategia es no almacenar ni procesar datos completos de tarjeta y delegar el pago a terminales/proveedores: https://www.pcisecuritystandards.org/es/document_library/.
- Ley argentina 25.326 y normativa complementaria: definir finalidad, minimización, acceso, retención, derechos del titular y seguridad de datos personales: https://www.argentina.gob.ar/normativa/nacional/ley-25326-64790/actualizacion.
- RG 1415 actualizada: el texto vigente incluye modificaciones posteriores, entre ellas RG 5678/2025 y RG 5866/2026. El artículo 27 contempla documentación del traslado y entrega aun cuando no sea una compraventa, con el detalle y excepciones que establezca la norma: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-1415-2003-81316/actualizacion.

La aplicación concreta de normas fiscales y de privacidad debe revisarse con profesionales responsables antes de producción. Esta documentación no reemplaza asesoramiento legal o contable.
