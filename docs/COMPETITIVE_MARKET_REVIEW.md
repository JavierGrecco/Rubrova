# Revisión competitiva: Rubrova frente al mercado

**Revisión:** 20 de noviembre de 2026  
**Estado:** análisis documental de funciones públicas; no equivale a pruebas funcionales de los productos comparados ni a una decisión de adopción.

## 1. Conclusión ejecutiva

Rubrova plantea una visión más amplia que un POS: un núcleo POS+ERP con varias áreas, canales, perfiles sectoriales, inventario, compras, administración, fiscalidad argentina, reportes y analítica comercial. Esa amplitud es valiosa como dirección, pero **no demuestra una ventaja competitiva por sí sola**: el repositorio contiene especificaciones, datasets sintéticos y pruebas de reglas, no una aplicación operativa.

El mercado ya ofrece buena parte de lo que definimos:
- POS offline/híbrido, ventas y stock multidepósito;
- compras, cuentas corrientes, caja, turnos y reportes;
- ventas por cliente/producto/canal y exportaciones Excel;
- CRM, segmentación, fidelización y automatización de campañas;
- ERP multiempresa, fabricación y contabilidad.

Por eso no conviene competir por cantidad de módulos ni reconstruir todo. La estrategia de mayor probabilidad de éxito es adoptar un núcleo POS+ERP maduro y concentrar Rubrova en las brechas que importan: datos históricos confiables desde la primera operación, visión transversal del cliente, análisis por marca/segmento y contribución real, demanda ajustada por disponibilidad, control local de los datos y exportación completa.

## 2. Comparación de opciones reales

Las capacidades de esta tabla están documentadas por sus proveedores o documentación oficial. Los límites relativos se señalan como hipótesis a probar, no como fallos confirmados.

