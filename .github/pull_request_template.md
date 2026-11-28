## Objetivo y alcance

<!-- Qué necesidad resuelve este cambio y qué queda fuera. -->

## Revisión obligatoria del mapeo de MyCompany / lsFusion

- [ ] Consulté `docs/platform-audit/README.md` y los dossiers relevantes.
- [ ] Identifiqué el nombre exacto declarado en `MODULE` y consulté `MYCOMPANY_6_2_MODULE_INTEGRATION_DIRECTORY.md` o ejecuté `node scripts/platform/module-integration-route.mjs --module NombreExacto`.
- [ ] Revisé la primera lectura indicada, la ficha del módulo y las lecturas transversales recomendadas.
- [ ] Revisé el módulo nativo, sus dependencias `REQUIRE`, sus consumidores directos y las extensiones.
- [ ] Confirmé si cada módulo está dentro o fuera del cierre de `RubrovaCustom`; no asumí que todo lo vendorizado está cargado.
- [ ] Revisé las capacidades pertinentes de lsFusion, cliente, API y utilidades.
- [ ] Seguí el flujo hasta documentos, estados, ledgers, reportes y efectos laterales.
- [ ] Actualicé/creé la ficha de integración y el Manual técnico, o expliqué por qué no corresponde.

**MODULE exacto (no sólo nombre de archivo):**

**Ruta(s) LSF y commit de origen:**

**Comando de consulta ejecutado y salida (si aplica):**

**Dossier y secciones de primera lectura:**

**REQUIRE directos:**

**Consumidores directos:**

**Entidades/documentos/ledgers dueños y afectados:**

**Estados, transiciones, APIs y permisos implicados:**

**Dependencias, consumidores y productores afectados:**

**Decisión de reutilización:** reutilizar nativo / extender nativo / adaptar por contrato / módulo propio / parche upstream / dependencia externa / no aplica.

**Evidencia y motivo de la decisión:**

## Datos, contratos y seguridad

- [ ] Autoridad de cada dato y claves identificadas.
- [ ] Unidades, moneda, precisión, NULL / cero / vacío y estados definidos.
- [ ] Idempotencia, concurrencia, permisos, auditoría y privacidad revisados.
- [ ] Efectos financieros, de inventario y externos identificados.
- [ ] Rollback, compensación o recuperación considerados.

## Validación y evidencia

**Pruebas ejecutadas (comando, SHA, entorno y resultado):**

**Escenarios positivos, negativos, concurrentes y de recuperación:**

**Qué quedó sin probar o aceptar:**

## Documentación

- [ ] README / manual / mapa / roadmap actualizados cuando corresponde.
- [ ] La descripción no presenta como implementado o aceptado algo que sólo está diseñado o inventariado.
