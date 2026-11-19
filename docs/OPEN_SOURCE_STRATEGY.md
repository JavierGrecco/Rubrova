# Estrategia de reutilización de código abierto

**Revisión:** 19 de noviembre de 2026  
**Estado:** evaluación de plataformas y componentes; no se incorporó código externo a Rubrova.

## Contexto de uso

El sistema se desarrolla para uso interno, personal y privado. No está previsto distribuir copias, revenderlo ni ofrecerlo como servicio a terceros. Por eso, GPL y AGPL no se descartan automáticamente: pueden permitirnos adoptar, modificar y utilizar internamente una aplicación completa. Aun así, se deben respetar los términos de cada licencia y las licencias independientes de componentes, paquetes, imágenes, fuentes, servicios y dependencias.

La AGPL merece una revisión específica si usuarios interactúan remotamente a través de una red con una versión modificada. Si cambia el alcance del proyecto —distribución, acceso por terceros o comercialización— se vuelve a evaluar la arquitectura y las obligaciones antes del cambio. Este documento es una guía técnica, no asesoramiento jurídico.

## Conclusión ejecutiva

La evaluación integral compara ahora tres candidatos:

1. **MyCompany/lsFusion 6.2:** ERP/POS modular con CRM, ventas, compras, inventario, fabricación, facturación, proyectos y RR. HH. La aplicación MyCompany declara Apache-2.0 y la plataforma lsFusion LGPL-3.0 por separado. Se debe probar la release 6.2 y su mecanismo de módulos, sin asumir que la documentación online 7.0 aplica a esa versión.
2. **Posnic 1.9.2:** candidato directo para POS local, Electron, ventas, caja e inventario. Código propio AGPL-3.0-only; el paquete incluye componentes con licencias distintas, entre ellos MongoDB SSPL-1.0 y amCharts 4 comercial. La edición self-hosted puede compartir una base local entre varios equipos, pero no sincroniza bases independientes de distintas cajas/sucursales. Su evidencia offline publicada es acotada.
3. **ERPNext 16.60.0 + Frappe Framework 16:** candidato de profundidad administrativa en compras, inventario, fabricación, costos y contabilidad. ERPNext es GPL-3.0; Frappe Framework es MIT. Hay que verificar POS, facilidad de uso, recuperación offline y localización argentina.

Ninguno está elegido ni aprobado. **No se debe construir la aplicación definitiva hasta ejecutar la prueba común** descrita en [Evaluación de plataformas](PLATFORM_EVALUATION.md). Si ambas alternativas fallan los controles críticos, la salida es un monolito modular propio, reutilizando únicamente componentes que encajen.

Odoo Community 20 y Medusa v2 dejan de ser finalistas de esta ronda. No se borran de la investigación, pero tampoco deben seguir apareciendo como decisión vigente en la arquitectura o el roadmap. NexoPOS queda condicionado a la aclaración de su discrepancia de licencia.

## Qué significa reutilizar código

Evaluamos cuatro formas, de mayor a menor alcance:

| Forma | Qué hacemos | Cuándo conviene |
|---|---|---|
| Adopción integral | Ejecutamos el producto existente y lo configuramos | Cuando cubre la mayor parte del flujo sin alterar el núcleo |
| Extensión | Construimos módulos propios sobre APIs y puntos de extensión | Cuando el modelo del framework encaja y es mantenible |
| Componente | Incorporamos una biblioteca o módulo acotado | Cuando resuelve una responsabilidad aislada |
| Fork | Mantenemos nuestra propia variante del proyecto | Cuando adaptar el producto completo es más barato que construirlo y podemos mantener los cambios |

La preferencia es aprovechar tanto código maduro como sea posible, pero no acumular frameworks ni mantener dos sistemas para ventas, caja, contabilidad o stock.

## Comparación de plataformas activas

### Posnic 1.9.2

