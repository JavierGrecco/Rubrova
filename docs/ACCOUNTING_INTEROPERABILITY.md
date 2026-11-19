# Interoperabilidad contable y administrativa argentina

**Revisión:** 19 de noviembre de 2026  
**Estado:** arquitectura de integración y mapa de proveedores. Ningún conector está operativo ni homologado.

## 1. Principio de diseño

Rubrova debe poder trabajar con un sistema contable/administrativo existente sin obligar a reemplazarlo. La operación comercial y logística puede vivir en Rubrova, mientras el software contable mantiene los libros, los comprobantes y procesos fiscales que el dueño y su estudio contable ya utilizan.

Se separan:
- fuente operativa de pedidos, stock, fulfillment, contratos y servicio;
- sistema autorizado para emitir el comprobante fiscal;
- sistema que mantiene el libro contable y la liquidación;
- reportes de gestión propios de Rubrova.

Una factura, cobro o asiento nunca se duplica por sincronizar. La integración inicial será controlada y preferentemente unidireccional por tipo de documento. Los intercambios bidireccionales se habilitan únicamente cuando la propiedad del dato, el conflicto y la conciliación estén definidos.

## 2. Proveedores investigados

### Tango Gestión / Axoft

Encontramos varias superficies oficiales, con alcances diferentes:

- **TangoDeltaApi:** repositorio público de la organización verificada TangoSoftware. Su documentación muestra CRUD de clientes y consulta/alta de pedidos; algunos métodos PUT/DELETE de pedido no están disponibles en la documentación revisada. La sección de facturación de ventas figura como próxima, por lo que no debe presentarse como API completa de facturación.
- **APIeCommerce / Tango Tiendas:** API REST de integración e-commerce. El README oficial documenta ingreso de pedidos individuales o por lote de hasta 25 y consulta de artículos, clientes, precios, listas, stock, comprobantes y órdenes. Requiere licencia y módulos de Tango que deben confirmarse para la instalación concreta; incluye notificaciones para algunos eventos.
- **ApiClientes:** API de Nexo Clientes para entregar JSON de comprobantes electrónicos con CAE. La documentación indica Tango Gestión 18.01 o superior, configuración en Tango Sync y posibilidad de notificar a una URL cuando hay comprobantes nuevos.
- **Tango Contabilidad:** Axoft documenta operaciones de asientos contables vía API, además de importación masiva desde Excel y procesos de asientos. La disponibilidad de API depende de versión/abono y puede tener costo adicional.

Fuentes:
- https://github.com/TangoSoftware/TangoDeltaApi
- https://github.com/TangoSoftware/APIeCommerce
- https://github.com/TangoSoftware/ApiTiendas
- https://github.com/TangoSoftware/ApiClientes
- https://axoft.com/tango/software-para-estudios-contables/soluciones/contabilidad.php

**Decisión:** prioridad alta para interoperabilidad. Primero determinar versión, módulos, licencias, endpoints habilitados y dirección de sincronización del Tango concreto. No conectar directamente con tablas internas si existe una API o mecanismo oficial.

### Catedral Software

La información oficial describe un sistema multiusuario cliente-servidor, personalización de grillas/informes y exportación a Excel y otros formatos; también declara importación desde Excel y otros formatos de aplicación. Su oferta para empresas incluye ventas, compras, cuentas corrientes, precios y vigencias, stock por depósito/serie/partida, requisición por punto de pedido, subdiarios, impuestos y exportaciones a aplicativos.

La documentación pública muestra intercambio de comprobantes entre Gestión Integral de la Empresa y Gestión Integral del Estudio, con requisitos como plan de cuentas, conceptos, períodos, jurisdicciones y regímenes de retenciones/percepciones. No encontré un portal público de API para desarrolladores que permita prometer integración REST.

Fuentes:
- https://www.catedralsoft.com.ar/
- https://catedralsoft.com.ar/
- https://catedralsoft.com.ar/Home/Requirements
- https://catedralsoft.com.ar/Ads/SoftEmpresas
- https://catedralsoft.com.ar/Ads/SoftEstudios
- https://catedralsoftware.blogspot.com/2014/07/guia-simple-importacion-y-exportacion.html

**Decisión:** diseñar primero un perfil de archivos CSV/XLSX y los formatos concretos que el proveedor entregue. Solicitar a Catedral layouts actuales de exportación/importación, ejemplos anonimizados, catálogo de cuentas/conceptos y reglas de validación. No hacer lectura/escritura directa en su SQL Server sin soporte y contrato documentado.

### Bejerman ERP

Thomson Reuters publica una API abierta para desarrolladores y WebService; la API está disponible como adicional desde el plan Intermedio. El producto declara cobertura de facturación, stock, ventas, compras, finanzas, contabilidad, impuestos, producción y logística. Sus planes incorporan funciones como conciliación bancaria, queries/reportes a medida, trazabilidad de stock y módulos opcionales.

