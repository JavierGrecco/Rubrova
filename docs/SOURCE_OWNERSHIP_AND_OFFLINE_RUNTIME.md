# Propiedad del código, fork controlado y funcionamiento local sin Internet

**Decisión:** Rubrova mantendrá dentro de su propio repositorio una copia versionada y modificable del código fuente completo de MyCompany 6.2 y del motor lsFusion 6.2. No usará el repositorio externo como dependencia de ejecución ni descargará JAR, WAR o imágenes upstream al iniciar.

## 1. Qué significa independencia

La independencia tiene tres planos:

1. **Código fuente:** el POS, ERP, motor, interfaz y personalizaciones quedan incluidos en Rubrova y en su historial Git. Podemos leerlos, modificarlos y mantener nuestra versión aunque el proyecto original cambie o desaparezca.
2. **Construcción:** una compilación reproducible parte de esas fuentes y de un conjunto cerrado de dependencias, versiones, herramientas y hashes. La primera preparación puede necesitar Internet para obtener bibliotecas Maven; después debe existir un kit verificado que permita compilar con Maven offline.
3. **Ejecución:** en la PC del negocio, el POS, ERP, base de datos, interfaz web y recursos se ejecutan localmente. Buscar artículos, vender, consultar stock, registrar compras, cerrar caja y consultar reportes no requiere conexión a Internet.

Tener fuentes locales no alcanza si cada inicio descarga un servidor remoto; tener imágenes locales no alcanza si el código no está disponible para modificarlo.

## 2. Fuentes incorporadas como base propia

