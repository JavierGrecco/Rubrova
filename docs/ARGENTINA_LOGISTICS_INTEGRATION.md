# Integración logística argentina y seguimiento unificado

**Revisión:** 19 de noviembre de 2026  
**Estado:** investigación documental. Ningún transportista está conectado todavía a Rubrova ni se han probado credenciales comerciales.

## 1. Objetivo

Rubrova debe permitir que cualquier área —online, minorista, mayorista/distribución o servicios— gestione retiros, reparto propio y despachos de terceros desde un mismo centro logístico.

El módulo no debe depender de un solo correo ni exigir que la guía exista al confirmar la venta. La venta, el fulfillment, el despacho, la contratación del transporte y el tracking son hechos separados.

## 2. Resultado de investigación por operador

| Operador | Vía de integración encontrada | Capacidades identificadas | Estado y límites |
|---|---|---|---|
| Andreani | API oficial para desarrolladores | Cotización, creación y consulta de envíos, trazas/seguimiento, sucursales y procesos de stock | Candidato directo prioritario. Se requieren alta comercial y credenciales QA/producción; la documentación indica sandbox |
| Correo Argentino PAQ.AR | API oficial MiCorreo/PAQ.AR | Cotizar, alta/importación de envíos, pago/etiquetas, consulta de sucursales e historial | Candidato directo prioritario. Credenciales y agreement por ambiente; confirmar el alcance exacto de cada operación en el manual vigente |
| OCA e-Pak | Web Services oficiales | Tarifas, plazos, centros de imposición, altas/retiros, etiquetas y servicios de tracking | Candidato directo. La operativa debe habilitarse con OCA; no se puede asumir que un código de operación se crea libremente desde la API |
| Vía Cargo | Tracking web oficial; proveedores terceros de tracking | Consulta individual mediante número de guía; AfterShip publica una integración nativa de seguimiento de Vía Cargo y 17TRACK lista el transportista | No se encontró API pública oficial para desarrolladores, alta de despacho o cotización. Separar tracking de contratación y generación de guías |
| Envíopack | API comercial de agregación logística | Cotización, gestión de envíos, tracking normalizado y notificaciones webhook | Candidato para reducir conectores. Confirmar transportistas, cobertura, tarifas, credenciales y funcionalidades habilitadas para nuestra cuenta |
| AfterShip Tracking | API comercial multitransportista | Seguimiento y normalización de estados; tiene integración publicada para Vía Cargo | Alternativa para tracking, no necesariamente para cotizar, contratar, pagar o generar etiquetas |
| 17TRACK | API comercial multitransportista | Directorio amplio de operadores, registro y consulta de tracking | Alternativa para tracking. Verificar el código actual de Vía Cargo, planes, cuotas, webhooks y latencia antes de adoptar |
| Kangu | No se confirmó API/operación argentina aplicable | Mercado Libre anunció su adquisición en 2021 y describió presencia de Kangu en Brasil, Colombia y México | No asumir que es un carrier disponible en Argentina. Mantener en observación hasta que el proveedor confirme país, servicio, cuenta y documentación |

### Fuentes oficiales y técnicas

- Andreani Developers: https://developers.andreani.com/
- Correo Argentino PAQ.AR: https://www.correoargentino.com.ar/MiCorreo/public/paq-ar
- Manual/API PAQ.AR: https://www.correoargentino.com.ar/MiCorreo/public/img/pag/apiPaqAr-v2.pdf
- OCA Developers e-Pak: https://developers.oca.com.ar/epak.html
- Vía Cargo: https://viacargo.com.ar/
- Envíopack Developers: https://developers.enviopack.com.ar/
- Envíopack Tracking y webhook: https://developers.enviopack.com.ar/tracking
- AfterShip Vía Cargo: https://www.aftership.com/integrations/carriers/viacargo-ar
- AfterShip cuentas de transportistas: https://support.aftership.com/en/tracking/articles/15441457-how-to-connect-carrier-accounts
- 17TRACK transportistas: https://help.17track.net/hc/en-us/articles/37467353177753-Supported-carriers-and-carrier-codes
- 17TRACK Vía Cargo: https://www.17track.net/es/carriers/via-cargo
- Adquisición de Kangu por Mercado Libre: https://www.mercadolibre.com.ar/institucional/comunicamos/noticias/adquisicion-de-kangu

