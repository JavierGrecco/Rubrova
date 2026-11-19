# Evaluación comparativa de plataformas

**Revisión:** 19 de noviembre de 2026  
**Estado:** protocolo preparado; ejecución local pendiente.  
**Alcance:** uso interno, personal y privado. No se prevé distribuir, revender ni ofrecer el sistema como servicio a terceros.

Este documento convierte la investigación en una prueba repetible. No elige una plataforma por su README, una demo o la cantidad de módulos anunciados. La elección depende de ejecutar los mismos flujos, con datos sintéticos, y comprobar integridad, recuperación, esfuerzo de adaptación y mantenimiento.

## Decisión de evaluación

La ronda activa queda reducida a dos candidatos integrales:

1. **Posnic 1.9.2**, para comprobar cuánto resuelve de POS local, caja, ventas e inventario y qué tan real es su continuidad offline.
2. **ERPNext 16.60.0 + Frappe Framework 16**, para comprobar cuánto adelanta de compras, inventario, producción, costos y contabilidad, sin asumir que su POS satisface nuestro requisito offline.

No se adoptan ambos ni se conectan como fuentes de verdad paralelas. Los demás proyectos quedan como componentes o referencias especializadas. Odoo Community 20 y Medusa v2 dejan de ser finalistas de esta ronda; pueden reabrirse solo si aparece evidencia técnica concreta que cambie la comparación.

**Resultado actual: ninguna plataforma está aprobada.** No se han ejecutado localmente Posnic ni ERPNext para Rubrova, no se ha incorporado código externo y no hay una aplicación de Rubrova implementada.

## Versiones y procedencia que se deben fijar

| Proyecto | Referencia de prueba | Procedencia comprobada | Precaución |
|---|---|---|---|
| Posnic | Tag `v1.9.2` | Commit `4096126edb1ff4fd337069697776254215dc2680`; release publicada el 16/11/2026 | No probar desde una rama móvil sin registrar commit. |
| Posnic, revisión adicional | Rama `main` | HEAD consultado: `bf97ab2e2cdfba88121d369cacf48dd877ac8b55`, seis commits posterior al tag | Comparar diferencias con el tag antes de decidir si un arreglo posterior cambia la evaluación. |
| ERPNext | Release `v16.60.0` | Tag asociado al commit `886ab6ae187244e7f1b852393384ab6019d56264`; publicada el 17/11/2026 | Mantener fija la versión durante la prueba. |
| Frappe Framework | Rama de versión `version-16` | Commit consultado: `2df0425571ebbaed878eabc3edc5b7e7c3327ae0`; actualización 16.60.2 del 18/11/2026 | Registrar el commit exacto desplegado y no actualizar durante la prueba. |

El repositorio Posnic declara `develop` como rama predeterminada, pero en la consulta del 19/11/2026 esa rama estaba divergida respecto del tag estable: dos commits por delante y 27 por detrás. La rama `main` tenía seis commits por delante del tag. Por reproducibilidad, la primera prueba debe usar el tag estable `v1.9.2`; las diferencias de `main` se revisan aparte. No usar `develop` como sustituto silencioso del release.

