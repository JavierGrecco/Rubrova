# Índice obligatorio de mapeo — MyCompany 6.2 y lsFusion 6.2

**Propósito:** que ninguna persona del equipo vuelva a diseñar, integrar o duplicar una capacidad sin conocer primero qué ofrecen las dos plataformas base, qué módulos la implementan, cómo se relacionan y qué evidencia existe.

**Estado del relevamiento: EN CURSO.** Este índice es la puerta de entrada y el registro de cobertura; no declara que los 800 módulos ni todas las capacidades de lsFusion estén funcionalmente auditados. La fuente de verdad de estado, decisiones, contratos y roadmap sigue siendo el [Manual técnico canónico](../ENGINEERING_MASTER.md). Los mapas de esta carpeta son dossiers de evidencia por dominio y se mantienen subordinados a ese manual.

## 1. Alcance real del inventario

### MyCompany 6.2

- Snapshot fijado: `lsfusion-solutions/mycompany`, versión 6.2, commit `d21ca6978717b98b6300d90267f9767db7414008`.
- Inventario estático: **800 módulos LSF**.
- Cierre de dependencias alcanzado desde `RubrovaCustom`: **719 módulos** — 688 de MyCompany, 24 de la plataforma lsFusion y 7 extensiones propias.
- Fuera del cierre actual: **112 módulos MyCompany** — 96 regionales y 16 no regionales. Estar fuera del cierre no significa que sean inútiles ni que deban descartarse.
- Documentación indexada: **347 archivos Markdown** — 112 en inglés, 121 en polaco y 114 en ruso. Las rutas no son equivalentes a una lectura funcional completa: faltan lectura y asociación sistemática de páginas con módulos, capacidades y flujos. No hay documentación MyCompany en español en el snapshot.

### lsFusion 6.2

- Snapshot fijado: `lsfusion/platform`, versión 6.2, commit `dd4dbe5bf9b136e73e18fe25d741253929324350`.
- Inventario indicado por la auditoría: **49 módulos LSF de plataforma** y **3.330 archivos Java**.
- Documentación indexada: **684 páginas Markdown** (342 en inglés y 342 en ruso) y **178 imágenes**.
- Hay 33 páginas por idioma sin encabezados Markdown estructurados; deben inspeccionarse individualmente, no excluirse del relevamiento.
- El mapa de capacidades sigue abierto: identificar operadores y conceptos no demuestra sus contratos reales, interacciones, efectos transaccionales, seguridad ni compatibilidad de runtime.

**Importante:** las cantidades de módulos de los mapas por dominio se solapan. Un mismo módulo puede extender otro dominio o estar físicamente en una carpeta compartida. No deben sumarse para inferir un total nuevo ni usarse en lugar del catálogo estructural generado desde la fuente.

## 2. Dossiers de MyCompany

| Área | Dossier | Cobertura declarada | Pendiente principal |
|---|---|---|---|
| Inventario funcional general | [MYCOMPANY_6_2_FUNCTIONAL_MAP.md](MYCOMPANY_6_2_FUNCTIONAL_MAP.md) | Catálogo general de 800 módulos, composición `REQUIRE`, dominios y documentación | Asociar y leer las 347 páginas; cerrar módulos y flujos aún no revisados |
| POS, retail y sesiones | [MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md](MYCOMPANY_6_2_RETAIL_POS_SESSIONS_MAP.md) | 30 fuentes; caja, sesiones, cobro, descuentos, venta, devoluciones y extensiones Rubrova | Aceptación E2E, hardware/fiscalidad y conciliación completa de caja |
| Ventas, precios y ledger comercial | [MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md](MYCOMPANY_6_2_SALES_PRICING_LEDGER_MAP.md) | 92 módulos; pedidos, precios, descuentos, despacho, facturación y margen; análisis parcial | Cierre de extensiones, estados, reportes y conciliación de runtime |
| Inventario, reservas y costos | [MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md](MYCOMPANY_6_2_INVENTORY_LEDGER_MAP.md) | Ledgers físicos, reservas/disponible, transferencias, ajustes, lotes y costos; análisis parcial | Pruebas de runtime y conciliación entre documentos, ledgers y costos |
| Compras y reposición | [MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md](MYCOMPANY_6_2_PURCHASE_REPLENISHMENT_MAP.md) | 49 módulos; pedidos, recepciones, facturación vinculada, listas de proveedor y reposición; lectura parcial | Extensiones, políticas, casos límite y conciliación de deuda/stock/costo |
| Facturación, deuda, pagos y cuentas | [MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md](MYCOMPANY_6_2_INVOICING_LEDGER_MAP.md) | 134 módulos; facturas, notas, pagos, impuestos y ledgers; lectura profunda de fuentes principales | Pruebas transaccionales, conciliación contable y adecuación fiscal argentina |
| Datos maestros y relaciones | [MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md](MYCOMPANY_6_2_MASTERDATA_RELATIONSHIPS_MAP.md) | 84 módulos; socios, empresas, personas, artículos, categorías, atributos, UOM, packs, códigos y contratos | Extensiones, privacidad, integridad, deduplicación, APIs y adecuación local |
| CRM y leads | [MYCOMPANY_6_2_CRM_LEADS_MAP.md](MYCOMPANY_6_2_CRM_LEADS_MAP.md) | 24 fuentes; ciclo del lead, estados, Kanban, comunicación, marketing y conversión | Runtime y conectores externos |
| RR. HH., reclutamiento, asistencia y haberes | [MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md](MYCOMPANY_6_2_HR_ATTENDANCE_PAYROLL_MAP.md) | 25 fuentes; circuitos principales de selección, asistencia y haberes | Runtime, privacidad, reglas laborales y liquidación argentina |
| Proyectos, tareas, equipos y tiempos | [MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md](MYCOMPANY_6_2_PROJECT_MANAGEMENT_INTEGRATIONS_MAP.md) | 78 módulos; workflow, horas, turnos e integraciones con otros dominios | Extensiones completas, permisos, costos y conciliación de runtime |
| Flota, conductores, servicios y gastos | [MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md](MYCOMPANY_6_2_FLEET_VEHICLE_COSTS_MAP.md) | 13 fuentes; entidades y relaciones principales | Runtime, gastos y automatizaciones de mantenimiento |
| Utilidades compartidas | [MYCOMPANY_6_2_UTILITY_MODULES.md](MYCOMPANY_6_2_UTILITY_MODULES.md) | 21 módulos transversales; lectura inicial de fuentes | Contratos de cada integración y pruebas de runtime |
| Regionalizaciones | [MYCOMPANY_6_2_REGIONAL_MODULES.md](MYCOMPANY_6_2_REGIONAL_MODULES.md) | 96 módulos de Bulgaria, Polonia y Rusia inventariados | Auditoría funcional individual; compatibilidad legal/técnica con Argentina |

