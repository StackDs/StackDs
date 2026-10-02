# Tarjeta interactiva del perfil — Diseño

## Objetivo

Publicar una versión web interactiva de la tarjeta del perfil para que los
enlaces sociales sean accionables dentro de la misma tarjeta. El perfil de
GitHub seguirá mostrando una vista previa estática, enlazada a la página
interactiva.

## Contexto y restricciones

- `README.md` muestra `assets/terminal.svg` o `assets/terminal-mobile.svg` como
  imágenes. Los enlaces dibujados dentro de esas imágenes no son accionables y
  GitHub no ejecuta JavaScript incrustado en el README.
- El repositorio no tiene una página web ni un despliegue de GitHub Pages
  configurado. El endpoint de configuración de Pages respondió 404 durante la
  exploración.
- El repositorio tiene un workflow de GitHub Actions para actualizar las
  imágenes de contribuciones, pero no uno para Pages.
- La página nueva debe conservar la identidad visual terminal/Arch, reutilizar
  los SVG generados y evitar dependencias de frameworks o de iconos remotos.

## Diseño

### Página interactiva

Crear `site/index.html` como página estática adaptable. Una tarjeta única
contendrá el banner actual —con la variante móvil según el ancho de pantalla— y
una sección `Links de interés` con íconos y controles HTML reales. Se conserva
el tema oscuro y los acentos azules del banner.

Los enlaces serán:

- Instagram: `https://www.instagram.com/_bryan.712/`
- PSN Profiles: `https://psnprofiles.com/StackDS`
- LinkedIn:
  `https://www.linkedin.com/in/bryan-aguirre-fuentes-1953642bb/?isSelfProfile=true`
- Portafolio: `#` hasta que se defina una URL.

Los enlaces externos serán enlaces HTML con nombres accesibles y apertura en
la misma pestaña. Los íconos serán SVG locales en línea para no depender de
servicios externos.

El ícono de correo será un botón que copia `stackctrlz@gmail.com` mediante la
Clipboard API y muestra el estado «Copiado». El estado se anunciará con una
región `aria-live`; si falla el acceso al portapapeles, se mostrará un mensaje
de error con la dirección para copiar manualmente.

### Publicación

Un workflow nuevo publicará el contenido de `site/` en GitHub Pages al subir a
`main` cambios relevantes de la página, del workflow o de los SVG del banner.
Durante el job de publicación se copiarán los SVG generados a `site/assets/`,
para que la página use las mismas imágenes del repositorio sin mantener copias
versionadas.

El workflow utilizará los permisos mínimos requeridos (`contents: read`,
`pages: write` e `id-token: write` en los jobs correspondientes), acciones
oficiales fijadas a revisiones concretas y un entorno de Pages. Se conservará
el workflow de contribuciones independiente.

El `README.md` enlazará la vista previa actual a
`https://stackds.github.io/StackDs/` y quitará la fila de insignias separada.
La vista previa no ejecuta las acciones: el usuario llega a la tarjeta
interactiva al abrir el enlace.

Para activar el primer despliegue, la fuente de GitHub Pages del repositorio
debe configurarse como **GitHub Actions** en Settings → Pages → Build and
deployment. La API de GitHub respondió 404 al consultar la configuración actual;
hay que confirmar o cambiar la fuente a Actions después de añadir el workflow.

## Accesibilidad y comportamiento

- La tarjeta se adapta a pantallas móviles y de escritorio.
- Los controles se pueden usar con teclado y muestran foco visible.
- Los íconos tienen nombre accesible; el estado de copiado se anuncia sin
  depender únicamente del color.
- Se respeta `prefers-reduced-motion` y no se agregan animaciones decorativas
  nuevas.
- Si Clipboard API no está disponible, la página muestra la dirección y un
  mensaje de fallo en lugar de afirmar que se copió.

## Verificación

- Revisar que la página y ambos banners carguen localmente y bajo la ruta de
  Pages `/StackDs/`.
- Comprobar los destinos de los cuatro enlaces externos y que el portafolio
  siga apuntando a `#`.
- Probar el copiado del correo en un contexto HTTPS y la respuesta de fallo
  cuando el portapapeles está denegado.
- Verificar navegación por teclado, foco, estado accesible, ancho móvil y
  escritorio.
- Validar el workflow y los artefactos publicados; ejecutar
  `git diff --check`.

## Fuera de alcance

- Definir la URL real del portafolio.
- Convertir el README de GitHub en una página con JavaScript; GitHub seguirá
  mostrando una imagen estática enlazada al sitio.
- Cambiar el contenido y la animación de las terminales más allá de reutilizar
  los SVG vigentes.
