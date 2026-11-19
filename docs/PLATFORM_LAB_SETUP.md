# Preparación del laboratorio de evaluación

**Revisión:** 19 de noviembre de 2026  
**Objetivo:** instalar Posnic y ERPNext en entornos aislados, usando datos sintéticos y versiones fijadas.  
**Regla principal:** no usar datos reales, instalaciones comerciales existentes, certificados fiscales de producción ni credenciales reales.

Este laboratorio no instala Rubrova ni incorpora código de terceros. Sirve para comprobar las dos plataformas antes de decidir si adoptamos una como base o construimos nuestro núcleo.

## 1. Qué vamos a instalar

| Candidato | Forma recomendada de evaluación | Versión |
|---|---|---|
| Posnic | Aplicación de escritorio en una VM limpia con Windows x64 o Ubuntu Desktop x86_64 | 1.9.2 |
| ERPNext | Demo desechable oficial con Docker Compose, publicada solo en localhost | 16.60.0 |

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

## 4. Cargar exactamente los mismos datos

Usar [platform-evaluation.json](fixtures/platform-evaluation.json) como fuente canónica. El archivo contiene productos ficticios, importes enteros en centavos, pagos, devolución parcial, compra y existencias esperadas.

No importar el JSON como si ambos productos compartieran un formato de importación. Cargar o crear los mismos datos mediante las pantallas de cada aplicación y conservar un registro de las diferencias de mapeo. La prueba compara resultados comerciales, no nombres de campos internos.

Antes de iniciar cada plataforma, ejecutar el validador del fixture desde la raíz del repositorio Rubrova:

    node scripts/evaluation/validate-fixture.mjs

El validador comprueba aritmética de venta, descuentos, pagos mixtos, caja, cantidades, devolución, recepción parcial y límites de homologación.

## 5. Registro de evidencia

Por cada prueba P01–P17, registrar:

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

## 6. Orden de ejecución

1. Validar el dataset.
2. Levantar ERPNext 16.60.0 y comprobar versión.
3. Cargar datos sintéticos y ejecutar P01–P10.
4. Ejecutar cortes, reinicio, idempotencia y restauración (P11–P15).
5. Registrar qué casos no puede demostrar la demo desechable por sus límites.
6. Preparar Posnic 1.9.2 en la VM compatible y repetir el mismo guion.
7. Ejecutar hardware simulado y fiscalidad en homologación (P16–P17) solo cuando existan adaptadores y dispositivos de prueba adecuados.
8. Comparar esfuerzo, limitaciones, licencias y costo de mantenimiento antes de elegir una base.

**Estado:** este documento prepara instalaciones reproducibles; no afirma que ya se hayan desplegado o probado en el equipo.