Los dossiers describen el estado que cada uno declara. Si uno cambia, el índice y el estado/resumen del Manual técnico deben actualizarse en el mismo cambio.

## 3. Dossier de capacidades de lsFusion

[LSFUSION_6_2_CAPABILITY_MAP.md](LSFUSION_6_2_CAPABILITY_MAP.md) es el mapa independiente de la plataforma; no debe confundirse con el mapa de MyCompany.

El relevamiento debe cubrir, al menos:

- Lenguaje y modelo lógico: clases, objetos, herencia, propiedades persistentes/calculadas/abstractas, acciones, operadores, expresiones, restricciones y eventos.
- Composición: módulos, espacios de nombres, `REQUIRE`, extensiones, puntos abstractos, orden y condiciones de carga.
- Interacción: formularios, grupos, filtros, ordenamientos, navegador, acciones, diálogos, atajos y permisos.
- Ejecución: sesiones, `APPLY`/`CANCEL`, transacciones, eventos sincrónicos/asincrónicos, concurrencia y aislamiento.
- Persistencia y rendimiento: tablas, índices, SQL generado, materializaciones, migraciones, bloqueos y profiler.
- Integraciones: APIs, autenticación/autorización, import/export, archivos, correo, procesos externos y errores.
- Clientes y runtime: web, escritorio, GWT/JavaScript, Java, RMI, recursos, despliegue, configuración, logs y recuperación.
- Operación y administración: usuarios, roles, seguridad, monitorización, scheduler, copias y herramientas de diagnóstico.

No alcanza con describir el operador o encontrar una clase: hay que seguir su uso concreto desde la pantalla/acción hasta los datos, transacciones, salidas y efectos laterales.

## 4. Inventario reproducible desde la fuente

Los registros estructurales se generan a partir de los snapshots fijados; no deben copiarse manualmente ni sustituir la lectura semántica.

Desde la raíz del repositorio:

```bash
node scripts/platform/audit-lsf-source.mjs \
  --json-output /tmp/rubrova-lsfusion-source-catalog.json \
  --markdown-output /tmp/rubrova-lsfusion-module-register.md

node scripts/platform/audit-source-docs.mjs \
  --json-output /tmp/rubrova-source-document-catalog.json \
  --markdown-output /tmp/rubrova-source-document-register.md
```

El primer registro identifica módulos, dominio/ruta, pertenencia al cierre de `RubrovaCustom`, namespace y conteos estructurales de clases, propiedades, acciones, formularios, restricciones, eventos y APIs; también reconoce otros tipos de recursos. El segundo indexa documentación por idioma, ruta, título y encabezados.

Ambos son catálogos de navegación y cobertura. **No prueban** que el código se cargue, que una pantalla esté habilitada, que una acción respete los permisos esperados ni que el flujo concilie correctamente.

## 5. Puerta obligatoria antes de diseñar o integrar

