# Parches Rubrova sobre lsFusion

Este directorio contiene parches propios que, por su alcance, no conviene implementar como una extensión lsFusion independiente.

Reglas:
- Preferir módulos en extensions/lsfusion/ siempre que el punto de extensión resulte adecuado.
- Un parche debe explicar el problema, los archivos originales afectados, la versión upstream a la que aplica, el motivo por el que una extensión no alcanza y las pruebas que lo protegen.
- Los parches se aplican automáticamente durante el build de Rubrova y deben fallar si el contexto original cambió; nunca usar coincidencias laxas ni editar archivos silenciosamente.
- Ningún parche puede integrarse a producción sin una comparación contra el árbol upstream y una ejecución completa de regresión.
- La actualización de lsFusion se hace en una candidata aislada; si un parche no aplica o rompe una prueba, se mantiene la versión estable.

## Parches activos

### lsFusion — `ZipServerSocket.java`

`ZipServerSocket.java` incorpora la propiedad optativa `lsfusion.rmi.bindAddress`:

- Si no se define, conserva el bind original de lsFusion (todas las interfaces), por lo que los despliegues Docker/LAN existentes mantienen su comportamiento.
- En el runtime nativo local, el supervisor define `-Dlsfusion.rmi.bindAddress=127.0.0.1`; el socket RMI queda limitado al equipo local.
- La compilación aplica el cambio mediante `scripts/platform/apply-rubrova-source-patches.py`, comprueba anclas exactas y vuelve a ejecutar el parche para demostrar idempotencia.
- El smoke nativo inspecciona el socket en escucha y exige `127.0.0.1:7652`; un bind `0.0.0.0` o `[::]` hace fallar la prueba.

Este parche es deliberadamente optativo. Un despliegue de sucursal que necesite acceso desde otras cajas deberá indicar una IP de interfaz privada y proteger el puerto con firewall y autenticación; nunca debe publicar RMI directamente en Internet.


### MyCompany 6.2 — `ReceiptRes.lsf`

Archivo protegido: `vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptRes.lsf`.

- **Defecto:** la recepción prevista podía seguir participando en `ReceiptResLedger` después de la cancelación nativa. Si luego se regeneraba una recepción, la cantidad antigua se sumaba a la nueva y alteraba `expected`, `planned` y `available`.
- **Motivo de parche directo:** el agregado `resLedger` pertenece al módulo upstream `ReceiptRes` y no expone un filtro/override equivalente para excluir cancelaciones desde `RubrovaCustom`. La extensión no puede retirar la fila agregada sin cambiar esa definición.
- **Cambio mínimo:** el módulo requiere `ReceiptCanceled` además de `ReceiptDone`, y el filtro añade `AND NOT canceled(receipt(line))`. No se usa `active(receipt)`: esa propiedad exige que la recepción esté `done` y excluiría indebidamente recepciones previstas todavía activas.
- **Aplicación:** `scripts/platform/apply-rubrova-source-patches.py` verifica anclas exactas, se niega ante drift/estado parcial y debe pasar dos ejecuciones consecutivas sin producir cambios adicionales.
- **Regresión:** `scripts/platform/test_apply_rubrova_source_patches.py` cubre aplicación limpia, idempotencia, estado parcial, drift y objetivo inexistente. La fixture runtime invoca `Inventory.cancel` nativo; no borra ni edita ledgers manualmente.
- **Evidencia:** [run #609](https://github.com/JavierGrecco/Rubrova/actions/runs/46113654320) terminó en `success` e informó valores conciliados iguales antes y después del reinicio. La prueba cubre recepción prevista Ready/no Done y generación de otra recepción; no cubre todavía cancelar una recepción Done, su stock por ubicación, put-away ni costo.

Este parche es de alcance MyCompany 6.2 fijado en `platform/source-lock.json`. Toda actualización upstream debe volver a aplicar la comparación, ejecutar el patcher y superar los smokes nativos antes de conservarlo.
