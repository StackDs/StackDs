#!/usr/bin/env python3
"""Regenerate the self-contained terminal illustrations (standard library only)."""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = [
    r" ____  _____  _    ____ _  __",
    r"/ ___||_   _|/ \  / ___| |/ /",
    r"\___ \  | | / _ \| |   | ' / ",
    r" ___) | | |/ ___ \ |___| . \ ",
    r"|____/  |_/_/   \_\____|_|\_\ ",
]


def text(x, y, value, fill="#E6EDF3", size=15, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'{extra}>{escape(value)}</text>')


def render(mobile=False):
    width, height = (420, 560) if mobile else (880, 390)
    left = 24 if mobile else 36
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Stack / Bryan — Arch Linux</title>
  <desc id="desc">Una terminal con arte ASCII de Stack. Bryan, estudiante de Ingeniería Civil Informática en Chile. Last in, first out.</desc>
  <style>
    text {{ font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace; }}
    .reveal {{ animation: type 1.8s steps(32, end) .4s both; }}
    .cursor {{ animation: blink .8s step-end 5 forwards; }}
    @keyframes type {{ from {{ width: 0; }} to {{ width: {width - 48}px; }} }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .reveal {{ animation: none; }}
      .cursor {{ animation: none; opacity: 0; }}
    }}
  </style>
  <defs><clipPath id="typing"><rect class="reveal" x="{left}" y="0" width="{width - 48}" height="{height}"/></clipPath></defs>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="#161B2B" stroke="#3B445C"/>
  <path d="M1 45H{width - 1}" stroke="#3B445C"/>
  <circle cx="25" cy="24" r="5" fill="#E9BD78"/>
  <circle cx="43" cy="24" r="5" fill="#B6A4EA"/>
  <circle cx="61" cy="24" r="5" fill="#86DCE5"/>
''']
    parts.append(text(width / 2, 29, "stack@arch: ~", "#B7C2D9", 12,
                      'text-anchor="middle"'))
    parts.append(text(left, 81, "~ $ fastfetch --logo stack", "#86DCE5", 14))

    for i, line in enumerate(ART):
        parts.append(text(left, 126 + i * (21 if mobile else 25), line,
                          "#B6A4EA" if i < 3 else "#86DCE5",
                          17 if mobile else 22, 'xml:space="preserve"'))

    info_x, info_y = (left, 265) if mobile else (490, 126)
    parts.append(text(info_x, info_y, "Bryan / Stack", "#E6EDF3", 21,
                      'font-weight="bold"'))
    for i, (label, value) in enumerate([
        ("os", "Arch Linux"),
        ("role", "Estudiante de informática"),
        ("loc", "Chile"),
        ("alias", "La mejor estructura de datos"),
    ]):
        y = info_y + 33 + i * 24
        parts.append(text(info_x, y, label, "#E9BD78", 14))
        parts.append(text(info_x + 52, y, value, "#E6EDF3", 14))

    parts.append(text(left, 242 if not mobile else 422,
                      "Last in, first out.", "#B7C2D9", 13))
    divider = 281 if not mobile else 447
    parts.append(f'<path d="M{left} {divider}H{width-left}" stroke="#3B445C"/>')
    parts.append(text(left, divider + 33, '~ $ stack.push("hello, world");',
                      "#86DCE5", 14, 'clip-path="url(#typing)"'))
    parts.append(f'<rect class="cursor" x="{left + 263}" y="{divider + 21}" width="8" height="16" fill="#86DCE5"/>')
    parts.append(text(left, divider + 63,
                      "Código, música y demasiados videojuegos.", "#E6EDF3", 14))
    if not mobile:
        parts.append(text(width-left, 81, "I use Arch, btw.", "#E9BD78", 12,
                          'text-anchor="end"'))
    parts.append("</svg>\n")
    return "\n".join(parts)


if __name__ == "__main__":
    (ROOT / "assets").mkdir(exist_ok=True)
    for filename, mobile in [("terminal.svg", False), ("terminal-mobile.svg", True)]:
        target = ROOT / "assets" / filename
        target.write_text(render(mobile), encoding="utf-8")
        print(target.relative_to(ROOT))
