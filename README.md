<p align="center">
  <img src="docs/assets/rubrova-hero.svg" alt="Rubrova: plataforma local de POS, ERP e inteligencia operativa" width="100%"/>
</p>

# Rubrova

<p align="center">
  <strong>POS + ERP + inteligencia operativa para comercios y negocios con múltiples canales.</strong><br/>
  Una operación comercial coherente, trazable y preparada para decidir.
</p>

<p align="center">
  <a href="docs/EXECUTIVE_PRODUCT_BRIEF.md">Brief ejecutivo</a> ·
  <a href="docs/PROJECT_STATUS.md">Estado real</a> ·
  <a href="docs/ARCHITECTURE.md">Arquitectura</a> ·
  <a href="docs/SECURITY_POSTURE.md">Seguridad y evidencia</a> ·
  <a href="docs/QUALITY_AND_TESTING.md">Calidad y pruebas</a>
</p>

<p align="center">
  <a href="https://github.com/JavierGrecco/Rubrova/actions/workflows/platform-extension.yml"><img alt="Platform CI" src="https://github.com/JavierGrecco/Rubrova/actions/workflows/platform-extension.yml/badge.svg?branch=main"/></a>
  <a href="https://github.com/JavierGrecco/Rubrova/actions/workflows/replenishment-planner.yml"><img alt="Replenishment tests" src="https://github.com/JavierGrecco/Rubrova/actions/workflows/replenishment-planner.yml/badge.svg?branch=main"/></a>
  <img alt="Etapa piloto en validación" src="https://img.shields.io/badge/etapa-piloto%20en%20validaci%C3%B3n-D69E36?style=flat"/>
  <img alt="Runtime local first" src="https://img.shields.io/badge/runtime-local--first-238A78?style=flat"/>
  <img alt="Java 21" src="https://img.shields.io/badge/Java-21-4776A8?style=flat"/>
  <img alt="PostgreSQL 18" src="https://img.shields.io/badge/PostgreSQL-18-4169E1?style=flat"/>
</p>

**POS + ERP + inteligencia operativa para comercios y negocios con múltiples canales.**

Rubrova es una plataforma de gestión comercial en desarrollo. Busca reunir la operación diaria del negocio —ventas, caja, inventario, compras, clientes y administración— sobre una base de datos coherente, trazable y preparada para análisis de gestión.

**Dirección de producto:** experiencia simple en el mostrador, control operativo completo para la administración y datos confiables para decidir.

