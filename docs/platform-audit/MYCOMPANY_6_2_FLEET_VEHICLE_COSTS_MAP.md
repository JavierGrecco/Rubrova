# MyCompany 6.2 — mapa de flota, conductores, kilometraje, servicios y gastos

**Estado: 13 fuentes LSF inventariadas; entidades y relaciones principales revisadas. Pruebas de runtime, conciliación de gastos y automatizaciones de mantenimiento pendientes.**

El dominio `fleet` administra vehículos, modelos, conductores, contratos, servicios y gastos asociados. No se debe asumir que tener campos de vencimiento o kilometraje implica alertas automáticas ni planificación preventiva.

## 1. Inventario de los 13 módulos

| Área | Módulos |
|---|---|
| Raíz y configuración | `Fleet`, `FleetSettings` |
| Vehículos | `Vehicle` |
| Fabricante y modelo | `VehicleManufacturer`, `VehicleModel` |
| Categorías y combustible | `VehicleCategory`, `FuelType` |
| Etiquetas | `VehicleTag` |
| Asignaciones de conductores | `VehicleDriver` |
| Contratos | `VehicleContract` |
| Servicios y mantenimiento registrado | `VehicleService`, `VehicleServiceType` |
| Integración con facturas de proveedor | `BillVehicleService` |

`Fleet` compone vehículo, servicio, contrato, conductor, etiquetas y su integración con facturas de proveedor.

## 2. Vehículo

Fuente: `fleet/vehicles/Vehicle.lsf`.

La ficha `Vehicle` guarda:
- ID/numeración propia;
- modelo;
- dominio/patente;
- VIN de 17 caracteres;
- empresa titular;
- categoría;
- color;
- año de fabricación;
- cantidad de asientos y puertas;
- cilindrada;
- transmisión automática (sí/no);
- tipo de combustible;
- fecha y costo de adquisición;
- fecha de inspección y fecha de vencimiento;
- nota y descripción;
- archivos y comentarios.

El nombre visible se compone con modelo y patente. El vehículo puede tener manufacturer/model como catálogos separados.

### 2.1 Catálogos de referencia

- `VehicleManufacturer` mantiene fabricantes.
- `VehicleModel` vincula modelo con fabricante.
- `VehicleCategory` clasifica vehículos.
- `FuelType` define combustibles.
- `VehicleTag` agrega etiquetas múltiples por vehículo y permite filtrar/listar.

Los catálogos son datos maestros; la ficha del vehículo no se completa correctamente si se dejan categorías/modelos/combustibles inconsistentes.

### 2.2 Inspecciones y vencimientos

La ficha tiene `inspectionDate` y `inspectionDueDate`. En la fuente revisada son datos almacenados en el vehículo. No encontré todavía:
- regla que calcule automáticamente el siguiente vencimiento;
- notificación o alerta por proximidad;
- bloqueo de asignación o uso al vencer;
- historial de inspecciones por evento.

Por lo tanto, no se debe afirmar que el sistema administra VTV/ITV o vencimientos automáticamente sólo por tener esos campos.

## 3. Asignación de conductores por período

Fuente: `fleet/vehicles/VehicleDriver.lsf`.

La entidad `VehicleDriver` enlaza:
- vehículo;
- fecha de inicio;
- fecha hasta;
- empleado/conductor;
- odómetro al momento de asignación;
- nota.

Al crear el vínculo se propone la fecha actual. Si no se especifica conductor, el código puede copiar el último conductor registrado para ese vehículo.

Para determinar conductor actual en una fecha:
- se consideran asignaciones cuya fecha sea menor o igual a la fecha consultada;
- se descartan asignaciones cuya fecha hasta sea anterior a esa fecha;
- se toma la última según fecha/orden.

Esto permite reconstruir conductor por período y mostrar un conductor actual en la ficha del vehículo.

**Pendiente:** probar asignaciones superpuestas, dos asignaciones con la misma fecha, cambio retroactivo, cierre de la asignación anterior, fecha hasta igual a fecha desde, vehículo sin conductor y fecha histórica. La fuente revisada no debe interpretarse como garantía de que los intervalos nunca se superponen.

## 4. Servicios, odómetro y gastos

Fuente: `fleet/vehicles/service/VehicleService.lsf`.

Cada `VehicleService` registra:
- vehículo;
- fecha;
- proveedor;
- tipo de servicio;
- odómetro;
- cantidad;
- precio unitario;
- importe sin impuestos;
- impuesto;
- nota y descripción.

Reglas observadas:
- fecha por defecto: fecha actual;
- al modificar cantidad o precio, recalcula importe como cantidad × precio;
- al cambiar vehículo, puede proponer el último proveedor y el último odómetro registrados para ese vehículo;
- la ficha del vehículo muestra servicios relacionados, con proveedor, tipo, fecha, odómetro, cantidad, precio e importes.

El módulo mantiene el servicio como un registro de gasto/actividad de vehículo. No equivale automáticamente a una orden de trabajo de taller ni a una reparación planificada.

### 4.1 Tipos de servicio

`VehicleServiceType` es un catálogo configurable de tipos (por ejemplo, mantenimiento, reparación u otras categorías que la organización configure). La fuente mantiene nombre/ID, sin un motor de planificación por sí solo.

