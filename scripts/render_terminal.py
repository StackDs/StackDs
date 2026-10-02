#!/usr/bin/env python3
"""Build the two standalone profile banners using only the standard library."""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Profile facts come from the original README and terminal illustration.
# Keep the prose in README.md in sync when changing these values.
PROFILE = {
    "name": "Bryan / Stack",
    "terminal": "stack@arch:~",
    "headline": "Estudiante de informática",
    "education": ("Ingeniería Civil", "Informática"),
    "location": "Chile",
    "system": "Arch Linux",
    "tagline": "Last in, first out.",
    "alias": ("Mi nick viene de la mejor", "estructura de datos: la pila."),
}

THEMES = {
    "dark": {
        "background": "#060C18", "background_end": "#0C1728",
        "surface": "#152238", "surface_opacity": ".35",
        "glass": "#B4D4FF", "glass_opacity": ".035",
        "ink": "#F0F5FF", "muted": "#A1B1C9", "faint": "#889CB9",
        "border": "#34475F", "line": "#293C54", "grid": "#8DAACF",
        "accent": "#77E0F4", "secondary": "#B5A1F8", "green": "#80DEC1",
        "bloom": "#254B89", "bloom_opacity": ".24",
        "halo": "#51328A", "halo_opacity": ".16",
        "shadow": "#000817", "shadow_opacity": ".32",
        "pill": "#193044", "pill_border": "#36576E",
        "console": "#060E1C", "console_opacity": ".55",
        "reflection": "#DAEDFF",
    },
    "light": {
        "background": "#F8FAFF", "background_end": "#EDF3FA",
        "surface": "#FFFFFF", "surface_opacity": ".35",
        "glass": "#FFFFFF", "glass_opacity": ".76",
        "ink": "#15263D", "muted": "#475B76", "faint": "#556B87",
        "border": "#BCCCDD", "line": "#CEDAE8", "grid": "#7495B9",
        "accent": "#116780", "secondary": "#6650AF", "green": "#18735F",
        "bloom": "#BCDDF4", "bloom_opacity": ".50",
        "halo": "#D6C9F2", "halo_opacity": ".28",
        "shadow": "#607997", "shadow_opacity": ".12",
        "pill": "#EAF4FA", "pill_border": "#B8D1E1",
        "console": "#E8EFF8", "console_opacity": ".75",
        "reflection": "#FFFFFF",
    },
}


def text(x, y, value, color="ink", size=16, extra=""):
    return (f'<text x="{x}" y="{y}" class="{color}" font-size="{size}" '
            f'{extra}>{escape(value)}</text>')


def entrance(delay, duration=.65):
    # Static opacity is always 1. The animation overrides it only while active.
    # Start together and hold before revealing, avoiding a flash before begin.
    total = delay + duration
    return (f'<animate attributeName="opacity" values=".15;.15;1" '
            f'keyTimes="0;{delay / total:.4f};1" begin="0s" '
            f'dur="{total:.3f}s" fill="remove"/>')


def inside(x, y, polygon):
    """Point-in-convex-polygon test for the character-rendered stack faces."""
    signs = []
    for start, end in zip(polygon, polygon[1:] + polygon[:1]):
        signs.append((end[0] - start[0]) * (y - start[1])
                     - (end[1] - start[1]) * (x - start[0]))
    return all(value >= 0 for value in signs) or all(value <= 0 for value in signs)


def stack_art():
    """An original 69 × 50 character illustration, not a raster conversion.

    Three isometric slabs express the existing Stack / LIFO identity. Each
    face has its own character density; sparse glints give the top depth.
    """
    cells = [[" " for _ in range(69)] for _ in range(50)]
    for layer in (24, 12, 0):
        top = [(34, layer), (66, layer + 10),
               (34, layer + 20), (2, layer + 10)]
        left = [(2, layer + 10), (34, layer + 20),
                (34, layer + 25), (2, layer + 15)]
        right = [(34, layer + 20), (66, layer + 10),
                 (66, layer + 15), (34, layer + 25)]
        for y in range(50):
            for x in range(69):
                if inside(x, y, left):
                    cells[y][x] = "+" if (x + y) % 3 == 0 else ":"
                if inside(x, y, right):
                    cells[y][x] = "#" if (x + y) % 3 == 0 else "*"
                if inside(x, y, top):
                    cells[y][x] = ":" if (x + y) % 3 == 0 else "·"
                    edge = min(abs(y - (layer + abs(x - 34) / 3.2)),
                               abs(y - (layer + 20 - abs(x - 34) / 3.2)))
                    if edge < .65:
                        cells[y][x] = "+"
                    elif 27 <= x <= 41 and abs(y - layer - 10) < 2:
                        cells[y][x] = "*"
    return ["".join(row) for row in cells]


