# Postura de seguridad y confianza operacional

**Revisión:** 25 de noviembre de 2026  
**Madurez del producto:** piloto integrado POS + ERP; todavía no productivo.  
**Documento complementario:** [Seguridad, permisos y auditoría](SECURITY_AND_AUDIT.md).

> **Resumen honesto:** Rubrova ya tiene controles verificables de gobierno del código, compilación propia y resiliencia acotada de integraciones. La autenticación reforzada, los permisos completos, la auditoría protegida, la gestión productiva de secretos y la recuperación probada siguen siendo requisitos de diseño o trabajo pendiente. No se declara una certificación, auditoría externa ni aprobación para datos comerciales reales.

## Cómo interpretar los estados

| Estado | Significado |
|---|---|
| **Verificado en CI** | Existe una ejecución automatizada que prueba ese escenario concreto. No implica que todos los caminos estén cubiertos. |
| **Implementado, alcance limitado** | Hay código o configuración, pero falta aceptación integral o pruebas en el entorno físico. |
| **Diseñado** | Está especificado como requisito o arquitectura; no debe anunciarse como capacidad disponible. |
| **Pendiente** | Falta implementación, evidencia o aceptación. |

## Fortalezas que podemos respaldar hoy

| Área | Estado y evidencia | Límite explícito |
|---|---|---|
| Propiedad y trazabilidad del código base | **Verificado en CI.** Los snapshots de lsFusion 6.2 y MyCompany 6.2 están fijados en el repositorio; Rubrova compila sus propias fuentes de servidor, cliente GWT y lógica. | Esto mejora la reproducibilidad y el control de cambios; no equivale a una firma de artefactos, SBOM o auditoría de dependencias. |
| Runtime local | **Verificado en runners CI macOS ARM64 y Linux x86_64** para arranque, login y recorridos sintéticos del POS. | Falta repetir en el Mac físico, completar Windows y aceptar la instalación limpia sin conexión. |
| Aislamiento de fallos HTTP | **Verificado en escenarios CI acotados.** Se probaron timeouts, clasificación de respuestas 408/429/503, persistencia de incidencias, Retry-After y recuperación de un proveedor simulado. | La cobertura demostrada se concentra en lecturas GET y simulaciones. No prueba todavía todos los flujos de escritura, webhooks, cobros ni integraciones productivas. |
| Separación entre operación local y servicios externos | **Principio arquitectónico y base inicial.** El POS no debe quedar bloqueado por la indisponibilidad de un conector externo; los resultados inciertos requieren conciliación antes de repetir. | La Outbox, idempotencia y circuit breaker deben validarse por operación y proveedor antes de habilitar conectores reales. |
| Datos de prueba | **Pruebas funcionales con datos sintéticos.** Las aceptaciones registradas no usan una jornada de negocio real. | No cargar datos de clientes, credenciales ni información comercial real en la vista previa. |
| Permisos del workflow de plataforma | **Verificado en configuración.** El workflow principal declara permisos de contenido de solo lectura (`contents: read`). | Esto no demuestra que todos los workflows tengan permisos mínimos ni sustituye una revisión de acciones y secretos. |

La fuente de verdad de cada aceptación es [Estado real del proyecto](PROJECT_STATUS.md) y la cobertura está descrita en [Calidad y pruebas](QUALITY_AND_TESTING.md). Una compilación correcta no demuestra por sí sola seguridad, integridad transaccional completa ni continuidad.

## Controles especificados, todavía no demostrados como capacidad del producto

| Control | Dirección definida | Qué falta para considerarlo aceptado |
|---|---|---|
| Identidad y sesiones | Usuarios individuales, recuperación controlada y sesiones bloqueadas según riesgo. | Implementación y pruebas de autenticación, cierre, expiración y recuperación. |
| Autorización | Permisos de servidor por acción, negocio, sucursal, caja, importe y contexto; aprobación separada para acciones sensibles. | Matriz de permisos ejecutable y pruebas negativas que demuestren que la API también rechaza acciones no autorizadas. |
| Auditoría | Eventos con actor, fecha, entidad, motivo, autorización y resultado; correcciones mediante movimientos compensatorios. | Registro persistente protegido, consulta restringida, integridad verificable y pruebas contra edición/borrado no autorizado. |
| Secretos y configuración | Credenciales fuera del código y de los registros; acceso mínimo. | Almacenamiento y rotación adecuados al sistema operativo, permisos de archivos, redacción de logs y prueba de recuperación. |
| Datos personales y pagos | Minimización; separar pagador de identidad del cliente; evitar almacenar datos completos de tarjeta. | Revisar flujos y persistencia reales, retención, exportaciones, proveedor de pagos y alcance PCI con especialistas. |
| Red y acceso remoto | Vista previa limitada a loopback; cualquier acceso remoto debe tener controles explícitos. | Endurecimiento de producción, TLS, firewall, autenticación, permisos de red y prueba desde otro equipo. |
| Backups y recuperación | Copias independientes, rollback y restauración en otro equipo. | Backup y restore reales, integridad comprobada y tiempos de recuperación medidos. |
| Cadena de suministro | Versiones y fuentes upstream fijadas y cambios controlados. | Fijar cada GitHub Action a un commit SHA inmutable, generar SBOM, analizar vulnerabilidades de dependencias, revisar licencias y mantener una política de actualización continua. |

