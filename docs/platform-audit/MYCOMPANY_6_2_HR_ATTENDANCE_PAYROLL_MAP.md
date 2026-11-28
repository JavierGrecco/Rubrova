# MyCompany 6.2 — mapa de RR. HH., reclutamiento, asistencia y haberes

**Estado: 25 fuentes LSF inventariadas; lectura de los circuitos principales realizada. Pruebas de runtime, reglas laborales locales y aceptación de liquidación argentina pendientes.**

El dominio integra tres circuitos que se deben estudiar por separado: selección de personal, control de asistencia y liquidación/pago de haberes.

## 1. Inventario de módulos

| Área | Módulos |
|---|---|
| Raíz/configuración | `HumanResources`, `HumanResourcesSettings` |
| Asistencia | `Attendance`, `AttendanceMobile`, `AttendanceKiosk` |
| Reclutamiento | `Application`, `ApplicationCall`, `ApplicationEmail`, `ApplicationHire`, `ApplicationInterview`, `ApplicationPosition`, `ApplicationRefuse`, `ApplicationTag` |
| Recibos/haberes | `Payslip`, `PayslipBatch`, `PayslipCategory`, `PayslipInitial`, `PayslipLedger`, `PayslipLine`, `PayslipLineBatch`, `PayslipType` |
| Deuda/pago de haberes | `PayslipDebt`, `PayslipOutgoingPayment`, `PayslipOutgoingPaymentInitial`, `PayslipTotal` |

El dominio también tiene dependencias con empleados, socios, departamentos, puestos, proyectos, documentos, pagos, geolocalización, archivos, correo y llamadas.

## 2. Reclutamiento: postulación → entrevista → contratación o rechazo

### 2.1 Postulación

Fuente: `humanResources/recruitment/applications/Application.lsf`.

La postulación guarda:
- fecha/hora y asunto;
- nombre, apellido y segundo nombre;
- teléfono y correo;
- reclutador/responsable (empleado);
- disponibilidad;
- tags;
- puesto y departamento;
- salario esperado y salario propuesto;
- descripción y resumen enriquecido;
- estado e historial;
- archivos, comentarios y actividades.

El reclutador se inicializa desde el usuario actual cuando éste es empleado. El departamento seleccionado debe pertenecer a una empresa propia; la empresa de la postulación se deriva de ese departamento.

### 2.2 Entrevistas

`ApplicationInterview` crea entrevistas relacionadas con la postulación:
- fecha/hora;
- uno o varios entrevistadores;
- resumen;
- última entrevista materializada;
- contador y datos de entrevistas en la postulación.

La presencia de una entrevista puede hacer que el estado se muestre como “Entrevista” mediante una extensión del estado. No significa que la entrevista haya sido aprobada: el resumen/resultado requiere interpretación o decisiones adicionales.

### 2.3 Contratación

`ApplicationHire` agrega el estado “Contratado” y la acción de contratar:
- marca la postulación como contratada/cerrada;
- crea un empleado;
- copia datos personales y de contacto;
- copia puesto y departamento;
- vincula el empleado creado con la postulación.

La empresa legal del empleado se deriva de su departamento, conforme a las reglas de datos maestros.

### 2.4 Rechazo

`ApplicationRefuse` mantiene motivos de rechazo y una posible plantilla de correo por motivo. La acción registra el motivo, marca la postulación como rechazada/cerrada y puede enviar el mensaje correspondiente.

### 2.5 Puestos y tablero

`ApplicationPosition` construye una vista por puesto con conteo por estado y fichas de postulaciones. Se pueden filtrar/ordenar las postulaciones por estado, responsable, etiquetas y otros atributos.

`ApplicationTag` permite clasificar postulaciones mediante tags. `ApplicationCall` y `ApplicationEmail` agregan seguimiento por llamadas/correos y bandeja de comunicaciones.

**Pendiente:** evitar empleados duplicados al contratar; probar cambio de empresa/departamento, postulaciones simultáneas, permisos, entrevistas múltiples, reabrir rechazos, plantillas de correo y calidad de datos.

## 3. Asistencia: entrada → salida → horas trabajadas

### 3.1 Registro

Fuente: `humanResources/attendance/Attendance.lsf`.

