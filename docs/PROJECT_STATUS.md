# Estado real del proyecto Rubrova

**Corte:** 20 de noviembre de 2026  
**Rama:** `main`  
**Commit:** `4d0a44c366ee7c10cea29b53f6f74da029f126f2`  
**Ejecución principal:** [CI 44810418808](https://github.com/JavierGrecco/Rubrova/actions/runs/44810418808)

## Resumen ejecutivo

Rubrova ya superó el punto de “sólo investigación y documentos”: MyCompany 6.2 arranca en un entorno efímero de CI, carga los dos módulos propios, permite iniciar sesión, navegar a Comercio → Punto de venta, seleccionar una caja sintética y abrir un turno. La sesión de prueba recibió el número `SM/000001` y la pantalla mostró `Cerrar turno`.

Eso es un avance técnico y funcional real, pero todavía no constituye un POS listo para el negocio. No se probó añadir un artículo, confirmar una venta, cobrar, calcular vuelto, afectar stock, devolver, cerrar/conciliar caja ni restaurar una copia. Tampoco está instalado en el equipo de uso.

**Conclusión de dirección:** el camino de reutilizar MyCompany está dando resultado para evitar construir desde cero el ERP/POS base. Pero el trabajo reciente se concentró demasiado en la infraestructura de aceptación. Desde ahora la prioridad debe pasar a demostrar operaciones comerciales reales en el entorno descartable, no seguir acumulando investigación ni otra plataforma ERP.

## Qué contiene hoy el repositorio

| Grupo | Archivos | Qué significa |
|---|---:|---|
| Documentación | 47 | Visión, requisitos, modelo, arquitectura, investigación y planes. No equivale a código implementado. |
| Extensión Rubrova | 3 | Entrada `RubrovaCustom`, diseño/localización POS y ResourceBundle `es_AR`. |
| Plataforma | 2 | Lock de MyCompany 6.2 y override Docker. |
| Scripts | 12 | Preparación/despliegue, runtime smoke test, inspección Chromium, fixture y benchmark. |
| Workflows CI | 3 | Validación de plataforma, dataset de evaluación y benchmark de demanda. |
| Otros | 2 | README y requisitos del benchmark. |
| **Total** | **69** | Repositorio pequeño en código propio y amplio en diseño/documentación. |

Los módulos fuente de MyCompany no están copiados al repositorio. Se consumen desde artefactos/imágenes fijados por versión y digest. Por eso no contamos las capacidades upstream como código escrito por Rubrova, aunque sí como funciones disponibles de la base candidata.

## Qué está probado hoy

| Capacidad | Estado | Evidencia / límite |
|---|---|---|
| MyCompany 6.2 en Linux x86_64 | **Aprobado en CI** | PostgreSQL, servidor y cliente levantan con artefactos fijados. |
| Extensión Rubrova | **Aprobado en CI** | `RubrovaPOSLocalization` y `RubrovaCustom` cargan sin editar upstream. |
| Inicio de sesión | **Aprobado en CI** | Chromium autentica en la instancia efímera. |
| Navegación | **Aprobado en CI** | Comercio → Punto de venta; el test exige encontrar el submenú y abrir la pantalla. |
| Pantalla POS | **Aprobado en CI** | Renderizado estable; caja sintética seleccionada. |
| Apertura de turno | **Aprobado en CI** | Se pulsa Abrir turno sólo en PostgreSQL temporal; aparece `SM/000001` y `Cerrar turno`. |
| Cierre de turno | Pendiente | La sesión se descarta al destruir el entorno; el botón no se pulsa. |
| Buscar/añadir artículo | Pendiente | Se prepara un producto sintético, precio, unidad y código de barras; aún no se verifica en el buscador. |
| Venta, pago y vuelto | Pendiente | No se confirmó ningún recibo ni cobro. |
| Stock y devoluciones | Pendiente | Sin conciliación funcional. |
| Traducción completa | Parcial | Los captions POS críticos se ven en español; siguen textos como `Master data`, `Settings`, `Date` y `Delete`. |
| Instalación en equipo de uso | Pendiente | Sólo se probó el runtime efímero de CI Linux x86_64. |
| Windows/macOS | Parcial | CI valida código, scripts y preparación; no demuestra runtime servidor nativo en esos sistemas. |
| ARCA, medios de pago y hardware | Investigación | Sin homologación, terminal física ni adaptadores productivos probados. |
| Offline, exportación y backup/restore | Pendiente | No hay una restauración comprobada. |

## Qué aporta MyCompany y qué es propio

MyCompany 6.2 ya ofrece módulos upstream de Retail POS, turnos, pagos, devoluciones, inventario, compras, ventas, facturación, costos y otras áreas ERP. Esa cobertura es la razón para usarlo como núcleo integrado, no para replicar todo desde cero.

Rubrova aporta por ahora:
- Un módulo de entrada que selecciona la composición `RubrovaCustom`.
- Un módulo de diseño/localización del POS.
- Un ResourceBundle español argentino parcial.
- Lock de artefactos, preparación y despliegue, pruebas de runtime y datos sintéticos.

Aún no hay un backend de negocio propio independiente, APIs de dominio propias, un libro mayor propio ni una capa de sincronización offline implementada. Eso no es un defecto por sí mismo: primero debemos comprobar si MyCompany cubre correctamente esos dominios y desarrollar sólo las brechas demostradas.

## ¿Está siendo productivo reutilizar proyectos avanzados?

**Sí, con una condición:** reutilizar una plataforma integrada como base está siendo más productivo que construir un POS/ERP completo desde cero. Ya podemos iniciar la aplicación, autenticar, entrar en el POS y abrir una sesión sin haber escrito esos módulos transaccionales.

**No sería productivo** seguir incorporando proyectos enteros, SDK o servicios antes de probar el circuito comercial. Cada nueva plataforma aumenta el costo de integración, actualización, licencias, seguridad y pruebas. MyCompany, Tryton y ERPNext no deben convertirse en tres implementaciones paralelas.

Decisión vigente:
1. MyCompany es el único piloto activo para cerrar POS + ERP.
2. Tryton queda como referencia fiscal argentina si aparece una brecha real.
3. ERPNext y Posnic quedan en reserva; no se integran ahora.
4. Los componentes especializados (ARCA, pagos, hardware, WMS, BI y logística) se evalúan sólo cuando el flujo principal identifique una necesidad concreta.

## Próximos bloques en orden

1. **Artículo → búsqueda → recibo:** verificar que el producto sintético aparezca en la pestaña Buscar artículos, añadirlo y comprobar cantidad/precio/total.
2. **Venta en efectivo:** confirmar un cobro sintético y conciliar exactamente un recibo, un pago, el movimiento de caja y el impacto esperado en stock.
3. **Pagos y vuelto:** cubrir importe exacto, vuelto, rechazo y estado incierto antes de probar pagos mixtos.
4. **Devolución y cierre:** devolución parcial, reintegro, conciliación de caja y cierre del turno.
5. **Calidad de uso:** completar español, revisar disposición y controles, probar permisos y exportación.
6. **Instalación y recuperación:** desplegar en el equipo elegido, asegurar administrador/firewall y probar backup/restore.
7. **Brechas argentinas:** recién entonces homologar ARCA, proveedores de pago y hardware físico.

La definición de terminado no es que aparezca un botón ni que CI quede verde: es que cada operación esté persistida una sola vez, sus efectos en dinero y stock concilien y la recuperación no pierda ni duplique operaciones.

## Riesgos y honestidad de la prueba

- La ejecución CI usa un administrador/instancia y datos sintéticos; no debe reutilizarse como configuración productiva.
- La base temporal y los volúmenes se eliminan al terminar el job.
- El test de apertura no cierra el turno; valida el estado abierto y luego descarta todo el entorno.
- Los logs de runtime incluyeron algunos `SQLTimeoutException` y `SQLConflictException` transitorios aunque el job completó con éxito. Se deben analizar y medir antes de declarar estabilidad.
- La imagen MyCompany 6.2 se ejecutó como `linux/amd64`; la validación de macOS Apple Silicon no equivale a ejecutar el servidor nativo ARM.
- Una captura o un test de interfaz no reemplazan pruebas de permisos, concurrencia, auditoría, fiscalidad, periféricos ni recuperación.

## Evidencia

- [CI multiplataforma + runtime + sesión abierta](https://github.com/JavierGrecco/Rubrova/actions/runs/44810418808)
- [Commit actual de main](https://github.com/JavierGrecco/Rubrova/commit/4d0a44c366ee7c10cea29b53f6f74da029f126f2)
- [Plan de implementación](IMPLEMENTATION_START.md)
- [Plan de trabajo](ROADMAP.md)
- [Calidad y pruebas](QUALITY_AND_TESTING.md)
