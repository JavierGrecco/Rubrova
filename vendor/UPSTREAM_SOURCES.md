# Fuentes de terceros incorporadas

Estas carpetas contienen snapshots completos, fijados por commit, de proyectos externos incorporados a Rubrova. No son submódulos Git y no se consultan repositorios externos al iniciar la aplicación.

- platform/: lsFusion 6.2. Código bajo LGPL-3.0; conservar LICENSE y avisos originales.
- mycompany/: MyCompany 6.2. Código bajo Apache-2.0; conservar LICENSE y avisos originales.

Los archivos .rubrova-source.json registran el repositorio, nombre y commit exacto. Los archivos de origen se mantienen dentro del repositorio Rubrova. Las modificaciones propias se registran en Git y se documentan; no se sobrescriben automáticamente al actualizar el origen.

Para comparar una futura versión, descargarla en un área temporal, generar un diff por archivo, revisar licencias/dependencias y ejecutar la batería completa. No se permite reemplazar estas carpetas con una rama flotante ni con latest.
