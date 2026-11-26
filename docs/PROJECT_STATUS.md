# Estado real del proyecto Rubrova

**Corte:** 26 de noviembre de 2026, 16:16 UTC  
**Rama canónica:** `main`  
**Commit integrado:** [`ac758d0`](https://github.com/JavierGrecco/Rubrova/commit/ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a)  
**Estado GitHub:** una única rama visible (`main`), cero pull requests abiertos. La rama no está protegida por ruleset de GitHub.

## Resumen ejecutivo

Rubrova dispone de un runtime propio de MyCompany 6.2 + lsFusion 6.2, compilado desde fuentes fijadas en el repositorio. El workflow [Validación del arranque de plataforma #417](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó correctamente e incluyó un smoke nativo macOS ARM64 sin Docker. La prueba pasó de inicio/login a venta, conciliación, cierre, reinicio y restauración lógica de PostgreSQL en una base nueva.

Esto habilita una siguiente etapa de ingeniería funcional sobre una base reproducible. **No significa que Rubrova esté listo para operación diaria ni producción.** Los datos del smoke son sintéticos, la exportación de reposición aún no se ha conciliado con una base comercial real y no se ha probado el runtime en el Mac físico del usuario.

## Última validación de plataforma

[Run 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565), SHA `ac758d01`, terminó con `success`.

| Trabajo | Resultado | Alcance real |
|---|---|---|
| Prevalidación local compartida | Aprobado | Suites Node/Python, contratos, scripts, configuración, listener y tests del backup |
| Validación Windows | Aprobado parcialmente | Sintaxis PowerShell; no instalación ni smoke funcional de Windows |
| Compilación del fork | Aprobado | Servidor lsFusion, cliente GWT y lógica MyCompany desde fuentes Rubrova |
| Smoke macOS ARM64 nativo | Aprobado | Java 21 ARM64, PostgreSQL 18, lsFusion/MyCompany, Tomcat y Chromium; sin Docker |
| Diagnóstico Linux nativo | Omitido | `skipped`; no es aprobación |
| Diagnóstico Docker/Linux | Omitido | `skipped`; no es aprobación |

La suite del planificador también aprobó en [run 45854940442](https://github.com/JavierGrecco/Rubrova/actions/runs/45854940442), sobre el commit anterior `c0dacb7`; el commit final `ac758d0` sólo corrigió el simulador de fallo de restauración.

## Evidencia funcional del smoke nativo

La ejecución [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) registró:

- Login autenticado con Chromium y navegación a Comercio → Punto de venta.
- Sondas autenticadas de inventario, compromisos de salida y recepciones con HTTP 200.
- Exportación nativa de sólo lectura, con colecciones verificadas contra fixtures sintéticas; no es aún conciliación con una base comercial real.
- Venta sintética de ARS 1.250, factura y pago en efectivo exacto; el inventario pasó de 10 a 9 unidades.
- Cierre del turno `SM/000001`, estado `CLOSED`, neto y efectivo de ARS 1.250.
- Reinicio de PostgreSQL/servidor/cliente y verificación de persistencia de factura, pago, stock, turno cerrado e incidencias.
- Segunda instancia Demo con configuración, puertos y base separada; abrió turno y encontró el artículo de muestra.
- Creación de respaldo lógico PostgreSQL; paquete y SHA-256 verificados; restauración a `rubrova_restore_ci`; la base activa `rubrova_dev` no se sobrescribió.
- Marcador de aceptación: `RUBROVA_NATIVE_POSTGRES_BACKUP_RESTORE=passed`.

El backup es **sólo PostgreSQL**. No incluye adjuntos, documentos externos, imágenes, binarios ni secretos. Tampoco existe todavía un asistente visual de restauración.

La ejecución usó `RUBROVA_NATIVE_EGRESS_BLOCKED=false` y dejó `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. No se certifica aún continuidad offline en macOS.

## Estado por capacidad

| Capacidad | Estado | Límite pendiente |
|---|---|---|
| Fuentes propias fijadas y compilación | Aprobado en CI | Mantener locks y revisión upstream |
| Runtime nativo macOS ARM64 | Smoke aprobado en runner | Ejecutar en el Mac físico |
| Login, navegación y POS básico | Aprobado con fixture sintético | No equivale a una jornada real |
| Venta, factura, pago y stock | Aprobado | Vuelto, medios mixtos, descuentos complejos y cancelaciones |
| Cierre básico de turno | Aprobado | Arqueo físico, diferencias e ingresos/retiros end-to-end |
| Persistencia tras reinicio | Aprobado | Recuperación integral y rollback |
| Exportación de reposición | API y fixtures aprobadas | Conciliar con base MyCompany local real |
| Planificador | Suite aprobada | Datos reales, cobertura y desempeño fuera de muestra |
| Backup lógico PostgreSQL | Creación, verificación y restore a nueva DB aprobados | Adjuntos, documentos, retención, disco externo y asistente |
| Devolución y reintegro | Componentes upstream existentes identificados | Activación del control de cantidad y recorrido E2E |
| Terminales de pago | Modelo y trazabilidad inicial | Proveedor, sandbox, hardware y homologación |
| ARCA/fiscalidad | Diseño e investigación | Integración y homologación |
| Offline macOS | Pendiente | Repetir con egress bloqueado |
| Windows nativo | Parcial | Instalación, operación, reinicio y persistencia funcional |
| Linux/Docker en último push | Omitido | Diagnóstico manual separado |
| Instalador y periféricos | Pendiente | PC limpia, lector, impresora, cajón, balanza y terminal |
| Uso productivo | No autorizado | Jornada supervisada, recuperación externa y homologación |

## Arquitectura y propiedad

- `vendor/platform/`: fuentes fijadas de lsFusion 6.2.
- `vendor/mycompany/`: fuentes fijadas de MyCompany 6.2.
- `extensions/lsfusion/`: módulos Rubrova y localización propia.
- `patches/lsfusion/`: cambios directos al motor sólo cuando una extensión no alcanza.
- `build/rubrova/pom.xml`: reactor de compilación propio.
- Runtime local prioritario: Java 21 + PostgreSQL 18 + Tomcat 9, sin Docker como requisito de ejecución.

La reposición es estrictamente de lectura: no ejecuta `fillAuto`, no crea órdenes ni altera inventario. Devoluciones, pagos y caja deben seguir usando los ledgers de MyCompany; Rubrova no debe introducir un segundo registro de existencias o efectivo.

## Próximas prioridades

1. **Devolución segura:** activar y probar el control de cantidad retornada contra la factura original; validar devolución parcial/total, reintegro al medio original y stock restaurado sin duplicaciones.
2. **Caja completa:** probar ingreso/retiro nativos, saldo teórico por medio y arqueo físico con diferencia registrada, responsable y hora.
3. **Prueba local en el Mac físico:** ejecutar preflight, doctor, arranque, venta, backup, restore y revisión de logs con Java 21 y PostgreSQL 18 ARM64.
4. **Continuidad offline macOS:** repetir el smoke con salida externa bloqueada y recuperación de integraciones pendientes.
5. **Windows x64:** instalación y smoke nativos completos.
6. **Backup integral:** adjuntos, documentos, manifiesto, checksums, retención, copia externa desconectable y restauración guiada en otro equipo.
7. **Reposición real:** capturar exportación autenticada de una base MyCompany local y conciliarla con sus ledgers antes de sugerir compras con datos reales.

## Protección de la rama principal

GitHub informa `protected: false` para `main`. No se debe confundir tener una sola rama con tener protección obligatoria. La protección debe activarse desde GitHub Settings con un ruleset que requiera los workflows aplicables, impida force-push y defina quién puede integrar. No se declara habilitada hasta verificarla.

## Límites de aceptación

No habilitar uso productivo hasta demostrar una jornada repetible con venta, devolución, pago/reintegro, caja, arqueo físico, stock, documentos fiscales, auditoría, modo offline, copia externa y restauración. Ningún smoke sintético sustituye esa aceptación.
