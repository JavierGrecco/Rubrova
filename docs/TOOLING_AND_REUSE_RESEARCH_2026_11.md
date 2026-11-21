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

La API de administración sólo se publica en `127.0.0.1:18474` durante CI. Además, CI genera un token bearer aleatorio para la ejecución, lo entrega al contenedor y lo utiliza en cada llamada a la API: el puerto limitado a loopback no sustituye la autenticación, porque otros contenedores de la red de pruebas podrían alcanzar el servicio. El token no se guarda en el repositorio ni en los registros. El contenedor se elimina junto con la base temporal al finalizar la prueba. El digest de la imagen AMD64 está fijado para que el test no cambie silenciosamente al actualizarse la etiqueta.

Esta mejora fortalece las pruebas de errores de red; no demuestra por sí sola el funcionamiento de todos los proveedores ni sustituye las pruebas de idempotencia, Outbox o conciliación.

## Componentes seleccionados para el siguiente salto

| Proyecto | Licencia / tecnología | Valor para Rubrova | Decisión |
|---|---|---|---|
| [Resilience4j 2.4.0](https://github.com/resilience4j/resilience4j) | Apache-2.0, Java 17+ | Circuit breaker, retry, rate limiter, bulkhead y time limiter; modular, permite sumar sólo los patrones necesarios | **Candidato principal** para el límite Java de integraciones. Probar compatibilidad con el runtime Java 21, estado del circuit breaker, métricas y comportamiento concurrente antes de fijar la versión. Los incidentes y la Outbox seguirán persistidos en Rubrova; no confiar en el estado en memoria de la biblioteca |
| [Testcontainers for Java 2.0.5](https://github.com/testcontainers/testcontainers-java) | MIT, Java/JUnit | PostgreSQL, servicios auxiliares y navegadores efímeros para pruebas de integración reproducibles | Adoptarlo para pruebas acotadas de persistencia, migraciones, conciliación y ledgers desde Java. La rama 2.0 cambia coordenadas y paquetes (por ejemplo, el módulo PostgreSQL usa `testcontainers-postgresql`), por eso se fijará y probará en un módulo nuevo, no se mezclará con el smoke Compose actual |
| [ARCA SDK `@arcasdk/core` 1.2.0](https://github.com/ralcorta/arcasdk) | MIT, TypeScript | SDK para Web Services de ARCA: autenticación, facturación electrónica, padrones, FCE y WSCT; paquete PDF separado `@arcasdk/pdf` | **Referencia fiscal prioritaria** para contrastar contratos, catálogos, errores SOAP, certificados y pruebas de homologación. El proyecto migró desde `afip.ts` al nombre `arcasdk`; no incorporar un proceso Node al runtime aún. Primero validar cobertura de servicios y casos argentinos reales, luego comparar un adaptador Java con el SDK |
| [Apache Camel 4.22.2 LTS](https://camel.apache.org/download/) | Apache-2.0, Java 17/21/25 | Catálogo de conectores y patrones de integración; LTS de octubre de 2026 con soporte publicado hasta agosto de 2027 | Mantener en evaluación. Puede ahorrar trabajo si muchos conectores repiten lógica, pero añade superficie y configuración para una aplicación local. Preferir Resilience4j y adaptadores pequeños hasta que una necesidad concreta justifique Camel |
| [Tryton 8.2](https://docs.tryton.org/8.2/) | GPL-3.0-or-later, Python | Referencia para ventas, stock, compras y contabilidad; 8.2 incorpora validaciones de tolerancia y variación de cantidad/costo en inventarios | **Referencia de reglas y pruebas**, no segunda aplicación. Comparar el inventario físico, las diferencias de costo y el cierre/apertura de períodos con los módulos MyCompany antes de diseñar extensiones propias |
| [ERPNext 16.60.0](https://github.com/frappe/erpnext/releases) | GPL-3.0, Python | Referencia de procesos comerciales; su release del 17 de noviembre incluye una corrección de devolución POS para excluir el vuelto ya entregado del importe reintegrado | Estudiar reglas y pruebas, no importar módulos completos: MyCompany ya cubre el núcleo. Usar esa corrección como caso de aceptación de Rubrova y revisar licencias antes de copiar cualquier código |

## Patrones concretos que vamos a tomar como referencia

- **Idempotencia fiscal:** consultar el estado de una emisión incierta antes de repetirla; reintentar consultas, no volver a emitir un comprobante a ciegas.
- **Devoluciones POS (ERPNext 16.60.0):** una venta de $1.250 con $1.500 entregados y $250 de vuelto debe generar una devolución máxima de $1.250, nunca de $1.500. La devolución debe partir de la factura original, repartir el reintegro por los medios realmente cobrados y revertir stock una sola vez.
- **Inventario (Tryton 8.2):** una toma física debe mostrar variación de cantidad y costo, permitir configurar tolerancias y exigir autorización cuando se excedan; el ajuste debe generar movimientos trazables y no modificar el historial de ventas.
- **Cierre de períodos (Tryton 8.2):** contrastar calendario, conciliación y cierre/apertura automáticos con el ejercicio contable de Rubrova; ninguna tarea programada debe cerrar un período con operaciones sin conciliar.
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

- [Toxiproxy: repositorio, licencia, autenticación bearer y documentación de fallos TCP](https://github.com/Shopify/toxiproxy)
- [Toxiproxy: contenedor 2.13.0 y digests publicados](https://github.com/Shopify/toxiproxy/pkgs/container/toxiproxy)
- [Resilience4j 2.4.0: patrones, licencia y soporte de Java](https://github.com/resilience4j/resilience4j/releases/tag/v2.4.0)
- [Testcontainers Java 2.0.5: release y cambios de compatibilidad](https://github.com/testcontainers/testcontainers-java/releases/tag/2.0.5)
- [Testcontainers: módulo PostgreSQL y coordenadas 2.x](https://github.com/testcontainers/testcontainers-java/blob/main/docs/modules/databases/postgres.md)
- [Testcontainers: licencia MIT](https://github.com/testcontainers/testcontainers-java/blob/main/LICENSE)
- [ARCA SDK: documentación actual, paquetes y migración de afip.ts](https://github.com/ralcorta/arcasdk)
- [ARCA SDK: changelog, WSFEX y WSFECred](https://github.com/ralcorta/arcasdk/blob/main/CHANGELOG.md)
- [Tryton 8.2: notas de versión de ventas](https://docs.tryton.org/8.2/modules-sale/releases.html)
- [Tryton 8.2: notas de versión de inventario](https://docs.tryton.org/8.2/modules-stock/releases.html)
- [Tryton: paquete 8.2.0 y licencia GPL-3.0-or-later](https://pypi.org/project/tryton/8.2.0/)
- [ERPNext: versión 16.60.0 y cambio de devolución POS](https://github.com/frappe/erpnext/releases)
- [ERPNext: licencia oficial GPLv3](https://docs.frappe.io/erpnext/open-source)
- [Apache Camel: Camel 4.22.2 LTS, Java 17/21/25](https://camel.apache.org/download/)
- [Apache Camel: calendario de releases y ciclo de soporte](https://camel.apache.org/releases/)
