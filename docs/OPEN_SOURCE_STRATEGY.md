# Estrategia de reutilización de código abierto

**Revisión:** 20 de noviembre de 2026  
**Estado:** uso interno privado confirmado; selección técnica pendiente; no se incorporó código externo.

## Objetivo

Rubrova se construye para uso interno. La prioridad es aprovechar aplicaciones, módulos, plugins y bibliotecas existentes que ahorren desarrollo real, sin sumar dependencias que terminen siendo más difíciles de mantener que una implementación pequeña.

No vamos a desarrollar desde cero funciones maduras de ERP, POS, inventario, compras, fabricación, fiscalidad, logística, hardware o analítica si podemos adoptarlas o integrarlas con garantías. La estrategia operativa se define en [Estrategia de implementación basada primero en reutilización](REUSE_FIRST_IMPLEMENTATION_STRATEGY.md). La investigación de bibliotecas y SDKs especializados está en [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md).

## Qué opciones evaluamos

1. **Adoptar una aplicación existente** y configurarla como autoridad de un dominio o de un conjunto coherente de procesos.
2. **Extenderla con módulos/plugins soportados**, manteniendo las modificaciones fuera del núcleo cuando sea posible.
3. **Integrar una aplicación especializada** como unidad de dominio independiente mediante su API y persistencia propias.
4. **Incorporar SDK, drivers o bibliotecas** para funciones técnicas concretas.
5. **Mantener un fork o extraer código** cuando se haya probado que es más económico que reemplazarlo y se pueda sostener con cada actualización.
6. **Crear código propio** sólo para necesidades que no estén cubiertas razonablemente.

No se adopta una plataforma por cantidad de pantallas, popularidad o amplitud declarada. Cada producto debe pasar pruebas de los flujos que le asignaríamos.

## Candidatos vigentes

- **MyCompany/lsFusion 6.2:** primera prueba por la amplitud ERP/POS, módulos propios externos y API HTTP. MyCompany declara Apache-2.0; lsFusion se licencia por separado bajo LGPL-3.0. Todos los módulos de una instalación comparten base de datos, por lo que no se deben describir como microservicios.
- **Tryton, serie 7.8:** comparación prioritaria por arquitectura de tres capas, PostgreSQL y clientes Windows/macOS. Incluye el módulo oficial `sale_point` para ventas, devoluciones, pagos y sesiones de caja; al contabilizar genera movimientos de stock y asientos en el mismo servidor/base. Fijar cada paquete por separado y probar la autoridad de stock/contabilidad.
- **Dolibarr 24.0.3:** comparación prioritaria por CRM/ERP modular y API REST, triggers y hooks. Sigue siendo una aplicación integrada, no una separación automática en microservicios.
- **ERPNext 16.60.0 + Frappe 16:** alternativa de amplia cobertura administrativa. ERPNext declara GPL-3.0 y Frappe Framework MIT; las licencias de otras apps y dependencias se revisan por separado.
- **Posnic 1.9.2:** candidato específico para POS local. El código propio declara AGPL-3.0-only; el paquete revisado incluye componentes con licencias independientes (MongoDB SSPL-1.0 y amCharts comercial). No se aprueba el paquete completo por su licencia raíz.
- **uniCenta oPOS 5.5.2:** queda pendiente de obtener y verificar el código fuente de esa versión; la descarga disponible requiere iniciar sesión. Los mirrors históricos no prueban la licencia ni la integridad del código actual.
- **Apache OFBiz 24.09.08:** referencia de arquitectura orientada a servicios de negocio; la serie 24.09 está congelada en funciones y recibe correcciones, y su complejidad requiere justificar una prueba específica.
- **InvenTree y OpenBoxes:** opciones especializadas para inventario técnico y WMS. Se evalúan si la profundidad de depósito/manufactura lo requiere y si pueden asumir una autoridad de stock sin duplicarla.
- **Odoo y localización argentina:** el addon público oficial `l10n_ar` existe en Odoo 19.0 y 20.0, declara LGPL-3 y cubre la base contable argentina; no es por sí solo el emisor electrónico. La documentación oficial enumera `l10n_ar_edi` para WSFE/CAE, pero esa ruta no aparece en el repositorio Community público consultado, por lo que el código/licencia de ese componente debe verificarse por separado.
- **leonobitech/l10n_ar_arca_edi:** addon comunitario con código Odoo 19 para WSAA/WSFEv1, versión 19.0.1.0.0, AGPL-3 y estado Beta; candidato para laboratorio, no producción.
- **OCA/l10n-argentina 19.0:** aunque el repositorio raíz declara AGPL-3, el árbol consultado no tiene módulos instalables. No contarlo como localización disponible hasta que se publiquen manifiestos y código de addons.

La lista y el estado de cada proyecto están en [Catálogo de código reutilizable](CODE_REUSE_CATALOG.md). Los releases, resultados y puntuaciones se registran en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