### 4.2 Historial de odómetro

El odómetro se registra en asignaciones y servicios. Permite consultar lecturas relacionadas con cambios de conductor y trabajos realizados. La fuente revisada no demuestra:
- validación universal de que el odómetro nunca retroceda;
- cálculo automático de kilómetros recorridos;
- alertas por intervalo de kilometraje;
- calendario automático de mantenimiento.

Estos comportamientos deben probarse o identificarse en otros módulos antes de considerarlos disponibles.

## 5. Contratos vinculados al vehículo

Fuente: `fleet/vehicles/VehicleContract.lsf`.

La extensión agrega al tipo de contrato una marca que determina si el contrato puede asociarse a un vehículo. Si el tipo no permite vehículo, la restricción impide seleccionar uno.

El vehículo muestra sus contratos asociados con:
- número;
- nombre/tipo;
- fecha y fecha final;
- empresa y socio;
- costo de activación;
- costo recurrente y período.

El módulo busca el contrato más reciente por vehículo/tipo para mostrar datos resumidos.

Esto permite asociar contratos de leasing/alquiler u otros tipos configurados, pero no demuestra una administración automática de renovaciones, seguros, patentes o vencimientos.

## 6. Integración con factura de proveedor

Fuente: `fleet/invoicing/bills/vehicles/BillVehicleService.lsf`.

El tipo de factura de proveedor tiene una marca `vehicle`. Cuando está activada:
- se puede asociar un registro de servicio de vehículo con una `Bill`;
- el registro de servicio copia fecha/proveedor/importe/impuesto de la factura si esos datos no fueron definidos;
- la factura muestra el listado de servicios de vehículo asociados;
- se agregan al pie de factura los totales sin impuestos e impuestos de esos servicios;
- la ficha del vehículo puede abrir la factura relacionada.

**Distinción contable:** el registro de servicio y la factura son objetos distintos unidos por una referencia. El costo de servicio no debe duplicarse con otra línea de factura ni contarse dos veces en reportes. Hay que probar el efecto en deuda, cuentas, impuestos, costo de vehículo y resultados.

## 7. Relaciones transversales

| Entidad | Relación |
|---|---|
| Empresa | Titular del vehículo |
| Fabricante/modelo | Catálogos de marca/modelo |
| Categoría/combustible | Clasificación del activo |
| Conductor/empleado | Asignaciones por fecha e historial |
| Odómetro | Lecturas al asignar conductor y registrar servicio |
| Servicio | Fecha, proveedor, tipo, cantidad, precio, impuesto |
| Factura de proveedor | Puede contener servicios de vehículo y consolidar importes |
| Contrato | Relación por tipo habilitado y vehículo |
| Archivos/comentarios | Documentación asociada al vehículo/servicio/contrato |

## 8. Funciones que no se deben dar por disponibles sin más evidencia

En el código revisado no se demostró un circuito completo para:
- vencimientos y alertas de seguro;
- VTV/ITV o revisiones regulatorias;
- patentes/impuestos del vehículo;
- mantenimiento preventivo por fecha o kilometraje;
- órdenes de reparación con diagnóstico, repuestos y mano de obra;
- combustible y consumo por kilómetro;
- planificación de viajes/recorridos;
- multas y siniestros;
- reserva de vehículos;
- indicadores automáticos de disponibilidad;
- asignación de conductores con control estricto de superposiciones;
- alerta de odómetro inconsistente.

Puede haber alguna capacidad en otras áreas, conectores o módulos opcionales, pero no debe asumirse a partir de los 13 archivos de Fleet.

## 9. Pruebas obligatorias

| Escenario | Qué validar |
|---|---|
| Alta de vehículo | Modelo/fabricante, empresa, categoría, combustible, patente y VIN |
| Historial de conductor | Asignación abierta, cerrada, superpuesta, retroactiva y fecha histórica |
| Odómetro | Lectura menor, igual, mayor, ausencia y consistencia cronológica |
| Servicio | Cantidad × precio, impuesto, proveedor y valor de odómetro |
| Servicio repetido | Copia, historial y cambio de vehículo/proveedor |
| Contrato | Tipo que permite/no permite vehículo, vigencia y costos recurrentes |
| Factura | Asociación de varios servicios, totales, cancelación y no duplicación |
| Privacidad/permisos | Acceso a documentos, datos de empleados y costos |
| Vencimientos | Verificar que no existen alertas nativas; definir brecha real sólo después de revisar otros módulos |

## 10. Adecuación argentina

El dominio genérico no demuestra integración con registros o servicios oficiales argentinos, patentes, VTV, seguros, multas ni consulta por dominio. Los campos de patente, VIN e inspección son datos registrables; no equivalen a validación normativa o interoperabilidad local.

## 11. Estado

Las 13 fuentes están inventariadas. Se identificaron los datos del vehículo, catálogos, conductores por fecha, odómetro, servicios, contratos y asociación de gastos con facturas de proveedor.

**No está aceptado:** faltan pruebas de runtime, conciliación contable de gastos, revisión de superposiciones de conductores y búsqueda en el resto del ERP para determinar si existen alertas/planificación complementarias. La puerta general sigue ABIERTA.
