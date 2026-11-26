# Estado real del proyecto Rubrova

**Corte:** 26 de noviembre de 2026, 16:20 UTC  
**Rama canónica:** `main` — commit integrado `ac758d01e8fb1ef2bfdd65900a23281c9aab3c3a`  
**Trabajo siguiente:** `work/retail-return-quantity-guard` — guard de cantidad devuelta minorista en preparación; aún no integrado ni aceptado.

## Resumen ejecutivo

Rubrova ya compila su propio fork MyCompany 6.2 + lsFusion 6.2 y completó el smoke nativo de Apple Silicon sin Docker. La validación [run 45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó en `success`: preflight, compilación completa, runtime macOS ARM64, flujo de venta, cierre, persistencia y primera restauración lógica PostgreSQL.

Esto es evidencia de ingeniería y de un piloto transaccional sintético. **No es aprobación para producción ni para operar una jornada comercial real.**

## Última validación de plataforma

| Trabajo | Resultado | Alcance real |
|---|---|---|
| Prevalidación local compartida | Aprobado | Tests Node/Python, contratos, scripts y configuración |
| Validación Windows | Aprobado | Sintaxis PowerShell; no instalación funcional |
| Compilación MyCompany/lsFusion/GWT | Aprobado | Servidor, lógica y cliente desde fuentes fijadas en Rubrova |
| Runtime nativo macOS ARM64 | Aprobado | Java 21 ARM64, PostgreSQL 18, Tomcat 9 y Chromium; sin Docker |
| Venta y POS | Aprobado con fixture | ARS 1.250, factura, pago efectivo y stock 10 → 9 |
| Cierre y reinicio | Aprobado | Turno CLOSED, caja y datos persistidos después de reinicio |
| Backup/restore PostgreSQL | Aprobado | Paquete creado, SHA-256 verificado y restaurado en `rubrova_restore_ci` |
| Diagnóstico Linux nativo y Docker/Linux | Omitidos | `skipped`; no son resultados aprobados |

Run independiente del planificador: [45854940442](https://github.com/JavierGrecco/Rubrova/actions/runs/45854940442), aprobado sobre el commit `c0dacb7`; la evidencia funcional más reciente de plataforma es el run 45855055565 sobre `ac758d0`.

## Evidencia funcional del smoke

- Login autenticado y navegación a Comercio → Punto de venta.
- Venta sintética de ARS 1.250: factura y pago en efectivo por el importe exacto.
- Inventario físico: entrada inicial 10, salida 1, existencia final 9.
- Turno cerrado con estado `CLOSED`; venta, devolución neta cero y efectivo conciliados.
- Reinicio del supervisor/servidor y posterior consulta autenticada: factura, pago, stock, turno y ocho incidencias siguen presentes.
- Segunda instancia Demo en otra base y puertos: aprobada.
- Backup de `rubrova_dev`: SHA-256 `a33397a27bed48f166b69549160fdbf82dd6ebfbea839ab6c57716adb4434bab`; restauración exitosa en `rubrova_restore_ci`. La base activa no se sobrescribió.

**Límite del backup:** el paquete actual protege PostgreSQL únicamente. No incluye documentos, adjuntos, imágenes, certificados, binarios ni secretos; no equivale a recuperación completa en otra computadora.

## Estado por capacidad

| Capacidad | Estado | Pendiente |
|---|---|---|
| Fuentes propias fijadas y compilación | Aprobado en CI | Repetir build local y conservar artefactos por SHA |
| POS básico, venta, pago y stock | Aprobado con fixture | Vuelto, pagos mixtos, descuentos/cancelaciones y hardware real |
| Cierre de turno | Aprobado | Arqueo físico contado, diferencias, ingresos/retiros probados |
| Backup lógico PostgreSQL | Aprobado en smoke nativo | Adjuntos/documentos, programación, copia externa y restore PC limpia |
| Exportación nativa de reposición | Aprobada contra fixtures | Conciliar con una base MyCompany de negocio real; sigue siendo sólo lectura |
| Devoluciones minoristas | Upstream localizado; guard Rubrova en desarrollo | Activar `checkReturnedQuantity`, validar reintegro, recibo y stock en runtime |
| Terminales de pago | Modelo y trazabilidad | SDK/adquirente, sandbox y homologación |
| ARCA y fiscalidad argentina | Diseño/investigación | Integración, CAE, notas y evitar doble facturación de marketplace |
| Offline macOS | No probado en el run actual | Repetir con egress bloqueado y cola/recuperación |
| Mac físico | Pendiente | Instalación y prueba en el equipo del usuario |
| Windows x64 | Parcial | Instalación real, arranque, parada, actualización y restore |
| Linux nativo | Diagnóstico omitido | Ejecutar gate sobre SHA estable |
| Periféricos y jornada real | Pendiente | Lector, impresora, cajón, balanza, terminal y piloto supervisado |

## Arquitectura y propiedad de datos

- `vendor/platform/`: fuentes fijadas de lsFusion 6.2.
- `vendor/mycompany/`: fuentes fijadas de MyCompany 6.2.
- `extensions/lsfusion/`: módulos propios Rubrova.
- `patches/lsfusion/`: cambios acotados al motor cuando una extensión no alcanza.
- `build/rubrova/pom.xml`: reactor que compila los componentes desde el repositorio.
- Ruta local prioritaria: Java 21 + PostgreSQL 18 + Tomcat 9, sin Docker como dependencia de ejecución.

MyCompany sigue siendo el dueño de ventas, notas de crédito, pagos, recibos de devolución y ledgers de caja/stock. Rubrova no debe crear otro libro paralelo. El saldo teórico del cajón tampoco se debe confundir con arqueo contado.

## Próximas prioridades

1. Terminar e integrar `RubrovaRetailControls`: habilitar en el tipo minorista el límite nativo de devoluciones acumuladas y verificar que el guard se cargue en todos los modos de runtime.
2. Extender el smoke con devolución parcial, rechazo de sobredevolución, reintegro limitado por medio de pago y reingreso de stock mediante el recibo nativo.
3. Validar ingresos/retiros y diseñar arqueo contado con diferencia, responsable y auditoría; no duplicar el ledger de MyCompany.
4. Ejecutar Rubrova en el Mac físico y repetir modo offline con egress bloqueado.
5. Completar paquete portable: documentos/adjuntos, manifiesto, copia externa, restauración guiada en otra PC.
6. Cerrar Windows nativo y periféricos; luego prueba piloto supervisada.

## Límites de aceptación

No habilitar producción hasta repetir una jornada de negocio con datos controlados y luego una prueba piloto supervisada: venta, pagos, vuelto, caja, devolución, stock, comprobantes fiscales, auditoría, modo offline, backup externo y restauración en un equipo limpio. Los smokes sintéticos no sustituyen esa aceptación.
