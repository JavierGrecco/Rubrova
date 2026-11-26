# Registro de decisiones técnicas

Este registro conserva el contexto y el motivo de las decisiones. Es acumulativo: una decisión posterior puede reemplazar a otra, pero no debe borrar la historia anterior.

Estados permitidos: **Propuesta**, **Aceptada**, **Reemplazada**, **Rechazada**. Una decisión aceptada en CI no implica por sí misma aceptación productiva.

## ADR-0001 — Respetar la versión de lenguaje fijada por la plataforma

- **Estado:** Aceptada.
- **Ámbito:** módulos lsFusion de Rubrova.
- **Contexto:** el runtime del proyecto está fijado a MyCompany 6.2 / lsFusion 6.2. La documentación de la plataforma cambia entre versiones; una forma válida en 7.x no necesariamente pertenece a la gramática 6.2.
- **Evidencia:** el run [45730502272](https://github.com/JavierGrecco/Rubrova/actions/runs/45730502272), commit `b189e2c7d526d5b9eebcf39590d845016ed8f742`, mostró al inicializar el servidor Linux y macOS: `RubrovaReplenishmentExport:11:12 mismatched input 'JSON' expecting ';'` al usar `RETURN JSON FROM`. El parser v6 define `RETURN` como una instrucción sin expresión. Los endpoints de CI existentes usan `EXPORT JSON FROM`.
- **Decisión:** todo módulo se escribe y revisa contra la documentación de la versión bloqueada en `platform/mycompany-6.2.lock.json`. Una actualización de plataforma requiere una prueba explícita de sintaxis y comportamiento; no copiar fragmentos de la documentación latest sin adaptación.
- **Consecuencia:** los cuatro endpoints de reposición vuelven a `EXPORT JSON FROM`. La regresión estática fija el contrato v6.
- **Referencias:** [lsFusion 6.x Access from an external system](https://docs.lsfusion.org/v6/Access_from_an_external_system/), [RETURN operator](https://docs.lsfusion.org/v6/RETURN_operator/), [EXPORT operator](https://docs.lsfusion.org/v6/EXPORT_operator/).
- **Límite:** queda pendiente validar en runtime el cuerpo HTTP y la regla de colecciones vacías bajo este patrón v6.

## ADR-0002 — No inferir una colección vacía por la ausencia de una propiedad JSON

- **Estado:** Aceptada como regla del adaptador; pendiente de aceptación nativa.
- **Ámbito:** exportaciones jerárquicas de MyCompany hacia Rubrova.
- **Contexto:** las pruebas nativas previas respondieron HTTP 200 y JSON parseable, pero el inspector no encontró `outgoingCommitments` como lista. El access log registró cuerpos de 12 bytes para sondas de compromisos en Linux y macOS. La prueba fallaba después del transporte.
- **Decisión:** las tres colecciones deben ir acompañadas de conteos independientes calculados con los mismos filtros. Sólo se normaliza una colección ausente a `[]` cuando el contador nativo vale cero; si el contador es positivo, falta la propiedad o la longitud no coincide, se rechaza.
- **Consecuencia:** se añaden `inventoryCount`, `outgoingCommitmentsCount` y `receiptsCount`; el adaptador y el inspector verifican ambos valores.
- **Riesgo pendiente:** falta confirmar que el conteo y el `JSON FROM` de lsFusion 6.2 recorren exactamente el mismo conjunto de filas con datos reales.

## ADR-0003 — La compilación no sustituye la carga del modelo en runtime

- **Estado:** Aceptada.
- **Ámbito:** CI de MyCompany/lsFusion y pruebas de módulos.
- **Contexto:** el build de artefactos del run [45730502272](https://github.com/JavierGrecco/Rubrova/actions/runs/45730502272) terminó correctamente, pero ambos servidores nativos fallaron al cargar el módulo por sintaxis inválida.
- **Decisión:** la aceptación requiere ejecutar el servidor recién construido, esperar la carga de módulos y ejecutar una acción autenticada de contrato. Los tests estáticos y la compilación son gates previos, no evidencia final de runtime.
- **Consecuencia:** el smoke nativo es obligatorio para afirmar que un módulo lsFusion puede ejecutarse. Un job marcado `continue-on-error` queda clasificado como diagnóstico y no como aceptación.

## ADR-0004 — Usar una clave compuesta de negocio para serializar líneas de venta

- **Estado:** Aceptada para el contrato de exportación; su estabilidad con distintas series/compañías requiere prueba de instalación real.
- **Ámbito:** identidad de compromisos de salida en la exportación nativa.
- **Contexto:** el agregado de negocio que se consolida es `Sales.OrderLine`, pero la capa de exportación no debe asumir que toda clase tenga un `id()` utilizable. La lógica actual serializa cada línea con el número comercial de la orden y el índice de la línea.
- **Decisión:** dentro de MyCompany se agrupa y suma por el objeto `Sales.OrderLine`; hacia JSON se expone `sourceLineId = Sales.number(Order) + Sales.index(OrderLine)`. Esta es una clave de intercambio, no una sustitución del agregado interno ni una promesa de clave primaria universal.
- **Consecuencia:** el adaptador rechaza claves compuestas duplicadas; la documentación de proyección debe describir la misma identidad. La versión de `main` consultada todavía contiene una redacción anterior que menciona `Sales.OrderLine.id`; esa diferencia se debe reconciliar al actualizar la rama contra `main`, sin reintroducir un ID que el contrato actual no usa.
- **Evidencia:** `RubrovaReplenishmentExport.lsf`, `scripts/replenishment/adapt_mycompany_native_export.py`, `docs/PROJECTED_STOCK_AND_REPLENISHMENT.md` de esta rama. Las pruebas estáticas prohíben el uso de `Sales.id(...)` y `Purchase.id(...)`.
- **Pendiente:** verificar unicidad de número de orden + índice dentro de las series, compañías y particiones del MyCompany real que se soporten. Si el ámbito de unicidad necesita compañía/serie, ampliar el contrato con una versión explícita.