El detalle de roles, auditoría, pagos y privacidad está en [Seguridad, permisos y auditoría](SECURITY_AND_AUDIT.md). El plan de recuperación está en [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md).

## Reglas que se mantienen desde el diseño

- Una falla de Mercado Libre, ARCA u otro proveedor no debe tumbar el POS local.
- No se reintenta a ciegas una escritura, cobro, emisión fiscal o despacho cuyo resultado pueda haber quedado incierto.
- Un pago sólo se marca confirmado con evidencia del proveedor o terminal correspondiente.
- La devolución conserva la operación original y usa movimientos compensatorios relacionados.
- Los datos de pagador usados para conciliar no se convierten automáticamente en identidad ni perfil comercial del cliente.
- Los logs no deben contener contraseñas, tokens, PAN completo, CVV, PIN ni datos personales innecesarios.
- La vista previa local es para desarrollo: no exponerla a la red ni utilizarla con información real.

Estas reglas son requisitos de arquitectura y aceptación; su presencia en la documentación no demuestra que todos los controles estén implementados.

## Puertas obligatorias antes de producción

1. **Identidad y permisos:** usuarios individuales, autorización en servidor, segregación de funciones y pruebas de acceso denegado.
2. **Datos y secretos:** clasificación de información, minimización, redacción de logs, gestión de credenciales y revisión de exposición de datos sensibles.
3. **Superficie de red:** configuración segura por defecto, TLS cuando corresponda, firewall y prueba de acceso remoto autorizado/no autorizado.
4. **Auditoría:** eventos críticos persistentes, protegidos, consultables y relacionados con las operaciones originales y compensatorias.
5. **Continuidad:** copia exportable, checksum, restauración en una máquina limpia y conciliación de ventas, pagos, caja y stock después del restore.
6. **Integraciones y pagos:** idempotencia, consultas de estado ante resultados inciertos, pruebas de fallos, sandbox y homologación con cada proveedor.
7. **Cadena de suministro:** inventario de dependencias, escaneo de vulnerabilidades, revisión de cambios upstream y artefactos trazables.
8. **Validación de seguridad:** mapa de controles contra OWASP ASVS según riesgo, pruebas negativas y revisión independiente antes de tratar el sistema como productivo.

## Qué no afirmamos

A la fecha de esta revisión, Rubrova **no** afirma estar certificado por OWASP, PCI DSS, ISO 27001 ni haber superado una auditoría externa. Tampoco afirma que estén terminados el RBAC completo, la auditoría inmutable, el cifrado integral, la instalación offline limpia o el backup/restore aceptado. El alcance legal, fiscal y de privacidad debe validarse con profesionales responsables.

## Evidencia y seguimiento

- [Estado real del proyecto](PROJECT_STATUS.md): capacidades aceptadas, parciales y pendientes.
- [Calidad y pruebas](QUALITY_AND_TESTING.md): estrategia y criterios de aceptación.
- [Resiliencia de integraciones](INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md): timeouts, reintentos, aislamiento y conciliación.
- [Continuidad operativa y recuperación](OPERATIONAL_RESILIENCE_AND_RECOVERY.md): backups, restore, rollback y escenarios de falla.
- [Arquitectura](ARCHITECTURE.md): límites del núcleo integrado y de los módulos Rubrova.

**Criterio editorial:** toda fortaleza que se muestre en el README debe enlazar a una prueba, una decisión técnica o una limitación visible. Si no hay evidencia reproducible, se presenta como objetivo, no como garantía.
