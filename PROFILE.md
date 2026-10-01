# Mantener el perfil

El contenido del perfil está en `README.md`. Las imágenes están guardadas en
este repositorio; la cabecera no depende de un servicio externo de banners.

## Cabecera

Editar `scripts/render_terminal.py` y regenerar los SVG:

```sh
python3 scripts/render_terminal.py
```

El README selecciona la versión compacta en pantallas de hasta 600 px. La
animación termina tras unos segundos y respeta `prefers-reduced-motion`.
La presentación también está escrita como texto en el README.

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