## Componentes transversales investigados

La shortlist actual también cubre sincronización offline (PowerSync), ecommerce headless/B2B (Spree y Saleor), inventario técnico/fabricación (InvenTree y addons OCA), contabilidad (Bigcapital, en evaluación frente a los libros mayores nativos de los ERP), analítica (DuckDB, Superset y Metabase), identidad (Keycloak), observabilidad (OpenTelemetry, Prometheus y Grafana) y backups (pgBackRest, restic y Kopia), además de importación, documentos, hardware, pagos, ARCA, logística y automatización.

Cada elemento tiene un uso acotado y sus propios límites. PowerSync no resuelve concurrencia de stock; Spree/Saleor no deben crear una segunda autoridad de inventario; Karrio no incluye conectores argentinos en el árbol revisado; QZ Tray exige una cadena de confianza para impresión silenciosa; los SDK de ARCA necesitan homologación y recuperación de estados inciertos; los backups de archivos no sustituyen backups consistentes de bases de datos; y OCR no contabiliza ni aprueba por sí solo.

Ver [Shortlist de componentes reutilizables](REUSE_COMPONENTS_SHORTLIST.md) para versiones, licencias, evidencia y orden de pruebas. Spree y Saleor se evalúan como canales online; PowerSync como sincronización de datos no conflictivos; InvenTree y OCA como opciones condicionadas para fabricación/stock; los módulos OCA se filtran por manifiesto y licencia individual.

## Licencias y uso privado

El sistema es para uso propio y no está previsto distribuirlo ni venderlo. Eso permite considerar proyectos GPL y AGPL como opciones reales, pero no elimina automáticamente sus obligaciones. Hay que revisar el modo de uso, si se modifican y ofrecen por red, si se entregan copias a terceros y las condiciones de cada paquete.

La licencia del repositorio no cubre necesariamente todos los artefactos instalados. Se revisan en forma independiente:

- Código fuente, archivos y módulos que realmente se incorporan.
- Dependencias directas y transitivas.
- Bases de datos, motores, extensiones y servicios incluidos en instaladores.
- Fuentes tipográficas, iconos, imágenes, plantillas y documentación.
- Componentes comerciales, Enterprise, duales, source-available o con restricciones especiales.
- Avisos de copyright, LICENSE, NOTICE, atribuciones y modificaciones.

No se incorporan dependencias sin licencia identificable ni se califica como open source a un componente que no cumpla una licencia reconocida como tal. Si cambia el alcance a distribución, acceso de terceros o servicio comercial, se vuelve a evaluar el modelo antes de habilitarlo. Esta guía técnica no sustituye asesoramiento jurídico.

## Registro obligatorio por componente

Antes de aprobar una dependencia se registra:

- Repositorio, URL, proveedor y responsable.
- Tag, release o commit exacto y hash del artefacto.
- Licencia de cada proyecto, paquete, recurso y dependencia relevante.
- Lenguaje, runtime, base, servicios auxiliares y sistemas operativos soportados.
- API, eventos, extensiones, permisos y límites de datos.
- Estado de mantenimiento, vulnerabilidades, pruebas y política de actualización.
- Cambios propios, parches, archivos reemplazados y costo de rebase.
- Datos que importa/exporta, backup y prueba de restauración.
- Evidencia de las pruebas funcionales y de recuperación.

Se conserva un inventario de dependencias y un SBOM SPDX o CycloneDX cuando el formato de distribución y las herramientas lo permitan. Los cambios de versión vuelven a disparar las verificaciones de licencia y seguridad.

## Reglas de arquitectura

- Cada dato transaccional tiene un único dueño.
- Un producto integrado puede compartir internamente su runtime y base sólo si se acepta como una unidad de dominio acotada; otros servicios no consultan ni modifican sus tablas.
- Los módulos independientes se conectan por APIs/eventos versionados, no por SQL directo.
- Una biblioteca se incorpora dentro del servicio que la necesita; no se convierte en un servicio adicional sin razón operativa.
- No se construyen dos versiones de stock, ventas o facturación en paralelo.
- Ningún código externo puede saltarse idempotencia, concurrencia, permisos, auditoría, backups o conciliación.
- La sustitución de una plataforma debe incluir migración, reconciliación y transición explícita de autoridad.

## Criterio de aprobación

La selección usa puertas obligatorias para fuente/licencia, instalación reproducible, API/aislamiento, propiedad de datos, exportación, backup/restore, seguridad y flujos transaccionales. Los candidatos que pasan reciben una puntuación con evidencia; el mejor candidato no se elige sólo por documentación.

La estrategia completa define el orden reuse-first, los candidatos y la selección en etapas. No hay decisión aprobada de lenguaje, base de datos o broker hasta conocer las plataformas que sobrevivan a las pruebas.

**Estado:** la documentación y el validador de datos sintéticos están versionados. No existe todavía una aplicación funcional de Rubrova ni código externo incorporado.