Fuentes:
- https://www.thomsonreuters.com.ar/es/c/software-de-gestion-bejerman-erp.html
- https://www.thomsonreuters.com.ar/es/productos/bejerman-erp.html

**Decisión:** candidato de alta prioridad como destino contable/administrativo adicional. Conseguir la especificación y una cuenta de prueba antes de implementar.

### Xubio

Xubio publica API REST 1.1 con documentación OpenAPI/Swagger y autenticación OAuth2 mediante Client ID y Secret ID. Los recursos documentados incluyen clientes, proveedores, productos, compras y ventas, facturación, cobranzas, órdenes de pago/compra, asientos manuales, cuentas, centros de costo, bancos, depósitos, impuestos, retenciones y percepciones.

La guía de facturación muestra que el alta de comprobante crea un borrador y que la autorización fiscal se realiza en otro paso mediante solicitarCAE. También documenta externalId para relacionar el comprobante con el sistema externo y rechazar duplicados. Las operaciones disponibles y límites dependen del plan.

Fuentes:
- https://main.xubio.com/API/documentation/index.html
- https://ayuda.xubio.com/es-ar/como-uso-api/
- https://ayuda.xubio.com/es-ar/como-creo-clientes-con-la-api/
- https://ayuda.xubio.com/es-ar/como-facturo-con-la-api/

**Decisión:** buen candidato para un adaptador REST completo, especialmente si se quiere enviar comprobantes y asientos, pero no hacer que Xubio facture y Rubrova facture el mismo hecho.

### Colppy

La documentación de ayuda deriva actualmente al portal de desarrolladores y declara operaciones para emitir comprobantes, sincronizar clientes/proveedores, registrar asientos e inventario. La referencia técnica se gestiona desde api.colppy.com y debe leerse allí, porque el centro de ayuda advierte que las guías externas pueden estar desactualizadas.

Fuentes:
- https://ayuda.colppy.com/es/articles/1335070-api-de-colppy
- https://api.colppy.com/

**Decisión:** candidato para un perfil REST después de revisar autenticación, operaciones, permisos y límites del plan.

### Asentia: conciliación bancaria como referencia funcional

Asentia es una solución comercial, no código abierto. Publica lectura de extractos PDF/escaneados/CSV/XLS/XLSX, conciliación contra el mayor y exportación de asientos en XLSX/CSV para Tango, Xubio, Colppy, Contabilium, Bejerman, Holistor, Odoo y otros destinos.

Fuente: https://www.asentia.io/

**Decisión:** no reutilizar como módulo; estudiar el flujo de conciliación y su interacción de revisión humana. Rubrova debe aspirar a conciliar movimientos bancarios, pagos de adquirentes, comisiones, retenciones, transferencias y asientos con trazabilidad.

## 3. Modelo canónico de intercambio

Rubrova no debe generar un formato distinto desde cada área. Primero arma un paquete contable canónico y después lo transforma mediante un perfil por destino.

Cada lote incluye:
- entidad legal, CUIT, ejercicio, período y fecha de corte;
- tipo de documento, punto de venta, número, fecha, vencimiento y referencia externa;
- cliente/proveedor y su código en destino;
- cuenta contable, subcuenta, concepto y centro de costo;
- unidad de negocio/centro de beneficio, sucursal, canal, proyecto/contrato y área;
- neto gravado/no gravado/exento, alícuotas, IVA y otros tributos según el caso;
- retenciones, percepciones, jurisdicción y régimen cuando corresponda;
- moneda, cotización, importes, redondeos y signo;
- forma y fecha de cobro/pago, cuenta financiera, lote de tarjeta y comisiones;
- referencia al pedido, venta, compra, envío, contrato y documento de origen;
- externalId, clave de idempotencia y versión del mapeo.

El paquete puede generar:
1. detalle de comprobantes;
2. asientos individuales;
3. asientos resumen por fecha/cuenta/centro;
4. movimientos de caja y banco;
5. subdiarios de ventas/compras;
6. inventario y valorización;
7. cuentas corrientes y vencimientos;
8. archivos de intercambio en CSV, XLSX, XML o JSON según destino.

## 4. Seguridad de la exportación contable

Cada perfil de ERP define catálogo de cuentas, códigos de IVA/tributos, conceptos, centros de costo, tipos de comprobante, sucursales y mapeo de clientes/proveedores.

El proceso siempre pasa por:
1. preparar lote en borrador;
2. validar mapeos y período;
3. comprobar partida doble y redondeo;
4. detectar duplicados y documentos ya exportados;
5. mostrar previsualización y totales;
6. aprobación explícita;
7. generar archivo o llamar API;
8. guardar respuesta/acuse/rechazo;
9. conciliar totales, documentos y saldos;
10. emitir reversión o lote correctivo, nunca alterar silenciosamente un registro ya contabilizado.