| Opción | Fortalezas documentadas | Encaje con Rubrova | Qué falta comprobar |
|---|---|---|---|
| **Tango Gestión + Tango Live** | ERP argentino modular; stock multidepósito, doble unidad, fraccionamiento, partidas/series, mermas, valorización, promedio ponderado, última compra/reposición, rentabilidad bruta y reportes multidimensionales; Tango Live ofrece pivots, consultas propias, compartir informes y navegar hasta comprobantes. | Referencia fuerte de profundidad administrativa, costos e informes para Argentina. | Coste total por módulos/usuarios, APIs realmente habilitadas, exportación masiva, POS de caja, integración omnicanal, historial de dimensiones y respaldo/restauración independiente. |
| **Contabilium** | ERP en la nube y una app POS separada para Windows; la app permite comprobantes sin conexión y sincroniza después. Documenta ranking de clientes, saldos, cobranzas pendientes, ventas por integración/canal y productos por cliente; reportes de stock y rentabilidad con histórico de costo. | Referencia directa de POS con continuidad offline y análisis por cliente/producto. | El POS tiene coste adicional; la documentación informa hasta tres ventas simultáneas. Verificar el alcance offline de todos los flujos, APIs/exports completos, multiárea y cuánto depende la gestión principal de la nube. |
| **Dux Software** | POS, ventas, compras, stock multidepósito, tesorería, portal de clientes, catálogo online, picking e integraciones ecommerce. Publica informes de ventas por cliente con última venta y total, y exportación a Excel. | Muy buen benchmark para comercio, distribución y venta omnicanal en Argentina. | Profundidad de contabilidad/producción, operación completamente local, backup portable, acceso a API y detalle histórico exportable. No asumir offline total sin prueba. |
| **Alegra POS** | POS, facturación argentina, turnos/caja, inventario en varios almacenes, vendedores, actualizaciones masivas e informes de ventas/stock. Planes con límites por usuarios, depósitos, puntos de venta y documentos. | Referencia de simplicidad de uso y puesta en marcha para comercios pequeños. | Alcance de gestión avanzada, APIs/exports, operación local real, trazabilidad histórica y analítica de cliente/marca. |
| **Fudo** | Especializado en gastronomía: mesa, mostrador, clientes, cuentas corrientes, comandas, KDS, delivery, recetas/ingredientes, mermas y reportes históricos a Excel por hora/día/canal/medio de pago, productos, stock y compras. | Referencia de experiencia sectorial para rotisería, panadería y gastronomía. | No es un ERP general para mayorista, distribución, servicios y múltiples áreas. La profundidad de CRM y perfil histórico por marcas debe verificarse. |
| **Maxirest One** | POS local que continúa sin internet, sincronizado con gestión/reportes/indicadores centralizados en nube; módulos de ventas, compras, stock, caja, bancos, personal, informes, ecommerce, KDS e IA según plan. | Referencia de POS híbrido y vertical gastronómico con back-office amplio. | La gestión y los informes dependen de conexión/nube. Revisar propiedad/uso de datos y términos de IA: los términos actuales contemplan uso agregado/anonimizado de datos operativos para entrenar/mejorar funciones del proveedor. |
| **Commercy** | Suite orientada al comercio online y omnicanal con POS, inventario, clientes, segmentos/audiencias, campañas, pipeline, finanzas, cuentas corrientes y B2B según plan; anuncia asistentes de IA conectados por MCP. | Referencia para CRM comercial, ecommerce y automatización de campañas. | Profundidad real de ERP/contabilidad, operación offline/local, exportación completa, licencia de conectores/modelos y tratamiento de datos por servicios externos. |
| **Odoo 19** | Suite modular con CRM, ventas, inventario, contabilidad, ecommerce, POS y automatización de marketing/segmentación; multiempresa y reportes consolidados. El plan comercial actual sitúa on-premise, API externa y multi-company en Custom. | Benchmark importante de amplitud ERP, CRM y marketing automation. | Coste real de Custom/Enterprise, diferencias Community/Enterprise, localización y emisión ARCA, integraciones locales, backup/restore y prueba POS/offline. No se incorpora automáticamente a la primera ronda. |
| **ERPNext 16** | Suite de código abierto con grupos jerárquicos de clientes, defaults de listas/precios/plazos/crédito, reportes de ventas por cliente/grupo/producto/vendedor/territorio, clientes inactivos/adquisición, gross profit y programa de fidelización por niveles. | Uno de los candidatos más completos para comprobar el núcleo integrado y una base CRM/BI reutilizable. | POS real en hardware local, experiencia táctil y velocidad, offline, localización Argentina/ARCA, calidad de migración y exportación íntegra. |
| **Tryton 8.0 + módulos argentinos** | Núcleo modular; el conjunto revisado agrega piezas contables/fiscales argentinas, pagos, bancos y punto de venta. | Candidato para un ERP adaptable con mayor control técnico y localización cercana. | Instalar los ocho módulos juntos, tests, homologación ARCA, POS de mostrador, experiencia, CRM y reportes cliente; esfuerzo de adaptación/mantenimiento. |
| **MyCompany 6.2 / lsFusion** | Suite integrada con Retail POS y amplitud de CRM, ventas, compras, inventario, fabricación y facturación; extensiones mediante módulos. | Candidato importante para evitar construir un ERP propio desde cero. | Profundidad argentina/ARCA, informes cliente y exportación, backup/restore, experiencia POS, licencias y costo de mantener extensiones. |
| **Dolibarr 24 / Posnic 1.9.2** | Dolibarr aporta ERP/CRM modular y API; Posnic sirve como referencia de POS local. | Alternativas de filtro, no la apuesta principal de plataforma. | Flujo completo de caja, integración argentina, robustez offline, datos de cliente y recuperación. |

## 3. Qué significa la comparación

### Donde los sistemas existentes ya son fuertes

