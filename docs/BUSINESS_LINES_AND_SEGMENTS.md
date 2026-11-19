# Áreas de negocio, unidades y dimensiones de gestión

**Revisión:** 19 de noviembre de 2026  
**Estado:** modelo funcional propuesto; requiere validación durante la selección de plataforma y las pruebas contables.

## Propósito

Rubrova debe permitir que una misma organización gestione actividades comerciales distintas sin duplicar clientes, productos, caja, inventario ni infraestructura. Puede existir una unidad de venta minorista, otra mayorista/distribuidora, comercio electrónico y una unidad de servicios B2B. Cada una puede tener reglas, responsables, objetivos, precios, costos y reportes propios, mientras comparte recursos cuando corresponde.

El modelo no debe asumir que toda empresa vende de una sola manera ni que cada canal equivale a un área de negocio.

## Conceptos que deben permanecer separados

| Concepto | Qué representa | Ejemplo |
|---|---|---|
| Entidad legal / compañía | Persona jurídica o sujeto fiscal que factura, declara impuestos y mantiene libros | Una sociedad con un CUIT |
| Área / unidad de negocio | Actividad con propuesta, reglas, ingresos y resultados que se quieren medir separadamente | Minorista, mayorista, servicios |
| Centro de beneficio | Responsable de generar resultado económico; puede coincidir con una unidad de negocio o agrupar varias | Distribución regional Norte |
| Centro de costo | Equipo/función donde se originan gastos y recursos | Depósito, marketing, administración |
| Canal | Por dónde se captó o atendió la operación | Local, web, vendedor, WhatsApp, marketplace |
| Sucursal / establecimiento | Lugar físico u operativo donde sucede la actividad | Local Oberá, depósito central |
| Depósito / ubicación | Lugar donde se mantiene stock y se realizan movimientos físicos | Depósito seco, cámara, picking |
| Territorio / zona | Área geográfica comercial o logística | Oberá, centro de Misiones, NEA |
| Proyecto / contrato | Compromiso o trabajo acotado al que se imputan ingresos y costos | Servicio anual a una empresa |
| Cliente / cuenta | Persona u organización que compra o contrata | Una empresa con varias sedes |

**No confundir:** una venta mayorista puede originarse en el canal vendedor/WhatsApp, salir del depósito central y pertenecer al área mayorista. Una venta minorista online puede pertenecer a la unidad minorista digital. El canal no define por sí solo el área ni el centro de beneficio.

## Estructura organizacional propuesta

`Organización → Entidad legal → Áreas de negocio / centros de beneficio`

Cada área usa dimensiones independientes:
- canales de venta y atención;
- sucursales, puntos de operación y depósitos;
- centros de costo y equipos;
- territorios y segmentos de cliente;
- proyectos y contratos.

Una entidad legal puede contener varias áreas. Una misma área puede operar en varias sucursales y canales. Si en el futuro hay más de una entidad legal, cada una necesita su propia contabilidad, impuestos, numeración fiscal y permisos; la vista consolidada deberá manejar eliminaciones intercompany y moneda cuando corresponda.

## Áreas y perfiles iniciales

Como mínimo, el modelo debe poder configurar:

1. **Venta minorista local:** caja, escaneo, precios públicos, promociones, pagos presenciales y retiro inmediato.
2. **Venta minorista digital:** tienda online, pedidos, pagos digitales, reserva de stock, preparación, retiro o envío.
3. **Mayorista / distribuidora:** cuentas empresariales, listas y acuerdos B2B, mínimos, escalas por cantidad/importe, crédito, vendedores, rutas y despacho.
4. **Servicios a empresas:** contratos, servicios recurrentes o puntuales, agenda, recursos, órdenes de trabajo, SLA, cumplimiento y facturación.

Estas áreas pueden compartir catálogo, inventario, clientes, personal, compras y administración. La configuración define qué comparte cada una y qué necesita separación.

## Una sola cuenta de cliente, varias relaciones comerciales

El cliente es un registro maestro compartido. Una organización puede comprar en mostrador, recibir precios mayoristas, venderle un servicio y tener varias direcciones o contactos.

Cada relación por área puede configurar:
- estado comercial, ejecutivo y territorio;
- lista de precios, condiciones, descuentos y vigencia;
- límite y plazo de crédito;
- direcciones, horarios, instrucciones y contactos;
- contratos, SLA y servicios contratados;
- condiciones logísticas y de entrega.

No crear tres clientes distintos para la misma empresa solo porque se atiende desde tres áreas. La visibilidad se controla por permisos, sucursales y relaciones; el historial consolidado se mantiene disponible según rol.

## Asignación de operaciones

Cada documento operativo lleva una unidad de negocio principal como valor por defecto. Cuando una operación incluye productos o servicios de áreas diferentes, la asignación económica puede hacerse por línea.

Campos/dimensiones de trazabilidad propuestos:
- entidad legal;
- unidad de negocio;
- centro de beneficio;
- centro de costo;
- canal;
- sucursal/depósito;
- territorio;
- cliente/segmento;
- proyecto/contrato;
- vendedor/equipo;
- período y moneda.

No todos los campos tienen que ser obligatorios en todo documento. Sí deben ser obligatorios cuando se produzca un asiento o una proyección económica que luego se quiera informar por esa dimensión.

## Recursos compartidos

Un depósito, un vehículo, un vendedor o una persona pueden servir a más de un área. La asignación debe distinguir:

- **propietario del recurso:** quién lo administra;
- **reserva/uso:** qué operación lo utiliza;
- **costo directo:** qué área consumió el recurso;
- **costo compartido:** qué parte se reparte y con qué criterio.

No duplicar físicamente el stock por unidad de negocio si es el mismo inventario. Puede existir disponibilidad o reserva por área/canal, pero los movimientos físicos se registran una vez y se mantiene un único libro de stock por ámbito de autoridad.

## Reglas de configuración

- Áreas activables/desactivables sin borrar datos históricos.
- Fechas de vigencia para cambios de precios, responsables, estructura y asignaciones.
- Valores por defecto heredados con posibilidad de excepción autorizada.
- Asignación por línea para documentos mixtos.
- Historial de quién cambió una unidad de negocio o un centro de costo y por qué.
- Permisos y reportes por entidad legal, área, sucursal, canal y equipo.
- Consolidación sin duplicar ventas, pagos o costos.

## Resultado esperado

El dueño puede ver la organización completa o entrar en cada área y entender quién vende, qué vende, por qué canal, a qué clientes, con qué costos, qué recursos consume y cuánto resultado aporta. Las áreas pueden trabajar con procesos diferentes sin convertirse en sistemas aislados.