Fuentes de versión:
- [Posnic v1.9.2](https://github.com/Posnic/POS/releases/tag/v1.9.2)
- [Posnic main](https://github.com/Posnic/POS/tree/main)
- [ERPNext v16.60.0](https://github.com/frappe/erpnext/releases/tag/v16.60.0)
- [Frappe Framework version-16](https://github.com/frappe/frappe/tree/version-16)

## Perfil técnico y riesgos conocidos

### Posnic

La aplicación de escritorio usa Electron y Node.js; la API local usa Express/Mongoose y MongoDB. El propio repositorio se identifica como AGPL-3.0-only y el paquete revisado exige Node.js >=22.12.

**Encaje potencial**
- POS para comercio minorista y gastronomía, catálogo, variantes, ventas, devoluciones, pagos parciales, compras, inventario, clientes, permisos y reportes.
- La edición de escritorio puede mantener API y base principal en el equipo de caja.
- La instalación self-hosted permite que varios equipos de una misma red local usen una base común.

**Límites que debemos probar**
- Self-hosted con varios clientes no significa varias bases independientes sincronizadas. La documentación del proyecto dice que sincronizar cajas o sucursales separadas corresponde a Posnic Cloud, un servicio aparte.
- La prueba offline publicada que acompaña al producto está acotada: una venta sintética en efectivo completada y reabierta en una versión anterior, dentro de Electron, con ciertos hosts bloqueados. No demuestra una jornada completa, corte de energía, recuperación tras matar el proceso, terminales de pago ni todos los flujos.
- El outbox local de sincronización es un acelerador opcional; el propio código aclara que no es el mecanismo de registro de la venta y que el escaneo periódico sigue siendo el respaldo.
- El modelo contiene campos y reglas orientados a India, incluidos datos GST. Hay que medir el trabajo para reemplazarlos o aislarlos frente a IVA, tipos de comprobante, CUIT, puntos de venta y ARCA.
- La dependencia de MongoDB/Mongoose y la arquitectura propia tienen costo de migración y mantenimiento; no asumir que se pueden extraer módulos sueltos sin arrastrar parte del sistema.

**Licencias y paquete**
- Código propio: AGPL-3.0-only. Para nuestro uso privado, GPL/AGPL no son descartes automáticos; sí debemos mantener avisos y revisar las condiciones si usuarios acceden remotamente a una versión modificada por red o si cambia el uso previsto.
- El paquete de escritorio revisado incorpora MongoDB Community Server 7.0.14 bajo SSPL-1.0, una licencia separada de la del POS. No describir el instalador entero como AGPL.
- El aviso de terceros identifica amCharts 4 como comercialmente licenciado. No reutilizar ese componente sin confirmar que la licencia permite nuestro uso; la opción segura puede ser reemplazarlo por una biblioteca compatible o no usar esa parte.
- Deben inspeccionarse los avisos y licencias de las dependencias transitivas del paquete exacto que se ejecute.

### ERPNext + Frappe

ERPNext aporta procesos ERP profundos: inventario, abastecimiento, compras, fabricación, contabilidad y administración. Frappe Framework proporciona el entorno de aplicaciones, documentos, permisos, API, formularios y tareas de fondo.

**Encaje potencial**
- Puede adelantar mucho trabajo de compras, proveedores, recepciones, costos, stock, producción, cuentas e informes.
- Los perfiles de POS configuran empresa, almacén, medios de pago, listas de precios, impuestos, terminal y comportamiento de la caja.
- Frappe Framework tiene licencia MIT; ERPNext tiene GPL-3.0. No confundir ambas licencias.

**Límites que debemos probar**
- La cobertura de ERP no garantiza una caja de alta velocidad ni una experiencia táctil simple.
- No damos por demostrado el offline duradero de la versión 16. Hay que cortar internet, cerrar el navegador o matar el proceso y recuperar las operaciones sin pérdidas ni duplicados.
- El stack habitual de Frappe/ERPNext gira alrededor de Python y MariaDB; PostgreSQL no se debe asumir como una opción equivalente o estable para esta evaluación.
- La adaptación del POS, localización argentina, hardware y experiencia de uso puede exigir extensiones considerables.

## Reglas de prueba comunes

- Usar instalaciones aisladas y bases nuevas. No cargar ventas reales, datos personales, certificados privados ni credenciales de producción.
- Usar el mismo conjunto de datos sintéticos, zona horaria, moneda, catálogo, flujo y casos de error.
- Registrar versiones, commits, sistema operativo, configuración, comandos, duración, resultados y capturas de evidencia.
- No modificar el núcleo de los candidatos durante la primera vuelta. Registrar cada extensión, parche o workaround por separado.
- Repetir cada escenario crítico al menos tres veces y repetir sincronizaciones o reintentos cuando corresponda.
- Mantener deshabilitadas las integraciones que generen cargos o efectos externos. ARCA se prueba únicamente en homologación, nunca con certificados de producción durante esta evaluación.
- Un escenario no probado se marca **pendiente**, no aprobado. Un flujo que solo funciona con la ventana abierta no pasa la recuperación.

## Datos sintéticos compartidos

La prueba debe representar una operación argentina sencilla, sin utilizar información real. Los datos canónicos, con importes en unidades menores enteras y resultados esperados, están en [dataset sintético](fixtures/platform-evaluation.json):

| Dato | Valor de prueba |
|---|---|
| Idioma y zona | Español (Argentina), `America/Argentina/Cordoba` |
| Moneda | ARS |
| Artículo por unidad | `SKU-UNIT-001`, precio de ejemplo $10.000 |
| Artículo por peso | `SKU-WEIGHT-001`, venta en kg, precisión de 0,001 kg |
| Variante | `SKU-VAR-001`, dos variantes con códigos distintos |
| Proveedor | `PROV-TEST-001` |
| Cliente | `CLI-TEST-001`, identidad ficticia |
| Caja inicial | $20.000 |
| Venta de prueba | Dos artículos; total de ejemplo $10.000 |
| Pago mixto | $6.000 efectivo + $4.000 transferencia simulada |
| Descuento | 10% en una línea, con motivo y operador registrados |

Los importes son datos didácticos y no representan precios de mercado ni reglas fiscales. La prueba debe incluir además una venta por peso de 0,325 kg y comprobar redondeos, cantidades, importe por línea y total.

## Guion de aceptación común

| ID | Escenario | Evidencia exigida | Falla crítica |
|---|---|---|---|
| P01 | Alta e importación de artículos, variantes, códigos y unidades | Datos conservados, búsqueda por código y errores de importación identificados | Artículo duplicado o unidad mal interpretada |
| P02 | Venta rápida con lector simulado | Carrito, precio aplicado, cantidad y ticket coinciden | Venta o línea perdida/duplicada |
| P03 | Descuento manual y promoción | Regla, valor previo, importe, motivo, operador y autorización auditables | Descuento silencioso o no trazable |
| P04 | Venta por peso | 0,325 kg, precisión y redondeo coherentes | Diferencia inexplicable entre balanza, línea y total |
| P05 | Pago mixto y vuelto | $6.000 + $4.000 para total $10.000; movimientos y medios separados | Pago duplicado, suma incorrecta o caja descuadrada |
| P06 | Apertura, cierre y arqueo | Saldo esperado, efectivo contado, diferencia y responsable | No poder reconstruir el saldo |
| P07 | Devolución parcial | Línea devuelta, motivo, reintegro y destino del stock diferenciados | Borrar o sobrescribir la venta original |
| P08 | Compra y recepción parcial | Proveedor, orden, cantidades recibidas, costo y stock | Stock o costo actualizado sin documento trazable |
| P09 | Producción básica | Receta/BOM, consumo, rendimiento y merma | Consumo de insumos sin trazabilidad |
| P10 | Dos puestos en la misma LAN | Permisos, concurrencia y consistencia sobre una única base local | Doble numeración, saldo o stock inconsistente |
| P11 | Corte de internet | Venta local guardada y estado de servicios externos visible | Bloquear o perder una venta local ya confirmada |
| P12 | Cierre forzado/reinicio | Reiniciar con operaciones pendientes y verificar recuperación | Pérdida, duplicación o corrupción |
| P13 | Reintento y sincronización repetida | Repetir el envío tres veces y conservar una única operación | Doble venta, pago, factura o movimiento |
| P14 | Conflicto de precio/stock | Conflicto explícito y conciliación con registro de decisión | Sobrescritura silenciosa o último cambio gana en dinero/stock |
| P15 | Backup y restauración | Restaurar en una instancia limpia y conciliar conteos/saldos | Backup ilegible o restauración incompleta |
| P16 | Hardware | Ticket de 80/57 mm, lector, balanza y cajón; primero simulado, luego físico | Confirmar compatibilidad por marca sin prueba |
| P17 | Fiscalidad argentina | Adaptador separado, comprobantes en homologación y recuperación de estado incierto | Emisión duplicada o reintento ciego |

En P11 se debe distinguir pérdida de internet de pérdida de red local. En un servidor local compartido, los otros puestos pueden seguir conectados por LAN; una caja con su propia base desconectada es un caso distinto y debe documentarse como tal.

En P17 no se emitirán comprobantes reales. Una respuesta incierta de ARCA debe pasar por consulta/recuperación antes de cualquier nuevo intento; nunca asumir que un timeout significa que no se emitió.

## Medición y decisión

Cada criterio se califica de 0 a 5 únicamente después de ejecutar la prueba:

| Nota | Interpretación |
|---:|---|
| 0 | No existe o no se pudo demostrar |
| 1 | Solo funciona con un workaround manual frágil |
| 2 | Requiere personalización invasiva o cambios del núcleo |
| 3 | Funciona mediante una extensión propia con esfuerzo apreciable |
| 4 | Funciona mediante extensión/configuración limpia y mantenible |
| 5 | Función nativa demostrada con pruebas repetibles y evidencia |

Ponderación propuesta:

| Área | Peso |
|---|---:|
| Integridad transaccional, offline, reinicio y restauración | 35% |
| POS, pagos, caja, devoluciones y operación del cajero | 20% |
| Inventario, compras, costos y producción | 15% |
| Extensibilidad, actualizaciones y esfuerzo de mantenimiento | 10% |
| Argentina, ARCA y adaptación fiscal | 10% |
| Hardware y tickets | 5% |
| Simplicidad de operación y experiencia de uso | 5% |

No se calculará un ganador ponderado si falla una condición excluyente. Para pasar la prueba, cada candidato debe demostrar: una venta confirmada y sus efectos asociados exactamente una vez; recuperación tras cierre forzado; backup restaurable; auditoría; roles correctos; y una ruta fiscal argentina viable. Si no supera esos mínimos, no compensa tener más pantallas o módulos.

La decisión final debe incluir también el costo de actualización, la cantidad de código que habría que mantener, la compatibilidad con nuestros perfiles sectoriales y qué partes conviene tomar como módulos separados.

## Componentes especializados: evaluar aparte

Estos componentes no convierten por sí solos a una plataforma en la base del producto:

- **pos-toolkit** (Apache-2.0): tiene código real para impresoras ESC/POS, cajón, scanners seriales, balanzas HID y constructor de tickets. El plugin de hardware es Rust/Tauri v2, por lo que requiere que esa arquitectura de escritorio tenga sentido; no es un plugin universal de navegador. `register-core` figura como planificado, no implementado.
- **emupos** y **ESCPost** (Apache-2.0): herramientas para simular periféricos y probar tickets. No certifican compatibilidad física.
- **arca-sdks**: el paquete `@ramiidv/arca-facturacion` 7.1.0 declara MIT y Node >=22.12; contiene WSAA/WSFE/WSFEX/CAEA y pruebas de homologación configurables. Es un adaptador candidato, no un motor contable ni una garantía de cumplimiento fiscal. Se probará solo en homologación.
- **PowerSync Open Edition** (Apache-2.0): candidato de sincronización SQLite/PostgreSQL, con funciones Enterprise/Cloud separadas. Debe medirse frente al requisito concreto; no resuelve por sí solo las invariantes de caja, stock o emisión fiscal.
- **Dexie.js** (Apache-2.0): persistencia IndexedDB, no sincronización distribuida completa.

La revisión de licencias se hace para la versión y los archivos que realmente se incorporen. El uso privado permite considerar código GPL/AGPL, pero no elimina las licencias separadas de dependencias, fuentes, imágenes, servicios o componentes comerciales.

## Estado de ejecución

| Actividad | Estado |
|---|---|
| Inspección documental y manifiestos de Posnic | Hecha |
| Fijación de release/commit para Posnic | Hecha |
| Inspección documental de ERPNext/Frappe v16 | Hecha parcialmente |
| Protocolo común y datos sintéticos | Preparados |
| Instalación local de Posnic | Pendiente |
| Instalación local de ERPNext/Frappe | Pendiente |
| Ejecución P01–P17 | Pendiente |
| Revisión completa de dependencias y seguridad | Pendiente |
| Decisión de plataforma | Pendiente |
| Incorporación de código externo | No iniciada |

**Próximo paso técnico:** desplegar las dos plataformas en entornos aislados, primero Posnic v1.9.2 y luego ERPNext v16.60.0/Frappe v16, y ejecutar el guion sin desarrollar aún módulos propios de Rubrova. Después de medir, decidiremos si adoptamos una base integral o construimos nuestro monolito modular tomando componentes especializados.
