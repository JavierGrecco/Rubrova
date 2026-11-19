# Calidad y pruebas

## Regla

Una capacidad no se considera terminada por mostrar una pantalla. Debe cumplir reglas, permisos, persistencia, integridad, accesibilidad, recuperación y pruebas.

## Estrategia

- Unitarias: cálculos, reglas, validaciones y estados.
- Integración: base de datos, transacciones, eventos y adaptadores.
- Contrato: APIs internas y externas.
- Componentes: interfaz y estados visibles.
- End-to-end: recorridos completos por perfil y canal.
- Resiliencia: desconexiones, reinicios, reintentos y fallos parciales.
- Seguridad: permisos, aislamiento, abuso y datos sensibles.
- Rendimiento: caja, búsqueda, sincronización y reportes.

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

La aprobación legal de una licencia no reemplaza la revisión técnica; una biblioteca permisiva también puede ser insegura, estar abandonada o no cumplir nuestras invariantes.