1. **Operación comercial probada:** ventas, stock, caja, turnos, compras, clientes y comprobantes ya están resueltos en muchos productos.
2. **Argentina:** Tango, Contabilium, Dux y Alegra parten de una realidad fiscal y comercial local; intentar replicar todo eso desde cero sería caro.
3. **Verticales:** Fudo y Maxirest son ejemplos de que gastronomía necesita mesas, comandas, cocina, recetas, merma y delivery integrados; una pantalla genérica de venta no alcanza.
4. **Reportes básicos:** exportar Excel, ranking de productos, ventas por cliente, rentabilidad por producto y stock son capacidades existentes.
5. **CRM:** Odoo y ERPNext demuestran que segmentación, grupos de clientes, fidelización y marketing pueden integrarse al ERP.

### Dónde Rubrova puede aspirar a ser mejor

- **Perfil 360 unificado:** la misma persona/empresa vista a través de mostrador, web, WhatsApp, mayorista, distribución y servicios, sin duplicar operaciones.
- **Preferencias de marca y categoría:** medir primeras, segundas, económicas y propias en unidades, frecuencia, ingresos y ganancia, ajustando por quiebres de stock y presentaciones comparables.
- **Rentabilidad por cliente:** no sólo cuánto compra, sino cuánto contribuye después de costo real, comisiones, descuentos, devoluciones, embalaje y logística.
- **Inteligencia temporal:** conocer qué se vendió, cuándo se recibió, cuánto tiempo estuvo disponible, qué precio y promoción regían y qué pasó con las marcas competidoras.
- **Datos exportables de verdad:** CSV/XLSX para el usuario y Parquet/JSON con relaciones, diccionario, filtros y fórmulas para análisis avanzado o IA.
- **Control y recuperación local:** no depender de un servicio externo para seguir operando o acceder a los datos esenciales; backups restaurables y verificables en otra PC.
- **Una sola verdad operativa:** usar el ERP para ventas, stock, pagos y contabilidad, evitando libros paralelos o dashboards que inventan números.

Estas son ventajas potenciales. Para convertirlas en ventajas reales necesitamos construirlas y medirlas con operaciones reproducibles.

## 4. Brechas del proyecto actual

| Área | Situación de Rubrova hoy | Prioridad |
|---|---|---|
| POS y caja | Requisitos definidos; sin software ejecutable | Crítica |
| ERP, compras e inventario | Modelo y selección en investigación; sin plataforma probada | Crítica |
| Fiscalidad argentina | Módulos y SDK investigados; homologación no realizada | Crítica |
| Perfil 360 cliente | Identidad y dimensiones básicas; falta módulo de análisis y RFM/retención | Alta, capturar datos desde el inicio |
| Marcas y preferencia | Segmentación comercial y demanda diseñadas; datos reales inexistentes | Alta, capturar datos desde el inicio |
| Reportes | Métricas y stack analítico propuestos; aún no hay dashboard funcional | Alta, reportes operativos mínimos desde la primera entrega |
| Backup/restore | Estrategia especificada; no implementada | Crítica antes de producción |
| Omnicanal | Modelo e integraciones estudiadas; conectores pendientes | Media, primero pedidos y referencias |
| Producción/gastronomía | Recetas, lotes, merma y flujos modelados; sin prueba funcional | Posterior al núcleo |
| Distribución/logística | Modelo y transportistas estudiados; conectores pendientes | Posterior |
| IA/forecasting | Benchmark sintético aprobado; no hay modelos con datos reales ni IA integrada | Posterior a datos fiables |

## 5. Decisiones recomendadas

