# Investigación de mercado y oportunidades adicionales

**Revisión:** 19 de noviembre de 2026  
**Estado:** investigación documental y recomendaciones para el backlog. No representa funcionalidades implementadas ni integraciones contratadas.

## 1. Qué problema debe resolver Rubrova

Rubrova no debe competir por cantidad de pantallas. Debe permitir que una organización entienda y controle el recorrido completo de su actividad:

- captar una consulta, cotización, pedido o venta;
- validar precios, disponibilidad, crédito y condiciones;
- reservar y mover inventario;
- preparar, entregar o despachar;
- cobrar, conciliar y emitir o vincular el comprobante fiscal;
- registrar compras, gastos, pagos y costos;
- entregar al contador información consistente;
- conocer qué área, sucursal, canal, producto, contrato o cliente genera margen y consume caja.

El diferencial debe ser la continuidad de punta a punta: los errores entre sistemas externos tienen que quedar visibles, recuperables y conciliables. Una integración que se limita a sincronizar cuando todo funciona no es suficiente.

## 2. Evidencia y límites de la investigación

### Adopción digital

La encuesta nacional de nadIA, con apoyo del BID y la Fundación Observatorio PyME, relevó 402 empresas industriales y de software entre noviembre y diciembre de 2025. Entre las empresas encuestadas, el 77,5% pagaba al menos una tecnología digital; el promedio fue de 2,26 tecnologías pagas por firma. Por categoría: nube 53,9%, comunicación digital 52,5%, ERP/facturación 48,1%, e-commerce/marketing 28,6% y logística 10,1%.

La encuesta muestra una brecha entre la adopción de herramientas de gestión y la contratación de soluciones logísticas especializadas. No es correcto extrapolar estos porcentajes a todos los comercios, servicios o empresas argentinas: la muestra se concentra en industria y software/servicios informáticos.

Fuentes:
- https://nadia.ar/investigacion/encuesta-pymes.html
- https://nadia.ar/extras/nadia_encuesta_pymesARG2026.pdf

### Problemas relatados por negocios

Las conversaciones públicas sirven para descubrir escenarios de prueba, no para estimar prevalencia:

- Una PyME que vende en Mercado Libre, prepara Tienda Nube y abrirá un local relató en octubre de 2026 que una falla de sincronización dejó más de 200 ventas sin facturar durante una semana. La enseñanza para Rubrova no es juzgar al proveedor mencionado, sino exigir bandejas de errores, conciliación entre plataformas y recuperación sin duplicar comprobantes.
- Otros relatos consultados en comunidades de negocios mencionan inventarios extensos sin código ni ubicación, dificultad para calcular margen real, necesidad de conectar ventas minoristas y mayoristas, problemas con plazos de cobro y falta de visibilidad sobre stock y compras.

Fuentes:
- https://www.reddit.com/r/NegociosArgentina/comments/1wzw2pp/sistema_erp/
- https://www.reddit.com/r/NegociosArgentina/comments/1sid1i0/tengo_una_ferreter%C3%ADa_con_10000_productos_en_un/
- https://www.reddit.com/r/NegociosArgentina/comments/1tzwagz/c%C3%B3mo_manejan_los_m%C3%A1rgenes_en_sus_negocios_fisicos/
- https://www.reddit.com/r/NegociosArgentina/comments/1uz8b2e/sistema_de_gesti%C3%B3n/

Un artículo de un proveedor argentino de software, basado en su propia experiencia comercial con clientes, identifica problemas reiterados de stock descontrolado, falta de información en tiempo real, diferencias de caja y dependencia de una persona. Es una observación útil para generar casos de prueba, pero no una fuente independiente ni una encuesta representativa.

Fuente:
- https://bcnsoft.com.ar/blog/observatorio-bcnsoft-problemas-gestion-pymes/

## 3. Necesidades que conviene convertir en capacidades reales

### A. Caja, pagos y continuidad

- Venta rápida con lector, teclado o pantalla táctil.
- Efectivo exacto, vuelto, pagos mixtos y anticipos.
- Cuenta corriente, límites de crédito, cobranzas parciales y promesas de pago.
- Estado de pago separado del estado de venta y del comprobante fiscal.
- Conciliación de terminal, PSP, transferencia, banco, comisiones, retenciones y liquidación.
- Bandeja de operaciones dudosas: por ejemplo, timeout después de que una terminal pudo haber aprobado el cobro.
- Caja y reportes que sigan disponibles durante una caída de Internet.

### B. Inventario y abastecimiento

