# Mantener el perfil

La vista previa del perfil está en `README.md` y enlaza a una tarjeta web
interactiva publicada en GitHub Pages. Las imágenes están guardadas en este
repositorio; el banner no depende de un servicio externo.

## Cabecera

El avatar predeterminado se lee de `ascii.txt` y se incorpora directamente a los
SVG. Regenerar las variantes de escritorio y móvil:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/render_terminal.py
```

Para usar la fotografía predeterminada en lugar del arte ASCII:

```sh
python3 scripts/render_terminal.py --photo
```

Para elegir al azar entre las imágenes compatibles de `assets/images/`:

```sh
python3 scripts/render_terminal.py --random
```

La misma imagen seleccionada se usa en los banners de escritorio y móvil. Pillow,
declarado en `requirements.txt`, solo se necesita para estos modos de fotografía.
Editar `ascii.txt` para cambiar el avatar predeterminado. Editar `QUOTES`, los
datos del perfil, las líneas de intereses y `ABOUT_ME_TEXT` en
`scripts/render_terminal.py`. Las citas se agrupan debajo del avatar,
ordenadas por longitud en dos columnas en escritorio y una en móvil; el texto va
en blanco y las atribuciones en gris comentario. Se ajustan en líneas; al añadir
más, el pie se desplaza para dejarles espacio. `about me` ajusta sus saltos de
línea al ancho disponible, conserva 24 px de margen derecho y usa 20 px entre
líneas.

La versión de escritorio, `assets/terminal.svg`, muestra el dibujo completo a
la izquierda y los datos a la derecha. El README selecciona
`assets/terminal-mobile.svg` en pantallas de hasta 600 px, con el dibujo encima
de los datos. El espaciado entre filas conserva la proporción cuadrada (1:1)
de la imagen de referencia; la altura de la terminal se adapta al dibujo para
evitar recortes. La proporción se configura con `REFERENCE_ASPECT_RATIO` en
el generador. Etiquetas y valores usan columnas estables; los campos largos se
ajustan a varias líneas y el contenido posterior se desplaza para evitar cruces.

En el modo de fotografía, la imagen se reduce a una cuadrícula de mayor
resolución y se dibuja con una rampa de 69 caracteres, corrección de proporción
para monospace, contraste local y enfoque de bordes. La zona central-superior
recibe un refuerzo suave de contraste y nitidez para definir los rasgos de la
cara. Tres tonos de cian
diferencian sombras, medios tonos y luces para conservar detalles pequeños como
ojos, lentes y contornos. El fondo blanco
exterior de JPEG se elimina y los píxeles transparentes de PNG se conservan
como espacios. Los SVG solo contienen el resultado en texto; no incrustan las
fotos originales. El azul `#088DDC` unifica los bordes del marco y del ASCII.
La animación SMIL se repite: las citas, el comando y
los datos aparecen carácter a carácter, se mantienen brevemente y se borran en
orden inverso. Un cursor acompaña la escritura y el borrado; a la vez, el escaneo
resalta las filas completas de arriba abajo y vuelve a empezar.

Con `prefers-reduced-motion`, el contenido queda completo y estático, sin cursor,
escaneo ni bordes animados. Los visores sin SMIL también muestran el contenido
completo. La descripción alternativa del README contiene la presentación en
texto.

## Tarjeta web interactiva

La página publicada en <https://stackds.github.io/StackDs/> reúne el banner y
los enlaces sociales en una tarjeta adaptable. Los enlaces y el botón de correo
son controles HTML; el correo copia `stackctrlz@gmail.com` y muestra feedback.
GitHub solo muestra la vista previa SVG estática en el README, por lo que hay
que abrirla para usar los controles.

El workflow `.github/workflows/pages.yml` publica `site/` cuando cambian la
página o los SVG del banner en `main`; también se puede ejecutar manualmente
desde GitHub Actions. Durante la publicación copia las dos variantes del banner
a `site/assets/`. La fuente de GitHub Pages del repositorio debe ser **GitHub
Actions** en **Settings → Pages → Build and deployment**.

Para probar la página localmente desde la raíz del repositorio:

```sh
mkdir -p site/assets
cp assets/terminal.svg assets/terminal-mobile.svg site/assets/
python3 -m http.server 8000 --directory site
```

Abrir <http://localhost:8000/>. El copiado del correo requiere un contexto
seguro como GitHub Pages para usar Clipboard API.

La paleta usa fondo `#0F1419`, acento `#088DDC`, texto `#ECEFF4`, secundario
`#D3C6AA` y color de comentario `#5c6370`. JetBrains Mono se importa desde
Google Fonts y tiene alternativas monospace para visores que bloquean fuentes
remotas. Los encabezados y prompts usan negrita; los valores y el cuerpo usan
peso normal.

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
