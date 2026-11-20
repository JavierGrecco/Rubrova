# Preparación del laboratorio de evaluación

**Revisión:** 20 de noviembre de 2026  
**Objetivo:** comparar POS + gestión comercial/ERP en entornos aislados, usando datos sintéticos y versiones fijadas.  
**Regla principal:** no usar datos reales, instalaciones comerciales existentes, certificados fiscales de producción ni credenciales reales.

Este laboratorio no instala Rubrova ni incorpora código de terceros. Sirve para comparar el circuito POS + ERP, medir cobertura real y decidir qué capacidades pueden reutilizarse sin vulnerar los límites de dominio.

## 1. Qué vamos a instalar

| Candidato | Forma recomendada de evaluación | Versión / prioridad |
|---|---|---|
| ERPNext / Frappe | Demo desechable oficial con Docker Compose, publicada sólo en localhost. Después de confirmar límites de la demo, preparar una instancia de laboratorio que permita extensiones propias. | ERPNext 16.60.0 / Frappe 16 — primera prueba |
| MyCompany / lsFusion | Instalador Windows x64 o servidor Linux con cliente web; desde Mac se accede por navegador a una VM local aislada. | MyCompany 6.2 / lsFusion 6.x — primera prueba |
| Tryton | Instancia aislada PostgreSQL con Tryton 8.0 y las ocho ramas tryton-ar 8.0; fijar commits individuales, instalar en conjunto y ejecutar tests. | Tryton 8.0 + módulos argentinos 8.0 — prueba prioritaria; Tryton 8.2 queda para upgrade posterior |
| Dolibarr | Instancia oficial local/aislada; revisar TakePOS, API, stock, caja, compras y exportación. | 24.0.3 — filtro corto |
| Posnic | Aplicación de escritorio en una VM limpia con Windows x64 o Ubuntu Desktop x86_64. | 1.9.2 — referencia POS secundaria |

### Restricción de Posnic en macOS

El conjunto de paquetes de Posnic 1.9.2 no incluye un instalador macOS. El manual oficial indica que la notarización de un binario nativo todavía estaba en corrección. No instalar un paquete no notarizado ni sustituirlo por un build de una rama móvil.

Para evaluar en un equipo Mac, usar una VM Ubuntu 24.04 Desktop y el AppImage oficial de Linux. En Windows, usar una VM Windows x64 limpia y el instalador firmado. No instalarlo encima de una instalación existente ni sobre una base con datos reales.

