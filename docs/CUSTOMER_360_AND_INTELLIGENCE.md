# Perfil 360 del cliente e inteligencia comercial

**Revisión:** 20 de noviembre de 2026  
**Estado:** especificación funcional para la evaluación de plataforma y diseño; no hay CRM ni analítica por cliente implementados en Rubrova.

## 1. Objetivo

Rubrova debe conocer la relación comercial completa con cada cliente sin convertir cada compra de mostrador en un trámite. El dueño debe poder abrir una ficha y comprender qué compra esa persona o empresa, con qué frecuencia, qué marcas y categorías elige, cuánto aporta a la facturación y a la ganancia, por qué canal compra, qué condiciones utiliza, qué reclamos tuvo y qué oportunidades comerciales existen.

La ficha no será sólo un formulario de datos personales. Será una vista temporal que reúne operaciones verificadas, preferencias declaradas, métricas calculadas e hipótesis predictivas claramente separadas.

## 2. Identidad sin duplicaciones ni identificaciones forzadas

### Tipos de relación

- **Consumidor anónimo:** ventas sin identificar; no crear un cliente ficticio por cada ticket.
- **Cliente minorista identificado:** persona que decide asociar compras a su ficha o programa de fidelización.
- **Cuenta empresa/B2B:** una organización con CUIT u otro identificador pertinente, varias sedes, contactos y roles de compra.
- **Cliente de servicios:** persona/empresa con contratos, órdenes de trabajo, SLA, horas, materiales y renovaciones.
- **Cliente compartido entre áreas:** una sola identidad con relaciones comerciales diferenciadas para minorista, mayorista, ecommerce, distribución o servicios.

Un mismo cliente puede tener varios domicilios, sucursales, contactos y usuarios autorizados. En B2B separar comprador, solicitante, aprobador, administración/cuentas a pagar, receptor y responsable operativo.

### Resolución de identidad

Conservar IDs internos estables y referencias de origen por canal. Normalizar CUIT, teléfono y correo, pero nunca fusionar dos clientes sólo por similitud de nombre. Los candidatos a duplicado deben revisarse; una fusión aprobada conserva los IDs anteriores, el motivo, el usuario y la fecha.

Vincular una venta al cliente cuando la identificación sea válida. No inferir identidad de un comprador anónimo por dispositivo, dirección IP o coincidencia débil. Si una venta anónima se asocia luego a una cuenta con evidencia suficiente y autorización, conservar el vínculo y su historial de auditoría.

## 3. Contenido de la ficha 360

### Identificación y contexto

- tipo de cliente y relación comercial;
- nombre/razón social, CUIT sólo cuando corresponda, contactos y sedes;
- fecha de alta, origen/canal de adquisición si se conoce y responsable comercial;
- áreas de negocio en las que opera;
- sucursales, territorios y canales utilizados;
- clasificación comercial estable, grupo, segmento y condiciones vigentes;
- preferencias declaradas (contacto, entrega, horario, idioma si corresponde);
- estado de consentimiento y oposición por finalidad y canal.

### Historia de compra

- primera compra, última compra y línea temporal completa;
- pedidos, ventas, presupuestos, facturas, notas de crédito, devoluciones y pagos;
- productos, variantes, marcas, segmentos comerciales y categorías compradas;
- cantidades y unidades normalizadas, presentaciones, frecuencia y regularidad;
- precio y descuento realmente aplicados, promociones y vigencias;
- canal, sucursal, cajero/vendedor, área, fecha y hora;
- preferencias de pago observadas, sin guardar datos sensibles de tarjetas;
- entregas, retiros, envíos, reclamos, incidencias y resolución;
- saldo, límite, vencimientos, cobranzas y comportamiento de pago, según permisos.

### Resumen económico

Mostrar por separado:
- ventas brutas, descuentos, devoluciones y ventas netas;
- costo real de mercadería/servicio y margen bruto;
- comisiones, costo de servir, embalaje, logística y otros costos variables;
- contribución del cliente y gastos compartidos asignados bajo política explícita;
- cuentas por cobrar, importes cobrados, pendientes y mora;
- rentabilidad por área, canal, producto, categoría y marca.

Nunca usar facturación como sinónimo de valor del cliente. Un comprador con mucho volumen y descuentos altos puede aportar menos contribución que otro con menor facturación.

## 4. Segmentación y métricas

Las segmentaciones deben ser configurables, reproducibles y fechadas. El usuario puede crear grupos con reglas y ver qué datos hacen que cada cliente pertenezca a ellos.

### RFM y ciclo de vida

- **Recency:** días desde última compra válida.
- **Frequency:** número de pedidos/ventas y frecuencia de recompra en ventana definida.
- **Monetary:** importe neto, y por separado contribución/margen en el mismo período.

Segmentos candidatos: nuevo, activo, frecuente, leal, alto valor, prometedor, ocasional, en riesgo de inactividad, inactivo y recuperado. No fijar umbrales universales: permitir períodos y percentiles por actividad/sector. Calcular siempre sobre ventas confirmadas netas de anulaciones y devoluciones, con reglas documentadas para pagos parciales y operaciones a crédito.

RFM es una señal descriptiva, no un diagnóstico de personalidad ni una predicción causal. Mostrar período, fecha de cálculo, umbral y datos que sustentan la categoría.

### Preferencias comerciales

Calcular:
- categorías, productos, marcas y segmentos más elegidos por unidades, frecuencia, ventas netas y contribución;
- participación de primera/líder, segunda, económica, propia y alternativas dentro de cada categoría;
- tamaño/presentación y precio comparable preferidos;
- sensibilidad observada a cambios de precio y promociones, únicamente cuando haya suficiente muestra y comparaciones razonables;
- canal, sucursal, horario, día de semana y modalidad de cumplimiento más utilizados;
- compras recurrentes, tiempo típico entre compras y productos que suelen adquirirse juntos;
- sustituciones aceptadas cuando falta stock y productos rechazados, si se registran expresamente.

