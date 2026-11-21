# Herramientas y componentes adicionales — evaluación del 20 de noviembre de 2026

## Criterio

No vamos a incorporar proyectos completos porque tengan muchas funciones. Rubrova ya reutiliza MyCompany 6.2 para el POS y el ERP. Una segunda plataforma comercial generaría maestros, inventarios, pagos, saldos y reglas duplicadas.

La prioridad es reutilizar bibliotecas pequeñas y maduras en los límites donde agregan calidad: pruebas reales de fallos, conectores externos, fiscalidad argentina y observabilidad. Cada componente debe tener versión fijada, licencia identificada, pruebas reproducibles y una razón concreta para entrar.

## Incorporado ahora: Toxiproxy para pruebas de fallos de red

**Proyecto:** [Shopify Toxiproxy](https://github.com/Shopify/toxiproxy)  
**Versión fijada en CI:** 2.13.0  
**Licencia:** MIT  
**Uso:** exclusivamente en el stack temporal de CI; no forma parte del runtime del usuario.

Toxiproxy permite interponer un proxy TCP entre Rubrova y un servicio simulado y manipular la conexión desde una API HTTP. Entre sus fallos reproducibles están la demora, pérdida de paquetes, cierre/reset de conexión y retención de datos hasta que el cliente agote su propio timeout.

El smoke test ahora usa dos caminos aislados hacia el simulador local:

- **Camino normal:** verifica respuestas HTTP 408, 429 y 503 y luego una recuperación exitosa.
- **Camino con respuesta retenida:** Toxiproxy descarta las respuestas sin cerrar inmediatamente la conexión. Rubrova debe salir por su timeout de 1 segundo, capturar el error y registrar la incidencia, sin derribar el servidor.

La API de administración sólo se publica en `127.0.0.1:18474` durante CI. El contenedor se elimina junto con la base temporal al finalizar la prueba. El digest de la imagen AMD64 está fijado para que el test no cambie silenciosamente al actualizarse la etiqueta.

Esta mejora fortalece las pruebas de errores de red; no demuestra por sí sola el funcionamiento de todos los proveedores ni sustituye las pruebas de idempotencia, Outbox o conciliación.

## Componentes seleccionados para el siguiente salto

| Proyecto | Licencia / tecnología | Valor para Rubrova | Decisión |
|---|---|---|---|
| [Resilience4j](https://github.com/resilience4j/resilience4j) | Apache-2.0, Java | Circuit breaker, retry, rate limiter, bulkhead y time limiter; permite combinar sólo los patrones necesarios | **Candidato principal** para el futuro límite Java de integraciones. Probar compatibilidad, estado persistente y métricas antes de fijar una versión. No copiar una máquina de estados propia si una biblioteca probada cubre el caso |
| [Testcontainers for Java](https://github.com/testcontainers/testcontainers-java) | MIT, Java/JUnit | Bases PostgreSQL desechables, servicios auxiliares y navegadores aislados para pruebas de integración | Incorporar cuando tengamos pruebas Java sobre persistencia, migraciones y ledgers. El smoke actual ya usa Compose; no sumar dos mecanismos para el mismo test |
| [ARCA SDK](https://github.com/ralcorta/arcasdk) | MIT, TypeScript | Paquetes para WSAA, facturación WSFE, WSFEX, CAEA, padrón, FCE, QR y errores tipados | **Referencia de implementación fiscal argentina**. Auditar fuentes, dependencias, contratos, certificados y estados inciertos. Por estar escrito en TypeScript no se añade todavía como proceso residente al runtime Java de Rubrova |
| [Apache Camel](https://github.com/apache/camel) | Apache-2.0, Java | Catálogo amplio de conectores y patrones de integración; la rama LTS 4.22 declara compatibilidad con Java 21 | Mantener en evaluación. Puede ahorrar trabajo si muchos conectores repiten lógica, pero es más infraestructura de la que necesitamos para empezar. Preferir primero una biblioteca pequeña y límites de módulo claros |
| [Tryton 8.2](https://docs.tryton.org/8.2/) | GPL-3.0, Python | Fuente de comparación para ventas, stock, compras, contabilidad y flujos de devolución | Actualizar la investigación sobre el lock argentino 8.0 y comparar cambios concretos. No incorporar una segunda aplicación ni duplicar los ledgers |
| [ERPNext 16.60](https://github.com/frappe/erpnext) | GPL-3.0, Python | Referencia viva de procesos comerciales, permisos y contabilización de devoluciones | Estudiar reglas y pruebas, no importar módulos completos: MyCompany ya cubre el núcleo. Revisar además las consecuencias de licencia antes de copiar código |

## Patrones concretos que vamos a tomar como referencia

- **Idempotencia fiscal:** consultar el estado de una emisión incierta antes de repetirla; reintentar consultas, no volver a emitir un comprobante a ciegas.
- **Devoluciones:** excluir el vuelto ya entregado del importe a reintegrar, vincular la devolución con la venta original y controlar importes por medio de pago.
- **Permisos:** aplicar autorización tanto al documento como a sus relaciones (cuenta, depósito, artículo, cliente/proveedor y sucursal); no confiar sólo en que un formulario o selector oculte registros.
- **Resiliencia:** separar circuit breaker, reintentos, límite de concurrencia y timeout. La política común no debe permitir que un fallo de Mercado Libre bloquee el POS local ni otros proveedores.

## Qué no se incorpora todavía

No agregamos ERPNext, Tryton, Camel ni un motor de workflows como segunda plataforma en producción. Tampoco introducimos un proceso Node sólo para hablar con ARCA antes de demostrar que un adaptador Java no cubre los contratos requeridos.

No se habilita una integración real hasta validar homologación, seguridad de certificados, tiempos máximos, clasificación de errores, idempotencia, estados inciertos, auditoría y recuperación.

## Orden de integración

1. Cerrar la jornada POS completa: búsqueda, carrito, precio, pago mixto, vuelto, venta, stock, devolución y cierre conciliados.
2. Construir el límite Java de integraciones y probar Resilience4j en un módulo pequeño con Toxiproxy; persistir Outbox y estados en Rubrova, no en un servicio externo.
3. Implementar y homologar ARCA con comprobantes de prueba antes de habilitar emisión real.
4. Consolidar compras, costos y stock; recién entonces activar reportes y analítica sobre datos transaccionales conciliados.
5. Incorporar canales y logística después del núcleo comercial y administrativo.

## Fuentes verificadas

- [Toxiproxy: repositorio, licencia y documentación de fallos TCP](https://github.com/Shopify/toxiproxy)
- [Toxiproxy: contenedor 2.13.0 y digests publicados](https://github.com/Shopify/toxiproxy/pkgs/container/toxiproxy)
- [Resilience4j: patrones de tolerancia a fallos y licencia Apache-2.0](https://github.com/resilience4j/resilience4j)
- [Testcontainers Java: pruebas con PostgreSQL y otros servicios desechables](https://github.com/testcontainers/testcontainers-java)
- [ARCA SDK: documentación y paquetes TypeScript](https://arca-sdk.dev/)
- [Tryton 8.2: notas de versión de ventas](https://docs.tryton.org/8.2/modules-sale/releases.html)
- [ERPNext: versión 16.60.0 y cambios de POS/devoluciones](https://github.com/frappe/erpnext/releases)
- [Apache Camel: releases LTS y compatibilidad Java](https://camel.apache.org/download/)