**Precisión importante:** una integración de tracking no permite crear un envío ni obliga al transportista a aceptar una carga. AfterShip/17TRACK se consideran servicios de visibilidad; Andreani/PAQ.AR/OCA y cualquier futura API directa son candidatos para ejecutar operaciones logísticas.

## 3. Arquitectura propuesta: un módulo logístico, adaptadores intercambiables

El módulo Logistics es propietario de los despachos, paquetes, tramos, guías y eventos de seguimiento. Ventas es propietario del pedido/venta; Inventario es propietario de los movimientos físicos; Finanzas es propietario de pagos, gastos y conciliación.

Cada transportista implementa un contrato común. Los métodos/capacidades no disponibles se declaran explícitamente, nunca se simulan:

- cotizar;
- reservar o crear envío;
- cancelar reserva/etiqueta;
- generar/descargar etiqueta;
- solicitar retiro;
- consultar sucursales/puntos;
- registrar manifiesto o despacho;
- consultar tracking;
- recibir webhooks;
- obtener prueba de entrega;
- gestionar logística inversa/reclamo cuando exista soporte.

Una capacidad puede tener estado supported, unsupported, account_required, manual_only o not_verified. La interfaz muestra solo acciones reales.

### Modalidades de fulfillment

1. Retiro por el comprador: turno, persona autorizada, preparación, código/firma y entrega.
2. Reparto propio: ruta, vehículo, chofer, paradas, costo por recorrido, intentos y prueba de entrega.
3. Carrier externo: booking, bultos, handoff, guía, eventos, reclamos y flete.
4. Agregador: cotización/booking/tracking mediante una API intermediaria, conservando siempre el operador físico final cuando se informe.

## 4. Ciclo de vida y tracking posterior a la venta

1. Pedido confirmado y venta registrada sin exigir guía.
2. Fulfillment creado y cantidades reservadas.
3. Picking, packing y pesaje/medición de bultos.
4. Cotización y elección del servicio, si se utiliza integración directa o agregador.
5. Booking/etiqueta/guía, cuando el operador la emite.
6. Handoff físico al carrier o retiro por el comprador.
7. Recepción de eventos de seguimiento por webhook o consulta controlada.
8. Entrega, excepción, rechazo, devolución o reclamo.

La guía puede quedar vacía en el pedido y en la venta. Se incorpora al Shipment con fecha, operador, servicio y usuario/sistema que la registró. Un pedido puede originar varios shipments; cada uno puede tener distintos carriers, guías y estados.

## 5. Modelo común de eventos

Cada evento de tracking debe guardar:

- tenant/entidad legal y referencia interna del envío;
- transportista y cuenta comercial utilizada;
- identificador externo del envío y número de guía;
- código y descripción originales del proveedor;
- estado normalizado de Rubrova y subestado;
- fecha/hora declarada por el transportista, zona horaria y fecha de recepción;
- ubicación/agencia cuando esté disponible;
- fuente: webhook, API, importación o carga manual;
- identificador del evento externo, correlación y hash del payload;
- resultado de validación, duplicado detectado y errores de procesamiento.

El historial es append-only. El estado actual es una proyección de eventos; los eventos tardíos o fuera de orden se conservan y reordenan según la fecha real sin borrar la evidencia original. Los webhooks repetidos son idempotentes.

Estados internos de referencia: label_pending, label_created, ready_for_handover, handed_over, in_transit, arrived_at_facility, out_for_delivery, delivery_attempt_failed, available_for_pickup, delivered, returned, lost/damaged y exception. El adaptador mantiene el estado original además del normalizado.

## 6. Webhooks, polling y contingencia

