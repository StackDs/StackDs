# Mantener el perfil

El contenido del perfil está en `README.md`. Las imágenes están guardadas en
este repositorio; la cabecera no depende de un servicio externo de banners.

## Cabecera

El dibujo está en `scripts/profile_ascii.py`, con los espacios y saltos de línea
del ASCII suministrado. La composición y los datos se editan en
`scripts/render_terminal.py`. Regenerar los SVG con Python 3, sin dependencias:

```sh
python3 scripts/render_terminal.py
```

La versión de escritorio, `assets/terminal.svg`, muestra el dibujo completo a
la izquierda y los datos a la derecha. El README selecciona
`assets/terminal-mobile.svg` en pantallas de hasta 600 px, con el dibujo encima
de los datos. El espaciado entre filas conserva la proporción cuadrada (1:1)
de la imagen de referencia; la altura de la terminal se adapta al dibujo para
evitar recortes. La proporción se configura con `REFERENCE_ASPECT_RATIO` en
el generador.

El dibujo usa texto SVG, sin imágenes incrustadas. Bordes de neón recorren el
marco exterior y el marco del ASCII. La animación SMIL se repite: el comando y
los datos aparecen carácter a carácter, se mantienen brevemente y se borran en
orden inverso. Un cursor acompaña la escritura y el borrado; a la vez, el escaneo
resalta las filas completas de arriba abajo y vuelve a empezar.

Con `prefers-reduced-motion`, el contenido queda completo y estático, sin cursor,
escaneo ni bordes animados. Los visores sin SMIL también muestran el contenido
completo. La descripción alternativa del README contiene la presentación en
texto.

## Snake

Las imágenes iniciales usan el calendario público de StackDs consultado el
1 de octubre de 2026. El workflow `Update contribution snake` las reemplaza
con datos actualizados a las 06:23 UTC cada día. También se ejecuta al subir
el propio workflow a `main` y permite ejecución manual desde GitHub Actions.

Se utiliza [Platane/snk](https://github.com/Platane/snk), fijado a una revisión
concreta, y el `GITHUB_TOKEN` automático de Actions. No necesita un token
personal ni GitHub Pages. Las imágenes se guardan en `assets/contributions/`
y se incluyen directamente desde el README.

Para activar la actualización, subir estos archivos a `main` y comprobar
la ejecución en **Actions → Update contribution snake**. Si Actions está
deshabilitado en el repositorio, habilitarlo primero. El trabajo necesita
`contents: write`; una regla que impida pushes del bot a `main` también
impedirá que guarde las imágenes. El horario programado puede sufrir demoras.

`scripts/reduce_snake_motion.py` añade soporte de movimiento reducido después
de cada generación. Los colores claro y oscuro se editan en `outputs` dentro
de `.github/workflows/contributions.yml`.

## Comprobación local

```sh
python3 scripts/render_terminal.py
python3 scripts/reduce_snake_motion.py
git diff --check
```

Comprobar también el README en GitHub: usa Markdown, HTML compatible y SVG,
sin JavaScript ni estilos CSS insertados en el Markdown.