Cada registro de asistencia guarda:
- empleado;
- fecha/hora de entrada;
- fecha/hora de salida;
- horas trabajadas (propiedad calculada);
- latitud/longitud de entrada;
- latitud/longitud de salida;
- foto de entrada y salida cuando se usa kiosco.

El empleado se inicializa desde el usuario actual. La duración se calcula entre entrada y salida y se convierte a horas con redondeo a una cifra decimal según la implementación visible.

La última asistencia de cada empleado determina el estado:
- si la última no tiene salida, se considera abierta;
- si está abierta, la siguiente marca es salida;
- si no hay asistencia abierta, la siguiente marca es entrada.

Hay listados de registros abiertos/cerrados y totales de la semana/mes.

### 3.2 Asistencia móvil

`AttendanceMobile`:
- muestra los registros del empleado conectado;
- permite iniciar/finalizar asistencia;
- captura hora y geolocalización;
- usa sesiones de cambio y aplica el registro;
- actualiza periódicamente la pantalla;
- muestra totales semanales y mensuales.

La entrada/salida móvil se deshabilita si no se reciben coordenadas, salvo que el empleado tenga habilitada la opción de asistir sin geolocalización.

### 3.3 Kiosco

`AttendanceKiosk`:
- usa `BarCodeReader` para leer la credencial/código del empleado;
- fotografía la entrada/salida;
- identifica el empleado por un valor de texto/código;
- mira si tiene una asistencia abierta para elegir entrada o salida;
- muestra un mensaje visual de confirmación;
- evita procesar una lectura repetida del mismo código durante aproximadamente 10 segundos;
- muestra empleados con asistencia abierta cerca del kiosco según comparación de coordenadas.

El filtro de proximidad visible usa diferencia de latitud/longitud (umbral 0,001 grados). No es una distancia métrica precisa ni prueba ubicación antifraude.

### 3.4 Privacidad y excepciones

Existe un indicador por empleado para permitir asistencia sin geolocalización. Esto constituye una excepción configurable, no una política universal.

**Pendiente:** consentimiento y privacidad, suplantación GPS/código, empleados fuera del área, turnos nocturnos que cruzan medianoche, entradas duplicadas, salida olvidada, modificaciones retroactivas, correcciones por supervisor, cámaras, retención de fotos/coordenadas y conciliación con horarios/ausencias.

## 4. Haberes: recibo → conceptos → neto

### 4.1 Recibo individual

Fuentes:
- `payroll/payslip/Payslip.lsf`
- `PayslipLine.lsf`
- `PayslipCategory.lsf`
- `PayslipLedger.lsf`

El recibo guarda:
- número y tipo;
- período (intervalo de fechas), inicio y fin;
- empleado;
- empresa;
- moneda;
- vencimiento;
- conceptos/renglones y comentarios.

El tipo de recibo usa un numerador propio. El grupo por período, empleado, empresa y tipo se utiliza para identificar recibos equivalentes.

### 4.2 Categorías y cálculo

La categoría de recibo tiene:
- nombre y orden;
- marca de descuento (deduction);
- marca Skip;
- marca Hide;
- marca editable.

Los datos iniciales crean categorías genéricas “Salary”, “Bonus” y “Tax”; la categoría Tax se marca como descuento. Esto es un ejemplo inicial, no una tabla de conceptos laborales argentinos.

Cada renglón guarda categoría, cantidad, importe y total. El total se calcula como cantidad × importe con redondeo a dos decimales; al editar total, la fuente permite recalcular el importe a partir de la cantidad.

El ledger aplica:
- haberes: total positivo;
- descuentos: total negativo;
- neto: suma de totales firmados, excluyendo categorías Skip;
- categorías Hide: no aparecen en la tabla, pero siguen participando del neto si no tienen Skip.

La distinción entre Hide y Skip es importante para entender recibos y auditoría.

### 4.3 Lotes

`PayslipBatch`:
- define período, empresa, tipo y nombre;
- agrupa recibos;
- genera un recibo para cada empleado activo de la empresa;
- evita duplicar el recibo para la combinación de período, empleado, empresa y tipo;
- valida que todos los empleados del lote pertenezcan a la empresa seleccionada;
- sincroniza período/empresa/tipo de los recibos ligados cuando cambian los campos del lote.

El punto abstracto `generate(Payslip)` permite que otras extensiones agreguen cálculo de líneas. No se debe afirmar que el lote calcula automáticamente todos los conceptos sin identificar esas implementaciones.

