# Estado real del proyecto Rubrova

**Corte:** 26 de noviembre de 2026, 15:45 UTC  
**Rama canónica:** `main`  
**Commit integrado:** [`f545c90`](https://github.com/JavierGrecco/Rubrova/commit/f545c907b12a9eed4cf5e532edd3434babb64139)  
**Estado GitHub:** una sola rama (`main`), cero pull requests abiertos. No quedan ramas de desarrollo separadas visibles.

## Resumen ejecutivo

Rubrova ya dispone de un runtime propio compilado desde las fuentes fijadas de MyCompany 6.2 + lsFusion 6.2 y acaba de superar el smoke nativo de Apple Silicon con PostgreSQL 18, Java 21 y Tomcat 9, sin Docker. La validación ya no se limita a iniciar el servidor: autenticó, consultó la exportación nativa de inventario, ejecutó una venta sintética, concilió caja y stock, cerró el turno, reinició el servidor y comprobó la persistencia.

Esto confirma una base técnica prometedora para continuar el piloto POS + ERP. **No significa que Rubrova esté listo para uso comercial diario o producción.** Los datos son sintéticos y aún faltan flujos importantes de caja, devoluciones, pagos, fiscalidad, instalación y recuperación completa.

## Última validación de plataforma

El workflow [Validación del arranque de plataforma, run 45847755524](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755524), ejecutado sobre el SHA `f545c907`, terminó en `success`.

| Trabajo | Resultado | Alcance real |
|---|---|---|
| Prevalidación local compartida | Aprobado | Tests Node/Python, contratos, scripts, configuración, listener y despliegue |
| Validación Windows | Aprobado | Comprobación de sintaxis PowerShell; no es todavía una instalación funcional completa |
| Compilación del fork | Aprobado | Servidor lsFusion, cliente GWT y lógica MyCompany desde fuentes Rubrova |
| Smoke macOS ARM64 nativo | Aprobado | Java 21, PostgreSQL 18, servidor lsFusion, Tomcat y Chromium; sin Docker |
| Docker/Linux y Linux nativo complementarios | Omitidos en este push | `skipped`; no deben contarse como aprobados por esta ejecución |

La evaluación del planificador también terminó correctamente en [run 45847755643](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755643).

## Evidencia funcional del smoke nativo

La ejecución [45847755524](https://github.com/JavierGrecco/Rubrova/actions/runs/45847755524) registró:

- Login autenticado en Chromium y navegación al módulo Comercio → Punto de venta.
- Las sondas autenticadas de inventario, compromisos de salida y recepciones respondieron HTTP 200.
- La exportación nativa devolvió JSON verificable: una fila de inventario, una línea de compromiso, una reserva vinculada y una recepción en el fixture de prueba. La reserva de 2 unidades quedó asociada a la línea de salida, sin duplicar el compromiso.
- Una venta sintética por ARS 1.250: una factura, un pago en efectivo por el mismo importe y una salida de una unidad (stock 10 → 9).
- Cierre del turno conciliado: estado `CLOSED`, venta neta y efectivo ARS 1.250.
- Reinicio de servidor y cliente, conservando PostgreSQL; factura, pago, existencia, turno cerrado y ocho incidencias permanecieron verificables.
- Segunda instancia de demostración con PostgreSQL, configuración y puertos separados; abrió turno y encontró su producto de muestra.

La prueba usó `RUBROVA_NATIVE_EGRESS_BLOCKED=false`; el log dejó explícito `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. Los diagnósticos Linux/Docker fueron omitidos en ese push.

## Estado por capacidad

| Capacidad | Estado | Límite pendiente |
|---|---|---|
| Fuentes fijadas y propiedad del código | Aprobado | Mantener los locks y la revisión de licencias/origen |
| Compilación MyCompany/lsFusion propia | Aprobado en CI | Repetir en el equipo local y conservar artefactos por SHA |
| Runtime nativo macOS ARM64 | Aprobado en runner CI | Validar en el Mac físico del usuario |
| Login, navegación y POS básico | Aprobado con fixture sintético | No equivale a una jornada de operación real |
| Venta, factura, pago exacto y stock | Aprobado | Vuelto, pagos mixtos, descuentos complejos y cancelaciones |
| Cierre básico del turno | Aprobado | Arqueo contado, diferencias, ingresos y retiros |
| Persistencia tras reinicio | Aprobado | Backups externos, restauración completa y rollback |
| Exportación nativa de reposición | Aprobada contra fixtures de MyCompany | Conciliar con una base real y mantener el modo sólo lectura |
| Planificador de reposición | Suite aprobada | Datos históricos reales, política por proveedor y evaluación fuera de muestra |
| Terminales de pago | Modelo y trazabilidad iniciales | SDK/proveedor, sandbox, hardware y homologación |
| ARCA y fiscalidad argentina | Diseño e investigación | Integración y homologación; evitar doble facturación de canales externos |
| Offline en macOS | Pendiente | Repetir el recorrido con egress bloqueado |
| Windows nativo | Parcial | La validación reciente sólo comprobó sintaxis; falta instalación y smoke funcional |
| Instalador offline y periféricos | Pendiente | PC limpia, lector, impresora, cajón, balanza y terminal |
| Backup/restore completo del negocio | Pendiente | El primer incremento cubre sólo PostgreSQL; faltan adjuntos, documentos y asistente guiado |

## Arquitectura y propiedad

- `vendor/platform/`: fuentes fijadas de lsFusion 6.2.
- `vendor/mycompany/`: fuentes fijadas de MyCompany 6.2.
- `extensions/lsfusion/`: módulos y localización propios.
- `patches/lsfusion/`: cambios directos al motor sólo cuando una extensión no alcanza.
- `build/rubrova/pom.xml`: reactor que compila los componentes desde el repositorio.
- Runtime local prioritario: Java 21 + PostgreSQL 18 + Tomcat 9, sin Docker como dependencia de ejecución.

La extensión de reposición es de sólo lectura. No ejecuta `fillAuto`, no crea órdenes de compra y no altera inventario. Las integraciones externas deben fallar de forma aislada y nunca convertirse en requisito para operar la caja local.

## Próximas prioridades

1. **Validar el primer backup lógico PostgreSQL** con el mismo clúster nativo: crear paquete, verificar checksum/legibilidad y restaurar a una base nueva sin tocar `rubrova_dev`.
2. **Probar el runtime en el Mac físico** con los artefactos y herramientas instaladas localmente; revisar arranque, cierre, logs y persistencia.
3. **Completar caja y POS:** arqueo contado, diferencias, ingresos/retiros, vuelto, pagos mixtos, cancelaciones y devolución parcial/total vinculada a la venta original.
4. **Probar continuidad offline en macOS** con salida externa bloqueada, incluyendo estados pendientes de proveedores y recuperación posterior.
5. **Cerrar Windows x64** con instalación, rutas, permisos, arranque, parada y persistencia nativos.
6. **Desarrollar backup completo y restauración guiada:** adjuntos, documentos, manifiesto, verificaciones de relaciones/ledgers y recuperación en otra PC.
7. Después de consolidar el núcleo, avanzar en compras/recepciones, costos, cuentas corrientes, fiscalidad, reportes e inteligencia comercial.

## Límites de aceptación

No se debe habilitar uso productivo hasta demostrar una jornada repetible con datos controlados y luego una prueba piloto supervisada: venta, pagos, caja, stock, devolución, documentos fiscales, auditoría, modo offline, copia externa y restauración. Ningún smoke sintético sustituye esa aceptación.
