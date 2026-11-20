# Parches Rubrova sobre lsFusion

Este directorio contiene parches propios que, por su alcance, no conviene implementar como una extensión lsFusion independiente.

Reglas:
- Preferir módulos en extensions/lsfusion/ siempre que el punto de extensión resulte adecuado.
- Un parche debe explicar el problema, los archivos originales afectados, la versión upstream a la que aplica, el motivo por el que una extensión no alcanza y las pruebas que lo protegen.
- Los parches se aplican automáticamente durante el build de Rubrova y deben fallar si el contexto original cambió; nunca usar coincidencias laxas ni editar archivos silenciosamente.
- Ningún parche puede integrarse a producción sin una comparación contra el árbol upstream y una ejecución completa de regresión.
- La actualización de lsFusion se hace en una candidata aislada; si un parche no aplica o rompe una prueba, se mantiene la versión estable.

Todavía no hay parches directos del motor aceptados. La existencia de este directorio establece el mecanismo y no significa que ya hayamos necesitado modificar el motor.
