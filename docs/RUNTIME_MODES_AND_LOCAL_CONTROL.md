# Modos de ejecución y control local de Rubrova

**Decisión de arquitectura:** separar el lugar donde corre el POS/ERP de la conectividad con proveedores externos. Ofrecer siempre un control independiente del servidor para consultar estado y cambiar el destino de ejecución.  
**Estado:** contrato de configuración inicial y validador implementados; lanzador nativo completo, panel visual y migración entre destinos pendientes.

## 1. Decisión

Rubrova tendrá tres destinos seleccionables desde un panel de control independiente:

| Destino | Dónde corre el servidor y la base | Requiere Docker | Requiere Internet para operar el núcleo |
|---|---|---:|---:|
| **Local nativo** | Java, PostgreSQL y Tomcat como procesos/servicios del propio equipo | No | No |
| **Docker local** | Los mismos componentes en contenedores en el propio equipo | Sí | No, una vez instalados y preparados |
| **Servidor remoto** | Servidor y base de datos en otra máquina o infraestructura | No en el puesto | Sí para acceder al servidor remoto |

El destino predeterminado para el desarrollo y la instalación local será **Local nativo**. Docker local se conserva como alternativa de aislamiento, repetibilidad y despliegue. Servidor remoto se configura con una URL HTTPS.

El contrato compartido está en `platform/runtime-config.schema.json`. La herramienta `scripts/platform/runtime-config.py` ya permite inicializar, validar, consultar y guardar el destino elegido. El validador rechaza URLs remotas sin TLS salvo loopback de desarrollo y no permite guardar contraseñas, tokens ni claves en el archivo.

## 2. No confundir ubicación con conectividad

Son dos decisiones diferentes:

- **Destino del núcleo:** dónde se ejecutan el servidor lsFusion/MyCompany, el cliente web y PostgreSQL.
- **Integraciones externas:** si Rubrova tiene habilitado llamar a ARCA, Mercado Pago, adquirentes, marketplaces, mensajería o transportistas.

Por eso, en Local nativo o Docker local se podrá pausar o habilitar las integraciones sin mover el servidor a la nube. Que Mercado Pago necesite Internet no significa que el POS deba estar alojado en Internet. En una caída de Internet el núcleo local seguirá atendiendo las operaciones admitidas; las autorizaciones remotas quedarán pendientes o inciertas y se conciliarán cuando vuelva el proveedor.

El modo híbrido de sucursal —base local autoritativa más sincronización durable con central— es un objetivo posterior, no un interruptor que debamos mostrar como terminado. Sólo se habilitará cuando Outbox/Inbox, idempotencia, conflictos de stock, recuperación y conciliación estén implementados y probados. Mientras tanto, el modo remoto no promete operar sin Internet.

## 3. Por qué conviene un runtime nativo sin Docker

El runtime de Rubrova está compuesto por piezas que pueden ejecutarse directamente en el sistema operativo:

1. **PostgreSQL 18:** proceso de base de datos nativo y persistencia local.
2. **Servidor lsFusion/Rubrova:** Java 21 ejecutando `lsfusion.server.logics.BusinessLogicsBootstrap`, con el artefacto `server.jar` compilado desde `vendor/platform`.
3. **Lógica MyCompany + extensiones Rubrova:** el JAR de lógica compilado desde `vendor/mycompany`, más los módulos y recursos de `extensions/lsfusion`, cargados por el classpath y `logics.topModule=RubrovaCustom`.
4. **Cliente web:** el WAR compilado desde `vendor/platform/web-client`, desplegado en Apache Tomcat 9 compatible con el cliente lsFusion 6.2.
5. **Control de ejecución:** un proceso supervisor que inicia, comprueba, registra, detiene y reinicia los procesos anteriores.

La imagen oficial `lsfusion/mycompany:6.2` publicada para Docker es `linux/amd64`; eso limita esa imagen en Apple Silicon, no convierte al JAR de lógica en un binario AMD64. Java, JAR y WAR son ejecutables por una JVM compatible; PostgreSQL y el runtime Java sí se deben elegir para la arquitectura del equipo. Por eso la ruta nativa evita la emulación de la imagen de lógica en tu Mac ARM64.

