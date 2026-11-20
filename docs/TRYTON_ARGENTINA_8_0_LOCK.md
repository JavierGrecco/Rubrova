# Conjunto argentino Tryton 8.0 — referencias fijadas para laboratorio

**Revisión:** 20 de noviembre de 2026  
**Estado:** candidato documentado y fijado por commit; no instalado ni aprobado funcionalmente.  
**Objetivo:** probar una plataforma POS/ERP con localización argentina sin mezclar ramas ni depender de `master`.

## 1. Decisión de evaluación

Se encontró un conjunto coherente de ocho ramas `8.0` en la organización `tryton-ar`. Los manifiestos declaran versiones 8.0.0 o 8.0.1 y los repositorios contienen tests. Esto permite probar primero Tryton 8.0 con localización argentina, en vez de empezar con los manifiestos actuales de `master` (que pueden pertenecer a otras series).

**Tryton 8.2** es una release oficial posterior, pero este conjunto argentino está preparado para la serie 8.0. No actualizar el servidor a 8.2 mientras se mantengan los módulos 8.0: primero se deberá portar o conseguir un conjunto equivalente para 8.2, ejecutar tests y repetir homologación fiscal.

## 2. Repositorios fijados

| Orden sugerido | Módulo | Rama / versión del manifiesto | Commit fijado | Licencia | Función |
|---:|---|---|---|---|---|
| 1 | [account_ar](https://github.com/tryton-ar/account_ar/tree/8.0) | 8.0 / 8.0.0 | `303ce82cb70a09892a18a15c776b20a0fb7f84c9` | GPL-3.0 | Plan contable argentino, impuestos y configuración contable |
| 2 | [party_ar](https://github.com/tryton-ar/party_ar/tree/8.0) | 8.0 / 8.0.0 | `3f10d1561706956af84f048a85aa284dfbacca3b` | GPL-3.0 | Entidades, CUIT, condición fiscal y consulta de padrón |
| 3 | [bank_ar](https://github.com/tryton-ar/bank_ar/tree/8.0) | 8.0 / 8.0.0 | `e583d927a40df6469b92ecd08dd277b55ad8e296` | GPL-3.0 | Datos bancarios argentinos, bancos y CBU |
| 4 | [account_invoice_ar](https://github.com/tryton-ar/account_invoice_ar/tree/8.0) | 8.0 / 8.0.1 | `09f4ba30af276f072cc0854f8b677375b25e65f1` | GPL-3.0 | WSFE/WSFEX, facturación electrónica, FCE, certificados y recuperación |
| 5 | [account_voucher_ar](https://github.com/tryton-ar/account_voucher_ar/tree/8.0) | 8.0 / 8.0.0 | `1f6817ca3a723ff48afabc0043e7b14e7cacb260` | GPL-3.0 | Recibos, pagos y modos de cobro/pago |
| 6 | [account_check_ar](https://github.com/tryton-ar/account_check_ar/tree/8.0) | 8.0 / 8.0.0 | `10e86cb5f545b24a84caf8bf8052d973c3dd8046` | GPL-3.0 | Cheques propios y de terceros, depósito, rechazo y reversión |
| 7 | [account_report_ar](https://github.com/tryton-ar/account_report_ar/tree/8.0) | 8.0 / 8.0.1 | `ae991abbada72f4e07297e1d2f0ef4ed2a496816` | GPL-3.0 | Subdiarios, reportes contables y exportaciones fiscales |
| 8 | [sale_pos_ar](https://github.com/tryton-ar/sale_pos_ar/tree/8.0) | 8.0 / 8.0.0 | `fe9251415c754b46ecfd9ea14bbfab46fba109e1` | GPL-3.0 | Vincula el punto de venta fiscal con la venta y la factura |
| Auxiliar | [pyafipws](https://github.com/tryton-ar/pyafipws) | rama `main` | `8c5d75f661e4e13d631d485cf239549a44a884f3` | LGPL-3.0 | Cliente y utilidades de Web Services argentinos |
| Build | [hatch-tryton-ar](https://github.com/tryton-ar/hatch-tryton-ar) | rama `main` | `0ee98f8a38ea567b5716ebad743334da6b514dfd` | MIT | Hook de build/dependencias para los paquetes tryton-ar que lo declaran |

Los SHA son referencias de inspección del 20/11/2026. Antes de instalar, volver a verificarlos contra GitHub y guardar los artefactos y checksums descargados en el laboratorio.

## 3. Dependencias funcionales importantes

- `account_ar` depende de módulos oficiales de contabilidad.
- `party_ar` amplía entidad, compañía y dirección; incluye los identificadores argentinos.
- `bank_ar` depende de la base bancaria oficial y `party_ar`.
- `account_invoice_ar` depende de `account_ar`, `account_invoice`, `bank_ar` y `party_ar`.
- `account_voucher_ar` depende de `party_ar`, `account_ar` y `account_invoice`.
- `account_check_ar` depende de `bank_ar`, `account_voucher_ar` y `account_ar`.
- `account_report_ar` depende de `party_ar` y `account_invoice_ar`.
- `sale_pos_ar` depende de `sale` y `account_invoice_ar`.

El módulo oficial **`sale_point`** es la interfaz POS minorista de Tryton: registra venta/devolución, medio de pago, vuelto y sesión; al contabilizar afecta stock y contabilidad. **`sale_pos_ar` es otro módulo**: añade el punto de venta fiscal a la venta y lo traslada al comprobante. Deben probarse ambos, con sus dependencias oficiales 8.0.

## 4. Cobertura de pruebas encontrada en el código

- `account_invoice_ar`: escenarios de factura electrónica, factura sin período, factura electrónica FCE, exportación WSFEX, factura de proveedor y recuperación de factura electrónica.
- `party_ar`: scenario de entidad y pruebas de módulo.
- `account_ar`: pruebas de módulo y escenarios contables.
- `account_voucher_ar`: escenario de recibos/vouchers y pruebas de módulo.
- `account_check_ar`: pruebas de módulo y escenarios de operaciones con cheques.
- `account_report_ar`: escenarios CITI y subdiarios, con fixtures de compras/ventas y alícuotas.
- `sale_pos_ar`: escenario de venta con punto de venta fiscal y pruebas de módulo.

La presencia de tests es evidencia favorable, no una aprobación. Es necesario ejecutarlos en un entorno limpio, con las versiones exactas de Tryton 8.0, módulos oficiales 8.0, PostgreSQL y dependencias.

## 5. Secuencia de instalación para el laboratorio

1. Preparar una VM o entorno aislado con la versión de Python/PostgreSQL compatible con Tryton 8.0. No usar información real ni certificados productivos.
2. Fijar y registrar la versión del servidor, cliente, módulos oficiales y PostgreSQL.
3. Crear el entorno Python aislado; instalar el conjunto de módulos oficiales 8.0 que requieren los módulos argentinos.
4. Descargar los ocho repositorios de la tabla desde sus commits fijados, no desde `master`.
5. Instalar dependencias de build y auxiliares con versiones fijadas. Inspeccionar los requisitos de `pyafipws` y `hatch-tryton-ar`; no seguir URLs móviles sin registrar el SHA real.
6. Ejecutar los tests de cada módulo y la activación conjunta sobre una base vacía.
7. Configurar una empresa y CUIT ficticios, plan contable, impuestos, bancos, punto de venta y certificados exclusivos de homologación.
8. Probar el ciclo catálogo → venta POS → medio de pago/vuelto → movimiento de stock → documento fiscal → asiento → reporte.
9. Probar anulaciones permitidas, notas de crédito, estados inciertos, recuperación de factura, pagos/cheques y exportaciones.
10. Guardar logs sin credenciales, versiones, SHAs, resultados, duración, problemas y pasos reproducibles.

No se debe marcar aprobado un módulo sólo porque se instaló. El set completo debe pasar el circuito POS/ERP, conciliación y homologación.

## 6. Riesgos y decisiones pendientes

- Los módulos Tryton comparten servidor y base; no se convierten automáticamente en servicios independientes. La prueba debe comprobar si pueden encapsularse dentro de una unidad de dominio sin absorber las autoridades que Rubrova mantendrá separadas.
- La documentación pública histórica de tryton-ar conserva referencias de instalación antiguas (incluso Tryton 3.0). La referencia para esta prueba es el código/manifest de cada rama 8.0, sus dependencias y tests.
- La integración de AFIP/ARCA no se habilita en producción hasta probar certificados, WSAA, WSFE/WSFEX, numeración, respuesta incierta, consultas de recuperación y normativa vigente en homologación.
- El repositorio `pyafipws` declara LGPL-3.0; cada módulo argentino declara GPL-3.0. Mantener avisos y revisar compatibilidad de licencias y dependencias.
- Tryton 8.2 es posterior. Cualquier actualización requiere versiones compatibles de todos los módulos argentinos, migraciones, suite completa de tests y nueva homologación; no actualizar sólo el servidor.

## 7. Resultado esperado

Esta prueba responde una pregunta concreta: ¿Tryton 8.0 más su localización argentina reduce sustancialmente el trabajo POS/ERP/fiscal y puede convivir con la arquitectura de servicios independientes de Rubrova? Si no supera integración, experiencia de caja, límites de datos, recuperación o homologación, se conserva como referencia de código/funcionalidad y se descarta como plataforma de adopción.