> **Estado del proyecto · 25 de noviembre de 2026**
>
> Rubrova está en etapa de piloto integrado POS + ERP. El código fuente de lsFusion 6.2 y MyCompany 6.2 está fijado dentro del repositorio. En la revisión actual de CI aprobaron el planificador, las validaciones estáticas, Windows, la compilación propia de servidor/cliente GWT/lógica y la publicación de artefactos; los smokes macOS ARM64 y Linux siguen ejecutándose. Un ciclo POS básico con datos sintéticos fue aceptado anteriormente. La exportación nativa de reposición es de solo lectura y continúa en validación: el último smoke completado permitió iniciar sesión, pero la llamada a la API respondió “Set operation is incorrect”. Se retiraron conversiones de índices que podían ocultar la fuente de los parámetros y la corrección está bajo revalidación. **No es una versión productiva ni está aprobada para operar con datos comerciales reales.**
>
> Seguimiento: [PR #8 — exportación nativa MyCompany](https://github.com/JavierGrecco/Rubrova/pull/8) · [último diagnóstico completado](https://github.com/JavierGrecco/Rubrova/actions/runs/45721155696) · [revalidación en curso](https://github.com/JavierGrecco/Rubrova/actions/runs/45723325906) · [estado y criterios de aceptación](docs/PROJECT_STATUS.md).

## Propuesta de producto

Rubrova está pensado para negocios que necesitan algo más que una caja registradora:

- **POS y operación comercial:** catálogo, carrito editable, precios, descuentos, pagos, turnos, caja, comprobantes y devoluciones.
- **ERP de gestión:** inventario, depósitos, compras, proveedores, recepción, costos, clientes, cuentas corrientes y sucursales.
- **Múltiples canales y áreas:** local físico, online, WhatsApp, marketplaces, mayorista, distribución y servicios B2B, con lectura consolidada y por unidad de negocio.
- **Control y trazabilidad:** permisos, auditoría, movimientos compensatorios e historial de las operaciones.
- **Inteligencia comercial:** rentabilidad, demanda, estacionalidad, marcas, promociones, reposición y análisis por producto, categoría, canal y cliente.

El alcance es progresivo: primero se consolida la operación transaccional; luego se amplían las capacidades administrativas, fiscales y analíticas. Las integraciones externas y la logística avanzada no son el centro de la primera entrega.

## Principios técnicos

**Local-first.** La dirección es que el núcleo POS + ERP pueda ejecutarse en el equipo del negocio sin depender de la disponibilidad de servicios cloud. La sincronización y los conectores externos deben tolerar cortes sin detener la operación local.

**Una autoridad por dato.** Ventas, pagos, caja, inventario y documentos fiscales tienen estados relacionados, pero ciclos de vida separados. Una venta no debe duplicarse ni facturarse dos veces.

**Modularidad pragmática.** El núcleo reutiliza MyCompany/lsFusion como suite integrada. No se presenta como microservicios: se separan servicios propios sólo cuando exista un límite operativo y de datos demostrable.

**Reutilización con control.** El código base está vendorizado y versionado en el directorio vendor; las extensiones Rubrova se mantienen separadas. Los cambios de upstream no se incorporan automáticamente.

**Datos auditables.** Toda recomendación analítica debe distinguir hechos observados, supuestos y estimaciones. El planificador de reposición no crea ni confirma órdenes.

## Arquitectura y tecnología

| Capa | Implementación |
|---|---|
| Núcleo POS + ERP | MyCompany 6.2 sobre lsFusion 6.2 |
| Backend y lógica | Java 21 / lsFusion |
| Cliente web | GWT servido por Apache Tomcat 9 |
| Persistencia | PostgreSQL 18 |
| Extensiones | Módulos Rubrova en extensions/lsfusion |
| Integración de reposición | API autenticada de solo lectura + adaptador Python |
| Validación | GitHub Actions, pruebas Python, pruebas de contrato y smokes de runtime |

El runtime local nativo es la ruta prioritaria para desarrollo en macOS Apple Silicon y Linux. Docker se conserva como entorno de diagnóstico y empaquetado, no como requisito de operación local.

### Mapa del piloto técnico

```mermaid
flowchart LR
    OP["Operación en caja y administración"] --> WEB["Cliente web GWT"]
    WEB --> TOM["Tomcat 9"]
    TOM --> CORE["MyCompany 6.2 + lsFusion 6.2"]
    EXT["Extensiones Rubrova"] --> CORE
    CORE --> DB[("PostgreSQL 18")]
    CI["GitHub Actions"] -. "compila y valida" .-> CORE
```

El diagrama representa el núcleo integrado que estamos construyendo y probando. No describe una arquitectura de microservicios ni implica que todas las integraciones externas estén habilitadas.

## Fortalezas de ingeniería verificables

| Fortaleza | Evidencia actual | Límite conocido |
|---|---|---|
| Control del código base | Fuentes upstream fijadas y compilación propia de lsFusion/MyCompany en CI | No equivale a una auditoría completa de dependencias ni a una SBOM |
| Ejecución local nativa | Arranque, login y recorridos sintéticos verificados en runners macOS ARM64 y Linux x86_64 | Falta aceptación en equipos físicos, Windows y una instalación limpia offline |
| Resiliencia de integraciones | Escenarios CI de timeout, respuestas HTTP 408/429/503, Retry-After y recuperación de proveedor simulado | Cobertura limitada; no valida todos los flujos de escritura ni conectores reales |
| Trazabilidad operativa | Modelo y criterios definidos para relacionar ventas, pagos, caja, inventario y movimientos compensatorios | Devoluciones, arqueo completo y auditoría protegida todavía no están aceptados |

La [postura de seguridad](docs/SECURITY_POSTURE.md) separa expresamente controles verificados, controles diseñados y puertas pendientes antes de producción. No se anuncian certificaciones ni garantías sin evidencia.



## Estado de implementación

| Área | Estado actual |
|---|---|
| Fuentes y compilación propia lsFusion/MyCompany | Implementado y compilado en CI |
| POS base MyCompany | Recorrido sintético básico aceptado en una ejecución anterior |
| Runtime nativo | Inicio y login verificados en runners macOS ARM64 y Linux; falta completar la aceptación del endpoint nuevo |
| Resiliencia de integraciones | Base inicial y pruebas de fallos HTTP; faltan conectores productivos y más escenarios de escritura |
| Terminales de pago | Modelo y trazabilidad inicial; sin adquirente ni cobro real homologado |
| Planificador de reposición | Motor y adaptador de snapshots con pruebas; puente nativo pendiente de aceptación |
| ARCA y fiscalidad productiva | Pendiente |
| Devoluciones, arqueo completo, vuelto y pagos mixtos | Cobertura funcional pendiente |
| Instalación limpia offline y backup/restore | Pendiente |
| Uso diario con datos reales | No autorizado todavía |

La evidencia y las limitaciones se mantienen en [Estado real del proyecto](docs/PROJECT_STATUS.md), no se infieren de una compilación exitosa.

## Ejecutar localmente

El repositorio incluye una vista previa nativa sin Docker. Es un entorno de desarrollo, no un instalador comercial ni una configuración productiva.

**Requisitos:** Java 21, Maven, Python 3, PostgreSQL 18 (herramientas initdb, pg_ctl, pg_isready, createdb y psql) y Tomcat 9.0.124. La primera compilación puede descargar dependencias Maven; la primera preparación también puede descargar Tomcat y verificar su SHA-512.

Desde la raíz del repositorio:

```bash
python3 scripts/platform/runtime-config.py init

mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package
mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package

python3 scripts/platform/run-local-native-preview.py doctor
python3 scripts/platform/run-local-native-preview.py --no-open start
```

Abrí [http://127.0.0.1:8080/login](http://127.0.0.1:8080/login). El supervisor mantiene una base de datos aislada en el directorio de datos de Rubrova y la conserva al detener los procesos con Ctrl+C.

En macOS con Homebrew, indicá las herramientas de PostgreSQL 18 antes de ejecutar el diagnóstico:

```bash
export RUBROVA_POSTGRES_BIN="$(brew --prefix postgresql@18)/bin"
export JAVA_HOME="$(/usr/libexec/java_home -v 21)"
export PATH="$JAVA_HOME/bin:$RUBROVA_POSTGRES_BIN:$PATH"
```

También existen los accesos **Iniciar Rubrova.command** y **Iniciar Rubrova - Demo.command** para macOS. La demostración usa una base separada. Consultá [Compatibilidad con macOS](docs/MACOS_SUPPORT.md) y [Instalación y runtime MyCompany](docs/MYCOMPANY_RUNTIME_INSTALL.md) antes de ejecutar.

**Seguridad de la vista previa:** se enlaza a loopback y usa una configuración local de desarrollo. No la expongas a la red ni cargues información comercial real. La instalación productiva requiere endurecimiento de credenciales, permisos, firewall, backups y restauración verificada.

## Organización del repositorio

- **main** es la fuente de verdad.
- Se mantiene una rama de funcionalidad activa; una segunda sólo para un arreglo urgente e independiente.
- Cada hito entra por un PR directo a main, después de validar el alcance afectado.
- Se prefiere squash merge y se elimina la rama después de integrar.
- Las ramas históricas no se vuelven a fusionar sin una diferencia de código comprobada.

Ver [Política de ramas e integración](docs/BRANCHING_STRATEGY.md).

## Documentación

| Documento | Contenido |
|---|---|
| [Brief ejecutivo](docs/EXECUTIVE_PRODUCT_BRIEF.md) | Propuesta de producto, segmentos, valor, diferenciadores y estado honesto |
| [Estado del proyecto](docs/PROJECT_STATUS.md) | Evidencia de CI, capacidades aceptadas, brechas y próximos criterios |
| [Plan de trabajo](docs/ROADMAP.md) | Fases, prioridades y próximos hitos |
| [Plan maestro](docs/MASTER_IMPLEMENTATION_PLAN.md) | Secuencia ejecutiva y alcance funcional |
| [Visión de producto](docs/PRODUCT_VISION.md) | Problema, usuarios, objetivos y principios |
| [Alcance funcional](docs/FUNCTIONAL_SCOPE.md) | Capacidades del producto y límites |
| [Requisitos del POS](docs/POS_REQUIREMENTS.md) | Venta, caja, cobro, devoluciones y operación diaria |
| [Arquitectura](docs/ARCHITECTURE.md) | Componentes, límites de dominio y decisiones técnicas |
| [Modelo de dominio](docs/DOMAIN_MODEL.md) | Entidades, estados, movimientos y relaciones |
| [Datos y base analítica](docs/DATA_CAPTURE_AND_ANALYTICAL_FOUNDATION.md) | Captura histórica y dimensiones necesarias para inteligencia |
| [Demanda, rentabilidad y marcas](docs/DEMAND_AND_MARGIN_INTELLIGENCE.md) | Diseño analítico, estimaciones y evaluación reproducible |
| [Stock proyectado y reposición](docs/PROJECTED_STOCK_AND_REPLENISHMENT.md) | Contrato del planificador y semántica de inventario |
| [Resiliencia de integraciones](docs/INTEGRATION_RESILIENCE_AND_ERROR_HANDLING.md) | Timeouts, reintentos, idempotencia y recuperación |
| [Postura de seguridad y evidencia](docs/SECURITY_POSTURE.md) | Qué está verificado, qué está diseñado y qué falta antes de producción |
| [Seguridad y auditoría](docs/SECURITY_AND_AUDIT.md) | Requisitos de identidad, permisos, privacidad, pagos y auditoría |
| [Continuidad y recuperación](docs/OPERATIONAL_RESILIENCE_AND_RECOVERY.md) | Backups, restore, rollback y fallos |
| [Compatibilidad con macOS](docs/MACOS_SUPPORT.md) | Ejecución nativa en Apple Silicon |
| [Calidad y pruebas](docs/QUALITY_AND_TESTING.md) | Estrategia de validación y puertas de aceptación |

## Alcance y responsabilidad

Rubrova está en desarrollo activo. Los resultados de CI demuestran escenarios específicos sobre bases sintéticas y descartables; no equivalen a homologación fiscal, pruebas con adquirentes, instalación limpia, restauración de datos ni validación de operación diaria. Las marcas, integraciones y dominios comerciales se mantienen sujetos a verificación legal y técnica antes de cualquier lanzamiento.
