# Ficha de integración — Pos

**Fuente fijada:** MyCompany 6.2 · commit `d21ca6978717b98b6300d90267f9767db7414008`  
**Composición:** incluido en el cierre actual de `RubrovaCustom`, según el catálogo estructural.  
**Evidencia:** revisión estática de fuente; runtime, conciliación y aceptación deben probarse aparte.

**Identificador:** `MODULE Pos` · **Namespace:** `Retail`  
**Fuente:** [Pos.lsf](../../../vendor/mycompany/src/main/lsfusion/retail/pos/Pos.lsf#L1-L55)  
**Dossier:** [Retail, POS, sesiones y devoluciones](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) §§1–3 y 9.

## 1. Lectura de 2 minutos

`Pos` representa una caja lógica o terminal comercial. Mantiene ID, nombre, empresa titular y asignación opcional a computadoras. No es la sesión/turno, el controlador fiscal ni el ledger de caja: esos comportamientos están en otros módulos.

**REQUIRE directos:** RetailSettings, Company, Authentication.

**Consumidores directos:** CRPTCodesOffline (regional ruso), Retail, PaymentMethod, CashRegister, PosDashboard y Session.

## 2. Datos y responsabilidad

Clase `Pos` con:
- ID STRING[20], nombre obligatorio ISTRING[100].
- Empresa propia asociada.
- Asignación por computadora mediante `in(Pos, Computer)`.
- Cuenta/computadora y driver se complementan en módulos CashRegister y Retail.

La empresa se propone desde `defaultCompany()`. La asignación a computadora puede limitar qué cajas ve el dashboard; si no hay asignación, el comportamiento del consumidor puede permitir selección entre las cajas disponibles.

## 3. Formularios y navegación

- `pos`: pantalla de edición de caja con nombre, ID, empresa y asignación a computadora/hostname.
- `poss`: listado de cajas con alta, edición y eliminación.
- `poss` aparece en el navegador bajo configuración.
- El formulario extiende la clase Computer y muestra asignación; no posee por sí mismo selección de sesión ni cobros.

## 4. Casos de uso y relaciones

| Necesidad | Módulo relacionado | Contrato a respetar |
|---|---|---|
| Configurar cajas | Pos | ID, nombre, empresa titular y computadora |
| Seleccionar medio de cobro por caja | PosPaymentMethod / PaymentMethod | Medio habilitado y cuenta titular de la empresa POS |
| Conectar controlador | CashRegister / CashRegisterFiscal | Driver, hardware y contrato fiscal abstracto |
| Abrir turno | Session | Una sesión abierta por POS; apertura/cierre y hooks |
| Operación de venta | PosDashboard | Usa el POS y sesión seleccionados; documentos nativos de ventas |
| Integración regional | CRPTCodesOffline | Código ruso regional, no asumir aplicabilidad argentina |

## 5. Configuración, seguridad y comunicación

- La empresa de POS es autoridad para titularidad de cuentas y medios de pago asignados.
- Asignación a computadora no es autenticación ni autorización por sí sola.
- La fuente exige Authentication; revisar usuario/rol y restricciones reales en formularios/acciones del consumidor.
- No deducir que una caja es fiscal por tener un CashRegister relacionado; el driver y la homologación son controles separados.
- El POS y la sesión forman una relación 1:N histórica, pero la lógica de unicidad de turno abierto reside en Session.

## 6. Pruebas mínimas

1. Crear POS con empresa válida y defaults.
2. ID duplicado, nombre vacío y cambios de empresa.
3. Una PC asignada a varios POS y un POS en varias PC, según configuración admitida.
4. Usuario autenticado con y sin permiso.
5. Cuenta/método de pago perteneciente a otra empresa: rechazo en contrato de pago.
6. Dos POS con sesiones simultáneas y dos aperturas concurrentes en el mismo POS.
7. Controlador/terminal desconectado, timeout y respuesta incierta.
8. Impresora/fiscal/hardware real y conciliación en equipo físico.

**Aceptación:** el dossier marca lectura de 30 fuentes retail; hardware/fiscal, runtime y conciliación siguen pendientes.

## 7. Lecturas siguientes

- [Session](Session.md), [Invoice](Invoice.md) y [Partner](Partner.md).
- [Mapa Retail/POS](../MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) §§2–5 y 9–11.
- [Integración de terminales](../../PAYMENT_TERMINAL_INTEGRATION_ARCHITECTURE.md), [identidad/conciliación](../../PAYMENT_IDENTITY_AND_RECONCILIATION.md) y [seguridad](../../SECURITY_POSTURE.md).
- [Resiliencia](../../INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) para desconexiones y recuperación.

**Regla de integración:** POS identifica la caja y empresa; Session identifica el turno; Payment/Invoice/CashRegister mantienen sus autoridades específicas.
