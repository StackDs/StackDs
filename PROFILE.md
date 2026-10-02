# Mantener el perfil

El contenido del perfil está en `README.md`. La cabecera usa `dark.svg` y
`light.svg`, guardados en la raíz del repositorio, sin servicios externos.

## Cabecera

Editar los datos de `PROFILE` y los colores de `THEMES` en
`scripts/render_terminal.py` y regenerar los SVG con Python 3, sin dependencias:

```sh
python3 scripts/render_terminal.py
```

El README selecciona la variante clara u oscura mediante `<picture>` y
`prefers-color-scheme`. Ambas comparten un lienzo de 1180 × 610 y se adaptan al
ancho disponible conservando las proporciones. En pantallas pequeñas, la
presentación también se puede leer como texto debajo de la imagen.

La pila isométrica está dibujada con caracteres SVG, sin imágenes incrustadas.
Las animaciones usan SMIL: entrada escalonada, cursor breve y dos barridos
suaves. Terminan a los 17 segundos. Con `prefers-reduced-motion: reduce`, se
ocultan los elementos en movimiento y el contenido aparece sin transiciones.
Si el visor no admite SMIL, la composición sigue siendo legible.

Al cambiar información personal, actualizar también el texto y la descripción
alternativa en `README.md`. Los textos actuales están ajustados al diseño;
revisar los saltos de línea y el espacio disponible si se añaden valores largos.

Para publicar la cabecera solo hacen falta `README.md`, `dark.svg` y `light.svg`.

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
