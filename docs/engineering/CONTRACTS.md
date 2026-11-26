# Contratos de integración y comunicación

**Estado general:** catálogo inicial; los contratos específicos de MyCompany están en estado candidato, pendientes de aceptación funcional nativa y conciliación real.  
**Regla:** el contrato es el acuerdo entre productor y consumidor. El código, los tests y la documentación deben coincidir.

## 1. Contrato común de módulos

### 1.1 Propiedad y límites

- Cada módulo declara qué conceptos y datos posee.
- El módulo propietario define las reglas de escritura y exposición.
- En una misma instancia lsFusion integrada, otros módulos consumen los elementos lógicos públicos mediante dependencias REQUIRE, clases, propiedades, acciones, restricciones y puntos abstractos de extensión. Esto no equivale a una API HTTP entre microservicios.
- No se debe eludir el modelo lógico escribiendo directamente por SQL en las tablas físicas que sostienen otro módulo ni depender de detalles internos no declarados como contrato.
- Entre servicios/procesos independientes, cada sistema conserva su almacenamiento y los datos se intercambian mediante APIs/eventos/archivos versionados; no hay escrituras cruzadas.
- Un adaptador transforma formatos y significados, pero no se convierte en dueño del dato original.
- La analítica conserva la procedencia y el período de los datos; no reemplaza el registro transaccional.

Para el contrato específico de módulos, extensiones y transacciones lsFusion/MyCompany 6.2, ver la [Guía de integración](LSFUSION_MYCOMPANY_INTEGRATION_GUIDE.md).

### 1.2 Intercambio síncrono

Toda API debe definir:

- nombre y versión del endpoint;
- método y transporte;
- autenticación y autorización;
- parámetros, formato, tamaño y validación;
- esquema de respuesta y tipos;
- significado de ausente, NULL, cero y colección vacía;
- unidad, precisión, moneda y zona horaria;
- errores funcionales y técnicos;
- timeout, concurrencia, límites y política de reintento;
- idempotencia, consistencia y trazabilidad;
- compatibilidad y política de retiro.

HTTP 200 sólo indica el estado de transporte. El consumidor valida el cuerpo y el contrato completo.

### 1.3 Eventos y procesos asíncronos

Cuando se incorpore mensajería/eventos:

- el evento representa un hecho ocurrido y no una orden implícita;
- lleva eventId, tipo, versión, fecha de ocurrencia, emisor, identificador de correlación y referencia de agregado;
- el consumidor deduplica de forma durable;
- la entrega puede ser al menos una vez; no se promete exactamente una vez sin evidencia;
- los estados finales no retroceden ante mensajes tardíos;
- se documenta orden esperado, particionado y estrategia de replay;
- los cambios incompatibles requieren versión/migración y ventana de coexistencia.

### 1.4 Reintentos y errores

- Todo llamado externo tiene timeout finito.
- Sólo se reintentan operaciones idempotentes o protegidas con una clave de idempotencia.
- Los errores distinguen validación, autorización, conflicto, saturación, timeout, indisponibilidad y fallo interno.
- Se registra correlación de extremo a extremo, sin exponer credenciales ni datos sensibles.
- La caída de una integración no debe derribar capacidades que no dependen de ella.

## 2. Contrato MyCompany 6.2 — fuente nativa de reposición

**Estado: candidato, no productivo.**

### 2.1 Identificación y seguridad

| Elemento | Contrato |
|---|---|
| Plataforma fijada | MyCompany 6.2 / lsFusion 6.2 |
| Módulo | RubrovaReplenishmentExport |
| Namespace | Rubrova |
| Acción principal | rubrovaExportReplenishmentSource |
| Sondas | rubrovaProbeInventory, rubrovaProbeOutgoingCommitments, rubrovaProbeReceipts |
| Exposición | acciones específicas con @@api |
| Seguridad | mantener enableAPI=0; llamadas autenticadas; no usar @@noauth ni habilitar evaluación arbitraria |
| Naturaleza | sólo lectura; no crea, modifica, confirma ni elimina documentos de MyCompany |

