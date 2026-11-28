# Plantilla obligatoria — ficha de integración por módulo MyCompany / lsFusion

> Copiar esta plantilla para documentar un módulo o grupo pequeño de módulos que forman un único circuito. No completar por inferencia. Los campos desconocidos deben decir **Pendiente de investigar** y enlazar la evidencia disponible. No borrar secciones: declarar **No aplica** y justificar.

**Regla:** una ficha de integración tiene que permitir que otra persona implemente una extensión, API o adaptación sin reconstruir el análisis desde cero ni duplicar una capacidad existente.

## 0. Resumen de integración — lectura de 2 minutos

| Pregunta | Respuesta obligatoria |
|---|---|
| Módulo(s) exacto(s) | Nombre declarado en `MODULE`, no sólo nombre de archivo |
| Fuente fijada | Repositorio, tag/commit de `platform/source-lock.json`, ruta y líneas |
| Dominio y responsable | Dominio, entidad dueña y límites de responsabilidad |
| Estado de composición | Incluido en `RubrovaCustom`, fuera del cierre, opcional o sólo extensión |
| Nivel de evidencia | Inventariado / fuente revisada / cargado / verificado / conciliado / aceptado |
| Caso de uso cubierto | Qué quiere realizar el usuario y qué documento/resultado debe obtener |
| Punto de entrada de escritura | Formulario/acción/API que inicia o modifica la operación |
| Punto de lectura | Propiedades, formularios, consultas, informes o APIs que exponen el resultado |
| Datos que posee | Clases/documentos/ledgers cuya autoridad corresponde a este módulo |
| Dependencias críticas | REQUIRE y dependencias de negocio; distinguir ambas |
| Efectos transversales | Inventario físico, reservas, costo, deuda, pagos, caja, impuestos, informes, etc. |
| Riesgo de integración | Restricción, estado, permiso, concurrencia, idempotencia o reversión que puede romperse |
| Decisión reuse-first | Nativo configurable / extensión nativa / adaptador / desarrollo propio / parche upstream |
| Prueba que desbloquea | Escenario mínimo reproducible y evidencia esperada |

### Ruta inmediata para quien va a trabajar en el módulo

1. Leer esta ficha y el dossier principal indicado.
2. Abrir los archivos LSF exactos y sus módulos REQUIRE; revisar también los módulos que dependen de éste.
3. Seguir un caso de uso completo desde la pantalla/acción hasta documento, estado, ledger y reporte consumidor.
4. Consultar las fichas de módulos relacionados indicadas aquí y en el directorio.
5. Antes de escribir código, registrar qué contrato nativo se reutiliza y qué brecha concreta queda.

## 1. Identidad, versión y composición

- Nombre exacto del módulo (`MODULE`):
- Namespace:
- Archivo(s) fuente:
- Commit/tag fijado:
- Dominio:
- Módulo raíz que lo incorpora:
- Estado de inclusión en `RubrovaCustom`:
- REQUIRE directos:
- Dependencias transitivas relevantes:
- Módulos que lo requieren (consumidores directos):
- Extensiones que lo modifican:
- Recursos asociados: Java, JS, CSS, SQL, JRXML, imágenes, bundles y configuración.

Adjuntar enlaces de repositorio con ruta y, para afirmaciones críticas, líneas de fuente. No confundir REQUIRE con una relación de negocio.

## 2. Responsabilidad y límites

**Qué responsabilidad resuelve:** 

**Qué datos/decisiones posee y puede modificar:** 

**Qué queda fuera de su responsabilidad:** 

**Qué módulo es autoridad para cada dato relacionado:**

| Dato / entidad | Módulo dueño | Este módulo lee / crea / modifica | Fuente de verdad |
|---|---|---|---|
| | | | |

No duplicar entidades, estados, numeradores, reglas o ledgers que ya pertenezcan a otro módulo.

## 3. Casos de uso y secuencia operativa

Describir cada caso con actor, precondiciones, pasos, resultado y excepciones. El diagrama debe reflejar el comportamiento observado en la versión fijada.

| Caso de uso | Actor/rol | Precondiciones | Entrada/pantalla/acción | Resultado/documento | Excepciones |
|---|---|---|---|---|---|
| Alta / creación | | | | | |
| Edición | | | | | |
| Confirmación / ejecución | | | | | |
| Cancelación / reversión | | | | | |
| Parcialidad / devolución / aceptación | | | | | |