def render(theme):
    c = THEMES[theme]
    p = PROFILE
    label = (f'{p["name"]}, estudiante de {" ".join(p["education"])} '
             f'en {p["location"]}. Usuario de {p["system"]}. {p["tagline"]}')
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610"
  viewBox="0 0 1180 610" fill="none" role="img" aria-label="{escape(label, quote=True)}"
  aria-labelledby="title desc" xml:lang="es">
  <title id="title">{escape(p["name"])} — perfil</title>
  <desc id="desc">{escape(label)} A la izquierda, una pila de tres bloques
  isométricos dibujados con caracteres. A la derecha, información del perfil.</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }}
    .ink {{ fill: {c["ink"]}; }}
    .muted {{ fill: {c["muted"]}; }}
    .faint {{ fill: {c["faint"]}; }}
    .accent {{ fill: {c["accent"]}; }}
    .secondary {{ fill: {c["secondary"]}; }}
    .ascii {{ fill: url(#ascii-ink); font-size: 8.3px; }}
    @media (prefers-reduced-motion: reduce) {{
      .motion {{ display: none; }}
      .entrance {{ opacity: 1 !important; }}
    }}
  </style>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1180" y2="610" gradientUnits="userSpaceOnUse">
      <stop stop-color="{c["background"]}"/>
      <stop offset="1" stop-color="{c["background_end"]}"/>
    </linearGradient>
    <radialGradient id="bloom">
      <stop stop-color="{c["bloom"]}" stop-opacity="{c["bloom_opacity"]}"/>
      <stop offset="1" stop-color="{c["bloom"]}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="halo">
      <stop stop-color="{c["halo"]}" stop-opacity="{c["halo_opacity"]}"/>
      <stop offset="1" stop-color="{c["halo"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="glass" x1="0" y1="0" x2=".75" y2="1">
      <stop stop-color="{c["glass"]}" stop-opacity="{c["glass_opacity"]}"/>
      <stop offset="1" stop-color="{c["surface"]}" stop-opacity="{c["surface_opacity"]}"/>
    </linearGradient>
    <linearGradient id="rim" x1="24" y1="88" x2="1156" y2="552" gradientUnits="userSpaceOnUse">
      <stop stop-color="{c["accent"]}" stop-opacity=".48"/>
      <stop offset=".35" stop-color="{c["border"]}"/>
      <stop offset=".78" stop-color="{c["border"]}"/>
      <stop offset="1" stop-color="{c["secondary"]}" stop-opacity=".4"/>
    </linearGradient>
    <linearGradient id="ascii-ink" x1="86" y1="165" x2="378" y2="407" gradientUnits="userSpaceOnUse">
      <stop stop-color="{c["accent"]}"/>
      <stop offset=".54" stop-color="{c["secondary"]}"/>
      <stop offset="1" stop-color="{c["accent"]}"/>
    </linearGradient>
    <linearGradient id="scan">
      <stop stop-color="{c["accent"]}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{c["accent"]}"/>
      <stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="reflection" x1="0" y1="0" x2="1" y2=".7">
      <stop stop-color="{c["reflection"]}" stop-opacity=".08"/>
      <stop offset="1" stop-color="{c["reflection"]}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0H0V24" stroke="{c["grid"]}" stroke-opacity=".055"/>
    </pattern>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse">
      <path d="M0 .5H4" stroke="{c["grid"]}" stroke-opacity=".045"/>
    </pattern>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="125%" color-interpolation-filters="sRGB">
      <feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="{c["shadow"]}" flood-opacity="{c["shadow_opacity"]}"/>
    </filter>
    <clipPath id="canvas"><rect x="1" y="1" width="1178" height="608" rx="24"/></clipPath>
    <clipPath id="visual"><rect x="48" y="152" width="384" height="264" rx="8"/></clipPath>
  </defs>

  <g clip-path="url(#canvas)">
    <rect x="1" y="1" width="1178" height="608" rx="24" fill="url(#background)"/>
    <ellipse cx="250" cy="210" rx="430" ry="370" fill="url(#halo)"/>
    <ellipse cx="920" cy="450" rx="600" ry="380" fill="url(#bloom)"/>
    <rect x="1" y="64" width="1178" height="545" fill="url(#grid)"/>
    <path d="M24 64H1156" stroke="{c["line"]}"/>

    <!-- Terminal chrome: controls are decorative, not buttons. -->
    <g aria-hidden="true">
      <circle cx="32" cy="33" r="5" fill="#F47B83"/>
      <circle cx="52" cy="33" r="5" fill="#E7BC65"/>
      <circle cx="72" cy="33" r="5" fill="#75C7A1"/>
    </g>
''']
    parts.extend([
        text(96, 38, p["terminal"], "muted", 13),
        text(590, 38, "~/profile", "faint", 12, 'text-anchor="middle"'),
        text(1148, 38, "perfil.svg", "faint", 12, 'text-anchor="end"'),
        f'''<g filter="url(#shadow)">
      <rect x="24" y="88" width="432" height="464" rx="16" fill="url(#glass)" stroke="url(#rim)"/>
      <rect x="472" y="88" width="684" height="464" rx="16" fill="url(#glass)" stroke="url(#rim)"/>
    </g>
    <path d="M40 89H440M488 89H1140" stroke="{c["reflection"]}" stroke-opacity=".16"/>
    <path d="M25 104Q25 89 40 89H440L25 346Z" fill="url(#reflection)"/>
    <path d="M48 140H432M504 140H1124" stroke="{c["line"]}"/>''',
        text(48, 120, "VISUAL.MAP", "muted", 12, 'letter-spacing="1.6"'),
        text(432, 120, "LIFO", "faint", 11, 'text-anchor="end" letter-spacing="1"'),
        text(504, 120, "SYSTEM.INFO", "muted", 12, 'letter-spacing="1.6"'),
        text(1124, 120, "[ perfil ]", "faint", 11, 'text-anchor="end"'),
        '<g clip-path="url(#visual)" aria-hidden="true">',
        '<rect x="48" y="152" width="384" height="264" fill="url(#scanlines)"/>',
    ])

    # Fixed per-row textLength keeps the illustration centered across local fonts.
    for i, row in enumerate(stack_art()):
        parts.append(f'<text class="ascii entrance" x="67.5" y="{164 + i * 4.85:.2f}" '
                     'textLength="345" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
                     f'{escape(row)}{entrance(round(.10 + i * .009, 3), .45)}</text>')

    parts.extend([
        '''<rect class="motion" x="64" y="164" width="352" height="1" fill="url(#scan)" opacity="0">
        <animate attributeName="y" values="164;407" begin="1s" dur="8s" repeatCount="2"/>
        <animate attributeName="opacity" values="0;.22;.22;0" keyTimes="0;.15;.85;1" begin="1s" dur="8s" repeatCount="2"/>
      </rect>
    </g>''',
        text(244, 446, "STACK", "ink", 36,
             'text-anchor="middle" letter-spacing="8" font-weight="700"'),
        text(240, 473, p["tagline"], "muted", 15, 'text-anchor="middle"'),
        f'<rect x="48" y="492" width="384" height="36" rx="8" fill="{c["console"]}" fill-opacity="{c["console_opacity"]}" stroke="{c["line"]}"/>',
        text(64, 515, '~ $ stack.push("hello");', "accent", 13),
        f'''<rect class="motion" x="248" y="503" width="7" height="14" fill="{c["accent"]}" opacity="0" aria-hidden="true">
      <animate attributeName="opacity" values="1;0;1" keyTimes="0;.5;1" calcMode="discrete" dur="1s" repeatCount="4"/>
    </rect>''',
        text(504, 168, p["terminal"] + "$ ./profile.sh", "faint", 13),
        '<g class="entrance">' + entrance(.20),
        text(814, 220, p["name"], "ink", 44, 'text-anchor="middle" font-weight="700" letter-spacing="-1.5"'),
        '</g><g class="entrance">' + entrance(.30),
        text(814, 254, p["headline"], "accent", 20, 'text-anchor="middle"'),
        f'</g><path d="M504 278H1124" stroke="{c["line"]}"/>',
        '<g class="entrance">' + entrance(.40),
        text(748, 318, "FORMACIÓN", "muted", 12, 'text-anchor="end" letter-spacing=".5"'),
        text(772, 318, p["education"][0], "ink", 18),
        text(772, 344, p["education"][1], "ink", 18),
        '</g><g class="entrance">' + entrance(.50),
        text(748, 384, "UBICACIÓN", "muted", 12, 'text-anchor="end" letter-spacing=".5"'),
        text(772, 384, p["location"], "ink", 18),
        '</g><g class="entrance">' + entrance(.60),
        text(748, 426, "SISTEMA", "muted", 12, 'text-anchor="end" letter-spacing=".5"'),
        f'<rect x="772" y="404" width="152" height="32" rx="8" fill="{c["pill"]}" stroke="{c["pill_border"]}"/>',
        f'<circle cx="788" cy="420" r="3" fill="{c["green"]}" aria-hidden="true"/>',
        text(802, 426, p["system"], "accent", 15),
        '</g><g class="entrance">' + entrance(.70),
        f'<path d="M504 461H1124" stroke="{c["line"]}"/>',
        text(656, 493, "//", "secondary", 18, 'aria-hidden="true"'),
        text(688, 493, p["alias"][0], "muted", 17),
        text(688, 518, p["alias"][1], "muted", 17),
        '</g>',
        text(32, 585, "stack / profile", "faint", 11),
        text(1148, 585, "UTF-8", "faint", 11, 'text-anchor="end"'),
        '</g>',
        f'<rect x="1" y="1" width="1178" height="608" rx="24" stroke="{c["border"]}"/>',
        '</svg>\n',
    ])
    return "\n".join(parts)


if __name__ == "__main__":
    for theme in THEMES:
        target = ROOT / f"{theme}.svg"
        target.write_text(render(theme), encoding="utf-8")
        print(target.relative_to(ROOT))
