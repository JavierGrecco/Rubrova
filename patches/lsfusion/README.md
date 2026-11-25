# Parches Rubrova sobre lsFusion

Este directorio contiene parches propios que, por su alcance, no conviene implementar como una extensión lsFusion independiente.

Reglas:
- Preferir módulos en extensions/lsfusion/ siempre que el punto de extensión resulte adecuado.
- Un parche debe explicar el problema, los archivos originales afectados, la versión upstream a la que aplica, el motivo por el que una extensión no alcanza y las pruebas que lo protegen.
- Los parches se aplican automáticamente durante el build de Rubrova y deben fallar si el contexto original cambió; nunca usar coincidencias laxas ni editar archivos silenciosamente.
- Ningún parche puede integrarse a producción sin una comparación contra el árbol upstream y una ejecución completa de regresión.
- La actualización de lsFusion se hace en una candidata aislada; si un parche no aplica o rompe una prueba, se mantiene la versión estable.

## Parche activo

`ZipServerSocket.java` incorpora la propiedad optativa `lsfusion.rmi.bindAddress`:

- Si no se define, conserva el bind original de lsFusion (todas las interfaces), por lo que los despliegues Docker/LAN existentes mantienen su comportamiento.
- En el runtime nativo local, el supervisor define `-Dlsfusion.rmi.bindAddress=127.0.0.1`; el socket RMI queda limitado al equipo local.
- La compilación aplica el cambio mediante `scripts/platform/apply-rubrova-source-patches.py`, comprueba anclas exactas y vuelve a ejecutar el parche para demostrar idempotencia.
- El smoke nativo inspecciona el socket en escucha y exige `127.0.0.1:7652`; un bind `0.0.0.0` o `[::]` hace fallar la prueba.

Este parche es deliberadamente optativo. Un despliegue de sucursal que necesite acceso desde otras cajas deberá indicar una IP de interfaz privada y proteger el puerto con firewall y autenticación; nunca debe publicar RMI directamente en Internet.
