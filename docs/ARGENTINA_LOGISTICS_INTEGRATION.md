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

Se revisaron repositorios, licencias declaradas, package manifests y actividad pública al 20/11/2026. La madurez y el grado de actualización varían bastante:

| Proyecto | Evidencia verificada | Valor posible | Decisión |
|---|---|---|---|
| [nchsala/andreani](https://github.com/nchsala/andreani) | MIT; paquete npm `@nchsala/andreani@1.0.2`; último push 24/10/2020. El README declara métodos de cotización, alta de órdenes domicilio/sucursal, búsqueda, trazas, sucursales y etiquetas. Depende de axios 0.21 y TypeScript 4.0.3. | Referencia valiosa de contratos y métodos para Andreani API v1/v2; reduce el trabajo de relevar nombres y modelos. | **No adoptar directamente.** Revisión de 2020: contrastar métodos y payloads contra la documentación oficial vigente, actualizar dependencias y ejecutar pruebas reales en sandbox. |
| [YamilEzequiel/correo-argentino](https://github.com/YamilEzequiel/correo-argentino) | MIT; paquete `ylazzari-correoargentino@0.1.0`; último push observado 04/07/2026 y actualización de repo 13/11/2026. El README declara registro/autenticación, validación de usuario, cotización, sucursales y alta/importación de envíos; soporta ambiente TEST y PROD. Requiere credenciales MiCorreo. El package manifest no define un script de tests. | Es el wrapper argentino más prometedor de esta revisión para acelerar la integración MiCorreo/PAQ.AR. | **Candidato a prueba acotada.** Fijar commit/tag, verificar el paquete publicado contra el código actual, agregar tests automatizados y contrastar cada endpoint con el manual oficial; usar credenciales TEST. |
| [esnim/CorreoArgentino](https://github.com/esnim/CorreoArgentino) | PHP; último push 10/08/2024; no se localizó LICENSE raíz. Su README declara únicamente cotización y advierte que el modo de pruebas puede no funcionar. | Ejemplo de payload y flujo de cotización. | **Sólo referencia.** No copiar código hasta aclarar licencia y validar la implementación contra PAQ.AR vigente. |
| [ombulabs/oca-epak](https://github.com/ombulabs/oca-epak) | MIT; Ruby/Savon; último push 29/11/2019. Tiene pruebas RSpec/VCR para credenciales, tarifas, retiro, etiquetas y tracking. El README distingue e-Pak y un endpoint OEP antiguo. También explica que el código de operativa debe habilitarlo OCA. | Referencia de contratos SOAP, estructura de operaciones, retiro y respuestas. | **No adoptar directamente.** Antiguo; usar como ejemplo para contrastar WSDL/servicios vigentes y requisitos de cuenta. |
| [teosibileau/py-oca-epak](https://github.com/teosibileau/py-oca-epak) | MIT; Python >=3.11; último push 01/03/2026. Tiene tests de geografía, tracking, etiquetas, QR, parsing y manejo de errores. Su `pyproject.toml` declara como homepage/repository `drkloc/py-oca-epak`, distinto del repositorio actual; esa procedencia debe aclararse. | Puede adelantar cliente SOAP Python y pruebas de tracking/etiquetas. | **Candidato condicionado.** Resolver la referencia de upstream/procedencia, fijar commit y validar WSDL y credenciales actuales de OCA. |
| [YipiApp/carriers-of-argentina-for-woocommerce](https://github.com/YipiApp/carriers-of-argentina-for-woocommerce) | README del plugin: GPLv2, versión estable 1.5.8, última actividad 14/08/2026; requiere WooCommerce y una membresía Cujiware paga. Declara cotización Correo/Andreani/OCA, selección de sucursales y etiquetas Andreani/OCA; Correo exige pasos adicionales. | Referencia de flujos multi-carrier de una tienda WooCommerce y de sus requisitos comerciales. | **No es un módulo autónomo.** Útil para observar flujos; no incorporar dependencias de WooCommerce/Cujiware ni asumir licencia/funciones fuera de su paquete. |

### Hallazgos de la búsqueda de repositorios

- La búsqueda dirigida no devolvió repositorios específicos y mantenidos de Vía Cargo ni de Kangu Argentina. Para Vía Cargo seguimos con la integración de tracking de AfterShip/17TRACK como opción a probar, no con una API propia confirmada. Para Kangu no se asume servicio argentino.
- Karrio aporta un marco multi-carrier y conectores internacionales, pero el árbol comunitario inspeccionado no contiene conectores para Andreani, PAQ.AR, OCA ni Vía Cargo.
- Para Andreani, Correo Argentino y OCA sí hay wrappers comunitarios, pero ninguno sustituye la documentación oficial ni la habilitación de cuenta. El wrapper MiCorreo más reciente es la primera prueba a priorizar; el wrapper Andreani más antiguo debe modernizarse; los wrappers OCA necesitan verificar WSDL, operativas y pruebas actuales.
- No surgieron repositorios públicos específicos y mantenidos para integrar directamente Tango, Catedral, Bejerman, Xubio o Colppy en esta búsqueda. Mantener exportación/importación por formatos oficiales como ruta inicial, y desarrollar adaptadores sólo cuando se reciban layouts/versiones y credenciales de prueba.

**Repositorios revisados:**
- https://github.com/nchsala/andreani
- https://github.com/YamilEzequiel/correo-argentino
- https://github.com/esnim/CorreoArgentino
- https://github.com/ombulabs/oca-epak
- https://github.com/teosibileau/py-oca-epak
- https://github.com/YipiApp/carriers-of-argentina-for-woocommerce

La presencia de un wrapper no demuestra compatibilidad con la versión actual de la API. Fijar commit, revisar dependencias, autenticación, tests, tratamiento de errores y documentación oficial antes de reutilizar.

## 9. Prioridad de implementación

1. Contrato de dominio Logistics y Shipment independiente de la venta.
2. Carga manual + seguimiento manual auditado, para cubrir cualquier carrier desde el comienzo.
3. Andreani y PAQ.AR como primeras integraciones directas, sujetas a credenciales de QA.
4. OCA e-Pak como siguiente adaptador directo, sujeto a cuenta/código operativo.
5. Envíopack como candidato de agregación; solicitar transportistas y funcionalidades habilitadas.
6. Comparar AfterShip y 17TRACK para seguimiento de Vía Cargo y otros operadores sin API directa.
7. Investigar Kangu solo cuando se confirme una operación/servicio aplicable a Argentina.

**No se declara ninguna integración activa.** La fase de prueba requiere credenciales de sandbox, números de guía de prueba, etiquetas, webhooks y evidencia de conciliación.