1. Mantener ERPNext, MyCompany y Tryton como principales pruebas de núcleo; incluir Tango, Contabilium y Dux como referencias de mercado y posibles destinos/integraciones, no necesariamente como código reutilizable.
2. Hacer un filtro funcional de Odoo por CRM/marketing y localización argentina; sólo reabrirlo como candidato profundo si demuestra una ventaja significativa y un costo/plan aceptable.
3. No intentar ganarle a Fudo/Maxirest en gastronomía antes de tener el POS/ERP general funcionando. Usarlos como referencias para perfiles de panadería/rotisería.
4. Adoptar la ficha 360 cliente, RFM, retención, marcas y contribución como un módulo analítico propio que consume hechos conciliados del núcleo.
5. Diseñar desde el inicio el identificador de cliente, área, canal, sucursal, formato, cajero, producto, marca/segmento, precio/costo, disponibilidad y pagos; el análisis se construye después.
6. Priorizar exportación abierta y reproducible sobre dashboards decorativos. El usuario debe poder trabajar con sus datos en Excel/LibreOffice, DuckDB y herramientas externas.
7. No convertir la amplitud del roadmap en una lista de funciones para desarrollar simultáneamente. Primero el circuito POS, ERP básico y recuperación; luego rentabilidad y CRM; después sectoriales/canales.

## 6. Criterio de comparación reproducible

Toda afirmación de marketing debe convertirse en prueba:
- instalar y operar con un conjunto idéntico de datos sintéticos;
- ejecutar ventas, compras, recepción parcial, devolución, pago mixto, cierre y recuperación;
- reconstruir un mismo cliente a través de canales;
- medir reporte de ventas, margen y preferencias de marca;
- exportar los datos y reproducir el cálculo en una herramienta externa;
- probar actualización, permisos, offline y restore.

No se selecciona plataforma por puntuación de una tabla documental. Una función se declara disponible sólo cuando está probada en la versión y plan que realmente usaríamos.

## Fuentes oficiales y de producto consultadas

- [Tango Gestión — Stock](https://www.axoft.com/tango/software-de-gestion/soluciones/stock.php) y [Tango Live](https://www.axoft.com/tango/software-de-gestion/soluciones/live.php).
- [Contabilium — POS sin conexión](https://ayuda.contabilium.com/hc/es/articles/360061319994--Qu%C3%A9-es-Contabilium-Punto-de-Venta), [reportes de gestión](https://ayuda.contabilium.com/hc/es/articles/1500003345382-Reportes-de-gesti%C3%B3n), [reportes de productos](https://ayuda.contabilium.com/hc/es/articles/360061803714-Reportes-de-productos).
- [Dux — funcionalidades](https://duxsoftware.com.ar/funcionalidades), [informes de clientes](https://ayuda.duxsoftware.com.ar/es/articles/9000590-informes-de-clientes-en-dux).
- [Alegra Argentina — POS](https://www.alegra.com/argentina/punto-venta/).
- [Fudo — funcionalidades](https://fu.do/es-ar/funcionalidades/) y [planes](https://fu.do/es-ar/precios/).
- [Maxirest One — términos y funcionamiento híbrido](https://maxirest.com.ar/terminos-y-condiciones/).
- [Commercy — gestión y CRM](https://commercy.com.ar/).
- [Odoo 19 — CRM](https://www.odoo.com/documentation/19.0/es/applications/sales/crm.html), [automatización de marketing](https://www.odoo.com/documentation/19.0/es_419/applications/marketing/marketing_automation.html), [multiempresa](https://www.odoo.com/documentation/19.0/applications/general/multi_company.html) y [planes](https://www.odoo.com/pricing).
- [ERPNext — grupos de clientes](https://docs.frappe.io/erpnext/customer-group), [reportes de ventas](https://docs.frappe.io/erpnext/sales-analytics), [fidelización](https://docs.frappe.io/erpnext/loyalty-program), [ventas](https://docs.frappe.io/erpnext/selling).
- [Ley 25.326 — texto actualizado](https://www.argentina.gob.ar/normativa/nacional/ley-25326-64790/actualizacion) y [AAIP — obligaciones de responsables](https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones).

Fuentes consultadas el 20/11/2026. Versiones, planes, límites y licencias deben volver a verificarse al instalar. La descripción pública de una función no reemplaza una prueba en el laboratorio.
