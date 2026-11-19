# Servicios a empresas, contratos y cumplimiento operativo

**Revisión:** 19 de noviembre de 2026  
**Estado:** alcance funcional definido; catálogo de servicios, calendarios, SLA y reglas de facturación se configuran por unidad de negocio.

## Objetivo

Rubrova debe poder administrar un área que venda servicios a empresas, además de productos. Una cuenta puede comprar mercadería mayorista y contratar servicios; no debe haber que crear una cuenta separada ni llevar la relación en una planilla externa.

El módulo debe cubrir desde la oportunidad y el contrato hasta la agenda, ejecución, evidencia, aceptación, facturación y rentabilidad.

## 1. Cuenta y relación B2B

La cuenta empresarial comparte identidad con las áreas de venta de productos. Se pueden registrar:
- razón social, CUIT, condición fiscal, domicilios y establecimientos;
- contactos, decisores, referentes técnicos y autorizados;
- responsable comercial y operativo;
- servicios contratados, contratos vigentes, renovaciones y reclamos;
- historial de visitas, tareas, comunicaciones, documentación y facturas;
- permisos de portal por contacto y establecimiento.

Una organización puede tener muchas sedes, y cada sede puede tener equipos, activos, horarios, instrucciones y personas responsables.

## 2. Catálogo de servicios

Un servicio tiene:
- código, nombre, descripción y categoría;
- unidad de facturación: visita, hora, jornada, mes, evento, unidad, bolsa de horas o hito;
- tarifa pública y tarifas negociadas;
- costo estándar y costo directo real;
- duración estimada, habilidades y recursos requeridos;
- materiales/insumos asociados;
- política de desplazamiento, viáticos, horario y urgencia;
- reglas de SLA, evidencia y aceptación;
- periodicidad y posibilidad de renovación.

Los servicios pueden ser puntuales, recurrentes, por abono, por bolsa de horas, por disponibilidad, por evento o por resultado/hito.

## 3. Contrato / acuerdo de servicio

El contrato debe ser versionado y contener:
- cliente, sedes, contactos, unidad de negocio y responsable;
- servicios cubiertos, cantidades/unidades y exclusiones;
- fecha de inicio/fin, renovación, preaviso y suspensión;
- precio fijo, recurrente, por uso, por hora o por hito;
- cupos incluidos, excedentes y regla de consumo;
- calendario, horario hábil, feriados y zonas de atención;
- SLA por prioridad: primera respuesta, atención, resolución y disponibilidad cuando aplique;
- ventanas de mantenimiento y restricciones;
- penalidades/créditos o compensaciones si se acuerdan;
- proceso de aprobación, documentación y firma;
- política de facturación, impuestos y reajustes;
- anexos, cambios, versiones y firmas.

El sistema debe poder comparar el servicio prometido contra lo ejecutado y lo facturado. La versión del contrato aplicada a una orden de trabajo queda congelada para no cambiar retrospectivamente las obligaciones.

## 4. Obligaciones y agenda

El contrato puede originar:
- visitas recurrentes (semanal, mensual, trimestral, anual);
- inspecciones y controles;
- tareas por fecha límite;
- hitos/proyectos;
- ventanas de disponibilidad y guardias;
- entregables periódicos;
- órdenes puntuales disparadas por solicitud del cliente.

Cada obligación tiene fecha prevista, fecha límite, calendario aplicable, responsable, equipo, recursos, ubicación, estado y evidencia requerida. Una agenda no es solo una reunión: debe mostrar trabajo por hacer, capacidad, conflictos, vencimientos y sobrecarga.

## 5. Orden de trabajo / intervención

Una orden de trabajo incluye:
- contrato/servicio y cliente/sede;
- motivo, alcance y prioridad;
- fecha comprometida y SLA;
- técnico/equipo responsable;
- checklist, tareas, materiales, herramientas y permisos;
- horas estimadas/reales y desplazamiento;
- fotos, mediciones, documentos, comentarios y firma;
- resultado, pendientes, causa de incumplimiento y próxima acción;
- aceptación del cliente o justificación de rechazo.

Estados de referencia:
- requested;
- triaged;
- scheduled;
- assigned;
- in_progress;
- blocked / awaiting_customer / awaiting_parts;
- completed_pending_acceptance;
- accepted;
- invoiced;
- closed;
- cancelled.

La transición debe estar controlada por permisos y evidencia. Marcar completado no debe borrar el vencimiento ni el SLA original.

## 6. Seguimiento y SLA