La documentación oficial de lsFusion describe instalaciones manuales y automáticas con servidor Java, PostgreSQL y Tomcat, además de Docker. MyCompany publica una ruta de instalación en Windows x64 y Linux; Rubrova debe empaquetar su propio runtime para macOS y para una instalación offline verificable, sin depender del instalador online de MyCompany.

## 4. Qué hará el supervisor

Para desarrollar y probar primero usaremos Python como **supervisor de procesos**, no como reemplazo del servidor, de PostgreSQL ni de Tomcat. La biblioteca estándar de Python alcanza para iniciar procesos, vigilar puertos, capturar logs, manejar señales, validar rutas y escribir configuración de forma atómica.

El supervisor nativo deberá:

- detectar Java 21, PostgreSQL 18 y Tomcat compatible;
- preparar un directorio de ejecución y una base local aislada para desarrollo;
- iniciar PostgreSQL y esperar a que acepte conexiones;
- iniciar el servidor Rubrova y esperar a que complete el arranque real, no sólo a que abra el puerto RMI;
- iniciar Tomcat y esperar a que el cliente web responda;
- mostrar URL, estado, logs y errores en español;
- cerrar en orden cliente, servidor y PostgreSQL, sin borrar datos;
- recuperar procesos interrumpidos y verificar que los PID/puertos correspondan a Rubrova antes de detenerlos;
- ejecutar el mismo flujo de aceptación contra runtime nativo y Docker, cuando las pruebas se hayan desacoplado del Compose.

Para Mac, PostgreSQL 18 tiene binarios nativos/universales disponibles; Postgres.app y Homebrew son opciones adecuadas para el laboratorio. Para el instalador comercial se distribuirán las dependencias verificadas junto con Rubrova o un instalador propio, no se exigirá instalar herramientas de desarrollo. El servidor de pruebas usará una instancia y un directorio de datos propios de Rubrova, no la base personal de Postgres.app ni una base productiva.

## 5. Panel de configuración siempre disponible

El selector no debe vivir exclusivamente dentro del POS: si el servidor no arranca, el operador igual necesita abrir Configuración, ver logs, corregir el destino y volver a iniciar.

La interfaz final tendrá dos accesos al mismo estado:

- **Rubrova Control**, una aplicación/menú independiente que puede seguir abierto aunque el servidor esté detenido. Desde allí se ve el destino activo, estado de PostgreSQL/servidor/cliente, URL, logs, diagnóstico, inicio/detención y configuración.
- **Administración dentro de Rubrova**, con un acceso a la misma configuración para que un administrador pueda consultar o preparar cambios mientras opera el sistema.

La app de control será independiente del proceso servidor. Primero se construirá y probará el backend supervisor en Python; después se lo empaquetará para cada sistema operativo y se conectará a una interfaz nativa sencilla. No se hará depender el producto de que el usuario tenga Python instalado: el intérprete y los recursos de soporte se incorporarán al paquete final o se utilizará un lanzador equivalente.

El archivo de configuración no contendrá contraseñas, tokens ni secretos. Esos datos irán a Keychain en macOS, Credential Manager/DPAPI en Windows o al almacén seguro correspondiente en Linux. La configuración se escribe de manera atómica y conserva la anterior ante un error.

## 6. Cambiar de destino sin perder datos

El control de ejecución estará disponible en todo momento, pero cambiar de destino no debe ser un simple cambio de URL cuando hay datos en dos bases distintas.

- **Native local ↔ Docker local:** cada runtime puede tener su propio clúster PostgreSQL. No se deben montar los archivos de datos nativos de macOS dentro de PostgreSQL Linux ni compartir el mismo directorio de base entre sistemas operativos. El cambio usará backup lógico y restore validado con versión compatible.
- **Local ↔ remoto:** requiere definir qué instalación es la autoridad de ventas, pagos, stock y caja. Si existe una cola de sincronización pendiente, no se permite cambiar a ciegas ni sobrescribir el estado más reciente.
- **Remote → local:** debe obtenerse una exportación/backup consistente del servidor remoto y restaurarse en el nodo local; después se comprueban saldos, ventas, pagos, turnos y stock.
- **Local → remote:** debe hacerse la misma validación en sentido inverso. Las operaciones locales no confirmadas o pendientes no pueden desaparecer.