Para cada nueva función, integración, ampliación, migración o cambio que afecte MyCompany/lsFusion:

1. Definir el caso de uso y el resultado de negocio esperado.
2. Buscar en este índice y en el catálogo estructural los módulos candidatos, sus dependencias `REQUIRE` y extensiones consumidoras/productoras.
3. Revisar los dossiers relevantes, los documentos fuente correspondientes y la implementación 6.2 fijada. Revisar también los módulos fuera del cierre y las regionalizaciones cuando puedan aportar una capacidad útil.
4. Seguir el recorrido real: navegación/formulario → acción → propiedades/eventos/restricciones → documento y líneas → ledgers/estados → reportes/APIs/efectos externos.
5. Identificar autoridad de datos, claves, unidades, moneda, precisión, NULL/0/vacío, estados, idempotencia, permisos, concurrencia, auditoría y rollback.
6. Decidir explícitamente: **reutilizar nativo**, **extender módulo nativo**, **adaptar mediante contrato/API**, **crear módulo propio**, **parchear upstream** o **agregar dependencia externa**. Justificar por qué las otras opciones no son mejores.
7. Probar los escenarios positivos, negativos, concurrentes y de recuperación; distinguir fuente, compilación, carga, prueba funcional, conciliación y aceptación.
8. Actualizar el dossier afectado, este índice cuando cambie la cobertura y el Manual técnico canónico en el mismo cambio.

Una implementación propia no se justifica sólo porque sea más cómoda o porque todavía no se conozca el módulo nativo. Primero se investiga. Si falta evidencia para cerrar una decisión, se registra como pendiente/bloqueada y no se declara inexistente la capacidad.

## 6. Niveles de evidencia — no confundir

| Nivel | Qué significa | Qué NO permite afirmar |
|---|---|---|
| Inventariado | Se conoce nombre, ruta y dominio inicial | Que se conozca la función |
| Documentado | Se encontró en manual o ayuda | Que el código coincida o funcione |
| Fuente revisada | Se siguió implementación, dependencias y efectos | Que forme parte del runtime activo |
| Composición resuelta | Se conoce si entra por `REQUIRE`/extensión | Que esté cargado o habilitado |
| Cargado | Se confirmó en la configuración/runtime concreto | Que el flujo esté bien conciliado |
| Verificado | Se ejecutó con evidencia reproducible | Que todos sus efectos sean correctos |
| Conciliado/aceptado | Se revisaron datos, permisos, errores, ledgers y recuperación | Que cumpla normativa o producción sin pruebas específicas |

## 7. Qué falta para poder decir “mapeo completo”

La cobertura sólo podrá cerrarse cuando:

- Los 800 módulos MyCompany estén clasificados por responsabilidad y consumidor/productor; los módulos fuera de `RubrovaCustom` tengan decisión explícita de interés/no interés y justificación.
- Las 347 páginas de documentación MyCompany estén leídas o descartadas con motivo y asociadas a módulos/capacidades/idioma; se revisen las instrucciones y recursos específicos regionales.
- Los 684 documentos y 178 imágenes de lsFusion estén clasificados y las páginas pertinentes se vinculen a conceptos, API, runtime y herramientas. Se aclaren las diferencias documentales de versión 6.1 que aparecen en el snapshot 6.2.
- Cada dominio relevante tenga grafo de dependencias, flujos de punta a punta, formularios, acciones, estados, restricciones, eventos, permisos, APIs, ledgers y reportes.
- Cada capacidad priorizada tenga pruebas de runtime, conciliación y recuperación, no sólo inspección estática.
- Se mantenga una matriz de compatibilidad Argentina: ARCA, impuestos, comprobantes, moneda, medios de pago, privacidad, trabajo, bancos y servicios externos, con fuentes y pruebas específicas.

**Criterio vigente:** el mapeo continúa abierto. Hasta cerrar esos puntos, cualquier documento o implementación debe usar estados parciales y límites explícitos. No se debe escribir “MyCompany/lsFusion ya fue completamente analizado”.

## 8. Regla de mantenimiento

- Un cambio de código que use o extienda la plataforma actualiza el dossier y su evidencia, incluso cuando la conclusión sea “se reutiliza sin cambios”.
- Una nueva capacidad descubierta actualiza el inventario y los vínculos; no crea otro mapa paralelo.
- Una actualización upstream obliga a regenerar catálogos y revalidar rutas, dependencias, contratos, permisos y pruebas.
- Todo PR o commit debe dejar clara la decisión de reutilización, los módulos/rutas revisados y qué quedó pendiente. Para contribuciones se usa la plantilla del repositorio y las instrucciones de `AGENTS.md`.
- Si el relevamiento encuentra una discrepancia entre este índice, el dossier y el Manual técnico, se corrige en el mismo cambio. La precedencia del estado y las decisiones la mantiene `docs/ENGINEERING_MASTER.md`.

