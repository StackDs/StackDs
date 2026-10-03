"""Static, responsive project cards; the README supplies the clickable link."""

from html import escape
from textwrap import wrap


def render(project, theme, mobile=False):
    width, left = (420, 24) if mobile else (880, 36)
    y, lines = 36, []
    for value, size, color, weight in (
        (project["name"], 18, theme["accent_light"], "bold"),
        (project["description"], 14, theme["text"], "normal"),
    ):
        columns = min(80, int((width - 2 * left) / (size * .602)))
        for line in wrap(value, width=columns, break_long_words=True,
                         break_on_hyphens=False):
            lines.append(f'<text x="{left}" y="{y}" font-size="{size}" '
                         f'font-weight="{weight}" fill="{color}">{escape(line)}</text>')
            y += size + 8
        y += 10
    height = y + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="en" data-motion="static">
  <title id="title">{escape(project['name'])}</title>
  <desc id="desc">{escape(project['description'])}</desc>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" fill="{theme['surface']}" stroke="{theme['border']}"/>
  <g font-family="DejaVu Sans Mono, Liberation Mono, monospace">
    {''.join(lines)}
  </g>
</svg>
'''
