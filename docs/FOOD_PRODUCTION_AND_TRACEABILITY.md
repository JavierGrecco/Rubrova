# Elaboración de alimentos, rotisería y trazabilidad

**Estado:** especificación funcional priorizada; no significa que el flujo completo esté implementado ni habilitado para uso sanitario/productivo.  
**Primer escenario:** comercio minorista con elaboración propia de comidas preparadas.  
**Principio:** una sola operación comercial e inventario; el perfil gastronómico amplía capacidades sin crear un ERP paralelo.

## 1. Objetivo

Rubrova debe permitir que un comercio venda mercadería comprada y, al mismo tiempo, transforme ingredientes propios en preparaciones, semielaborados y comidas listas para vender. La misma plataforma debe poder crecer hacia panadería, cafetería, restaurante, mayorista, distribución u otros rubros sin rehacer catálogo, clientes, caja, compras, pagos o inventario.

El flujo de elaboración tiene que responder, con datos verificables:

- qué ingredientes y lotes se usaron;
- quién, cuándo y dónde preparó cada tanda;
- qué cantidad se planificó y qué cantidad se obtuvo realmente;
- qué se consumió, qué quedó sin usar y qué se descartó;
- cuánto costó cada tanda y cada porción vendible;
- qué lote de comida terminada sigue disponible y hasta cuándo puede comercializarse según la política aprobada;
- qué ventas o productos terminados podrían verse afectados si se inmoviliza o retira un lote de ingrediente.

Rubrova organiza los datos y controles operativos. No determina por sí solo si una receta, proceso, duración, temperatura o establecimiento cumple la normativa sanitaria.

## 2. Cómo se representa el negocio

Una organización puede combinar, sin duplicar maestros:

- **Comercio minorista:** artículos adquiridos a proveedores, venta por unidad/peso, promociones, caja y atención de mostrador.
- **Elaboración / rotisería:** materias primas, preparaciones intermedias, recetas, tandas, productos terminados, porciones, mermas y pedidos anticipados.
- **Canales:** mostrador, retiro, teléfono, WhatsApp, web y delivery. El canal no crea un inventario ni una venta paralelos.
- **Áreas de resultado:** comercio y elaboración pueden medirse por separado, con consolidación del mismo negocio. Los traslados internos no deben contabilizarse como ventas externas.

### Tipos funcionales de artículo

La clasificación debe ser configurable y no debe sustituir al tipo contable ni al maestro nativo:

1. **Ingrediente / materia prima:** harina, carne, verduras, aceite, condimentos, envases, etc.
2. **Preparación intermedia:** masa, salsa, relleno, caldo o componente que se usa en otra receta.
3. **Producto elaborado:** comida lista, panificado, postre o bebida preparada.
4. **Presentación de venta:** unidad, porción, bandeja, peso o combo. Puede reutilizar el producto elaborado con una regla de presentación, sin crear stock ficticio.
5. **Subproducto aprovechable:** resultado secundario que puede volver a usarse o venderse sólo si el proceso y la política lo permiten.
6. **Merma / descarte:** cantidad que deja de ser utilizable, con motivo, responsable y registro de inventario cuando corresponda.

Las conversiones entre kg, g, litros, ml, unidades, bandejas y porciones deben ser explícitas. No se permite mezclar cantidades incompatibles ni redondear silenciosamente el consumo de ingredientes.

## 3. Reutilización de MyCompany 6.2

La inspección de las fuentes vendorizadas confirma que MyCompany ya incluye un módulo de fabricación requerido por `MyCompany.lsf`. Contiene listas de materiales (BOM/recetas), componentes, subproductos, órdenes de fabricación, consumo, productos terminados, costos, merma y lotes:

- [Módulo de fabricación](../vendor/mycompany/src/main/lsfusion/manufacturing/Manufacturing.lsf)
- [BOM y componentes](../vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf)
- [Órdenes de fabricación](../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf)
- [Consumo, producción y costo](../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrderCost.lsf)
- [Lotes de producción](../vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrderLot.lsf)

También existe inventario por lote en [InvLedgerLot](../vendor/mycompany/src/main/lsfusion/inventory/ledgers/inv/InvLedgerLot.lsf) y captura de lotes en el POS mediante [PosDashboardLot](../vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboardLot.lsf). Las extensiones nativas de fabricación y facturación conservan las cantidades por lote en líneas de consumo/producción y venta.