```text
Actor → pantalla / API → acción nativa → validaciones
      → documento/cabecera y líneas → estado
      → ledger(s) / relaciones → informe o consumidor
```

Identificar el nombre exacto de formularios, navegadores, acciones, propiedades y eventos. Una declaración detectada por el parser no demuestra que esté visible o habilitada en el runtime.

## 4. Modelo de datos y relaciones

### 4.1 Entidades y cardinalidades

| Entidad / clase | Módulo que la define | Clave/identidad | Relación y cardinalidad | Ciclo de vida |
|---|---|---|---|---|
| Cabecera | | | | |
| Línea | | | | |
| Documento origen | | | | |
| Documento destino | | | | |
| Maestro relacionado | | | | |

Documentar las clases, herencia, claves, referencias, cardinalidades y restricciones reales. Distinguir ID técnico, número visible, clave compuesta de negocio y claves externas.

### 4.2 Propiedades y semántica

| Propiedad | Clase/firma | Persistente/calculada/abstracta | Unidad/moneda/precisión | NULL/0/vacío | Productor y consumidores |
|---|---|---|---|---|---|
| | | | | | |

Explicar si la propiedad se materializa, cómo se recalcula y en qué fecha/huso horario se evalúa. No inferir significado por nombre.

### 4.3 Relaciones que deben preservarse

- Documento origen ↔ documento derivado:
- Cabecera ↔ líneas:
- Producto / socio / empresa / ubicación:
- Identidad externa / correlación:
- Historial y snapshots:
- Eliminación lógica, archivo o retención:

## 5. Formularios, navegación y experiencia de uso

| Elemento | Nombre exacto | Uso | Roles/condiciones | Acciones disponibles |
|---|---|---|---|---|
| Navegador / menú | | | | |
| Formulario principal | | | | |
| Grilla / detalle | | | | |
| Diálogo / selector | | | | |
| Informe / impresión | | | | |
| Importador / exportador | | | | |

Registrar filtros, orden, selección múltiple, edición en grilla, atajos, componentes web/móvil y textos localizados que afectan la operación. Indicar lo que cambia entre clientes.

## 6. Contratos de integración y comunicación

### 6.1 Integración dentro de lsFusion/MyCompany

- Módulos REQUIRE y extensiones permitidas:
- Clases/propiedades/acciones públicas que consume otro módulo:
- Hooks abstractos/overrides que deben utilizarse:
- Sesión/transacción y frontera APPLY/CANCEL:
- Eventos que disparan cambios:
- Lecturas permitidas y escrituras prohibidas:
- Orden de composición/carga:

No tratar un acceso lógico dentro de una misma instancia lsFusion como si fuera una API HTTP ni escribir SQL directamente en tablas físicas de otro módulo para eludir su contrato.

### 6.2 API / integración externa

| Endpoint/acción | Transporte | Auth/permisos | Entrada/filtro | Respuesta | Efecto | Idempotencia/errores |
|---|---|---|---|---|---|---|
| | | | | | | |

Documentar método, versión, esquema, tamaño, unidades, moneda, zona horaria, NULL/0/vacío, errores, timeout, concurrencia, reintentos, deduplicación, correlación y compatibilidad. Para `@@api`, `EXEC/EVAL` y acceso externo, seguir el mapa de capacidades lsFusion y los contratos del Manual técnico.

### 6.3 Integraciones de proveedor/hardware

Separar la autoridad del negocio, el adaptador, el proveedor y el dispositivo. Documentar autenticación, secretos, homologación, sandbox, estados inciertos, callback, conciliación y contingencia.

## 7. Estados, transacciones y efectos secundarios

### 7.1 Máquina de estados

| Estado origen | Acción/transición | Estado destino | Quién puede ejecutarla | Efectos | Reversión |
|---|---|---|---|---|---|
| | | | | | |

Registrar estados nativos, no sólo los captions. Distinguir listo, confirmado, completado, cancelado, pagado, aceptado y archivado.

### 7.2 Semántica transaccional