- Código interno propio aunque el proveedor no informe GTIN.
- Importación masiva, detección de duplicados y normalización de nombres, medidas y presentaciones.
- Ubicaciones físicas: depósito, zona, pasillo, estante, nivel y posición.
- Unidades de compra, almacenamiento y venta con conversiones controladas.
- Stock disponible, reservado, en preparación, en tránsito, dañado y comprometido.
- Lotes, series, vencimientos, FEFO y trazabilidad de retiros.
- Conteos cíclicos ABC, diferencias autorizadas y trazabilidad de ajustes.
- Punto de pedido, stock de seguridad, lead time, mínimo de compra y sugerencias explicables.
- Recepción parcial, faltantes, sustituciones y devolución al proveedor.

### C. Costo, precio y margen

No usar un porcentaje único de markup como sustituto del costo real. El usuario debe poder comparar costo promedio, última compra, costo de reposición y costo puesto en depósito.

El costo de una venta debe poder explicar:
- costo de mercadería y su método de valuación;
- flete de compra, seguro y gastos de ingreso distribuidos mediante reglas;
- comisión del canal y del medio de pago;
- embalaje, preparación y logística;
- descuento, bonificación, devolución y merma;
- impuestos y conceptos que correspondan según el reporte y la configuración.

La simulación de precios y promociones debe mostrar el efecto en contribución y margen antes de aplicar cambios. Guardar el costo vigente al momento de la operación para no reescribir la historia cuando sube el precio del proveedor.

### D. Tesorería y capital de trabajo

- Flujo de caja diario, saldos conciliados y movimientos pendientes.
- Cuentas por cobrar y pagar con vencimientos, aging y responsables.
- Proyección móvil de 13 semanas con escenarios de cobro tardío, menores ventas y cambios de costos.
- Liquidaciones futuras de medios de pago, retenciones y comisiones.
- Comparación entre caja prevista y real.
- Alertas de compromisos que vencen y clientes que exceden su límite.
- Separación visual entre dinero disponible, cobros probables y escenarios.

### E. Migración e incorporación

El primer uso no debería exigir una carga manual de miles de artículos. El proceso debe:
1. admitir CSV/XLSX y formatos documentados de otros sistemas;
2. mostrar hojas, columnas y tipos detectados;
3. sugerir equivalencias con catálogo, proveedor, cliente, unidad y ubicación;
4. normalizar CUIT, códigos, fechas, importes y unidades sin perder el original;
5. identificar duplicados, datos ausentes y valores ambiguos;
6. generar una previsualización y simulación sin escritura;
7. aplicar un lote idempotente con informe fila por fila;
8. conservar un identificador de lote y permitir reversión controlada si no existen operaciones dependientes posteriores.

### F. Información y decisiones

- Reportes globales y por unidad, sucursal, canal, depósito, cliente, producto, vendedor, proyecto y contrato.
- Definición, fuente, período y fecha de actualización de cada indicador.
- Acceso desde el total hasta las operaciones que lo explican.
- Exportación XLSX/CSV y envío programado.
- Identificación de datos faltantes y cobertura: no mostrar margen como exacto cuando falta el costo de un artículo.
- Pronósticos con comparación contra un baseline y resultados reales, nunca como hechos confirmados.

## 4. Adaptación a distintas actividades

Mantener un solo núcleo de ventas, compras, pagos, inventario, personas, permisos y auditoría. La actividad se configura con paquetes de procesos, campos y pantallas; no con forks del modelo.

| Perfil configurable | Capacidades particulares |
|---|---|
| Comercio minorista, kiosco, almacén y ferretería | Caja rápida, fiados, códigos internos, variantes, stock por ubicación, precios y reposición |
| Supermercado y autoservicio | Cajas múltiples, balanzas, PLU, pesables, lotes, vencimientos, promociones y conteos |
| Panadería, pastelería y gastronomía | Recetas, ingredientes, tandas, rendimiento, mermas, comandas, cocina y encargos |
| Mayorista y distribuidora | Listas por cliente, mínimos, múltiplos, escalas, crédito, preparación, reparto y envíos parciales |
| E-commerce y venta omnicanal | Pedidos externos, catálogo por canal, reserva coordinada, fulfillment, tracking y conciliación |
| Manufactura y taller | BOM/recetas, órdenes de producción, materiales, partes, consumos, costos, mano de obra y control de calidad |
| Servicios y operaciones de campo | Contratos, SLA, agenda, órdenes de trabajo, técnicos, materiales, viáticos y aceptación |
| Alquileres y servicios recurrentes | Activos, disponibilidad, reservas, entrega/devolución, garantías, contratos y cargos periódicos |

