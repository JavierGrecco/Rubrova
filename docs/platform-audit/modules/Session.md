# Ficha de integración — Session


**Fuente fijada:** MyCompany 6.2 · commit d21ca6978717b98b6300d90267f9767db7414008  
**Composición:** dentro del cierre actual de RubrovaCustom, según el catálogo estructural.  
**Evidencia:** lectura de fuente estática; no equivale a runtime, conciliación ni aceptación.

**Identificador real:** MODULE Session · **Namespace:** Retail  
**Fuente:** [Session.lsf](../../../vendor/mycompany/src/main/lsfusion/retail/sessions/Session.lsf#L1-L124)  
**Dossier:** [Retail, POS, sesiones y devoluciones](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) §§3 y 11.

## 1. Resumen de 2 minutos

Session representa el turno de una caja POS: apertura, cierre, número y POS asociado. Define hooks para extender comportamiento antes y después de abrir/cerrar. Facturas, notas, despachos y pagos se asocian mediante módulos consumidores.

**REQUIRE directos:** MetaNumerator, Time, DateUtils, RetailSettings, Pos.

**Consumidores directos:** Retail, PosDashboard y SessionInvoice.

## 2. Entidad y reglas

Clase: Session.

| Propiedad | Semántica |
|---|---|
| openingDateTime | Fecha/hora de apertura, inicializada al crear |
| closingDateTime | Fecha/hora de cierre |
| opened | Abierta cuando hay apertura y no hay cierre |
| number | Numerador de sesión |
| pos | POS al que pertenece |

Una constraint impide cierre anterior a la apertura. openedSession(Pos) agrupa la sesión abierta por POS.

## 3. Abrir una sesión

La acción openSession(Pos p):
1. Cancela la sesión de contexto anterior.
2. Abre NEWSESSION.
3. Comprueba que no exista otra sesión abierta para ese POS.
4. Crea una sesión y asigna POS.
5. Ejecuta beforeOpen.
6. Si breakSession() no interrumpe el flujo, ejecuta APPLY.
7. Sólo si no queda cancelada, ejecuta afterOpen.

Si ya hay una sesión abierta para esa caja, muestra un mensaje y no crea otra.

## 4. Cerrar una sesión

La acción close(Session s):
1. Cancela el contexto anterior y abre NEWSESSION.
2. Asigna closingDateTime con la hora actual.
3. Ejecuta beforeClose.
4. Si no se interrumpe el proceso, ejecuta APPLY.
5. Si no queda cancelado, ejecuta afterClose.

Los hooks abstractos son beforeOpen, afterOpen, beforeClose y afterClose. Son puntos de extensión previstos; no insertar otra rutina de apertura/cierre sin revisar extensiones existentes.

## 5. Comunicación y efectos

- Pos es requisito y determina la caja de la sesión.
- PosDashboard consume la sesión para operar en caja.
- SessionInvoice vincula facturas/notas al turno y calcula ventas, devoluciones y neto.
- SessionPayment presenta cobros/reintegros por medio; revisar su relación con IncomingPayment/OutgoingPayment.
- SessionShipment relaciona despachos con el turno.
- Session no reemplaza la autoridad de factura, pago, caja/banco ni stock.

## 6. Seguridad y operación

La unicidad del turno abierto está implementada en la acción por POS. Esta ficha no demuestra el comportamiento concurrente bajo doble clic, dos terminales o múltiples servidores. Revisar permisos de POS/usuario y visibilidad del dashboard en runtime.

No cerrar la sesión si conciliaciones u operaciones pendientes no concluyeron, salvo política explícita y evidencia de recuperación. Registrar qué ocurre con documentos abiertos, pagos pendientes y desconexión.

## 7. Pruebas mínimas

1. Abrir sesiones en dos POS distintos: ambas deben coexistir.
2. Segunda sesión abierta para el mismo POS: debe impedirse.
3. Dos aperturas concurrentes para el mismo POS: comprobar que no se duplique.
4. beforeOpen que interrumpe: no debe persistir la sesión.
5. afterOpen: sólo tras APPLY exitoso.
6. Cierre normal y cierre interrumpido por beforeClose.
7. No permitir cierre anterior a apertura.
8. Asociar facturas, notas, pagos y despachos; conciliar totales por sesión.
9. Corte/reapertura: verificar sesión persistida y documentos pendientes.

**Estado de aceptación:** fuente revisada; concurrencia, cierre y conciliación pendientes.

## 8. Lecturas siguientes

- [Mapa Retail/POS](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) §§2–5 y §11.
- Pos, PosDashboard, SessionInvoice, SessionPayment, SessionShipment.
- [Facturación y pagos](../MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) y [ventas](../MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md).
- [Capacidades lsFusion](../LSFUSION_6_2_CAPABILITY_MAP.md) para NEWSESSION/APPLY/CANCEL y hooks.
- [Resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) para interrupciones y operaciones inciertas.

**Definición de terminado:** demostrar asociación, autorización, conciliación de importes y recuperación ante corte.