No se marcan lotes como exportados solo porque el archivo se haya descargado; se distingue preparado, enviado, recibido, importado, contabilizado, rechazado y conciliado.

## 5. Reportes que Rubrova debería preparar

### Gestión económica
- Estado de resultados por unidad de negocio y consolidado.
- Margen bruto, contribución, costos directos y distribución de gastos compartidos.
- Ventas y márgenes por producto, SKU, cliente, segmento, vendedor, canal y sucursal.
- Compras, evolución de costo de reposición, costo puesto en depósito y variación de precios.
- Rentabilidad por pedido, envío, contrato, servicio, ruta y cliente.
- Punto de equilibrio, contribución marginal y escenarios de precio/volumen.

### Tesorería y capital de trabajo
- Caja diaria y cierres por terminal/turno.
- Bancos, movimientos pendientes y conciliación.
- Saldos de Mercado Pago/adquirentes y liquidaciones netas.
- Comisiones, retenciones, percepciones y diferencias de liquidación.
- Flujo de fondos proyectado, preferentemente con horizonte móvil de 13 semanas.
- Cuentas por cobrar/pagar vencidas y próximas a vencer.
- Aging por tramos configurables, promesas de pago, morosidad y riesgo de cliente.
- Capital de trabajo, ciclo de conversión de efectivo y brecha de cobro/pago.

### Impuestos y comprobantes para el estudio
- Ventas/compras por comprobante, cliente/proveedor, punto de venta y período.
- Bases imponibles y tributos por alícuota/categoría.
- Retenciones/percepciones sufridas y practicadas.
- Notas de crédito/débito y su vinculación con el comprobante origen.
- Exportación de comprobantes y reportes para el sistema contable.
- Diferencias entre ventas operativas, comprobantes fiscales, pagos y liquidaciones.

Estos reportes son auxiliares de gestión y preparación de información. No reemplazan los libros oficiales, las presentaciones fiscales ni la validación del contador.

### Inventario y costos
- Existencias y valorización por depósito, ubicación, lote/serie y fecha.
- Movimientos, ajustes, transferencias, mermas y diferencias de inventario.
- Rotación, antigüedad, stock inmovilizado, quiebres y faltantes.
- Costo promedio/última compra/costo de reposición, mostrando el método.
- Compras sugeridas, punto de pedido, stock de seguridad y lead time.
- Costo por fulfillment y logística.

## 6. Reglas de autoridad y sincronización

| Dato | Autoridad inicial propuesta | Sincronización |
|---|---|---|
| Pedido/fulfillment/envío | Rubrova | Hacia el ERP cuando corresponda |
| Cliente/proveedor | Maestro compartido con ID externo por sistema | Importación y conciliación con clave fiscal/código |
| Producto/SKU | Rubrova o ERP elegido, decidido por instalación | Mapeo de códigos y unidades |
| Stock operativo | Libro de inventario de Rubrova si se elige Rubrova como base | No mantener dos saldos editables sin un sistema maestro |
| Comprobante fiscal | Sistema que efectivamente lo emite y recibe autorización | Vincular por tipo, punto de venta, número, CAE y referencia externa |
| Libro contable | ERP/estudio contable designado | Exportar lotes conciliables; importar confirmación/saldos |
| Gestión de áreas y rentabilidad | Rubrova | Exportar dimensiones y conservar comparabilidad |

## 7. Pruebas de interoperabilidad obligatorias

- Mismo lote exportado dos veces: no duplica comprobantes ni asientos.
- Lote rechazado parcialmente: reintentar solo los documentos rechazados.
- Período contable cerrado: detener y explicar.
- Cliente/proveedor sin código o cuenta: mostrar mapeo pendiente.
- Impuestos/retenciones con código desconocido: no inventar equivalencias.
- Redondeos: débitos = créditos y totales de comprobantes conciliados.
- Nota de crédito: se vincula al documento original y revierte el hecho correcto.
- Multimoneda: conserva moneda, cotización y diferencia.
- Asiento resumen: conserva acceso al detalle operativo original.
- Cancelación/reversión: genera documento compensatorio y auditoría.
- Lote importado en Tango/Catedral/Bejerman/Xubio/Colppy: comparar totales, saldos, centros de costo y dimensiones.
- Backup de exportaciones, respuestas y archivos fuente.

## 8. Próximo paso

Solicitar a cada proveedor una versión y documentación concreta:
- Tango: release, módulos, licencia Tango Tiendas, API contable y entorno de prueba.
- Catedral: formatos exactos de exportación e importación empresa/estudio y un set anonimizado de archivos.
- Bejerman: documentación de API/WebService y plan que la habilita.
- Xubio y Colppy: credenciales sandbox/demo, recursos permitidos por plan y límites.
- Contador: plan de cuentas, conceptos, centros de costo, impuestos y formato de intercambio que realmente utiliza.

No desarrollar el conector de un ERP en base a nombres comerciales únicamente; la versión, licencia y esquema real deben quedar registrados.
