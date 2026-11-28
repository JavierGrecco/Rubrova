# Ficha de integración — Bom

**Estado:** fuente central revisada; aceptación runtime E2E pendiente.  
**Dominio:** MyCompany 6.2 / Manufacturing.

## Responsabilidad

\`Bom\` define la estructura normativa de un producto: cantidad base, componentes, subproductos y, por extensión, operaciones/routing. Es la fuente nativa para generar líneas planificadas en una orden de fabricación o desarme.

**Fuente:** [Bom.lsf](../../../vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf).

## Entidades y datos propietarios

- \`Bom\`: número, artículo, cantidad base/unidad derivada, nombre, archivado y marca default.
- \`ComponentLine\`: artículo componente, cantidad normativa y coeficiente de distribución de costo.
- \`ByproductLine\`: producto/unidad y cantidad normativa.
- \`Operation\` (extensión \`BomOperation\`): operación, centro de trabajo, hora de inicio y duración.
- \`BomNested\`: relación de componente con otra BOM, recorrido recursivo y clasificación de intermedio.

## Interacción nativa

Formulario \`bom\` con cabecera, componentes, subproductos y operaciones; lista \`boms\`; diálogo para seleccionar BOM; acciones para copiar, copiar operaciones y ver/imprimir estructura y costo; importación/exportación XLSX de BOM, componentes y subproductos.

Guía de usuario: \`vendor/mycompany/src/main/resources/docs/en/manufacturing/bom.md\`.

## Reglas y efectos

- La BOM default debe estar activa y corresponder al artículo; la orden comprueba que el artículo de la BOM coincida con el artículo que fabrica.
- Las cantidades de componentes/subproductos se calculan proporcionalmente a la cantidad base.
- Las BOM anidadas calculan cantidades recursivamente; el código prohíbe ciclos.
- Las operaciones pueden generar WorkOrders. Las operaciones de BOM intermedia marcada como intermediate pueden formar parte del routing de la orden.
- La estructura/costo usa costos de artículos y suma los componentes de la estructura.
- Al copiar BOM se copian componentes, subproductos y operaciones mediante puntos de extensión.

## Integración en Rubrova

1. Mantener un solo maestro de artículos/unidades.
2. Configurar BOM nativa por artículo y definir base de medida explícita.
3. Crear BOM nueva cuando cambie sustancialmente la estructura; archivar la anterior y cambiar el default con trazabilidad.
4. Recalcular líneas sólo antes de registrar ejecución real o después de evaluar qué reemplaza.
5. No crear una tabla Rubrova de recetas o componentes paralela.

## Límites y pruebas

El código revisado no demuestra versionado temporal/effective-dated completo, aprobación de receta, control de sustituciones, tolerancias de proceso ni liberación sanitaria. Probar conversiones de unidades, redondeos, BOM multinivel, subproductos, operaciones, ciclo prohibido, importación de códigos desconocidos y cambios de BOM en órdenes ya iniciadas.

## Dependencias

\`Product\`, \`Item\`, \`Company\`, \`ManufacturingSettings\`, \`BomNested\`, \`BomOperation\`, \`BomStructureCost\`, \`ManufacturingOrder\`.

Seguir la [guía obligatoria Fabricación + Proyectos](../MYCOMPANY_6_2_MANUFACTURING_PROJECTS_INTEGRATION.md).
