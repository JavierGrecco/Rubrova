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