`PayslipLineBatch` permite modificar en lote el total por categoría; crea o elimina el renglón según el valor y descripción.

### 4.4 Integraciones de cálculo

La documentación describe un vínculo opcional con entradas de tiempo de proyectos:
- horas por empleado/período/proyecto;
- tarifa por hora;
- cálculo de importe por horas × tarifa;
- tarifa que puede depender del empleado, asignación al proyecto o equipo.

Esto requiere revisar las extensiones de proyectos/haberes y no forma parte de la regla genérica base de los renglones.

## 5. Deuda y pago de haberes

`PayslipDebt` extiende `Payslip` como `IncomingDebt`:
- socio = empleado;
- empresa = empresa del recibo;
- moneda = moneda del recibo;
- importe = neto;
- fecha del documento = fin del período;
- vencimiento = fecha de vencimiento;
- el punto abstracto `skipDebt` puede excluir el recibo del ledger.

`PayslipOutgoingPayment` agrega “Registrar pago”:
- crea un `OutgoingPayment`;
- toma tipo de pago configurado;
- copia empresa/empleado/cuentas;
- propone el importe pendiente;
- imputa el pago al recibo mediante el ledger de deuda.

`PayslipTotal` permite consultar neto, pagado y saldo por empleado/rango de fechas y registrar pagos agrupados. Puede haber pagos parciales; el saldo pendiente se conserva.

**Pendiente:** probar pago parcial, varios recibos en un pago, varias monedas, cancelación del pago, cambio de importe del recibo después de imputar, cuentas del empleado y conciliación bancaria.

## 6. Tipos y numeración

`PayslipType` permite crear tipos y asignar un numerador. Los datos iniciales crean “Regular”, serie PSL y categorías genéricas de haberes/descuentos. La numeración es configurable y debe probarse con concurrencia, anulación y distintos tipos/empresas.

## 7. Advertencia crítica: no equivale a liquidación argentina

El motor de recibos es genérico y configurable. La existencia de categorías Salary/Bonus/Tax, cantidades, importes, neto y pagos no demuestra cumplimiento argentino.

Falta validar, como mínimo:
- convenios colectivos y escalas salariales;
- remunerativos/no remunerativos;
- horas extras, feriados, nocturnidad y presentismo;
- vacaciones, licencias, ausencias, enfermedad y SAC;
- aportes y contribuciones;
- obra social, sindicato, jubilación, ART;
- retenciones y embargos;
- bases imponibles, topes y redondeos;
- Libro de Sueldos Digital y SICOSS/ARCA;
- recibo legal, firma, conservación y auditoría;
- normativa provincial y municipal aplicable.

No se debe desarrollar un reemplazo de haberes sin estudiar primero las extensiones existentes y sus límites, pero tampoco se debe presentar el módulo genérico como listo para liquidar legalmente en Argentina.

## 8. Pruebas obligatorias

| Escenario | Qué validar |
|---|---|
| Reclutamiento | Alta, entrevista, contratar, rechazar, duplicados y permisos |
| Contratación | Copia de datos, departamento, empresa y usuario |
| Asistencia móvil | Entrada/salida, GPS válido/faltante, excepción, medianoche |
| Kiosco | Credencial válida/inválida, doble lectura, cámara, coordenadas y proximidad |
| Corrección asistencia | Entrada abierta, salida olvidada, modificación retroactiva y auditoría |
| Recibo | Cantidad × tarifa, edición del total, descuento, Skip y Hide |
| Lote | Empleados activos, empresa distinta, duplicados y nueva ejecución |
| Integración proyectos | Horas, tarifa histórica, aprobación y período |
| Pago | Total/parcial, varios recibos, cancelación y cuenta |
| Argentina | Convenio, conceptos legales, retenciones, aportes, SAC y reportes regulatorios |

## 9. Estado

Las 25 fuentes están inventariadas. Se identificó el ciclo de reclutamiento, entrevista, contratación/rechazo, asistencia móvil/kiosco, cálculo de recibos, lotes, deuda y pagos.

**No está aceptado:** faltan pruebas de runtime y validación de la normativa laboral argentina. El módulo genérico no debe usarse en producción como liquidación legal hasta superar esa revisión. La puerta general de relevamiento sigue ABIERTA.