No intentar desarrollar todos los paquetes en la primera entrega. El asistente de configuración debe permitir combinar actividades, activar capacidades después y conservar los datos comunes.

## 5. Proyectos y soluciones que merecen atención

Los proyectos se evalúan por dominio y no se ejecutan simultáneamente como autoridades paralelas de ventas, caja, contabilidad o stock.

### InvenTree

- Repositorio: https://github.com/inventree/InvenTree
- Documentación: https://docs.inventree.org/
- Licencia raíz: MIT.
- La documentación describe stock, ubicaciones jerárquicas, proveedores, partes, serialización, listas de materiales, builds, API REST y plugins.
- La documentación de releases consultada indica InvenTree 1.7.3 publicado el 17/11/2026.
- Recomendación: candidato de laboratorio para inventario de componentes, manufactura ligera, trazabilidad y API. No asumir que su modelo de partes/BOM sustituye a un catálogo retail completo ni convertirlo en segundo dueño del stock de Rubrova.

### OpenBoxes

- Repositorio: https://github.com/openboxes/openboxes
- Funcionalidad: https://openboxes.com/features/
- Licencia del repositorio: Eclipse Public License 1.0.
- Cubre ubicaciones, lotes/series, vencimientos, proveedores, órdenes de compra, recepciones parciales, stock history, conteos cíclicos, FEFO, picking, packing, shipping e importaciones.
- Recomendación: referencia WMS de alto valor para estudiar flujos físicos, conteos y abastecimiento. Su especialización y despliegue pueden ser excesivos para el comercio chico; evaluar sólo si la operación de depósitos lo justifica.

### OpenWMS.org

- Repositorio: https://github.com/openwms/org.openwms
- La raíz publica Apache-2.0, pero la familia tiene componentes con disponibilidad y licencias diferentes.
- Recomendación: estudiar conceptos de warehouse execution y control de materiales. No incorporar un subproyecto hasta verificar la licencia y el mantenimiento de ese componente exacto.

### Dolibarr

- Repositorio: https://github.com/Dolibarr/dolibarr
- Funciones: https://www.dolibarr.org/
- La release estable consultada es 24.0.3, publicada el 11/11/2026; 25 figura como beta/freeze, no como release estable.
- Combina CRM, pedidos, presupuestos, contratos, stock, compras, envíos, fabricación, POS, pagos, conciliación bancaria y contabilidad de doble partida.
- Recomendación: ampliar el laboratorio integral con Dolibarr 24.0.3 si su licencia, instalación, localización argentina y adaptación al POS/offline resultan razonables. No elegirlo sólo por amplitud funcional.

### Localización argentina de Odoo

- OCA: https://github.com/OCA/l10n-argentina
- Documentación oficial de Odoo 19: https://www.odoo.com/documentation/19.0/es/applications/finance/fiscal_localizations/argentina.html
- OCA mantiene una rama 19.0 bajo AGPL-3.0, pero la inspección actual del README y raíz no muestra todavía un catálogo de addons generado en esa rama. No afirmar que contiene módulos listos para integrar.
- La documentación oficial de Odoo 19 describe 'l10n_ar', 'l10n_ar_reports', 'l10n_ar_edi' y 'l10n_ar_withholding'.
- Recomendación: usar la localización oficial como referencia funcional y como prueba de una alternativa Odoo si se abre esa evaluación; revisar licencia y procedencia de cada módulo. No trasladar automáticamente código acoplado al ORM de Odoo al núcleo propio.

### PyARCA y SDKs fiscales

- PyARCA: https://github.com/GeraCollante/PyARCA
- ARCA oficial: https://www.arca.gob.ar/ws/documentacion/ws-factura-electronica.asp
- PyARCA es una CLI comunitaria derivada de PyAfipWs. Tiene interés como referencia Python y para probar escenarios de emisión, pero no es un servicio oficial de ARCA. Revisar su licencia y dependencias por archivo antes de incorporar.
- El catálogo de Rubrova ya contiene 'arca-sdks' como candidato TypeScript MIT; deben compararse ambos mediante contratos y pruebas de homologación, sin duplicar lógica fiscal.
- La documentación oficial ARCA publica manuales de 'wsfev1', 'wsmtxca' y otros servicios, así como certificados para homologación. La autorización debe respetar puntos de venta y correlatividad. Fuentes:
  - https://www.arca.gob.ar/ws/documentacion/ws-factura-electronica.asp
  - https://www.arca.gob.ar/fe/ayuda/webservice.asp
  - https://www.arca.gob.ar/ws/documentacion/certificados.asp
  - https://www.arca.gob.ar/fe/emision-autorizacion/solicitud-autorizacion.asp