- APPLY / CANCEL:
- NEWSESSION / NESTEDSESSION:
- WHEN / eventos:
- Concurrencia y bloqueos:
- Reintentos seguros:
- Operaciones no idempotentes:
- Resultado de rechazo y recuperación:

### 7.3 Ledgers y efectos

| Efecto | Ledger/autoridad | Momento exacto | Regla de signo | Clave de conciliación | Consumidores |
|---|---|---|---|---|---|
| Movimiento físico | | | | | |
| Reserva / esperado | | | | | |
| Costo / valoración | | | | | |
| Deuda / pago / caja | | | | | |
| Impuesto / documento fiscal | | | | | |
| Reportes / analítica | | | | | |

Un pedido no es un movimiento físico; una reserva no es stock; una factura no es un cobro; una recomendación no es una orden. Documentar qué hecho produce cada ledger.

## 8. Seguridad, permisos y auditoría

- Roles/membresías requeridos:
- Permisos de navegación, formulario, acción y propiedad:
- Seguridad por usuario, empresa, sucursal y ubicación:
- Restricciones de API y autenticación:
- Acciones privilegiadas y secretos:
- Auditoría de actor, fecha, origen y correlación:
- Información personal/financiera expuesta:
- Pruebas negativas (denegación esperada):

No asumir que un botón oculto es autorización suficiente. Verificar en servidor y por API.

## 9. Configuración y prerrequisitos de runtime

- Parámetros, tipos y defaults:
- Empresa, sucursal, POS, ubicación, usuario y moneda:
- Datos iniciales/numeradores:
- Cliente, navegador, permisos y recursos:
- Servicios externos, driver, archivos, impresora o dispositivo:
- Requisito de red / modo offline:
- Scheduler / trabajos:
- Backups, restore y retención:
- Localización `es_AR`:

## 10. Excepciones y límites conocidos

| Situación | Comportamiento de fuente | Riesgo | Evidencia | Tratamiento/decisión |
|---|---|---|---|---|
| Duplicado | | | | |
| Operación parcial | | | | |
| Cancelación después de confirmar | | | | |
| Edición retroactiva | | | | |
| Concurrencia | | | | |
| Timeout / corte / respuesta incierta | | | | |
| Datos faltantes / NULL / cero | | | | |
| Usuario sin permiso | | | | |
| Recuperación / restore | | | | |

## 11. Matriz de pruebas y evidencia

| Prueba | Nivel (estática / build / runtime / E2E) | Datos/escenario | Resultado esperado | Resultado observado | Evidencia/commit |
|---|---|---|---|---|---|
| Camino feliz | | | | | |
| Validaciones | | | | | |
| Permisos | | | | | |
| Parcialidad | | | | | |
| Cancelación/reversión | | | | | |
| Concurrencia | | | | | |
| Conciliación | | | | | |
| Recuperación | | | | | |

Etiquetar cada afirmación como hecho de fuente, hecho de prueba, interpretación, hipótesis, decisión o pendiente. Registrar SHA, entorno, configuración, datos sintéticos/anónimos y resultado reproducible.

## 12. Decisión reuse-first y plan de integración

| Alternativa | Evaluación | Decisión | Motivo y evidencia |
|---|---|---|---|
| Nativo configurable | | | |
| Extensión nativa / hook | | | |
| Adaptador externo | | | |
| Módulo Rubrova nuevo | | | |
| Parche upstream | | | |
| Dependencia de terceros | | | |

**Brecha demostrada que justifica el cambio:**

**Diseño aprobado / contrato que se preserva:**

**Cambios permitidos:**

**Cambios explícitamente prohibidos:**

**Plan de migración/compatibilidad/rollback:**

**Pendientes que bloquean aceptación:**

## 13. Relaciones y rutas de lectura

- Fichas de módulos relacionados:
- Dossiers de dominio:
- Dossier de datos maestros:
- Dossier de utilidades:
- Capacidades lsFusion:
- Contratos y ADR del Manual técnico:
- Seguridad / resiliencia / backup:
- Tests y fixtures:

### Definición de terminado de esta ficha

La ficha es **apta como guía de integración** sólo cuando cubre fuente y composición, entidad dueña, contratos, estados, efectos, permisos, pruebas y módulos relacionados. Su estado de runtime/aceptación debe declararse aparte. No elevar una ficha de fuente revisada a aceptada por estar completa documentalmente.