**Compatibilidad de sintaxis:** la línea base del proyecto es lsFusion 6.2. En esa versión RETURN es un operador de salida sin expresión; la forma RETURN JSON FROM no es válida para el parser 6.2. Los endpoints existentes de Rubrova para CI usan EXPORT JSON FROM sin destino explícito, según el patrón de la API de esa versión. No trasladar sintaxis de documentación 7.x sin comprobarla contra la versión fijada. Referencias:
- [lsFusion 6.x — Access from an external system](https://docs.lsfusion.org/v6/Access_from_an_external_system/)
- [lsFusion 6.x — RETURN operator](https://docs.lsfusion.org/v6/RETURN_operator/)
- [lsFusion 6.x — EXPORT operator](https://docs.lsfusion.org/v6/EXPORT_operator/)

La semántica de respuesta y la selección de propiedades de resultado deben seguir la documentación v6 y los endpoints existentes. El test estático protege el patrón sintáctico; el smoke autenticado debe confirmar el cuerpo HTTP real.

### 2.2 Esquema de nivel superior

| Campo | Tipo / regla | Significado |
|---|---|---|
| schemaVersion | entero, actualmente 2 | versión del esquema de Rubrova; v2 exporta componentes nativos de reserva por ShipmentLine |
| snapshotType | string fijo | mycompany-replenishment-source-export |
| sourceSystem | string fijo | MyCompany |
| sourceVersion | string fijo | 6.2 |
| asOf | fecha ISO YYYY-MM-DD | fecha de corte |
| asOfDateTime | fecha-hora ISO actual del servidor | instante de corte; la zona/offset explícitos siguen pendientes de formalización |
| quantityUnit | string fijo | product-uom; la cantidad está en la unidad del producto |
| quantityPrecision | entero fijo 3 | precisión de cantidades; no redondear silenciosamente |
| readOnly | booleano true | declaración del carácter de sólo lectura |
| sourceSemantics | objeto | diccionario explícito de significado de cada campo |
| inventoryCount | entero no negativo | conteo independiente bajo el mismo filtro de inventario |
| outgoingCommitmentsCount | entero no negativo | conteo independiente bajo el mismo filtro de compromisos |
| outgoingReservationsCount | entero no negativo | conteo independiente de líneas de envío enlazadas a compromisos abiertos |
| receiptsCount | entero no negativo | conteo independiente bajo el mismo filtro de recepciones |
| inventory | lista de objetos | hechos de inventario por producto/ubicación |
| outgoingCommitments | lista de objetos | líneas de venta confirmadas aún abiertas |
| outgoingReservations | lista de objetos | hechos nativos por ShipmentLine, separados por despacho parcial |
| receipts | lista de objetos | recepciones de compra elegibles pendientes |

### 2.3 Semántica de inventario

No intercambiar estas magnitudes:

- onHand: existencia física nativa, derivada del ledger físico de MyCompany.
- available: disponible nativo calculado por MyCompany.
- plannedNetReservation: reserva neta firmada que participa en el disponible.
- La conciliación adoptada por el adaptador es available = onHand - plannedNetReservation. Si no coincide a precisión de tres decimales, se bloquea el snapshot.
- grossReserved y expectedInbound no son sinónimos de la reserva neta; se conservan por separado.
- Los campos *Native preservan el valor nativo crudo cuando puede ser NULL; los campos efectivos usan respaldo numérico explícito cuando la regla del contrato lo permite.

La definición de expectedInbound cubre las reservas entrantes negativas de los ledgers para la ubicación/producto exactos; no equivale automáticamente a la lista de recepciones que el planificador considera elegibles.

### 2.4 Compromisos de salida

- Origen: Sales.OrderLine de una orden confirmada.
- Sólo se exportan líneas con Sales.toShip(ol) > 0.
- openQuantity representa lo que todavía queda por despachar.
- outgoingReservations emite una fila por ShipmentLine enlazada a una Sales.OrderLine confirmada y todavía abierta. Incluye reservedQuantityNative = OVERRIDE Inventory.reserved(ShipmentLine), 0, ledgerReservedQuantityNative = OVERRIDE Inventory.ledgerReserved(ShipmentLine), 0, shipmentId, shipmentLineId, sourceLineId y reserveEligible; ambos campos se serializan aunque el valor nativo sea NULL.
- El adaptador normaliza cada componente NULL a cero y calcula lineReserved = reservedQuantityNative - ledgerReservedQuantityNative; sólo suma diferencias positivas cuando reserveEligible=true, agrupadas por sourceLineId.
- Varios despachos parciales no deben duplicar una línea abierta.
- Identidad compuesta acordada: número de orden + índice de línea. La identidad debe ser estable dentro del documento y no debe inventarse a partir de IDs no expuestos por MyCompany.

### 2.5 Recepciones previstas

- Origen: ReceiptResLedger y su línea/recepción relacionada.
- Elegibilidad actual: recepción ready, no done, no cancelada y orden de compra confirmada.
- expectedReservationSigned conserva el signo nativo negativo.
- expectedQuantity es la magnitud positiva calculada como 0 - expectedReservationSigned.
- Se conserva increaseAvailableStock; no se debe asumir que toda recepción incrementa el disponible inmediatamente.
- La identidad compuesta conserva número de recepción + índice de línea y referencia a la línea de orden de compra.

### 2.6 Colecciones vacías y conteos

El consumidor nunca debe convertir una respuesta ausente en lista vacía sin evidencia.

Regla:
1. cada consulta calcula un contador nativo independiente con el mismo filtro que su colección;
2. si la propiedad JSON está ausente y el contador es exactamente cero, el adaptador puede normalizarla a [];
3. si el contador es mayor que cero y la propiedad está ausente, se rechaza;
4. si la lista está presente pero su longitud no coincide con el contador, se rechaza;
5. un NULL, cuerpo vacío, texto plano o JSON con otra forma no equivale a una lista vacía.

Este control evita confundir “no hay filas” con “la API no entregó la colección”.

### 2.7 Adaptador y límites de responsabilidad

- adapt_mycompany_native_export.py sólo lee un documento JSON ya exportado.
- No abre conexiones a PostgreSQL, RMI, HTTP ni al servidor MyCompany.
- Convierte cantidades a milésimas enteras sin redondear.
- Valida cabecera, versión, semánticas, conteos, claves únicas, política de planificación y conciliación antes de producir un snapshot del planificador.
- No inventa demanda, lead time, stock de seguridad, MOQ ni múltiplos.
- No crea ni modifica objetos en MyCompany.

### 2.8 Pruebas de contrato exigidas

- JSON de raíz válido y cabecera exacta.
- Las cuatro colecciones presentes o ausentes sólo bajo la regla de conteos.
- Conteo = longitud de filas.
- Elementos de cada colección son objetos.
- Campos obligatorios, tipos, unidades y precisión.
- IDs compuestos únicos y estables.
- Magnitudes y signos conciliados.
- Despachos parciales consolidados.
- Recepciones elegibles, no elegibles e increaseAvailableStock.
- Inventario físico/disponible/reservado diferenciado.
- Rechazo seguro ante versión desconocida, campos incompatibles o datos no conciliados.
- Sólo lectura comprobada por revisión del módulo y permisos.

## 3. Estados de madurez de un contrato

- **Propuesto:** diseño documentado, aún no implementado.
- **Candidato:** implementado y con pruebas locales/unitarias, pero no aceptado en todos los runtimes o con datos reales.
- **Aceptado en CI:** pruebas de contrato y runtimes requeridos aprobados sobre un SHA identificable.
- **Aceptado con datos reales:** además concilia contra una base de origen real controlada, con evidencia anonimizada.
- **Productivo:** supera instalación, operación, seguridad, backup/restore, monitoreo y procedimientos de recuperación del entorno objetivo.
- **Retirado:** sustituido por otro contrato; se conserva la referencia histórica y la guía de migración.

No usar “terminado” como estado ambiguo.


## 4. Reutilización de módulos incorporados

Antes de proponer una entidad, API o proceso nuevo, consultar la [auditoría de reutilización de la base incorporada](BASE_REUSE_AUDIT.md). Allí se catalogan los circuitos de MyCompany 6.2, módulos regionales opcionales, APIs existentes y límites conocidos que deben superar pruebas antes de uso productivo. La regla es reutilizar primero el dueño/ledger nativo y añadir una extensión Rubrova sólo para el comportamiento que realmente falta.