### Referencias de soluciones comerciales

- Tango/Axoft: APIeCommerce, TangoDeltaApi, ApiClientes y servicios de Contabilidad. Cada API tiene alcance, versión, módulos y licencias propios. APIeCommerce requiere Tango Delta 6 o superior y puesta en marcha del producto eCommerce.
- Catedral: la evidencia pública respalda intercambio por archivos y Excel, pero no una API REST pública de desarrollador. Priorizar formatos de archivo verificables.
- Bejerman, Xubio y Colppy: estudiar los accesos y operaciones de API disponibles según plan, permisos y contrato.
- Asentia: referencia comercial para conciliación de extractos bancarios y exportación de asientos; estudiar la experiencia de revisión, no suponer código reutilizable.
- Correo Argentino PAQ.AR confirma sus APIs para integrar sistemas propios/ERP; exige registro y credenciales. Fuente: https://www.correoargentino.com.ar/MiCorreo/public/paq-ar
- ARCA mantiene manuales y entorno de homologación; no probar certificados reales dentro del laboratorio.

## 6. Prioridades recomendadas

| Prioridad | Capacidad | Razón de negocio | Criterio de aceptación |
|---|---|---|---|
| P0 | Centro de operaciones e integraciones | Detectar ventas, pedidos, pagos y facturas pendientes | Ningún evento externo desaparece; se concilia y reprocesa sin duplicar |
| P0 | Núcleo transaccional y recuperación local | Proteger cobro, caja y stock | Corte y reinicio sin pérdida de operaciones confirmadas |
| P0 | Exportación contable y conciliación | Trabajar con el contador y sistemas existentes | Lotes balanceados, mapeados, idempotentes y con acuse |
| P0 | Importación y migración asistida | Reducir tiempo y riesgo de cambio | Simulación, conflictos por fila y reversión controlada |
| P1 | Stock avanzado y reposición | Evitar faltantes, sobrantes y búsquedas manuales | Conteos, ubicación, vencimiento y sugerencia explicable |
| P1 | Costo de reposición y precios | Proteger rentabilidad | Simulación antes de autorizar cambios |
| P1 | Tesorería, cobranza y flujo 13 semanas | Anticipar necesidades de caja | Diferencia entre previsto, confirmado y real |
| P1 | Mayorista, reparto y logística unificada | Acelerar venta y cumplimiento | Pedido, despacho parcial, guía y tracking separados y conciliados |
| P2 | Archivo documental y OCR | Reducir carga administrativa | Original inmutable, extracción revisable y vínculo a operación |
| P2 | Automatización y BI avanzada | Reducir tareas repetitivas | Métricas correctas y automatizaciones auditables |

## 7. Decisiones de producto

1. No reducir Rubrova a POS ni convertir la investigación en una colección de microservicios.
2. Una sola autoridad por venta, caja, pago, inventario, comprobante fiscal y libro contable.
3. Diseñar primero perfiles contables y logísticos; habilitar conectores luego de confirmar versiones, licencias y credenciales.
4. Empezar por flujos que reduzcan errores y tiempo de trabajo: importación, escaneo, cobro, conciliación, reposición y reportes operativos.
5. Diferenciar lo confirmado de lo estimado y lo pendiente.
6. Medir el beneficio de cada módulo frente a su costo de instalación, soporte y actualización.

## 8. Próximas verificaciones

- Ejecutar el protocolo común sobre MyCompany, Posnic y ERPNext; sumar Dolibarr 24.0.3 sólo si hay capacidad para una prueba equivalente.
- Instalar InvenTree 1.7.3 y hacer una prueba acotada de ubicaciones, códigos, proveedores, BOM y API.
- Evaluar OpenBoxes con datos sintéticos sólo si InvenTree/gestión central no cubren picking, FEFO y cycle count.
- Obtener documentación concreta y credenciales de QA para operadores y proveedores contables.
- Confirmar con el contador los reportes y layouts que utiliza en el trabajo real.
- Confirmar versión, módulos, licencias y autoridad del dato antes de desarrollar cualquier adaptador.

La documentación y las versiones deben volver a verificarse antes de comenzar una integración: los proveedores y proyectos liberan cambios con frecuencia.