- Priorizar webhooks cuando el proveedor los ofrece.
- En Envíopack, su documentación advierte que no debe consultarse repetidamente el tracking del mismo envío mediante cron; se debe implementar la notificación envio-cambio-condicion.
- Cuando no haya webhook, usar polling con límites y backoff por operador, ventana temporal y estado.
- Respetar rate limits y cuotas; aplicar circuit breaker y reintentos con jitter.
- Enviar eventos no procesables a una cola de revisión, sin perder el payload original.
- Disponer de carga manual auditada para carriers sin API o para contingencias.
- Tener conciliación de shipments sin guía, guías desconocidas, entregas no confirmadas, tracking atrasado y diferencias entre pedidos y cantidades despachadas.
- Si una API está caída, no borrar la venta ni crear una segunda etiqueta al reintentar.

## 7. Costos logísticos y rentabilidad

Capturar flete cotizado, contratado y facturado por separado; seguro, valor declarado, adicionales, embalaje, retiro, reintentos, devoluciones y costos de reparto propio. Comparar presupuesto contra costo final y margen del pedido.

Distribuir costos de un viaje consolidado usando peso, volumen, bultos, pallets, cantidad o regla contractual. Guardar el método, base, versión y ajuste de redondeo. El costo asignado debe conciliar exactamente con el gasto original.

Métricas: costo por envío/pedido/kg/m³/parada; entrega a tiempo; primer intento exitoso; demora entre venta, preparación, booking y handoff; incidencias; costo de devoluciones; margen luego de logística; rendimiento por carrier, zona y área de negocio.

## 8. Proyectos reutilizables y decisiones

| Proyecto | Licencia / estado | Uso posible | Decisión |
|---|---|---|---|
| nchsala/andreani | MIT, Node/TypeScript, wrapper antiguo | Ejemplos de autenticación, cotización, órdenes y trazas Andreani | Inspeccionar tests y actualizar contra API oficial; no copiar sin pruebas |
| YamilEzequiel/correo-argentino | MIT, TypeScript, wrapper MiCorreo | Cotización, token, agencias y shipping/import | Candidato de adaptación; verificar que endpoints y modelos coincidan con API actual |
| esnim/CorreoArgentino | Sin LICENSE raíz localizada | Ejemplo PHP de cotización PAQ.AR | Solo referencia; no copiar hasta aclarar licencia y actualidad |
| ombulabs/oca-epak | MIT, Ruby/Savon, wrapper SOAP | Tarifas, operación, órdenes de retiro y funciones e-Pak | Útil como referencia; stack Ruby no obliga a adoptarlo |
| teosibileau/py-oca-epak | MIT, Python | Centros, regiones, servicios y tracking OCA SOAP | Útil como referencia de contratos SOAP |
| YipiApp/carriers-of-argentina-for-woocommerce | GPL-2.0 declarado, requiere WooCommerce y membresía Cujiware | Une cotización de Correo, Andreani, OCA y sucursales; etiquetas Andreani/OCA | Inspeccionar como referencia de flujos; dependencias comerciales y licencia limitan su uso como módulo autónomo |

Repositorios:
- https://github.com/nchsala/andreani
- https://github.com/YamilEzequiel/correo-argentino
- https://github.com/esnim/CorreoArgentino
- https://github.com/ombulabs/oca-epak
- https://github.com/teosibileau/py-oca-epak
- https://github.com/YipiApp/carriers-of-argentina-for-woocommerce

La presencia de un wrapper no prueba que sea compatible con la versión actual de la API del transportista. Fijar commit, revisar dependencias, autenticación, tests, tratamiento de errores y documentación vigente antes de reutilizar.

## 9. Prioridad de implementación

1. Contrato de dominio Logistics y Shipment independiente de la venta.
2. Carga manual + seguimiento manual auditado, para cubrir cualquier carrier desde el comienzo.
3. Andreani y PAQ.AR como primeras integraciones directas, sujetas a credenciales de QA.
4. OCA e-Pak como siguiente adaptador directo, sujeto a cuenta/código operativo.
5. Envíopack como candidato de agregación; solicitar transportistas y funcionalidades habilitadas.
6. Comparar AfterShip y 17TRACK para seguimiento de Vía Cargo y otros operadores sin API directa.
7. Investigar Kangu solo cuando se confirme una operación/servicio aplicable a Argentina.

**No se declara ninguna integración activa.** La fase de prueba requiere credenciales de sandbox, números de guía de prueba, etiquetas, webhooks y evidencia de conciliación.