Fuentes:
- [Release Posnic 1.9.2](https://github.com/Posnic/POS/releases/tag/v1.9.2)
- [Disponibilidad de paquetes por sistema operativo](https://www.posnic.com/guides/posnic-pos-complete-user-guide/setup/update-posnic-1-9-2/)
- [Guía oficial de instalación local y self-hosted](https://github.com/Posnic/POS/blob/v1.9.2/docs/SELF_HOSTING.md)

## 2. Preparar Posnic 1.9.2

### Opción A — Windows x64

Usar una VM Windows limpia. El instalador publicado ocupa aproximadamente 230 MB.

1. Descargar Posnic-1.9.2-windows-x64-installer.exe desde la [release oficial](https://github.com/Posnic/POS/releases/tag/v1.9.2).
2. Verificar su SHA-256 en PowerShell:

    Get-FileHash .\Posnic-1.9.2-windows-x64-installer.exe -Algorithm SHA256

   El valor publicado debe coincidir con:

    b61fad4f9f852263ec0e4a7465c6e15ca66ff812a0962349fadd573459004140

3. Comprobar la firma antes de abrirlo:

    Get-AuthenticodeSignature .\Posnic-1.9.2-windows-x64-installer.exe | Format-List Status,SignerCertificate

   Si la firma no aparece como válida o el hash no coincide, detener la prueba.
4. Instalar en la VM limpia y crear un negocio ficticio. No seleccionar una instalación existente ni importar datos reales.

### Opción B — Ubuntu Desktop x86_64

En una VM Ubuntu 24.04 Desktop limpia:

1. Descargar Posnic-1.9.2-linux-x86_64.AppImage desde la [release oficial](https://github.com/Posnic/POS/releases/tag/v1.9.2).
2. Verificar el SHA-256:

    sha256sum Posnic-1.9.2-linux-x86_64.AppImage

   Debe coincidir con:

    3b8013994ce2bb40c98c3ec8fa017d8dad8b171e151a05cebd3084b30b713ecb

3. Dar permiso de ejecución y abrirlo:

    chmod +x Posnic-1.9.2-linux-x86_64.AppImage

    ./Posnic-1.9.2-linux-x86_64.AppImage

4. Completar el primer inicio con un negocio y usuarios ficticios.

El paquete AppImage publicado ocupa aproximadamente 364 MB. El paquete Debian también está disponible, pero no hace falta descargar ambos para esta prueba.

### Precauciones específicas

- No ejecutar el script de instalación de servidor que descarga la rama develop: no fija la versión de evaluación.
- No abrir el puerto 27017 de MongoDB a la red.
- No exponer la aplicación por internet.
- No habilitar pagos reales, correo, WhatsApp ni integraciones externas.
- La modalidad self-hosted usa una base común en LAN; no demuestra sincronización de varias bases independientes. Esa capacidad no forma parte de esta prueba local.

## 3. Preparar ERPNext 16.60.0 en Docker

El repositorio oficial frappe_docker ofrece pwd.yml, una configuración de demostración desechable. No es una instalación de producción y no permite agregar aplicaciones propias. Es adecuada para la primera comparación de funciones nativas.

### Requisitos del equipo de evaluación

- Docker Desktop o Docker Engine.
- Docker Compose v2.
- Git.
- Como objetivo práctico para este laboratorio: 8 GB de RAM disponibles y alrededor de 20 GB de espacio libre para imágenes, contenedores y datos. Es una recomendación de laboratorio, no un mínimo oficial del fabricante.

### Fijar la configuración y levantarla

En Terminal (macOS/Linux), ejecutar:

    mkdir -p "$HOME/rubrova-lab"
    cd "$HOME/rubrova-lab"
    git clone https://github.com/frappe/frappe_docker.git
    cd frappe_docker

Fijar el repositorio de despliegue al commit revisado:

    git checkout ef24ebc0a411b6237694765f0b51d8f8f8dd13ce

Comprobar que la configuración use la imagen exacta:

    grep -F 'image: frappe/erpnext:v16.60.0' pwd.yml

La línea debe aparecer para los servicios ERPNext de la demostración. Si la versión no coincide, no continuar: la configuración cambió y hay que revisar el archivo antes de ejecutar.

Copiar la configuración para la evaluación:

    cp pwd.yml pwd.rubrova.yml

Editar pwd.rubrova.yml y cambiar únicamente la publicación del frontend:

    - "8080:8080"

por:

    - "127.0.0.1:8080:8080"

Esto limita el acceso al propio equipo y evita publicar la pantalla de administración en la red local.

Validar la configuración antes de arrancar:

    docker compose -f pwd.rubrova.yml config

Revisar que el puerto publicado aparezca ligado a 127.0.0.1, no a todas las interfaces.

Levantar la demostración:

    docker compose -f pwd.rubrova.yml up -d

Comprobar los servicios:

    docker compose -f pwd.rubrova.yml ps

Revisar el proceso de creación del sitio:

    docker compose -f pwd.rubrova.yml logs --tail=100 create-site

Cuando el contenedor de creación haya finalizado correctamente, abrir:

    http://127.0.0.1:8080

Acceso inicial de la demo oficial:
- Usuario: Administrator
- Contraseña: admin

Cambiar la contraseña inmediatamente y mantener la demo accesible solo desde localhost. Usar exclusivamente el negocio ficticio del dataset.

### Registrar las versiones efectivas

Ejecutar:

    docker compose -f pwd.rubrova.yml exec backend bench version

Guardar la salida junto con la evidencia. La imagen ERPNext está fijada por tag; la salida de Bench registra las versiones efectivas de ERPNext y Frappe contenidas en esa imagen.

### Detener y eliminar el entorno

Para detener los servicios sin borrar los datos:

    docker compose -f pwd.rubrova.yml down

Cuando la evaluación haya terminado y ya se hayan guardado las evidencias necesarias, eliminar también los volúmenes de la demo:

    docker compose -f pwd.rubrova.yml down -v

**Atención:** down -v elimina la base y los volúmenes de esa instalación. No ejecutar sobre otro proyecto Compose.

Fuentes:
- [Repositorio oficial Frappe Docker](https://github.com/frappe/frappe_docker)
- [Configuración oficial pwd.yml](https://github.com/frappe/frappe_docker/blob/ef24ebc0a411b6237694765f0b51d8f8f8dd13ce/pwd.yml)
- [Guía oficial de demostración desechable](https://github.com/frappe/frappe_docker#demo-setup)

## 4. Preparar MyCompany / lsFusion 6.2

MyCompany es el tercer candidato integral. Para esta prueba se fija la release 6.2 y no se deben mezclar instrucciones o imágenes de la documentación 7.0.

### Procedencia y archivos fijados

- Repositorio: https://github.com/lsfusion-solutions/mycompany
- Release: https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2
- Commit del tag: d21ca6978717b98b6300d90267f9767db7414008
- Instalador Windows x64: mycompany-6.2-x64.exe
- SHA-256 del instalador: 0167322fea03e269abfae2a140ab4df5205f07633d2520a3d78e381346fbce75
- JAR de lógica MyCompany 6.2: mycompany-6.2.jar
- SHA-256 del JAR: fe5a9bda49295f2292ae229a30c9461a16c137fc350a0aa944df7812a1e2f392

La release identifica el JAR y el instalador como artefactos de la versión 6.2. La etiqueta del código está sin firma; verificar los artefactos por SHA-256 y conservar las fuentes.

### Opción A — Windows x64 (camino inicial recomendado)

Realizarlo en una VM Windows x64 limpia, no en el equipo principal ni sobre una instalación previa.

1. Crear una carpeta de laboratorio:

    New-Item -ItemType Directory -Force "$HOME\rubrova-lab\mycompany"

2. Descargar el instalador desde el servidor oficial:

    Invoke-WebRequest "https://download.lsfusion.org/solutions/mycompany-6.2-x64.exe" -OutFile "$HOME\rubrova-lab\mycompany\mycompany-6.2-x64.exe"

3. Verificar el SHA-256:

    Get-FileHash "$HOME\rubrova-lab\mycompany\mycompany-6.2-x64.exe" -Algorithm SHA256

   Debe coincidir exactamente con el hash publicado arriba. Si no coincide, detenerse.

4. Descargar el JAR de lógica fijado:

    Invoke-WebRequest "https://download.lsfusion.org/solutions/mycompany-6.2.jar" -OutFile "$HOME\rubrova-lab\mycompany\mycompany-6.2.jar"

5. Verificar el JAR:

    Get-FileHash "$HOME\rubrova-lab\mycompany\mycompany-6.2.jar" -Algorithm SHA256

   Debe coincidir exactamente con el hash publicado arriba.

6. Comprobar la firma Authenticode del instalador. Si la firma existe y no es válida, no ejecutar. El hash es el control obligatorio incluso si la firma no está disponible.
7. Ejecutar el instalador dentro de la VM aislada y completar la instalación. El proceso requiere conexión a Internet para descargar componentes.
8. Detener el servicio lsFusion 6 Server desde Servicios de Windows. Conservar una copia del JAR instalado y colocar el archivo verificado mycompany-6.2.jar en C:\\Program Files\\lsFusion 6\\Server\\lib. Asegurarse de que quede un solo archivo mycompany*.jar en esa carpeta y reiniciar el servicio. La guía oficial documenta esa ubicación para el JAR de MyCompany.
9. Registrar versión del runtime, hash del JAR activo y hash del instalador. Si no se puede confirmar que el JAR activo corresponde al artefacto 6.2 verificado, marcar la evaluación como bloqueada.
10. La guía indica que el cliente web utiliza el puerto 8080 y el cliente de escritorio el 7652. Mantener la VM en una red host-only o sin acceso entrante desde la LAN.
11. Abrir el cliente web desde la propia VM:

    http://127.0.0.1:8080

12. El manual indica un usuario inicial admin sin contraseña. No exponer la instalación así a la LAN ni a Internet. Mantenerla aislada hasta configurar credenciales y permisos de prueba.

### Opción B — Linux x86_64

Para evaluar en Linux, utilizar una VM limpia. La guía oficial soporta Ubuntu/Debian y RHEL/Fedora. El instalador rápido descarga componentes desde el servidor del proveedor, por lo que se debe revisar el script antes de ejecutarlo.

La guía de instalación Linux coloca el JAR de lógica en /var/lib/lsfusion y reinicia el servicio lsfusion6-server. Después de instalar el runtime:

1. Detener el servicio lsFusion Server.
2. Conservar una copia del JAR que haya instalado el script.
3. Colocar el artefacto mycompany-6.2.jar verificado por SHA-256 en /var/lib/lsfusion.
4. Asegurarse de que exista un solo JAR de MyCompany en el classpath.
5. Iniciar el servicio y revisar /var/log/lsfusion6-server/start.log.
6. Registrar la versión efectiva del runtime lsFusion y los hashes utilizados. Si no se puede confirmar el runtime 6.x exacto, marcar la comparación de esa instalación como bloqueada hasta fijarlo.

No utilizar una descarga SNAPSHOT ni la rama master como sustituto de la release 6.2.

### Evaluación desde macOS

La release 6.2 no publica un cliente/instalador macOS. Eso no descarta la plataforma: el cliente web funciona en el navegador del Mac si el servidor corre en una VM Windows o Linux local. Para la prueba desde macOS, abrir el navegador del host hacia la IP host-only de la VM o configurar un reenvío de puerto estrictamente local. No abrir 8080 ni 7652 a Internet.

Esto prueba acceso web desde macOS; no demuestra un cliente de escritorio nativo para macOS. Rubrova mantiene como objetivo final Windows, Linux y macOS mediante su arquitectura y adaptadores.

### Prueba de composición de módulos

La documentación de lsFusion 6.x permite añadir un archivo de módulo propio, declarar dependencias con REQUIRE y seleccionarlo como módulo superior sin editar el código de MyCompany.

En una copia desechable del laboratorio, crear un módulo de prueba que declare únicamente las capacidades seleccionadas. La documentación 6.x muestra como ejemplo:

    MODULE RubrovaProbe;
    REQUIRE Eval, ProcessMonitor, Backup, Chat, Documentation,
            MasterDataP, Inventory,
            Invoicing, InvoicingInventory,
            Purchase, Sales, Retail;

Agregar el archivo a la ruta de módulos indicada por la instalación y configurar logics.topModule = RubrovaProbe en settings.properties, siguiendo la guía correspondiente al runtime. Reiniciar y comprobar que el servidor arranque y que los módulos declarados estén disponibles.

No modificar el JAR base ni reutilizar datos reales. Registrar el módulo de prueba, el archivo de configuración y los errores. Este ensayo debe demostrar que una extensión propia puede convivir con la aplicación base y sobrevivir una actualización controlada.

Fuentes:
- [Release MyCompany 6.2 y hashes](https://github.com/lsfusion-solutions/mycompany/releases/tag/6.2)
- [Instalación oficial MyCompany](https://mycompany-docs.lsfusion.org/administration/installation/)
- [Desarrollo y módulos propios para lsFusion 6.x](https://mycompany-docs.lsfusion.org/v6/administration/development/)
- [Docker lsFusion 6.x](https://docs.lsfusion.org/v6/Docker/)

## 5. Cargar exactamente los mismos datos

Usar [platform-evaluation.json](fixtures/platform-evaluation.json) como fuente canónica. El archivo contiene productos ficticios, importes enteros en centavos, pagos, devolución parcial, compra, carrito editable, vuelto, flujo de terminal y existencias esperadas.

No importar el JSON como si ambos productos compartieran un formato de importación. Cargar o crear los mismos datos mediante las pantallas de cada aplicación y conservar un registro de las diferencias de mapeo. La prueba compara resultados comerciales, no nombres de campos internos.

Antes de iniciar cada plataforma, ejecutar el validador del fixture desde la raíz del repositorio Rubrova:

    node scripts/evaluation/validate-fixture.mjs

El validador comprueba aritmética de venta, descuentos, pagos mixtos, caja, cantidades, devolución, recepción parcial, retiro de artículos del carrito, vuelto, estados de terminal y límites de homologación.

## 6. Registro de evidencia

Por cada prueba P01–P26, registrar:

| Campo | Qué guardar |
|---|---|
| Plataforma y versión | Versión visible y salida de bench version cuando aplique |
| Sistema operativo | Versión y arquitectura |
| Identificador de escenario | P01 a P17 |
| Resultado | Pendiente, aprobado, fallido o bloqueado |
| Evidencia | Captura o log sin credenciales ni datos reales |
| Adaptación | Configuración, módulo, parche o workaround requerido |
| Tiempo | Tiempo real de preparación y ejecución |
| Observaciones | Diferencias, límites y errores reproducibles |

No marcar una prueba como aprobada por ver una pantalla o completar una demo. Para los controles críticos se necesita repetir el caso, comprobar los registros y reconciliar caja, pagos e inventario.

## 7. Orden de ejecución

1. Validar el dataset y confirmar que todos los importes, cantidades y resultados esperados sean coherentes.
2. Levantar ERPNext 16.60.0 y recorrer el circuito de catálogo, POS, caja, inventario, devolución y reportes básicos.
3. Preparar MyCompany/lsFusion 6.2 y repetir exactamente el mismo circuito.
4. Preparar Tryton 8.0 y las ocho ramas tryton-ar 8.0 en un entorno limpio; fijar commits y dependencias, instalar el conjunto completo, ejecutar suites de pruebas y probar WSFE/WSFEX en homologación. Mantener Tryton 8.2 como comparación de actualización posterior.
5. Ejecutar un filtro corto de Dolibarr 24.0.3; ampliar sólo si pasa los mínimos de caja y gestión.
6. Preparar Posnic 1.9.2 como referencia de POS secundario, no como sustituto del ERP.
7. En los dos mejores candidatos, ejecutar escenarios P01–P26, y los P27–P44 que correspondan a sus límites de dominio y arquitectura.
8. Ejecutar hardware simulado, terminales y fiscalidad en homologación sólo cuando existan adaptadores y dispositivos de prueba adecuados.
9. Comparar experiencia, esfuerzo de adaptación, licencias, APIs, exportación, backup/restore, reinicio y costo de actualización antes de elegir.


**Estado:** este documento prepara instalaciones reproducibles; no afirma que ya se hayan desplegado o probado en el equipo.