| Componente | Versión fijada | Origen | Destino | Licencia |
|---|---|---|---|---|
| Motor lsFusion: servidor, API, cliente web/desktop y build | 6.2, commit dd4dbe5bf9b136e73e18fe25d741253929324350 | [lsfusion/platform](https://github.com/lsfusion/platform/tree/6.2) | vendor/platform/ | LGPL-3.0 |
| Aplicación MyCompany: POS + ERP | 6.2, commit d21ca6978717b98b6300d90267f9767db7414008 | [lsfusion-solutions/mycompany](https://github.com/lsfusion-solutions/mycompany/tree/6.2) | vendor/mycompany/ | Apache-2.0 |

MyCompany contiene alrededor de 800 módulos lsFusion, además de informes, recursos y utilidades. El motor contiene alrededor de 3.330 archivos Java y sus componentes de servidor, API, cliente web, cliente de escritorio y herramientas de compilación. CI verifica las cantidades exactas importadas.

La distribución de carpetas es deliberada: el POM original de MyCompany espera encontrar lsFusion en ../platform. Por eso el motor queda en vendor/platform y MyCompany en vendor/mycompany. El agregador build/rubrova/pom.xml compone ambos en un mismo reactor Maven.

Incorporar todo el código no implica habilitar todas las funciones de golpe. Las capacidades se activarán, traducirán, adaptarán y probarán por bloques.

## 3. Cómo modificaremos el código

La regla ya no es nunca tocar upstream. La regla es evitar modificaciones innecesarias, pero no prohibirlas.

Orden recomendado:
1. Configuración y opciones nativas.
2. Módulos Rubrova propios en extensions/lsfusion/ que extiendan clases, acciones, formularios y diseños.
3. Adaptadores o módulos adicionales Rubrova.
4. Parches pequeños y documentados sobre MyCompany o lsFusion cuando una brecha real no pueda resolverse por extensión.
5. Reemplazo de una parte mayor sólo si el análisis y las pruebas demuestran que conviene.

El código original se conserva reconocible. Los cambios directos se anotan en el archivo afectado con motivo y referencia a la prueba. Los parches del motor que puedan mantenerse como parches se guardan en patches/lsfusion/. No se mezcla una modificación Rubrova con una actualización upstream sin revisión.

Podemos modificar reglas del motor, comportamiento de acciones, búsqueda, carrito, precios, descuentos, pagos, vuelto, sesiones, devoluciones, modelos, procesos administrativos, formularios, navegación, distribución visual, atajos, etiquetas, ResourceBundles, mensajes, filtros, errores, recursos, informes, validaciones, migraciones, seguridad y rendimiento.

La extensión es la primera opción porque facilita comparar versiones. No es una barrera para adaptar el motor cuando sea necesario.

## 4. Compilación propia sin JAR upstream

El agregador build/rubrova/pom.xml declara el motor y MyCompany como módulos del mismo build. La compilación debe producir nuestros propios artefactos de servidor lsFusion, lógica MyCompany más extensiones Rubrova, cliente web y, si se decide distribuirlo, cliente de escritorio e imágenes locales.

No se aceptará como producto final un Dockerfile que use ADD con una URL remota para obtener servidor o cliente, ni un Compose que descargue la lógica desde una imagen upstream. Los Dockerfiles Rubrova copiarán artefactos construidos en nuestro pipeline. Las imágenes base, PostgreSQL y Java quedarán fijadas por versión y digest.

El proyecto utiliza Maven y bibliotecas/plugins de terceros. No sería honesto afirmar que incorporar las fuentes elimina toda dependencia técnica. La solución correcta es fijar cada dependencia, auditar su licencia, resolverla una vez, conservar sus artefactos en un repositorio Maven local y probar una recompilación con mvn -o. Las dependencias de ejecución quedarán dentro de los JAR/WAR o imágenes Rubrova; no se descargarán al abrir el POS.

El primer build desde fuentes está pendiente hasta que CI compile ambos proyectos desde vendor/. El build offline está pendiente hasta que compile sin acceso a repositorios remotos usando sólo el repositorio local preparado.

## 5. Ejecución local aislada de Internet

El objetivo operativo es una PC. En ella se ejecutará un conjunto local: aplicación Rubrova y servidor propio; motor MyCompany/lsFusion compilado desde nuestras fuentes; PostgreSQL local y persistente; cliente web y todos sus CSS, JavaScript, fuentes, imágenes e informes; servicios auxiliares estrictamente necesarios, también locales.

Para el paquete Docker, los contenedores se construirán antes de instalar y se entregarán en un archivo de imágenes cargable en la PC. El Compose utilizará pull_policy: never; la prueba de aceptación usará una red Docker interna sin salida a Internet y verificará que la interfaz siga abriendo desde el navegador local.

La instalación inicial del sistema operativo o Docker puede ser una preparación del equipo. Una vez instalado Rubrova y cargadas las imágenes, la aplicación no debe consultar registros de contenedores ni repositorios Maven.

## 6. Qué sí puede necesitar Internet

Las funciones que dependen por naturaleza de terceros son opcionales: ARCA y servicios fiscales remotos; autorizaciones de Mercado Pago, tarjetas o adquirentes; marketplaces y tiendas online; transportistas, seguimiento y etiquetas; mensajería y otros proveedores.

Sin conexión, Rubrova seguirá funcionando para las tareas locales permitidas. Las integraciones remotas informarán su estado real, registrarán pendientes y reintentarán de forma controlada. Nunca fingirán que una autorización fiscal o un pago remoto se completó si no hay confirmación. La caída de Internet no debe detener catálogo, POS local, inventario, compras ni consulta de datos guardados.

## 7. Cómo evitaremos que un cambio upstream rompa producción

No habrá actualizaciones automáticas de MyCompany ni de lsFusion en producción. El origen es una referencia de cambios, no una dependencia flotante.

Cada actualización seguirá estas puertas:
1. Fijar el nuevo tag y commit; comparar el árbol completo.
2. Producir un informe de archivos agregados, eliminados y modificados, incluyendo módulos de los que dependan nuestras extensiones y parches.
3. Revisar cambios de base de datos, reglas transaccionales, APIs, formularios, seguridad, dependencias y licencias.
4. Reaplicar o adaptar los parches Rubrova explícitamente; no resolver conflictos automáticamente.
5. Compilar desde cero y ejecutar pruebas unitarias, integración, contratos, seguridad, interfaz y flujos POS/ERP.
6. Probar migraciones sobre una copia de la base real, nunca primero en producción.
7. Restaurar un backup en una instalación limpia y verificar saldos, ventas, pagos, stock, documentos y auditoría.
8. Ejecutar regresión y operación offline con la versión candidata completa.
9. Conservar el paquete anterior y su procedimiento de recuperación. El despliegue cambia sólo cuando la candidata aprueba.

En producción se mantendrá el último paquete estable, sin actualizaciones silenciosas. Antes de cada cambio se hará un backup verificable. Recuperar la aplicación y recuperar la base de datos son procedimientos separados: volver a un binario anterior no revierte una migración ni una venta.

El objetivo es detectar un error en CI o en una copia de pruebas, no con el negocio detenido. Si una actualización no supera una prueba, se mantiene la versión estable y se corrige la candidata.

## 8. Otros proyectos que sumemos

Cada proyecto reutilizado tendrá uno de estos tratamientos: código incorporado bajo vendor con fuente, licencia, commit y pruebas; lógica portada a módulos Rubrova con atribución y licencia; servicio local empaquetado con sus dependencias y base delimitada; o integración remota opcional sólo para un proveedor que por naturaleza opere fuera de nuestra PC.

No incorporaremos una segunda suite ERP completa sólo para extraer una pantalla o unas reglas. Proyectos como Tryton Argentina se podrán estudiar para aprovechar lógica fiscal, reportes o reglas verificadas; antes de integrar un proceso completo decidiremos si conviene portar su lógica o ejecutar un servicio local separado. Nunca permitiremos que dos motores confirmen la misma venta, pago o movimiento de stock.

## 9. Puertas de aceptación de independencia

- [ ] Los fuentes completos y avisos de licencia de MyCompany y lsFusion están en main.
- [ ] Se compilan artefactos desde vendor/, sin descargar JAR/WAR upstream.
- [ ] La compilación offline funciona con el repositorio Maven previamente preparado.
- [ ] Las imágenes Rubrova contienen lógica, servidor, cliente y base de datos fijados; no usan latest.
- [ ] El paquete de instalación restaura las imágenes sin Internet.
- [ ] La aplicación inicia desde una PC limpia con la red externa desactivada.
- [ ] El navegador carga todos sus recursos desde la máquina local.
- [ ] Se registra una venta, se consulta stock y caja, se reinicia la PC y los datos siguen íntegros.
- [ ] Backup y restauración se prueban sin depender de un proveedor externo.
- [ ] Se conserva el paquete estable anterior y se demuestra la recuperación.

**Estado actual:** se fijaron las fuentes y se añadió la automatización para incorporarlas a main. La importación completa, el build desde fuentes, el paquete offline y la prueba real en PC son hitos distintos; no se declaran aprobados por haber escrito esta estrategia.

## Referencias de origen

- [MyCompany 6.2 y Apache 2.0](https://github.com/lsfusion-solutions/mycompany/tree/6.2)
- [MyCompany 6.2 LICENSE](https://github.com/lsfusion-solutions/mycompany/blob/6.2/LICENSE)
- [lsFusion 6.2](https://github.com/lsfusion/platform/tree/6.2)
- [lsFusion LICENSE](https://github.com/lsfusion/platform/blob/6.2/LICENSE)
- [POM de MyCompany 6.2](https://github.com/lsfusion-solutions/mycompany/blob/6.2/pom.xml)
- [Dockerfile original de servidor](https://github.com/lsfusion/platform/blob/6.2/server/Dockerfile)
- [Dockerfile original del cliente web](https://github.com/lsfusion/platform/blob/6.2/web-client/Dockerfile)