- **Tecnología:** Electron, Node.js, Express, Mongoose y MongoDB; la aplicación local mantiene su propia API y persistencia.
- **Aporte:** POS minorista/gastronómico, ventas, devoluciones, pagos parciales, catálogo, variantes, compras, stock, clientes, permisos y reportes.
- **Uso local:** el escritorio opera en el equipo de caja; el modo self-hosted permite varios clientes en una red local sobre una misma base. No es sincronización entre bases independientes.
- **Offline:** el README describe una prueba sintética acotada en una versión previa. No demuestra cierre forzado, pérdida de energía, jornada completa ni todos los medios de pago. El outbox de sincronización es un acelerador opcional, no el registro contable de la venta.
- **Adaptación argentina:** hay campos y reglas orientados a India/GST. Se debe medir la adaptación de IVA, CUIT, comprobantes, puntos de venta, ARCA, nomencladores y reportes.
- **Licencias:** AGPL-3.0-only para su código. El instalador revisado incluye MongoDB Community Server 7.0.14 bajo SSPL-1.0 y amCharts 4 comercial. Cada dependencia del paquete necesita revisión propia.
- **Fijación de prueba:** tag `v1.9.2`, commit `4096126edb1ff4fd337069697776254215dc2680`. La rama `main` tenía seis commits posteriores; `develop` estaba divergida. Se debe comparar, no cambiar de fuente silenciosamente.
- **Riesgo principal:** puede resolver bien una caja local, pero aún no sabemos si sus límites de offline, localización y modelo de datos permiten cumplir nuestros requisitos sin una reescritura profunda.

### ERPNext 16.60.0 + Frappe Framework 16

- **Tecnología:** framework Python/JavaScript, aplicaciones Frappe, MariaDB como base habitual y módulos ERPNext.
- **Aporte:** abastecimiento, compras, recepción, inventario, fabricación, costos, contabilidad, usuarios, permisos y reportes; perfiles de POS con configuración de empresa, almacén, medios de pago y precios.
- **Offline:** no asumimos que el POS actual resuelva recuperación duradera tras cerrar o matar el proceso. Se debe probar la versión fijada; las guías antiguas no prueban el comportamiento de v16.
- **Adaptación argentina:** evaluar impuestos, comprobantes, CUIT, puntos de venta y ARCA por módulo y extensión. No contar como disponible una integración cuyo código, licencia y pruebas no se hayan verificado.
- **Licencias:** ERPNext GPL-3.0; Frappe Framework MIT. La licencia del framework no cambia la del código de ERPNext.
- **Fijación de prueba:** ERPNext `v16.60.0`; fijar también el commit exacto de Frappe Framework 16 durante la instalación.
- **Riesgo principal:** puede ahorrar trabajo administrativo y de producción, pero la experiencia de caja y la continuidad offline pueden exigir adaptación considerable.

### Candidatos fuera de la ronda activa

- **Odoo Community 20:** se mantiene como referencia histórica de cobertura POS/ERP, pero su offline documentado advierte que no se cierre ni recargue el navegador antes de sincronizar. No es finalista de la prueba actual.
- **Medusa v2:** su núcleo TypeScript/MIT sirve para una plataforma de comercio propia, pero no aporta por sí solo POS, caja, compras, producción, contabilidad y offline. No es finalista de esta ronda.
- **NexoPOS:** sigue siendo interesante por POS e inventario, pero el archivo LICENSE raíz declara GPLv3 y composer.json declara MIT. No incorporar ni aprobar hasta resolverlo.

## Prueba técnica obligatoria

Se ejecuta el mismo conjunto de datos y escenarios sobre MyCompany, Posnic y ERPNext. Además de los flujos comunes, en MyCompany se prueba un módulo propio separado que declare sus dependencias mediante REQUIRE. Se debe probar como mínimo:

- Alta de artículos, variantes, códigos, unidades y productos vendidos por peso.
- Venta rápida con lector simulado, descuentos manuales y promociones.
- Pagos mixtos, vuelto, apertura, cierre y arqueo de caja.
- Devolución parcial, reintegro y efecto de stock.
- Compra, recepción parcial y actualización de costo.
- Producción mediante receta/BOM, consumo y merma.
- Dos puestos conectados por LAN.
- Corte de internet, cierre forzado, reinicio, reintentos y conciliación.
- Backup y restauración en una instalación limpia.
- Impresión, cajón, lector y balanza; simulación primero y hardware físico después.
- Adaptación fiscal argentina y ARCA exclusivamente en homologación.

La pauta completa, la tabla de evidencia P01–P19 y la escala de puntuación están en [Evaluación de plataformas](PLATFORM_EVALUATION.md).

