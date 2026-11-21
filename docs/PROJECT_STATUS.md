# Estado real del proyecto Rubrova

**Corte:** 20 de noviembre de 2026  
**Rama de trabajo:** main  
**Última prueba funcional:** [CI 44811714783](https://github.com/JavierGrecco/Rubrova/actions/runs/44811714783)

## Resumen ejecutivo

Rubrova ya ejecuta MyCompany 6.2 en un entorno CI Linux x86_64 descartable. Se verificaron el inicio, la extensión propia, el login, la navegación al POS, la apertura de turno y, en la ejecución 44811714783, la búsqueda de un producto sintético y su incorporación al recibo con cantidad 1 y precio 1.250. La prueba se detuvo antes de cobrar. No hubo venta ni pago.

La decisión arquitectónica cambió para priorizar la independencia del código y la operación local. Rubrova incorporará como código propio versionado los árboles completos de MyCompany 6.2 y del motor lsFusion 6.2. La fuente queda dentro del repositorio como snapshots identificados por commit, no como submódulos Git ni dependencias descargadas en el arranque. La automatización de importación y validación ya está preparada; la compilación desde fuente, la imagen de ejecución propia y el paquete offline son validaciones separadas que todavía deben aprobarse.

## Qué hay probado

| Capacidad | Estado | Alcance |
|---|---|---|
| Runtime MyCompany 6.2 | Aprobado en CI Linux x86_64 | Contenedores temporales y artefactos fijados; no es instalación productiva |
| Módulos Rubrova | Aprobado en CI | Punto de entrada y captions propios cargan |
| Login y navegación | Aprobado en CI | Chromium llega a Comercio → Punto de venta |
| Abrir turno | Aprobado en CI | Turno sintético en base descartable |
| Buscar producto | Aprobado en CI | El fixture aparece en Buscar artículos |
| Añadir al recibo | Aprobado en CI | Cantidad 1, código de barras y precio 1.250 visibles; sin cobro |
| Venta/cobro/vuelto | Pendiente | No se ha confirmado ninguna venta o pago |
| Stock, devolución y cierre | Pendiente | Falta reconciliar cada movimiento con la venta y caja |
| Localización completa | Parcial | En la interfaz siguen apareciendo títulos y campos en inglés |
| Fuente MyCompany + motor lsFusion en main | Importación automatizada en curso | Fijar snapshot y validar árbol/licencia |
| Compilación Rubrova desde fuente propia | Pendiente | El build inicial se ejecuta en CI como diagnóstico |
| Build completamente offline | Pendiente | Debe pasar con Maven -o y repositorio local preparado |
| Runtime local sin Internet | Pendiente | Faltan imágenes propias, paquete offline y prueba con red aislada |
| Instalación y recuperación en la PC de uso | Pendiente | No se ha hecho instalación final ni restauración |
| ARCA, pagos externos y logística | Pendiente | Cada conector debe aprobar timeout, circuit breaker, idempotencia, fallos simulados y recuperación antes de habilitarse |

## Código que Rubrova mantiene

- vendor/platform/: snapshot del motor lsFusion 6.2 (servidor, API, cliente web/desktop y build).
- vendor/mycompany/: snapshot completo de MyCompany 6.2 (POS y ERP).
- extensions/lsfusion/: módulos y localización propios.
- patches/lsfusion/: mecanismo documentado para modificaciones directas del motor cuando una extensión no alcanza.
- build/rubrova/pom.xml: reactor Maven que compone las fuentes del motor y de MyCompany.

Los commits y las licencias de origen están en platform/source-lock.json y los marcadores dentro de cada árbol vendorizado. MyCompany usa Apache 2.0; el código lsFusion usa LGPL 3.0. Se conservan los avisos y archivos originales. Las dependencias Maven de terceros se auditarán, fijarán y empaquetarán; no se afirmará que desaparecen por incorporar los repositorios.

## Arquitectura objetivo para una PC local

El runtime productivo será una instalación local con servidor propio, aplicación MyCompany adaptada, cliente web servido desde el mismo equipo y base PostgreSQL local/persistente. Las imágenes necesarias se construirán desde nuestras fuentes y se entregarán en un paquete que se puede cargar sin descargar imágenes. Compose usará pull_policy: never y una red interna sin salida externa en la prueba offline.

El núcleo POS/ERP debe poder operar sin Internet. ARCA, adquirentes/QR, marketplaces, mensajería y transportistas son integraciones naturalmente remotas: si no hay red, quedan pendientes o informan indisponibilidad sin bloquear catálogo, caja local, ventas permitidas, compras, stock e informes.

## Cómo protegeremos producción

No se actualizará automáticamente ningún componente. Cada versión candidata debe superar comparación con su origen, reaplicación de cambios Rubrova, compilación, regresión funcional, migración probada sobre copia de base, backup/restore y prueba offline. Se mantiene el último paquete estable y una ruta de recuperación. Nunca probaremos primero una migración sobre la única base productiva.

## Próximo orden de implementación

1. Incorporar y validar los dos árboles completos de fuentes en main.
2. Conseguir un build Maven real de lsFusion + MyCompany desde vendor/; corregir cualquier incompatibilidad del reactor.
3. Sustituir los Dockerfiles/Compose upstream que descargan artefactos por imágenes Rubrova construidas localmente y fijadas.
4. Conseguir un runtime de Rubrova que arranque sin descargar imágenes ni artefactos.
5. Terminar carrito y validar importes; luego cobrar efectivo en base descartable y conciliar venta, pago, caja y stock.
6. Probar pagos, vuelto, devolución, cierre, conciliación, permisos y auditoría.
7. Completar traducción y experiencia visual sobre las fuentes que ahora controlamos.
8. Preparar paquete offline y probar en una PC limpia con Internet desactivado; luego backup, restauración y recuperación.
9. Adaptar fiscalidad argentina y conectores externos sin bloquear el funcionamiento local.

El proyecto no se declara listo por importar fuentes ni por tener CI verde. Se acepta cuando una instalación local conserva las operaciones y los datos después de reiniciar, concilia dinero y stock, puede recuperarse desde un backup probado y demuestra que las fallas de integraciones quedan aisladas mediante timeout, estado persistido, mensajes claros y pruebas de fault injection.


## Política transversal de errores

Se añadió [Resiliencia de integraciones y tratamiento de errores](INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md). El motor lsFusion 6.2 ofrece timeoutHttp() y TRY/CATCH, pero eso no equivale a tener la política implementada. El registro común de incidentes y el helper GET ya están en el módulo Rubrova; el motor vendorizado ahora impone un timeout de 10 s por defecto y 60 s máximo a todo `EXTERNAL HTTP`; el cambio está reproducido como parche idempotente y validado en cada importación de fuentes. Faltan terminar la validación runtime de ese módulo, los estados Outbox/circuit breaker y ampliar las pruebas simuladas más allá de GET. Mercado Libre y los demás conectores no se habilitarán en producción sin esas puertas.


La prueba de precios del POS utiliza `RubrovaCISalesFixture` sólo en CI para asignar ARS al tipo minorista; la venta no se valida con el importe de la búsqueda sino con el precio del renglón y el total del recibo.
