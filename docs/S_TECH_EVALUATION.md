# Evaluación de S-Tech para Rubrova

**Revisión:** 20 de noviembre de 2026  
**Estado:** análisis de información pública; no se han solicitado cotizaciones, SDK, demo técnica ni pruebas de hardware.

## 1. Qué es S-Tech

S-Tech (Soluciones en Tecnología Aplicada S.R.L., Argentina) no aparece en la documentación pública revisada como un ERP integral comparable con ERPNext, MyCompany, Tryton, Tango o Dux. Su posicionamiento principal es **hardware transaccional, autoservicio y gestión inteligente del efectivo**, junto con software especializado, integración e instalación.

El sitio declara que diseña y fabrica terminales de autoservicio/kioscos/tótems, soluciones de gestión inteligente del efectivo y equipos para comercios que combinan cobros con tarjeta y efectivo con posibilidad de entregar vuelto. En la página de transformación de comercios también menciona marketing interactivo e inteligencia de clientes para conocerlos y ofrecer productos adecuados. La descripción no publica un esquema funcional detallado de CRM, POS/ERP, APIs ni el modelo de propiedad/exportación de datos.

Su política de calidad documenta actividades en cajeros automáticos, terminales de autogestión, cajas fuertes y mantenimiento de terminales Payway. S-Tech también declara servicios de instalación, mantenimiento, asistencia y puesta en marcha a escala nacional.

## 2. Soluciones públicas identificadas

### A. Transformación de comercios

La página de producto describe hardware y software para operaciones de cobro con tarjetas y efectivo, con entrega de vuelto. También menciona:
- marketing interactivo;
- inteligencia de clientes;
- capacidad de conocer mejor al consumidor y ofrecer productos pertinentes;
- nuevo canal de contacto.

**Encaje para Rubrova:** podría complementar un POS con terminal de autoservicio, caja asistida/autónoma o kiosco, en lugar de reemplazar el ERP. La entrega de vuelto automatizada es particularmente interesante para minimercados, supermercados, estaciones, cadenas y comercios con mucho efectivo.

**No está demostrado públicamente:** cómo se conectan los artículos/totales de un ERP, qué medios de pago acepta cada modelo, cómo devuelve el estado de cobro, cómo administra el efectivo en tránsito/escrow, si dispensa cambio en todas las configuraciones, APIs/SDK, protocolos, modo offline, conciliación, actualización remota ni exportación de datos de clientes.

### B. Gestión inteligente de efectivo

La empresa publica terminales de depósito/recicladores, Smart Safes, clasificadoras de billetes y un sistema inteligente de operación y transporte.

Es potencialmente útil cuando una organización maneja mucho efectivo o varias sucursales. No es una necesidad inmediata del primer POS de Rubrova, pero sí una expansión posible si crece el volumen de caja, aparecen depósitos nocturnos, recaudación o necesidad de reducir traslados manuales.

### C. CashFore

S-Tech describe CashFore como sistema de predicción de utilización/consumo de efectivo:
- monitorea el efectivo restante en sucursales, cajeros y oficinas de cobro;
- pronostica futuras demandas de reabastecimiento;
- declara el uso de más de 150 factores/variables;
- puede generar planes de reposición y visualización del efectivo en tiempo real.

**Aprendizaje para Rubrova:** la predicción no sólo sirve para cuántas unidades de cada producto comprar. También podemos estimar cuánto efectivo de cada denominación necesitamos en cada caja o sucursal, cuánto cambio reservar y cuándo reponer cajones/recicladores.

**Límite de la evidencia:** "150 variables", "IA" y "alta precisión" son afirmaciones del proveedor. No se publican lista de variables, métricas de error, horizonte, benchmark, ejemplos de clientes, API, propiedad de los datos o condiciones de exportación. No podemos asumir su precisión ni que CashFore sea reutilizable.

### D. CashSchedule

S-Tech describe CashSchedule para planificar flotas y tareas de transporte de efectivo, con AI + GIS, monitoreo de vehículos/personal, tareas temporales, modificación de secuencias y app de campo.

**Aprendizaje para Rubrova:** comparte principios con el futuro módulo de planificación de reparto/operaciones: ventanas horarias, duración de tareas, reordenamiento de paradas, seguimiento de estado y asignación de recursos.

**No es un sustituto directo de logística de pedidos:** el foco divulgado es transporte y gestión de efectivo. Debe evaluarse si sirve como inspiración o integración puntual para tareas de recaudación/reposición.