## Componentes especializados a evaluar por separado

- **pos-toolkit** (Apache-2.0): plugin Rust/Tauri v2 para ESC/POS, cajón, USB, lectores seriales y balanzas HID; además, constructor TypeScript de tickets de 57/80 mm. El plugin no es universal para navegador. `register-core` figura como planificado.
- **emupos** y **ESCPost** (Apache-2.0): simulación y diagnóstico de periféricos, render de tickets y escenarios de error. No reemplazan pruebas con dispositivos reales.
- **arca-sdks**: `@ramiidv/arca-facturacion` 7.1.0 declara MIT y Node >=22.12. Candidato para WSAA/WSFE/WSFEX/CAEA; las emisiones no se reintentan ciegamente y los estados inciertos necesitan recuperación. Solo homologación en esta fase.
- **PowerSync Open Edition** (Apache-2.0): opción de sincronización SQLite/PostgreSQL; distinguir funciones Enterprise/Cloud.
- **Dexie.js** (Apache-2.0): almacenamiento IndexedDB, no sincronización completa.

Se evalúan estos componentes contra la arquitectura finalmente elegida. No se importan solo porque sus README los describan como útiles.

## Reglas de licencias y procedencia

1. Registrar repositorio, commit/tag, autor, licencia por archivo/paquete y fecha de revisión.
2. Revisar dependencias directas y transitivas del paquete que realmente se ejecuta.
3. Conservar LICENSE, NOTICE, copyright, atribuciones y modificaciones.
4. Tratar licencias comerciales, SSPL, source-available, marcas y recursos visuales por separado.
5. No llamar “open source” a una dependencia que no cumpla una licencia reconocida como tal.
6. No asumir que uso privado elimina todas las condiciones de licencia.
7. Repetir la revisión si cambia versión, modo de despliegue, acceso remoto o intención de distribución.

## Control de dependencias incorporadas

Antes de integrar un componente aprobado se debe guardar su origen exacto, licencia, hash, versión, SBOM si está disponible, pruebas ejecutadas, cambios realizados y responsable de mantenimiento. Las dependencias deben poder actualizarse o reemplazarse sin alterar las reglas propias de venta, pago, caja, inventario y fiscalidad.

No incorporar dos motores para el mismo dato. La plataforma elegida será la única fuente de verdad; los componentes externos actuarán como adaptadores, herramientas o módulos claramente delimitados.

## Estado de la decisión

- [x] Uso interno privado confirmado como alcance previsto.
- [x] GPL/AGPL incluidas en la estrategia de evaluación.
- [x] Posnic 1.9.2 y ERPNext 16.60.0/Frappe 16 definidos como ronda activa.
- [x] Protocolo P01–P17 documentado.
- [x] Componentes de hardware, fiscalidad y offline separados de las plataformas integrales.
- [ ] Instalación y pruebas locales de MyCompany/lsFusion 6.2, incluido módulo custom.
- [ ] Instalación y pruebas locales de Posnic.
- [ ] Instalación y pruebas locales de ERPNext/Frappe.
- [ ] Puntuación con evidencias y cálculo de esfuerzo de adaptación.
- [ ] Elección de plataforma o aprobación del monolito modular propio.
- [ ] Incorporación de código externo con inventario de licencias y procedencia.

**No hay código externo incorporado ni módulos funcionales implementados en Rubrova todavía.** El siguiente avance debe surgir de ejecutar el protocolo, no de ampliar indefinidamente la lista de repositorios.


## Composición de módulos heterogéneos y compatibilidad

La meta no es que un solo repositorio cubra todos los dominios. Podemos adoptar una plataforma integral y complementarla con módulos especializados, siempre que cada agregado tenga un único propietario, los módulos se comuniquen por puertos/contratos, los eventos sean idempotentes y las operaciones externas se concilien.

Windows, Linux y macOS son objetivos del producto final, no una condición para que cada biblioteca soporte los tres desde el primer día. Los drivers de hardware pueden ser específicos por OS detrás de una interfaz común. Un módulo de servidor/web se evalúa por su runtime y el acceso desde navegador, no por el OS del puesto.

Ver [Composición de módulos y contratos](MODULE_COMPOSITION.md) y [Investigación ampliada](MODULAR_COMPONENT_RESEARCH.md).