**Límites adicionales confirmados en la fuente actual:**

- El maestro nativo `Inventory.Lot` guarda identificador y producto, pero no fecha de elaboración, vencimiento ni condiciones de conservación.
- La acción nativa `Manufacturing.checkAvailability` de `ManufacturingOrderReady.lsf` calcula disponibilidad por ubicación y producto (`prevAvailable(location, item))); no elige ni reserva lotes FEFO. La existencia de `ManufacturingOrderLot.lsf` permite asignar cantidades por lote en las líneas, pero no demuestra que el chequeo de disponibilidad haya validado cada lote.
- El macro nativo `defineDocLot` verifica que el producto del lote coincida con el de la línea y que la suma asignada a lotes no quede por debajo de la cantidad cuando el documento queda listo. No evalúa vencimiento, cuarentena ni vida útil.
- `PosDashboardLot.processBarCode` incrementa la cantidad del lote escaneado en la línea POS, pero el código inspeccionado no comprueba allí vencimiento ni retención. El escaneo debe seguir siendo una captura; la autorización debe comprobarse antes de confirmar la venta y contabilizar su salida.
- `ReceiptDone.validate` puede ofrecer completar cantidades recibidas vacías con `initialDemand` en recepciones no inmediatas; para alimentos no se debe confundir la cantidad prevista con la pesada/contada. Hay que exigir confirmación del dato físico y verificar el comportamiento de recepciones inmediatas en el runtime concreto.
- `ManufacturingOrderDone.markAsDone` completa cantidades reales desde las cantidades planificadas cuando esas cantidades no fueron ingresadas. Para alimentos, ese comportamiento requiere una barrera explícita de confirmación/revisión antes de cerrar una tanda.

### Mapa técnico de trazabilidad nativa

La ruta de los datos ya está distribuida entre los documentos y el ledger existentes:

| Etapa | Módulo nativo | Dato que ya relaciona | Trabajo propio pendiente |
|---|---|---|---|
| Recepción | `ReceiptLot` | Lote en cada línea de recepción (`ReceiptLine`) y movimientos en `ReceiptInvLedger` | Incorporar metadata alimentaria y retención de lotes; no marcar como apto por el solo hecho de recibirlo |
| Factura de compra → recepción | `BillReceiptLot` | Copia las cantidades por lote de la factura a las líneas recibidas | Comprobar que la metadata y las referencias del lote sobrevivan el flujo real de recepción |
| Consumo de ingredientes | `ManufacturingOrderLot` | Lotes y cantidades por línea consumida | Rechazar lotes bloqueados/vencidos en el momento de consumo y validar saldo disponible del lote |
| Producto terminado | `ManufacturingOrderLot` | Lotes y cantidades producidas; permite generar identificadores para nuevos lotes | Exigir cantidad real, responsable y fecha/vida útil aprobada antes de cerrar la tanda |
| Venta POS | `PosDashboardLot` + `InvoiceLot` | Captura lote en el POS y mantiene cantidad por lote en la línea de venta | Aplicar elegibilidad, vigencia y saldo por lote antes de confirmar la venta |
| Despacho | `ShipmentLot` + `InvoiceShipmentLot` | Conserva la asignación de lote en las líneas despachadas | Comprobar que no pueda despacharse una cantidad mayor ni un lote retenido |
| Devolución | `CreditNoteLot` | Copia los lotes de las líneas originales a la nota de crédito | Definir cuarentena/inspección del retorno; no reincorporar automáticamente alimentos devueltos al stock vendible |
| Saldo y movimientos | `InvLedgerLot` | Calcula entradas, salidas y existencia por ubicación y lote | Mantener el ledger nativo como autoridad y conciliar el agregado por producto con sus lotes |

La relación de documentos y los movimientos por lote son la base de la trazabilidad hacia atrás y hacia adelante. La interfaz de consulta consolidada todavía debe construirse y verificarse con documentos reales del runtime; no se presume que una relación existente en fuente sea ya un informe de recall operativo.

### Contrato propuesto para la extensión Rubrova

- Mantener `Inventory.Lot` como identidad maestra. Agregarle metadata propia (fecha/hora de elaboración o fraccionamiento, límite de duración aprobado, tipo de fecha, condición de conservación, estado de retención/bloqueo, motivo y responsable), sin duplicar el lote ni los movimientos.
- Distinguir los productos que requieren trazabilidad alimentaria de los que usan lotes por otros motivos. El flag nativo `MasterData.dataUseLot(Product)` controla el uso general de lotes; la política de inocuidad debe aplicarse sólo al subconjunto alimentario que se configure explícitamente.
- Permitir recibir un lote y dejarlo en revisión/retención. La recepción física no constituye por sí sola una autorización de uso o venta.
- En la salida para consumo, fabricación, venta o despacho, comprobar en una única transacción: producto correcto, lote elegible para la fecha de operación, no retenido, saldo positivo suficiente y cantidad asignada igual a la línea.
- Al terminar fabricación, no completar cantidades reales con el plan. Exigir revisión explícita de consumos y rendimiento; los lotes de salida deben tener su fecha de elaboración y un límite de uso aprobado por el responsable.
- En devoluciones de alimentos, conservar el vínculo con lote original y registrar inspección/retención antes de cualquier reincorporación al inventario vendible.
- Mantener historial de cambios de metadata y acciones de retención; los usuarios operativos no deben poder borrar o alterar retroactivamente el origen.

No se activará FEFO automático hasta que exista una asignación por lote determinista, con bloqueo transaccional, manejo de concurrencia y pruebas contra doble consumo. Una lista ordenada por vencimiento no es una reserva. No se inventarán duraciones, temperaturas ni plazos genéricos.

Por lo tanto, el POS admite captura de lotes y fabricación mantiene relaciones por lote, pero **Rubrova todavía no selecciona automáticamente FEFO, no bloquea alimentos vencidos/retendidos ni garantiza reservas/consumos válidos por lote**.

La estrategia es extender los documentos, lotes y ledgers nativos; no crear una segunda receta, un segundo stock, una segunda caja ni un ledger alternativo en Python.

## 4. Recetas y versiones

Cada receta debe tener:

- producto resultante y cantidad base/rendimiento esperado;
- componentes, cantidad y unidad;
- subrecetas o preparaciones intermedias;
- cantidades variables y tolerancias autorizadas cuando existan;
- rendimiento teórico, porciones y presentación de venta;
- pasos, centro de trabajo y tiempos planificados cuando el perfil lo requiera;
- costo estimado y origen de cada costo;
- vigencia, estado, responsable de aprobación y motivo de revisión.

**Regla de versionado:** una receta que ya se utilizó en producción no se modifica para reescribir el pasado. Se crea una nueva versión/BOM, se conserva la anterior y cada orden de fabricación mantiene la receta y las cantidades que se usaron al planificarla. La revisión debe comprobar cómo se comporta el snapshot de líneas en MyCompany antes de dar por garantizada esa inmutabilidad.

Los cambios de proveedor, marca o precio de un ingrediente pueden cambiar el costo sin que necesariamente cambie la formulación. Una modificación de ingredientes, proporciones, proceso o rendimiento sí requiere una nueva versión y revisión de los datos asociados.

Las declaraciones de alérgenos deben ser revisables por personas responsables. La composición teórica de una receta no permite asegurar ausencia de contaminación cruzada.

## 5. Orden de elaboración y tanda

Cada tanda se gestiona como una orden nativa de fabricación con:

- sucursal, sector, ubicación de ingredientes y ubicación de producto terminado;
- fecha y franja planificada, prioridad, responsable y estado;
- receta vigente y rendimiento previsto;
- ingredientes y lotes que se reservarán/consumirán;
- producción real por producto y lote;
- cantidades no utilizadas, sustituciones y diferencias;
- subproductos, mermas, descartes y motivo;
- tiempos, controles y observaciones requeridos por el procedimiento del negocio.

Estados funcionales propuestos: borrador, planificada, preparada, en elaboración, pendiente de control, terminada, cancelada. Deben mapearse a estados nativos siempre que sea posible; no se agrega un segundo ciclo de vida si MyCompany ya representa el mismo concepto.

### Diferenciar plan de realidad

Una cantidad planificada no puede presentarse como cantidad realmente elaborada. La confirmación final debe exigir revisión explícita de cantidades reales de ingredientes y productos terminados, con registro del responsable. Si un flujo nativo completa automáticamente valores planificados cuando faltan datos, Rubrova debe colocar una barrera de revisión para el perfil alimentario antes de habilitarlo en un comercio real.

Una tanda terminada debe producir, dentro del mismo circuito transaccional:

- movimientos de salida de los ingredientes realmente consumidos;
- movimientos de entrada de los productos efectivamente obtenidos;
- lotes de entrada/salida vinculados a la orden;
- costos trazables;
- registros de merma y subproductos;
- historial persistente después de reiniciar el sistema.

No se contabiliza como venta el pase de ingredientes a producción ni el ingreso de una comida terminada al depósito.

## 6. Lotes y trazabilidad de dos vías

El vínculo de trazabilidad debe poder recorrerse en ambos sentidos:

**Proveedor → recepción → lote de ingrediente → orden/tanda → lote de producto elaborado → ubicación/venta/pedido.**

Y a la inversa:

**Lote de producto elaborado → tanda → ingredientes y lotes usados → recepciones/proveedores → otras tandas afectadas.**

El registro de lote alimentario debe contemplar, como mínimo:

- código de lote legible y único dentro de la política definida;
- producto, proveedor u orden de fabricación de origen;
- fecha/hora de recepción cuando aplique;
- fecha/hora de elaboración o fraccionamiento cuando aplique;
- fecha/hora límite o de duración aprobada para el uso previsto;
- tipo de fecha declarado (por ejemplo, consumo preferente o vencimiento, según corresponda);
- ubicación y condición de conservación;
- cantidad recibida, producida, consumida, transferida, vendida y descartada;
- responsable y evidencia de los cambios.

No se debe inventar vida útil a partir de una receta ni aplicar un plazo universal a comidas preparadas. La vida útil, las condiciones de almacenamiento y la clasificación/rotulado deben ser definidas por el responsable competente y ajustarse al producto, proceso y normativa aplicable.

### FEFO, vencimiento e inmovilización

El sistema debe sugerir primero los lotes elegibles con vencimiento más próximo (FEFO), siempre que su disponibilidad y ubicación lo permitan. La regla debe:

- impedir asignar lotes vencidos a nuevas ventas;
- impedir consumir en producción lotes vencidos o bloqueados;
- alertar lotes próximos a vencer sin convertir una alerta en autorización para vender;
- soportar bloqueo, cuarentena, retiro y descarte autorizados;
- registrar la excepción, el usuario y el motivo sin permitir borrar el historial;
- conciliar el saldo por lote con el saldo total del producto.

Si la venta requiere trazabilidad por lote, el cobro no se confirma con una cantidad sin lote o con un lote no elegible. La asignación debe funcionar también con lectores y pantalla táctil, no sólo desde una ficha administrativa.

## 7. Inocuidad y controles de proceso

El perfil debe permitir registrar controles operativos definidos por el establecimiento, por ejemplo:

- temperatura de recepción, almacenamiento, cocción, enfriamiento, exhibición y despacho;
- fecha/hora, punto de control, equipo/termómetro, lectura, responsable y resultado;
- procedimiento aplicable, límite configurado y acción correctiva;
- limpieza y desinfección de equipos/superficies cuando el proceso lo requiera;
- incidente, lote afectado, decisión de retener/descartar y aprobación.

Los límites deben parametrizarse por tipo de alimento, etapa y procedimiento validado. No se debe convertir un valor ilustrativo de un manual en un límite universal. Una lectura faltante no se debe tratar como un control aprobado.

Una alerta de temperatura fuera de rango debe dejar la partida o lote identificado para revisión. El software registra la observación y el flujo de respuesta; no decide que un alimento sea seguro ni sustituye el criterio sanitario.

## 8. Costo y rentabilidad de cada preparación

El costo real de una tanda debe separar:

- costo de ingredientes según el ledger y la política de valoración;
- envases y consumibles;
- mano de obra imputada;
- energía, servicios u otros costos indirectos cuando exista un método transparente de asignación;
- merma normal/anormal y subproductos;
- cantidad real vendible y unidades de medida.

Indicadores: costo planificado vs real, rendimiento teórico vs real, costo por kg/unidad/porción, margen de contribución y variación explicada. Nunca se debe calcular el costo unitario dividiendo por el rendimiento previsto cuando la producción real fue distinta, ni presentar un costo incompleto como si fuera el costo total.

Las ventas, consumos internos, pérdidas, invitaciones y descartes deben permanecer diferenciados.

## 9. Planificación de la producción

La planificación debe combinar, en este orden de madurez:

1. pedidos y encargos confirmados;
2. ventas históricas comparables por día y franja;
3. estacionalidad y calendario;
4. disponibilidad real de ingredientes, reservas, vencimientos y plazos de proveedor;
5. capacidad de cocina, equipos y personal;
6. criterio y ajuste manual del responsable.

El pronóstico debe distinguir ventas observadas de demanda no atendida por falta de stock. Una sugerencia de producción no debe crear órdenes ni consumir inventario sin aprobación.

## 10. Aceptación mínima antes del piloto

No basta con que el módulo compile. Como mínimo deben existir escenarios automatizados y aceptación supervisada de:

1. Crear receta, cambiar su versión y demostrar que una tanda histórica conserva cantidades y receta original.
2. Planificar una tanda, reservar ingredientes y rechazar una reserva insuficiente.
3. Consumir cantidades reales distintas del plan y registrar mermas con motivo.
4. Producir más de un producto/subproducto y conciliar cantidades y costos.
5. Asignar lotes de ingredientes a la tanda y generar lotes de salida.
6. Consultar trazabilidad hacia atrás y hacia adelante desde cualquier lote.
7. Rechazar lotes vencidos/bloqueados al consumir o vender.
8. Aplicar FEFO sin asignar más cantidad que la disponible por lote.
9. Reconciliar por producto y lote después de reinicio y restauración.
10. Registrar controles de temperatura y mostrar una desviación como pendiente de resolución, nunca como aprobación automática.
11. Ejecutar ventas simultáneas y confirmar que no haya doble consumo de stock ni saldo negativo.
12. Verificar permisos, auditoría y reversión compensatoria de operaciones erróneas.

Los datos iniciales deben ser sintéticos y reproducibles. El piloto con alimentos y datos comerciales requiere validación presencial, responsables identificados y procedimientos aprobados por el establecimiento.

## 11. Implementación por etapas

### P0 — base segura de elaboración
- comprobar en runtime nativo MyCompany BOM, orden, reservas, consumo, producto terminado, lote y costo;
- prueba de principio a fin con datos sintéticos, conciliación y persistencia;
- distinguir plan/realidad y bloquear cierres sin revisión explícita;
- definir contrato de metadatos de lote y política FEFO;
- documentar límites de la cobertura y no habilitar funciones incompletas en el perfil real.

### P1 — uso diario de rotisería
- recetas/versiones y costos por porción;
- programación de tandas y tablero de cocina;
- captura rápida de consumos, rendimiento, merma y sobrantes;
- lotes/fechas/ubicaciones, etiquetas y alertas;
- venta y despacho vinculados con productos preparados.

### P2 — control y crecimiento
- controles de temperatura/proceso, retenciones y acciones correctivas;
- trazabilidad inversa para retiro/recall;
- pronóstico por día/franja y sugerencia de producción;
- costos indirectos, capacidad y rentabilidad por unidad de negocio;
- pedidos online, WhatsApp/delivery y múltiples sucursales.

No avanzar a P2 mientras P0 no esté probado en la operación concreta.

## 12. Marco sanitario y límites del sistema

El diseño debe mantenerse alineado con la normativa vigente y la clasificación que corresponda a cada producto y establecimiento. El Código Alimentario Argentino es una norma técnica de actualización permanente y distribuye competencias entre autoridades nacionales, provinciales y municipales. Los requisitos de rotulado, identificación de lote, duración, registros y habilitaciones pueden variar según el producto, proceso, presentación y ámbito de comercialización.

Fuentes oficiales de referencia:

- [Código Alimentario Argentino — ANMAT / Argentina.gob.ar](https://www.argentina.gob.ar/salud/codigoalimentario)
- [Manual de Manipulación Segura de Alimentos — ANMAT, 3.ª edición, diciembre de 2025](https://www.argentina.gob.ar/sites/default/files/anmat_manual_ma_2025.pdf)
- [Rotulado de alimentos — Argentina.gob.ar](https://www.argentina.gob.ar/node/104711)
- [Normativa actualizada — identificación de lote y fecha de duración](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-149-2005-110017/actualizacion)

Este documento define requisitos de producto, no un dictamen bromatológico. Antes de activar funciones de rotulado, vida útil, temperatura o habilitación hay que confirmar su alcance con la autoridad sanitaria competente y el responsable de alimentos del establecimiento.