### E. Autogestión / kioscos / terminales

El menú público también enumera soluciones de estacionamiento, turnos, impresión, consultas, trámites/gestión, pagos/cobros y salud. Esto sugiere una plataforma o familia de terminales de autoservicio configurable para diferentes escenarios, pero la información abierta no presenta un catálogo técnico de modelos, sistema operativo, APIs o capacidades reutilizables.

## 3. Comparación con Rubrova

| Capacidad | S-Tech según información pública | Rubrova |
|---|---|---|
| POS/checkout general | Se mencionan terminales transaccionales y sistemas POS, sin alcance de ERP detallado | POS+ERP completo en diseño, sin ejecución |
| Catálogo, precios, compras, stock y contabilidad | No documentado públicamente con suficiente detalle | Modelo y selección de núcleo en curso |
| Tarjeta + efectivo + vuelto | Sí, explícito en transformación de comercios | Requisito del POS; integración física pendiente |
| Autoservicio/kioscos/tótems | Núcleo de su oferta | Capacidad futura de canal/dispositivo |
| CRM/marketing de clientes | Se menciona inteligencia de clientes y marketing interactivo; sin especificación pública | Ficha 360, marcas, preferencia, RFM, rentabilidad y retención especificadas |
| Inteligencia de efectivo | CashFore, pronóstico de reposición y stock de efectivo | Todavía no especificado con igual profundidad |
| Optimización de flota | CashSchedule, rutas de tareas de gestión de efectivo | Modelo de logística de productos; planificación general por desarrollar |
| APIs/exportación de datos | No verificadas en material público | Requisito obligatorio de selección |
| Código reutilizable | No se identificó código abierto o licencia pública de software | No incorporar software sin licencia/contrato confirmado |

**Conclusión:** S-Tech no desplaza la selección de POS+ERP. Es un potencial proveedor/integrador tecnológico para terminales, automatización de cobros, cash management y autoservicio. Su oferta de inteligencia de clientes merece una demo, pero no podemos asumir que resuelve el perfil 360 que queremos para Rubrova.

## 4. Dónde podría aportar valor

Prioridad de evaluación recomendada:

1. **Terminal de cobro con efectivo y vuelto:** el caso más cercano al POS. Medir denominaciones admitidas, validación/rechazo de billetes, atascos, devolución, retiro de efectivo, cuadre y resultado de una transacción.
2. **Conexión al POS/ERP:** exigir una interfaz documentada, estado final/pendiente, IDs de operación, idempotencia, consulta/reverso, liquidación y pruebas de pérdida de conexión.
3. **Autoservicio:** permitir al cliente buscar artículos, consultar precio, armar carrito, pagar y recibir comprobante sin crear otra fuente de ventas/stock. Rubrova sigue siendo la autoridad.
4. **Inteligencia de clientes:** revisar qué identidad captura, si es voluntaria, qué significa "cliente" o "consumidor", cómo separa comprador/pagador, consentimiento, datos exportables y compatibilidad con el perfil 360 de Rubrova.
5. **CashFore:** si existe operación de mucho efectivo, pedir un benchmark retrospectivo de demanda de efectivo con datos reales anonimizados y predicciones por denominación/sucursal.
6. **CashSchedule:** sólo después de entender el proceso de reposición/traslado de dinero y validar que aporta algo que la planificación propia no cubre.

## 5. Preguntas técnicas y comerciales para S-Tech

### Hardware y operación
- Modelos exactos, fotos/videos de operación y ficha técnica.
- ¿Qué denominaciones de billetes y monedas aceptan, reciclan y dispensan?
- ¿Cómo identifican billetes falsos, deteriorados, atascos y operaciones incompletas?
- ¿Pueden entregar vuelto automáticamente cuando el cliente paga en efectivo?
- ¿Cómo hacen cierre, arqueo, retiro de recaudación y conciliación por caja/turno?
- ¿Qué medios de pago funcionan: chip, contactless, QR interoperable, billeteras y tarjetas?
- ¿Qué certificaciones de seguridad física, eléctrica, EMV/PCI y del dispositivo están vigentes por modelo?