El sistema debe alertar sobre:
- obligación próxima a vencer;
- orden sin asignar;
- visita no confirmada;
- técnico retrasado;
- material faltante;
- SLA próximo a incumplirse o ya incumplido;
- trabajo completado sin aceptación;
- facturación pendiente;
- contrato por vencer o con consumo próximo al límite.

El cómputo del SLA debe respetar horario de cobertura, feriados, zona horaria y pausas autorizadas (por ejemplo, espera de acceso o repuesto, si el contrato lo permite). Se guarda tiempo calendario y tiempo hábil.

## 7. Facturación y consumo

El módulo debe soportar:
- abono fijo recurrente;
- servicio por evento/visita;
- hora consumida;
- bolsa de horas con saldo;
- materiales + mano de obra;
- hito o entregable;
- excedentes, urgencias, guardias y viáticos;
- facturación consolidada de varias órdenes del mismo cliente;
- nota de crédito o reversión por incumplimiento/ajuste según acuerdo.

Cada consumo se vincula al contrato y a la orden de trabajo. No se factura dos veces un mismo servicio ni se consumen horas sin movimiento de saldo. El cobro y la factura siguen separados.

## 8. La misma capacidad puede servir a mayoristas

No debe existir un subsistema exclusivo de contratos para servicios B2B y otro para mayoristas. Una distribuidora puede firmar acuerdos de suministro con:
- volumen mensual o mínimo de compra;
- calendario fijo de entregas;
- días y ventanas de recepción;
- condiciones de reposición/stock dedicado;
- nivel de servicio de preparación y despacho;
- documentación de calidad o trazabilidad;
- precio y revisión periódica;
- penalidades acordadas y gestión de reclamos.

Estos acuerdos pueden crear pedidos recurrentes y obligaciones logísticas, usando el mismo motor de contratos, agenda y cumplimiento, pero con plantillas y tipos de obligación distintos.

## 9. Rentabilidad del área de servicios

Para cada contrato/cliente/servicio deben registrarse ingresos y costos directos:
- horas reales por rol y costo horario cargado;
- materiales consumidos;
- desplazamiento, kilometraje, combustible, peajes;
- subcontratistas;
- equipos/herramientas y alquileres;
- licencias/insumos recurrentes;
- comisión comercial y cobro;
- retrabajos, garantías, tiempos improductivos y SLA incumplido.

Métricas:
- ingreso mensual recurrente (cuando aplica);
- margen bruto y margen de contribución por contrato;
- costo real por orden/visita/hora;
- horas contratadas vs consumidas;
- utilización facturable y no facturable;
- renovación, churn, morosidad;
- cumplimiento SLA, resolución en primera visita, retrabajo;
- rentabilidad por técnico/equipo, servicio, cliente y unidad de negocio.

## 10. Aceptación del módulo

- Crear empresa cliente con varias sedes y contactos.
- Definir contrato de 12 meses con renovaciones y distintos SLA.
- Generar calendario recurrente y órdenes de trabajo.
- Reasignar recursos sin perder historial ni cambiar el SLA original.
- Registrar horas, materiales, viáticos y evidencia.
- Obtener aceptación del cliente.
- Facturar abono y excedentes sin duplicar.
- Medir rentabilidad de cada contrato y comparar con su presupuesto.
- Usar un acuerdo de suministro mayorista con entregas programadas y seguimiento.
- Mostrar alertas de vencimiento, SLA, renovación y facturación.

## Proyectos investigados

- **Dolibarr 24.0.3:** contratos/suscripciones, intervenciones, agenda, proyectos, pedidos, envíos, POS y contabilidad en módulos. Es un candidato integral adicional para estudiar.
- **ERPNext:** contrato, SLA, mantenimiento programado, proyectos, tiempos y centros de costo/dimensiones.
- **OCA Field Service 19.0:** addons para acuerdos, calendarios, recurrencia, stock, gastos, vehículos y partes de horas. Los módulos se revisan individualmente; el addon de acuerdos aparece en estado Beta.
- **OpenFieldPro:** FSM self-hosted con CRM, agenda, dispatch, work orders, estimaciones, facturas, pagos, planes de servicio y app técnica móvil. Está en etapa de hardening de release candidate, por lo que se considera fuente de código y patrones, no base aprobada.

Fuentes:
- https://docs.frappe.io/erpnext/contract
- https://docs.frappe.io/erpnext/service-level-agreement
- https://docs.frappe.io/erpnext/maintenance-schedule
- https://github.com/OCA/field-service
- https://github.com/niko4244/openfieldpro
- https://wiki.dolibarr.org/index.php/Module_Interventions_En