Antes de aplicar un cambio, el panel debe mostrar qué base se usará, crear un backup, comprobar espacio, detener servicios, migrar, iniciar el nuevo destino y ejecutar validaciones de lectura y conciliación. Si algo falla, conserva el destino anterior y ofrece volver atrás. El selector actual sólo guarda preferencias; no afirma que la migración esté implementada.

## 7. Versiones y compatibilidad

- Java 21 es la línea del build del fork actual; se probará y empaquetará la misma versión de runtime.
- PostgreSQL 18 es la versión fijada actualmente en los artefactos de Rubrova.
- lsFusion 6.2 usa un cliente web basado en APIs Java EE `javax.*`; por eso el runtime actual emplea Tomcat 9, no se debe cambiarlo a Tomcat 10/11 sin probar la migración del cliente.
- Riesgo de mantenimiento: Apache anunció el fin de soporte de Tomcat 9.0.x para el 31 de marzo de 2027. Debemos planificar y probar la compatibilidad del cliente lsFusion con la siguiente rama soportada antes de esa fecha; no debemos ignorar ese vencimiento ni forzar una actualización no validada.

## 8. Pruebas que deben ejecutarse sin Docker

El pipeline debe tener un camino de aceptación nativo, además del actual camino Docker:

1. preparar Java 21, PostgreSQL 18 y Tomcat 9 dentro del runner Linux;
2. construir server JAR, MyCompany logic JAR y client WAR desde las fuentes de Rubrova;
3. iniciar PostgreSQL con un directorio de datos temporal;
4. iniciar servidor y Tomcat mediante el supervisor nativo;
5. abrir la UI con Chromium y realizar una venta sintética en efectivo;
6. comprobar factura, pago, caja, stock y turno desde los datos persistidos;
7. reiniciar servidor y cliente sin borrar PostgreSQL y volver a conciliar;
8. simular falta de Internet, manteniendo los procesos locales, y comprobar que las funciones del núcleo siguen disponibles;
9. detener procesos y borrar exclusivamente el directorio temporal de CI.

La prueba nativa será la ruta rápida de desarrollo y el Docker smoke conservará su utilidad como verificación de empaquetado/aislamiento. Ninguna se marcará aprobada antes de ejecutar el flujo completo.

## 9. Estado real y siguiente entrega

**Implementado en este bloque:** esquema JSON de configuración, validador Python, comandos de lectura/validación y cambios de destino con confirmación explícita de que el archivo no migra ni copia datos.

**Todavía pendiente:** panel visual independiente, supervisor de PostgreSQL/Java/Tomcat, empaquetado nativo macOS/Windows, migración segura entre bases y smoke funcional nativo sin Docker.

El primer objetivo de prueba será tu MacBook Air: ejecutar los mismos JAR/WAR del proyecto en Java 21 nativo ARM64, con PostgreSQL 18 y Tomcat local, sin Docker Desktop. Después incorporaremos el paquete autónomo para una PC limpia y Windows.

## Referencias técnicas

- lsFusion, [opciones de instalación: manual, automática y Docker](https://docs.lsfusion.org/v6/Install/).
- lsFusion, [instalación de producción](https://docs.lsfusion.org/Execution_auto/).
- MyCompany, [guía de instalación](https://mycompany-docs.lsfusion.org/administration/installation/).
- PostgreSQL, [plataformas soportadas](https://www.postgresql.org/docs/18/supported-platforms.html) y [paquetes macOS](https://www.postgresql.org/download/macosx/).
- Postgres.app, [descargas de PostgreSQL 18](https://postgresapp.com/downloads.html).
- Apache Tomcat, [Tomcat 9.0.124](https://downloads.apache.org/tomcat/tomcat-9/v9.0.124/bin/) y [fin de soporte de Tomcat 9.0.x](https://tomcat.apache.org/tomcat-9.0.x-eos).
- Eclipse Temurin, [Java 21 para macOS ARM64 y Windows x64](https://adoptium.net/temurin/releases/?version=21).
