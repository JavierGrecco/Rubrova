# Calidad y pruebas

## Regla

Una capacidad no se considera terminada por mostrar una pantalla. Debe cumplir reglas, permisos, persistencia, integridad, accesibilidad, recuperación y pruebas.

## Memoria técnica y contratos

Toda modificación de lógica, datos o integración debe actualizar la [base de conocimiento de ingeniería](engineering/README.md): [contratos](engineering/CONTRACTS.md), [decisiones](engineering/DECISION_LOG.md), [relaciones entre dominios](engineering/DOMAIN_RELATIONSHIPS.md) e [iteraciones](engineering/ITERATION_LOG.md). La documentación conserva la razón y la evidencia; no reemplaza a los tests.

## Prevalidación local compartida con CI

Antes de publicar cambios, ejecutá desde la raíz:

```bash
bash scripts/platform/local-preflight.sh
```

Las capas se pueden ejecutar por separado:

```bash
bash scripts/platform/local-preflight.sh --platform
bash scripts/platform/local-preflight.sh --replenishment
```

El mismo script se invoca en GitHub Actions. Comprueba Node/Python, extensiones estáticas, tests del supervisor, scripts y shell, suite del planificador, fixtures y el puente JSON nativo. Es una primera barrera rápida y repetible; **no** demuestra que el módulo lsFusion pueda cargarse, ni que la API autenticada funcione contra MyCompany.



## Estrategia

- Unitarias: cálculos, reglas, validaciones y estados.
- Integración: base de datos, transacciones, eventos y adaptadores.
- Contrato: APIs internas y externas.
- Componentes: interfaz y estados visibles.
- End-to-end: recorridos completos por perfil y canal.
- Resiliencia: desconexiones, reinicios, reintentos y fallos parciales.
- Seguridad: permisos, aislamiento, abuso y datos sensibles.
- Rendimiento: caja, búsqueda, sincronización y reportes.

## Entorno de ejecución para pruebas

Para el desarrollo local se prioriza el runtime nativo, sin Docker: Java 21, PostgreSQL 18 y Tomcat 9.0.124. El supervisor utiliza una carpeta PostgreSQL exclusiva, no adopta ni detiene servicios personales de la máquina y conserva los datos cuando se detienen los procesos.

En CI, la puerta principal del runtime es el smoke nativo macOS ARM64, ejecutado después de la compilación completa. Los diagnósticos Linux nativo y Docker/Linux se ejecutan manualmente mediante `workflow_dispatch`; no retrasan cada pull request y no son gates de aceptación. Un job con `continue-on-error` nunca se interpreta como aprobación funcional.

### Estado de evidencia