### Integración con Rubrova
- ¿Existe API/SDK pública o privada y documentación de sandbox?
- ¿Comunicación local USB, Ethernet, Wi-Fi, serial, REST, Android intent o protocolo propietario?
- ¿Devuelve un identificador único, monto, denominaciones, estado final y detalle del vuelto?
- ¿Qué ocurre si Rubrova se cierra luego de enviar el cobro?
- ¿Hay idempotencia, consulta de estado, cancelación, reverso y recuperación de una operación incierta?
- ¿Puede trabajar en LAN sin nube? ¿Qué servicios dejan de funcionar sin Internet?
- ¿Podemos mantener Rubrova como dueño del catálogo, precio, venta, cliente, inventario y caja, sin duplicar ledgers en el software de S-Tech?

### Inteligencia de clientes y datos
- ¿Qué datos concretos recopila la solución?
- ¿Identifica al comprador, usuario de la terminal o titular del medio de pago? ¿Cómo diferencia esas personas?
- ¿Cómo obtiene la identidad y qué consentimiento/aviso presenta?
- ¿Ofrece API de eventos y exportación completa CSV/XLSX/JSON?
- ¿Quién es titular/responsable de los datos, dónde se alojan y cómo se recuperan si finaliza el contrato?
- ¿Permite desactivar marketing/perfilado y borrar/rectificar según reglas aplicables?
- ¿Se puede integrar su inteligencia con un CustomerAccount ya existente en Rubrova sin duplicar clientes?

### CashFore y CashSchedule
- Lista de factores, features y variables que usa CashFore.
- Horizonte de pronóstico, granularidad, intervalos y métricas MAE/WAPE/bias por sucursal y denominación.
- Prueba de backtesting con predicciones guardadas antes de conocer el resultado.
- API para consultar pronóstico y cantidades recomendadas.
- Para CashSchedule: optimización, restricciones, ventanas, capacidad y prueba comparativa de rutas.
- ¿Qué significa el tercer módulo anunciado? La página declara que la suite tiene tres módulos, pero el material público consultado sólo detalla CashFore y CashSchedule.

### Contrato, licencia y continuidad
- Precio de hardware, licencia, instalación, mantenimiento, repuestos y costos recurrentes.
- Qué componentes son software propietario y cuáles se licencian por suscripción.
- SLA, tiempos de atención fuera del AMBA y garantía.
- Procedimiento para cambiar de proveedor y exportar operaciones/documentos.
- Posibilidad de comprar equipos sin contratar el módulo de inteligencia, y viceversa.

## 6. Decisión

**No incorporar S-Tech como núcleo de Rubrova ni desarrollar una dependencia ahora.** Mantenerlo como candidato a hardware/automatización de caja, autoservicio y cash management.

Antes de comprar, pediría una demo técnica y una prueba de integración que ejecute una venta real de laboratorio:
- Rubrova envía el total y la referencia.
- La terminal recibe billetes o confirma el medio de pago.
- Calcula/entrega vuelto.
- Devuelve estado y referencia.
- Rubrova confirma la operación una sola vez.
- Se reconstruye cierre por caja/turno y se exporta el detalle.
- Se mata la aplicación durante el flujo y se demuestra recuperación sin doble cobro.

La parte de IA sólo se evalúa tras recibir variables, historial de pronósticos y resultados medibles. No se acepta el claim de "más de 150 variables" como evidencia suficiente.

## Fuentes públicas consultadas

- [S-Tech — página principal](https://s-tech.com.ar/): autogestión, gestión inteligente de efectivo y transformación de comercios.
- [Transformación de comercios](https://s-tech.com.ar/transformacion-de-comercios/): cobros con tarjeta/efectivo, entrega de vuelto, marketing interactivo e inteligencia de clientes.
- [Sistema inteligente de operación y transporte](https://s-tech.com.ar/sistema-inteligente-de-operacion-y-transporte/): CashFore y CashSchedule.
- [Gestión inteligente de efectivo](https://s-tech.com.ar/gestion-inteligente-de-efectivo/): línea de equipos.
- [Terminales de depósito/recicladores](https://s-tech.com.ar/terminales-de-deposito-recicladores/) y [Smart Safes](https://s-tech.com.ar/smart-safes/).
- [Política de calidad y medio ambiente](https://s-tech.com.ar/D00.pdf): actividad de la empresa y mantenimiento de terminales Payway.
- [S-Tech Metal — sobre nosotros](https://metal.s-tech.com.ar/sobre-nosotros/): fabricación, instalación, desarrollo y licenciamiento de software.

El material público consultado no contiene API/SDK, pricing, contrato de licencia, ficha técnica de terminales, benchmark de IA ni esquema de exportación. Esos puntos quedan pendientes de confirmación directa con la empresa.

**Contacto público de la empresa:** info@s-tech.com.ar · +54 11 5217-0175.