No confundir "marca más comprada" con preferencia si otra marca estuvo agotada. Separar observación de inferencia y mostrar cantidad de operaciones, período, cobertura y confianza.

### Retención y valor futuro

- cohortes por mes/estación de primera compra;
- tasa de repetición y retención por cohortes;
- intervalos entre compras y cambio de frecuencia;
- clientes nuevos, recurrentes, recuperados y perdidos;
- valor de vida del cliente (CLV) basado primero en contribución histórica, no sólo facturación;
- CLV futuro o probabilidad de recompra como estimaciones con horizonte, rango y error de backtesting;
- clientes concentrados en una sola categoría/marca/canal y oportunidades de diversificación comercial.

Los clientes B2B requieren además recurrencia por sede, volumen contratado vs consumido, pedidos completos/parciales, condiciones de crédito, plazos de pago, cumplimiento y rentabilidad después de costos de entrega/servicio.

## 5. Recomendaciones accionables

Rubrova podrá proponer, sin ejecutar automáticamente:
- reposición o recordatorio de productos recurrentes cuando el intervalo esperado se haya excedido;
- productos complementarios basados en cestas reales y compatibilidad comercial;
- sustitutos equivalentes cuando un SKU esté agotado;
- ofertas pertinentes por categoría/marca y margen disponible;
- recuperación de clientes inactivos mediante campañas autorizadas;
- cambio de lista, escala mayorista o condición comercial para revisión;
- atención prioritaria ante reclamos pendientes, mora o entregas incompletas.

Cada recomendación muestra evidencia, regla/modelo, fecha de cálculo, impacto estimado, margen esperado, stock disponible, supuestos y confianza. Descuentos, precios, crédito y mensajes necesitan autorización según rol y política.

## 6. Privacidad y uso responsable

El historial transaccional necesario para administrar una relación comercial se mantiene separado del permiso para enviar comunicaciones promocionales. Registrar finalidad, aviso informado, fecha/fuente, versión del texto y preferencias por correo, WhatsApp, SMS u otros canales. Una baja en marketing no borra documentos que deban conservarse por obligaciones comerciales/fiscales, pero bloquea el uso promocional pertinente.

No recopilar ni inferir datos sensibles (salud, religión, política, afiliación sindical, sexualidad, origen étnico). No deducir vulnerabilidad económica, estado de salud o características personales a partir de productos comprados. No usar perfiles automáticos como única base de decisiones perjudiciales sobre crédito, precio o acceso; ofrecer revisión humana y explicación de las reglas.

Aplicar minimización por finalidad, exactitud, plazos de retención, control de acceso, exportación de los datos del titular y procesos de rectificación/actualización/supresión cuando legalmente correspondan. La ficha completa se muestra según rol; cajeros no necesitan ver notas financieras o datos personales no necesarios para vender.

El tratamiento debe revisarse bajo la Ley 25.326 y las guías vigentes de AAIP. La aplicación debe facilitar el cumplimiento, pero no declarar por sí misma que el negocio está exento de inscripción u otras obligaciones.

## 7. Datos de origen obligatorios

El perfil depende de que las áreas operativas capturen:
- ID de cliente o indicador explícito de venta anónima;
- pedido/venta y sus líneas, estados y cancelaciones;
- SKU, marca/segmento, categoría, presentación y unidad histórica;
- fechas de evento, registro y fecha comercial;
- área, canal, sucursal, vendedor/cajero y campaña;
- precio, descuento, impuesto, devolución y costo/valuación;
- disponibilidad y quiebres de stock;
- pagos, intentos, reintegros, liquidaciones y deuda;
- entregas, reclamos, satisfacción o resolución cuando se registren;
- fuente, permiso y preferencia de comunicación.

La especificación completa de captura está en [Captura de datos y base analítica](DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md).

## 8. Presentación y exportación

La interfaz propone:
1. **Resumen:** perfil, segmento vigente, valor económico, última compra y alertas.
2. **Preferencias:** categorías, marcas, productos, presentaciones y canales, con base muestral.
3. **Actividad:** línea temporal de ventas, pagos, entregas, reclamos y devoluciones.
4. **Economía:** ventas, costos, contribución y cuentas corrientes.
5. **Retención:** cohortes, RFM, recompra, inactividad y CLV estimado.
6. **Acciones:** recomendaciones pendientes, campañas autorizadas y seguimiento.

Permitir exportar el perfil autorizado y sus datos fuente en CSV/XLSX/JSON/Parquet. Cada exportación declara fecha de corte, filtros, definiciones, granularidad, IDs y cobertura. Las notas internas y datos de otros clientes nunca se incluyen por accidente.

## 9. Pruebas de aceptación para plataformas

- **P58 — Cliente 360 multicanal:** una cuenta única aparece correctamente en local, online, WhatsApp, mayorista y servicios sin duplicar compras; las ventas anónimas permanecen anónimas.
- **P59 — Preferencias, RFM y rentabilidad:** obtener productos/marcas/categorías preferidas, RFM, frecuencia, retención y contribución neta reproducibles, controlando devoluciones, promociones y quiebres de stock.
- **P60 — Privacidad y gobierno del perfil:** demostrar permisos por rol, historial y finalidad de datos, preferencias de marketing por canal, baja promocional, acceso/exportación y corrección, además de evitar atributos sensibles/inferencias prohibidas.

## Estado

La ficha 360 y las métricas propuestas amplían el alcance CRM/BI y deben evaluarse en el núcleo POS+ERP antes de desarrollarlas. No constituyen capacidades ya implementadas.