- La última revisión integrada de `main` es `ac758d01`. El workflow [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) terminó con `success`: preflight compartido, validación sintáctica Windows, compilación completa y smoke nativo macOS ARM64.
- En el runtime autenticado se completó una venta sintética de ARS 1.250, pago exacto en efectivo, salida de stock 10 → 9 y cierre de turno. Después de reiniciar, factura, pago, existencia, turno y ocho incidencias siguieron presentes.
- El smoke creó un paquete lógico PostgreSQL, verificó manifiesto y SHA-256, comprobó legibilidad con `pg_restore --list` y restauró a `rubrova_restore_ci`. La base activa `rubrova_dev` no se sobrescribió.
- Los nueve tests de `test_native_postgres_backup.py` pasaron en preflight; incluyen rechazo de paquete alterado, manifiesto alterado, entradas extra, clúster ajeno, destino existente y limpieza de restore parcial.
- El planificador independiente aprobó en [45854940442](https://github.com/JavierGrecco/Rubrova/actions/runs/45854940442), sobre el commit previo `c0dacb7`; usa fixtures y no implica aceptación de compras reales.
- La ejecución 45855055565 tuvo egress habilitado y dejó `RUBROVA_NATIVE_OFFLINE_ACCEPTANCE=not_tested`. Linux nativo y Docker/Linux fueron `skipped`; Windows fue sólo validación sintáctica.
- El backup continúa limitado a PostgreSQL: faltan documentos, adjuntos, exportación portable y restauración en PC limpia.
- La rama `work/retail-return-quantity-guard` agrega el límite de cantidad devuelta minorista usando la restricción de MyCompany. Su preflight, compilación y smoke quedan pendientes; no se considera aceptada hasta que pase la CI y se pruebe la devolución real en runtime.
- Siguen pendientes la conciliación de reposición con una base MyCompany real, prueba en Mac físico, instalación Windows, periféricos y jornada comercial supervisada.

### Controles del smoke nativo

- Inicio desde una base vacía, verificación del servidor, RMI, `onStarted` y respuesta web.
- Login y navegación en español mediante Chromium.
- Verificación de la API autenticada cuando el cambio modifica el contrato.
- Captura de errores del navegador, requests fallidos, respuestas HTTP y tiempos de `dispatch`.
- Ejecución con salida externa bloqueada cuando se evalúa la continuidad offline; distinguirla de los smokes que habilitan Internet para dependencias o integraciones simuladas.
- Crear un paquete PostgreSQL, verificar checksums y restaurarlo en una base nueva sin modificar la base activa.
- Rechazar paquetes alterados, bases destino existentes y restauraciones parciales; comprobar que la limpieza sólo retire la base nueva creada por esa operación.

Los tests unitarios del supervisor no sustituyen las pruebas de runtime, y el inicio de sesión no sustituye la prueba de una API de dominio.

## Flujos POS obligatorios

Venta en efectivo con vuelto; venta con medios mixtos; descuentos por línea, carrito, cupón, combo y horario; reglas de acumulación; excepción autorizada; devolución parcial y total; anulación; productos pesables; caja compartida; apertura, arqueo, cierre y diferencia; impresión y recuperación ante impresora desconectada.

## Integridad y auditoría

- El operador no aprueba su propia excepción cuando la política exige separación.
- Los registros de auditoría no se editan ni borran desde la aplicación.
- Cada devolución remite al original.
- Repetir solicitud no duplica venta ni pago.
- Cambiar un precio no modifica ventas anteriores.
- Una salida interna no se cuenta como venta.
- Los perfiles sin permiso no acceden a operaciones restringidas.
- Un usuario no accede a otro negocio alterando identificadores.

## Offline y sincronización

Probar desconexión antes/durante/después de confirmar; cierre y reapertura con pendientes; reinicio; interrupción y repetición de sincronización; mensajes externos repetidos; cambios concurrentes; ventas desde cajas desconectadas; conflictos de stock; restauración de backup.

Criterios: una operación confirmada no se pierde; no se procesa dos veces; el usuario ve qué está pendiente; no se simula autorización fiscal o pago sin confirmación; los conflictos relevantes siguen reglas explícitas.

## Fiscalidad e integraciones

Homologación ARCA; factura y nota de crédito; integración de facturación externa y propia; no doble emisión; webhooks repetidos/tardíos/fuera de orden; pago autorizado, rechazado, pendiente y reembolsado; caída de proveedor; conciliación con liquidaciones.

## Inteligencia y datos

Cálculos financieros con casos conocidos; ventas netas, costo, margen y contribución; períodos incompletos y días sin stock; estacionalidad con datos sintéticos e históricos; no inferir causalidad de correlaciones; pronósticos fuera de muestra; error, sesgo e intervalos; promociones con contribución incremental; datos faltantes reducen confianza y se declaran.

## Seguridad

Pruebas de roles y permisos en servidor; aislamiento de negocios y sucursales; sesión; límites de solicitudes; secretos fuera del código; logs sin datos sensibles; validación de entradas/salidas; dependencias y secretos analizados en CI; revisión de cambios de autenticación, autorización y auditoría.

## Experiencia y rendimiento

Venta habitual con pocos pasos; teclado, lector y pantalla táctil; errores accionables; contraste, foco y semántica; pantallas pequeñas y grandes; latencia de búsqueda y confirmación; informes no bloquean caja.

## Evidencia

Cada entrega registra qué se probó, entorno y versión, resultado, evidencia, limitaciones y riesgos pendientes. No se informa "aprobado" sin ejecutar las pruebas correspondientes. Los datos de prueba son sintéticos.


## Marcos de calidad y accesibilidad

- **ISO/IEC 25010:2023** como modelo de calidad de producto: adecuación funcional, eficiencia de desempeño, compatibilidad, capacidad de interacción, fiabilidad, seguridad, mantenibilidad, flexibilidad y seguridad operacional según el modelo vigente. Traducir las características aplicables en métricas y pruebas: https://www.iso.org/standard/78176.html.
- **WCAG 2.2 nivel AA** como objetivo de accesibilidad para las interfaces web y administrativas. Validar teclado, foco, contraste, tamaño de objetivos, etiquetas, mensajes y compatibilidad con tecnologías de asistencia: https://www.w3.org/TR/wcag/.
- **OWASP ASVS 5.0** para requisitos verificables de seguridad: https://asvs.owasp.org/.
- **NIST SSDF SP 800-218 v1.1** como guía de prácticas de desarrollo seguro. La revisión 1.2 figuraba como borrador en la consulta del 19/11/2026 y se volverá a verificar antes de adoptar sus identificadores: https://csrc.nist.gov/Projects/ssdf/publications.
- **PCI DSS v4.0.1** cuando el alcance de pagos lo requiera. Se busca reducir dicho alcance mediante terminales y proveedores certificados: https://www.pcisecuritystandards.org/es/document_library/.

Estos marcos guían requisitos y pruebas. No se afirmará cumplimiento o certificación sin una evaluación formal y evidencia suficiente.


## Código de terceros y licencias

Toda dependencia, plugin, fragmento de código, plantilla, fuente, icono o recurso externo debe pasar una revisión antes de incorporarse.

La revisión registra:

- Repositorio y URL de origen.
- Versión, etiqueta o commit exacto.
- Licencia efectiva del archivo y del proyecto, más avisos y excepciones.
- Licencias de dependencias transitivas y recursos incluidos.
- Partes comerciales, Enterprise, duales o con condiciones especiales.
- Archivos modificados, avisos que deben conservarse y obligaciones de distribución.
- Mantenimiento, vulnerabilidades conocidas, cobertura de pruebas y compatibilidad.

Reglas de aceptación:

1. Preferir MIT, ISC, BSD y Apache 2.0 cuando el componente cubra la necesidad y su calidad sea suficiente.
2. Revisar LGPL con detalle antes de combinar, modificar o distribuir.
3. No incorporar GPL o AGPL al núcleo sin una decisión explícita sobre la licencia y el modelo de distribución del producto.
4. No usar código sin licencia identificable ni asumir que un repositorio público concede permiso de reutilización.
5. No incorporar código o recursos de una edición Enterprise/comercial sin contrato válido.
6. Conservar avisos, archivos LICENSE y NOTICE, atribuciones y fuentes de origen según las condiciones aplicables.
7. Fijar versiones; no depender de ramas flotantes para software de producción.
8. Mantener un SBOM en SPDX o CycloneDX y analizar dependencias, vulnerabilidades y licencias en CI.
9. Un cambio de versión obliga a revisar cambios de licencia y dependencias transitivas.

La guía completa y las licencias de los candidatos están en [Estrategia de reutilización de código abierto](OPEN_SOURCE_STRATEGY.md).

Para el protocolo de respaldo portable, migración de equipo, cifrado y restauración en Windows limpio, ver [Copias de seguridad y recuperación](BACKUP_AND_MIGRATION_STRATEGY.md).

La aprobación legal de una licencia no reemplaza la revisión técnica; una biblioteca permisiva también puede ser insegura, estar abandonada o no cumplir nuestras invariantes.


## Continuidad y recuperación

Además de las pruebas funcionales P01–P26, la aceptación de confiabilidad debe ejecutar P27–P48. Simulan terminación abrupta del proceso (sin apagar físicamente el equipo), comandos y webhooks duplicados, conflicto de clave, concurrencia CAS, cuotas offline, restauración, migraciones, despliegue independiente, Outbox y Sagas. El guion completo está en [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md).

## Arquitectura distribuida y aislamiento de servicios

- Cada servicio tiene almacenamiento/credenciales privados; se prueba que otros servicios no puedan leer ni escribir tablas ajenas.
- APIs y eventos con esquema/versionado, autenticación y pruebas de compatibilidad entre versiones coexistentes.
- Outbox/Inbox durables, idempotencia atómica y claves estables; reintentos concurrentes producen un solo efecto.
- Correlation ID de extremo a extremo, métricas y trazas que permiten reconstruir el recorrido de una operación.
- Reiniciar o actualizar un servicio no debe obligar a reiniciar o desplegar todos los demás.
- Un servicio nuevo o caído debe degradar sólo capacidades dependientes; los estados quedan visibles.
- Las transacciones distribuidas se prueban mediante Sagas y compensaciones idempotentes.
- Las copias de varios servicios se restauran con un manifiesto coherente de versiones y offsets de eventos.

## Contratos entre módulos externos

- Prueba de contrato de cada puerto/API con ejemplos válidos, inválidos y esquemas versionados.
- Reintentos repetidos con la misma clave no duplican venta, pago, movimiento, cupón ni factura.
- Webhooks duplicados o fuera de orden se deduplican y no retroceden estados finales.
- Un módulo no puede leer ni modificar el agregado de otro módulo por acceso directo a tablas.
- Aislamiento por negocio, sucursal, caja, dispositivo y permiso.
- Caída del servicio externo, timeout, respuesta parcial y recuperación.
- Outbox/inbox durables, dead-letter, replay autorizado y conciliación.
- Sustitución de adaptador sin modificar la lógica de negocio.
- Compatibilidad y build de cada puente en Windows, Linux y macOS por separado.

## Pruebas de checkout y terminal

- Retirar un producto del carrito antes del pago: total, descuentos e impuestos recalculados; sin venta ni salida de stock para esa línea.
- No permitir cambios silenciosos del importe una vez enviada la orden a terminal.
- Efectivo exacto, exceso y faltante: vuelto y neto de caja correctos al centavo.
- Pago mixto: suma de asignaciones igual al total; cada medio conserva su importe y estado.
- Terminal creada/en terminal/no confirmada: nunca se marca pagada.
- Aprobación, rechazo, cancelación, expiración, acción requerida y reembolso.
- Timeout después de que el cliente pudo haber pagado: consulta de estado antes de otro intento.
- Repetición de webhook y request: un único efecto.
- Voucher de terminal, ticket de venta y documento fiscal se concilian por separado.
