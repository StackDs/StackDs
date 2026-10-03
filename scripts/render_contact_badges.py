"""Static contact badges with local glyphs and readable labels."""

from html import escape
from math import ceil

from profile_icons import icon_for


def render(contact, theme):
    label = escape(contact["label"])
    width, height = ceil(46 + len(contact["label"]) * 13 * .602 + 14), 36
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title" xml:lang="en" data-motion="static">
  <title id="title">{label}</title>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="6" fill="{theme['surface']}" stroke="{theme['border']}"/>
  <style>.icon-fill {{ fill: {theme['accent_light']}; stroke: none; }}</style>
  <g transform="translate(11 7) scale(.9)" fill="none" stroke="{theme['accent_light']}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    {icon_for(contact['id'])}
  </g>
  <text x="43" y="23" font-family="DejaVu Sans Mono, Liberation Mono, monospace" font-size="13" fill="{theme['text']}">{label}</text>
</svg>
'''
