# Plan de implementación: tarjeta interactiva del perfil

> **Para el agente que ejecute este plan:** implementar las tareas en orden,
> verificar cada etapa y conservar los cambios locales preexistentes.

**Objetivo:** Publicar en GitHub Pages una tarjeta adaptable que integre el
banner actual con enlaces sociales clicables y copiado del correo, y enlazarla
desde la vista previa del perfil de GitHub.

**Arquitectura:** sitio estático sin frameworks bajo `site/`; HTML semántico
para enlaces y botón de correo, CSS adaptable con la paleta terminal actual,
JavaScript mínimo para Clipboard API y estado accesible. GitHub Actions copiará
los SVG generados a la carpeta del artefacto y publicará con Pages. El README
seguirá usando su vista previa SVG, enlazada a la página interactiva.

**Tecnologías:** HTML, CSS, JavaScript nativo, SVG existentes y GitHub Actions
Pages.

---

## Tarea 1: crear el esqueleto de la página

**Archivos:** `site/index.html`, `site/styles.css`

- Añadir estructura semántica: `main`, tarjeta, `picture` para variante de
  escritorio/móvil, título `Links de interés` y navegación social.
- Usar rutas relativas `./assets/terminal.svg` y
  `./assets/terminal-mobile.svg`, válidas bajo la ruta base `/StackDs/`.
- Crear el marco común de tarjeta y la barra de enlaces con la identidad
  existente: fondo `#0F1419`, acento `#088DDC`, texto claro y fuente monospace.
- Incluir foco visible, layout responsive y soporte para `prefers-reduced-motion`.
- Mantener la vista previa del SVG accesible con texto alternativo descriptivo.

**Verificación:** servir `site/` localmente después de copiar los SVG a
`site/assets/`; revisar carga de imágenes, ancho móvil/escritorio y consola del
navegador.

## Tarea 2: integrar enlaces e iconografía accesible

**Archivos:** `site/index.html`, `site/styles.css`

- Añadir iconos SVG en línea y enlaces a Instagram, PSN Profiles, LinkedIn y
  Portafolio (`#`).
- Usar etiquetas accesibles para todos los enlaces; los íconos decorativos se
  ocultan a lectores de pantalla cuando el enlace ya tiene nombre.
- Añadir el control de correo con `stackctrlz@gmail.com` y una región de estado
  `aria-live`.

**Verificación:** validar los cuatro destinos y recorrer los controles solo con
teclado; confirmar indicador de foco y nombres accesibles.

## Tarea 3: implementar el copiado de correo

**Archivos:** `site/app.js`, `site/index.html`, `site/styles.css`

- En el clic del botón de correo, copiar `stackctrlz@gmail.com` con
  `navigator.clipboard.writeText`.
- Mostrar «Copiado» brevemente en el estado accesible al completar.
- Si Clipboard API falla o no existe, indicar el fallo y mostrar la dirección
  para copia manual; nunca anunciar éxito falso.
- Mantener el botón funcional con teclado y sin dependencia de librerías.

**Verificación:** probar éxito en HTTPS y la ruta de fallo del portapapeles en
un navegador; comprobar que el feedback vuelve al estado inicial.

## Tarea 4: configurar GitHub Pages

**Archivos:** `.github/workflows/pages.yml`

- Añadir workflow en `push` a `main` para cambios en `site/**`,
  `assets/terminal*.svg` y el workflow; añadir también `workflow_dispatch`.
- Fijar acciones oficiales a revisiones inmutables, siguiendo el patrón del
  workflow de contribuciones.
- Con permisos mínimos, copiar los archivos de `site/` y ambos SVG a una carpeta
  de artefacto; subirla con `upload-pages-artifact` y publicarla con
  `deploy-pages` en el entorno `github-pages`.
- Mantener este workflow independiente del workflow de contribuciones.

**Verificación:** validar YAML, rutas del artefacto y permisos; comprobar una
ejecución de Actions tras subir a `main`. La fuente de Pages en Settings debe
ser GitHub Actions, configuración que el usuario indicó haber realizado.

## Tarea 5: enlazar la vista previa del perfil

**Archivos:** `README.md`, `PROFILE.md`

- Envolver la vista previa `picture` existente en un enlace a
  `https://stackds.github.io/StackDs/`.
- Quitar la fila de insignias sociales que se había añadido debajo: los enlaces
  reales estarán en la tarjeta interactiva.
- Documentar la URL, el flujo de despliegue y la dependencia de GitHub Pages en
  `PROFILE.md`.

**Verificación:** revisar el HTML/Markdown resultante y confirmar que la imagen
del perfil abre la página interactiva sin romper la selección móvil.

## Tarea 6: comprobaciones integrales

**Archivos:** todos los anteriores

- Ejecutar `python scripts/render_terminal.py` solo si se modifican fuentes de
  los SVG; preservar la selección de imagen existente.
- Ejecutar `git diff --check` y comprobar referencias locales de recursos,
  enlaces sociales, URL del perfil y ausencia de insignias antiguas.
- Probar la página en navegador en escritorio y móvil, incluyendo foco de
  teclado, movimiento reducido, copiado exitoso y error de portapapeles.
- Revisar el workflow de GitHub Actions y el sitio publicado después de la
  primera ejecución.

## Orden y ejecución

Completar tareas 1 a 3 para construir y probar la interfaz; después tarea 4
para publicación y tarea 5 para conectar el perfil; terminar con tarea 6.
La ejecución recomendada es en línea y secuencial para revisar juntos la
presentación de la tarjeta y reducir cambios simultáneos en los SVG/README.
