# Mapa de dominios, relaciones y propiedad de datos

**Alcance inicial:** integración de reposición con MyCompany 6.2.  
**Estado:** extensión integrada en `main`; el smoke macOS ARM64 [45855055565](https://github.com/JavierGrecco/Rubrova/actions/runs/45855055565) ejecutó las sondas y verificó las colecciones de exportación contra fixtures sintéticas. Sigue pendiente la conciliación contra una base MyCompany local con datos comerciales controlados.  
**Regla de lectura:** una expresión de relación usada por el código es evidencia de cómo el módulo navega el modelo; no implica que conozcamos todas las restricciones internas, cardinalidades o claves físicas del ERP.

## 1. Recorrido entre componentes

```text
MyCompany 6.2 / lsFusion 6.2
    |
    | consultas autenticadas @@api (solo lectura)
    v
RubrovaReplenishmentExport
    |-- inventario por ubicación/producto
    |-- compromisos por línea de venta
    |-- recepciones por ledger
    |
    v
JSON nativo versionado
    |
    +--> inspect-mycompany-ui.py
    |       valida HTTP, esquema, conteos y conciliaciones en el smoke
    |
    +--> adapt_mycompany_native_export.py
            valida y normaliza un archivo JSON
                |
                v
        import_mycompany_snapshot.py
                |
                v
        plan_replenishment.py
```

El adaptador Python no consulta directamente la base de datos ni llama a RMI/HTTP de MyCompany. La comunicación con el ERP está aislada en las acciones nativas autenticadas y en el proceso de inspección del smoke.

## 2. Matriz de propiedad

| Concepto | Fuente propietaria actual | Consumidor | Observación |
|---|---|---|---|
| Stock físico | MyCompany `Inventory` | Exportación / planificador | Ledger de movimientos físicos |
| Disponible nativo | MyCompany `Inventory.available` | Exportación / planificador | No recalcularlo sustituyendo la propiedad nativa |
| Reserva neta planificada | MyCompany `Inventory.planned` | Exportación / planificador | Conserva signo y semántica del ERP |
| Línea abierta de venta | MyCompany `Sales.OrderLine` | Exportación / planificador | La cantidad abierta procede de `Sales.toShip` |
| Reserva de despacho | MyCompany `ShipmentResLedger` | Exportación / planificador | Se consolida por línea de venta |
| Recepción prevista | MyCompany `ReceiptResLedger` y entidades relacionadas | Exportación / planificador | Se mantiene el signo del ledger |
| Política de planificación | Fixture/configuración explícita de Rubrova | Adaptador / planificador | No se infiere a partir de stock ni de ventas |
| Snapshot de planificación | Adaptador de Rubrova | Planificador | Es una representación derivada, no reemplaza el origen |

## 3. Relaciones observadas en las expresiones LSF

### 3.1 Inventario por ubicación y producto

La consulta usa el par `(Location, Product)` como ámbito de inventario y consulta las propiedades:

- `Inventory.inQuantity(l, p)`
- `Inventory.outQuantity(l, p)`
- `Inventory.onHand(l, p)`
- `Inventory.available(l, p)`
- `Inventory.reserved(l, p)`
- `Inventory.planned(l, p)`
- `Inventory.expected(l, p)`

**Interpretación adoptada:** la clave de conciliación del inventario exportado es `(productId, locationId)`. Es obligatorio rechazar pares duplicados.

**Distinción de dominio:** `onHand` representa existencia física; `available` es el valor nativo del ERP; `planned` representa reservas netas firmadas que participan en el cálculo de disponible. No son campos intercambiables.

**Conciliación actual del adaptador:** `available = onHand - plannedNetReservation`. Se rechaza cualquier diferencia a la precisión que declara el contrato. Esta regla tiene que mantenerse compatible con la versión fijada de MyCompany y volver a comprobarse ante cambios de versión o de configuración de inventario.

### 3.2 Compromisos de salida

Las relaciones navegadas por el módulo son:

1. `Sales.OrderLine ol` identifica la línea.
2. `Sales.order(ol)` navega a la orden.
3. `Sales.shippedProduct(ol)` obtiene el producto.
4. `Sales.location(Sales.order(ol))` obtiene la ubicación asociada a la orden.
5. `Sales.toShip(ol)` determina la cantidad todavía abierta.
6. `Sales.scheduledDateTime(Sales.order(ol))` determina la fecha prevista.
7. `Inventory.ShipmentResLedger rr` se relaciona con la línea de MyCompany mediante `Sales.orderLine(Inventory.line(rr)) = ol`.
8. La suma de `Inventory.lineReserved(Inventory.line(rr))` se agrupa por la línea `ol`.

Filtro exportado: orden confirmada, cantidad abierta mayor que cero y producto/ubicación navegables.

**Interpretación:** una línea de venta parcialmente despachada se representa una sola vez con la cantidad que falta despachar y la reserva efectiva agregada. No generar un compromiso por cada movimiento parcial del ledger.

**Identidad de intercambio:** `Sales.number(Order) + Sales.index(OrderLine)`. Esta clave compuesta es una identidad de contrato, no una promesa de que sea el identificador primario interno de la base.

### 3.3 Recepciones previstas

Relaciones navegadas:

1. `Inventory.ReceiptResLedger rr` identifica la reserva de recepción.
2. `Inventory.line(rr)` navega a la línea de inventario.
3. `Inventory.receipt(Inventory.line(rr))` navega a la recepción.
4. `Purchase.orderLine(Inventory.line(rr))` obtiene la línea de orden de compra relacionada.
5. `Purchase.order(...)` obtiene la orden de compra.
6. `Inventory.product(Inventory.line(rr))` obtiene el producto.
7. `Inventory.location(Inventory.receipt(...))` obtiene la ubicación asociada.
8. `Inventory.scheduledDateTime(...)` determina la fecha prevista.
9. `Inventory.increaseAvailableStock(Inventory.type(...))` conserva la política del tipo de recepción.

Filtro exportado: recepción lista, no completada, no cancelada y orden de compra confirmada.

**Semántica de cantidad:** `Inventory.reserved(rr)` conserva el signo negativo del ledger; `expectedQuantity` se representa como `0 - reserved`, una magnitud positiva.

**Identidad de intercambio:** número de recepción + índice de línea. Se exporta además la referencia compuesta a la línea de compra para trazabilidad.

## 4. Relaciones que todavía no deben asumirse

- No asumir que el número visible de un documento es una clave primaria global, ni que lo es fuera de la compañía/serie correspondiente.
- No asumir cardinalidad uno-a-uno entre una línea de venta y sus movimientos de despacho: precisamente se agregan varios registros del ledger por línea.
- No asumir que cada reserva negativa del ledger representa una recepción elegible: la política de elegibilidad filtra las recepciones que el planificador puede tratar como entrada confirmada.
- No asumir que todas las recepciones incrementan el disponible de inmediato: conservar `increaseAvailableStock`.
- No asumir que una ubicación con cero movimientos debe aparecer en el listado actual: el filtro de inventario selecciona pares con cantidades o reservas relevantes.
- No inferir moneda, unidad de medida, conversión de unidades o zona horaria a partir de nombres o valores; deben ser campos explícitos del contrato.
- No tratar identificadores compuestos del contrato como claves de escritura hacia MyCompany.

## 5. Pendientes para confirmar con base real

1. Obtener una exportación autenticada desde una base MyCompany local controlada.
2. Comparar `inventoryCount` y longitudes de listas con una consulta de referencia dentro del ERP.
3. Confirmar conteos y cardinalidades de líneas parcialmente despachadas y recepciones parciales.
4. Verificar ubicaciones, productos inactivos, productos sin movimiento y registros sin referencia comercial.
5. Comprobar fechas con configuración regional/zona horaria y cambios de horario.
6. Verificar la unicidad práctica de las identidades compuestas en las series y compañías que soporte la instalación objetivo.
7. Registrar cualquier diferencia entre fixture, código y datos reales como decisión o iteración nueva.

## 6. Regla para ampliar este mapa

Cada módulo nuevo debe añadir:

- dueño de cada dato;
- entidad/propiedad de origen;
- relaciones usadas y sentido de navegación;
- cardinalidad observada o desconocida;
- clave técnica y clave de intercambio (si son distintas);
- invariantes y filtros;
- consumidores;
- nivel de evidencia;
- comportamiento ante ausencia, duplicado, borrado lógico y cambio de versión.

La falta de conocimiento se registra como desconocida; nunca se completa inventando una relación.
