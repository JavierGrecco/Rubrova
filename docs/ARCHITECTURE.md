undefined

## Composición de módulos de terceros

La arquitectura permite reutilizar módulos, adaptadores y servicios de proyectos diferentes. Se define cómo incorporarlos en [Composición de módulos y contratos](MODULE_COMPOSITION.md).

Reglas obligatorias:
- Cada agregado y cada ledger tienen un único módulo responsable.
- Los módulos ajenos se integran por puertos/capacidades y adaptadores; no comparten tablas ni hacen escrituras SQL directas entre sí.
- Las APIs y eventos se versionan, autentican, correlacionan y prueban.
- Los webhooks y mensajes se procesan de manera idempotente; los estados inciertos se concilian con el sistema autoritativo.
- Las operaciones distribuidas usan procesos durables y compensaciones explícitas cuando no existe una transacción común.
- La integración debe poder sustituirse sin reescribir reglas comerciales.
- La licencia, el commit, las dependencias, los avisos y las pruebas de cada componente quedan inventariados.

## Compatibilidad multiplataforma

Windows, Linux y macOS son objetivos de producto. No obligan a que todos los componentes compartan el mismo binario:

| Capa | Estrategia |
|---|---|
| Dominio, casos de uso y contratos | Neutral respecto del OS |
| Interfaz web/PWA | Navegador en Windows, Linux y macOS; móvil/handheld según capacidad |
| API y módulos de servidor | Contenedores/runtime compatible, independiente del sistema del puesto |
| Integraciones cloud y webhooks | Adaptador de servidor |
| Hardware USB/serie/Bluetooth | Puente local con implementaciones por OS y modelo |
| Paquete nativo | Solo cuando la experiencia o el acceso a dispositivo lo exijan |

Un componente valioso de Linux, Android o Windows no se descarta por sí solo. Se incorpora detrás de una capacidad estable y se crea otro adaptador para los sistemas faltantes. La matriz de compatibilidad registra qué está probado de verdad.

La selección de plataformas integrales y la investigación de módulos ya no son la misma decisión: Posnic, ERPNext y MyCompany/lsFusion se comparan como posibles bases; Simple WMS, OpenLinker, OfferKit y las herramientas analíticas se estudian como módulos/adaptadores.
