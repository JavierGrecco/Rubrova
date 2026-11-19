# Canales e integraciones

## Objetivo

Unificar pedidos y resultados sin perder la identidad de cada canal ni duplicar ventas, pagos, inventario o comprobantes.

## Dimensiones de una operación

Registrar por separado: canal de origen, canal de contratación, canal de cobro, plataforma intermediaria, sucursal que prepara, ubicación que entrega, modalidad de entrega y campaña/fuente cuando exista.

Ejemplo: un pedido llega por WhatsApp, se paga por transferencia, se prepara en una sucursal y se retira allí. Canal, medio de pago y entrega son dimensiones diferentes.

## Ciclo del pedido

Estados configurables: recibido, pendiente de pago, confirmado, reservado, en preparación, listo para retiro, despachado, entregado, cancelado, devuelto parcial o totalmente. Cada transición valida reglas, permisos y efectos en stock, pagos y fiscalidad.

## Stock y reservas omnicanal

- Stock compartido o asignado por canal.
- Reservas con vencimiento.
- Pedidos pagados, pendientes y cancelados.
- Liberación de reservas.
- Prevención de sobreventa.
- Política para sucursales con varias cajas offline.
- Idempotencia para pedidos externos repetidos.

## ARCA y facturación

La venta comercial, el pago y el comprobante fiscal son estados independientes.

- Identificar quién es responsable de emitir por cada canal.
- Si una plataforma ya emitió, importar y vincular; no emitir otro.
- Si la aplicación propia es emisora, obtener autorización válida y asociar el documento al pedido externo.
- Si no se puede confirmar si ya existe comprobante, detener emisión automática y enviar a conciliación.
- Conservar tipo, punto de venta, número, fecha, CAE/CAEA y referencia al original.
- Una factura autorizada no se elimina: su corrección sigue el procedimiento aplicable.
- Mantener homologación y revisar cambios normativos.

WSFEv1, WSMTXCA y otras opciones se eligen según comprobante y caso fiscal. ARCA es la fuente de verdad.

## Mercado Libre

- Importar pedidos y estados.
- Identificar cuenta, vendedor, operación y paquete.
- Consultar estado de facturación.
- Distinguir facturación del Facturador de Mercado Libre de facturación propia.
- Vincular PDF/XML/JSON o referencia del documento.
- Adjuntar factura propia cuando el flujo lo requiera.
- Importar comisiones, devoluciones y cargos por separado.
- Conciliar pedidos, cobros, envíos, documentos y liquidaciones.

Regla: no emitir desde dos sistemas para una misma obligación fiscal. Webhooks repetidos o fuera de orden deben procesarse con idempotencia. Validar permisos, endpoints, campos y flujos vigentes en documentación oficial y cuenta de prueba.

## Mercado Pago y pagos externos

Usar identificador interno único y claves de idempotencia; verificar firma y autenticidad de notificaciones; consultar estado cuando sea necesario; no acreditar por una captura del cliente; relacionar pago, devolución y liquidación; separar comisión, retención, costo financiero y neto acreditado. No almacenar datos completos de tarjeta ni CVV.

## WhatsApp y mensajería

Catálogo, consultas, pedidos e interpretación asistida de texto, audio e imágenes. Confirmación humana ante ambigüedad. Consentimiento para comunicaciones comerciales. Registrar origen del pedido. No usar conversaciones privadas para entrenar modelos sin base legal, consentimiento y controles.

## Hardware e integraciones

Cada integración tiene contrato y versión, autenticación mínima, idempotencia, errores y reintentos, correlación, pruebas o sandbox, recuperación y responsable. La indisponibilidad externa no debe borrar una venta.

## Reportes por canal

Global, físico y online comparten definiciones de ventas netas, costos, margen y devoluciones. Cada canal suma sus costos: comisión, envío, embalaje, publicidad, contracargos y adquisición cuando se conozcan. Los pedidos externos y las ventas locales se reconcilian sin doble conteo.


## Terminales de pago presenciales

Los pagos presenciales se conectan por adaptador del adquirente, separado de la venta y del módulo fiscal. La matriz inicial de investigación incluye:

- Mercado Pago Point: Orders API, terminales, webhooks y consulta de estado.
- Getnet Get POS Integrado: API cloud-to-cloud o SDK local USB/Wi-Fi, sujeto a habilitación.
- Fiserv/Posnet: modalidad POS Integrado Trx a Trx, con programa/cable y homologación.
- Payway: capacidades de terminal/PINpad a confirmar con documentación técnica y acceso de desarrollador.

El adaptador publica capacidades reales: iniciar pago, consultar, recibir notificación, cancelar, reembolsar, imprimir voucher y cerrar lote. No todas estarán disponibles en todos los proveedores.

El estado externo no se deduce de la pantalla ni de un timeout. Las órdenes creadas o recibidas por la terminal siguen pendientes hasta confirmación final. Un resultado incierto se consulta y concilia. La clave de idempotencia y la referencia de operación impiden duplicados.

La guía de flujo, estados, impresión y pruebas está en [Checkout y terminales](CHECKOUT_AND_PAYMENT_TERMINALS.md).


## Logística y transportistas argentinos

El módulo de logística no está acoplado a un proveedor. Separa el despacho del pedido/venta y expone adaptadores para cotizar, crear envíos, obtener etiquetas, recibir seguimiento y registrar prueba de entrega según las capacidades de cada operador.

La investigación de APIs, proyectos y límites está en [Logística argentina y seguimiento unificado](ARGENTINA_LOGISTICS_INTEGRATION.md). No asumir que un agregador de tracking puede crear una guía ni contratar un flete.

## Interoperabilidad contable

El sistema debe exportar ventas, compras, cobros, pagos, asientos, centros de costo y dimensiones de gestión a los paquetes contables que use la empresa o su estudio. La compatibilidad con Tango, Catedral, Bejerman, Xubio, Colppy y perfiles de archivos se documenta en [Interoperabilidad contable y administrativa](ACCOUNTING_INTEROPERABILITY.md).

La integración no debe emitir dos comprobantes fiscales ni mantener dos libros contables editables. La fuente de verdad y las claves externas se definen por tipo de documento.
