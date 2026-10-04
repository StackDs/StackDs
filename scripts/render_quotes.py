"""Render the closing terminal: one command, sequential output, then a prompt."""

from html import escape
from textwrap import wrap

from render_terminal import seconds, terminal_cursor, text

CLOSING_MESSAGE = "Gobernar es Educar - Pedro Aguirre Cerda."


def reveal(at):
    """Hide only during playback; the base SVG always contains visible text."""
    return (f'<animate class="reveal" attributeName="opacity" values="0;1" '
            f'keyTimes="0;1" calcMode="discrete" begin="0s" '
            f'dur="{seconds(at)}" fill="remove"/>')


def render(profile, theme, mobile=False):
    width, left = (420, 24) if mobile else (880, 36)
    size, line_height = 14, 22
    advance = size * .602
    columns = min(80, int((width - 2 * left) / advance))
    clock, y = 200, 81
    frames, content = {}, []

    def cursor(x, baseline):
        frames[clock] = (x + 1.5, baseline - size * .85, advance * .8, size + 2)

    command = "~ $ cat hall-of-fame.txt"
    spans = []
    cursor(left, y)
    for i, character in enumerate(command):
        clock += 25
        spans.append(f'<tspan class="typed-char" x="{left + i * advance:.3f}">'
                     f'{escape(character)}{reveal(clock)}</tspan>')
        cursor(left + (i + 1) * advance, y)
    content.append(f'<text x="{left}" y="{y}" fill="{theme["accent"]}" '
                   f'font-size="{size}" font-weight="bold" xml:space="preserve">'
                   f'{"".join(spans)}</text>')
    y += 39
    clock += 200

    for index, quote in enumerate(profile["quotes"]):
        content.append(f'<g class="quote" id="quote-{index + 1}">')
        for value, color in ((quote["text"], theme["text"]),
                             ("— " + quote["author"], theme["accent_light"])):
            for line in wrap(value, width=columns, break_long_words=True,
                             break_on_hyphens=False):
                clock += 160
                content.append(
                    f'<text class="quote-line" x="{left}" y="{y}" '
                    f'font-size="{size}" fill="{color}">'
                    f'{escape(line)}{reveal(clock)}</text>')
                cursor(left + len(line) * advance, y)
                y += line_height
        content.append("</g>")
        y += 18
        clock += 120

    divider = y - 5
    y += 24
    prompt_y = y
    spans = []
    closing_lines = wrap("~ $ " + CLOSING_MESSAGE, width=columns - 1,
                         break_on_hyphens=False, drop_whitespace=False)
    for line_index, line in enumerate(closing_lines):
        if line_index:
            y += line_height
            clock += 80
        cursor(left, y)
        for i, character in enumerate(line):
            clock += 35
            spans.append(f'<tspan class="typed-char" x="{left + i * advance:.3f}" y="{y}">'
                         f'{escape(character)}{reveal(clock)}</tspan>')
            cursor(left + (i + 1) * advance, y)
    content.append(f'<text id="closing-prompt" x="{left}" y="{prompt_y}" font-size="{size}" '
                   f'fill="{theme["accent"]}" xml:space="preserve">{"".join(spans)}</text>')
    height = y + 32
    description = " ".join(f'{quote["text"]} — {quote["author"]}.'
                           for quote in profile["quotes"])
    description += " " + CLOSING_MESSAGE
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="en">
  <title id="title">Hall of Fame — intercepted transmissions</title>
  <desc id="desc">{escape(description)}</desc>
  <style>
    text {{ font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace; font-variant-ligatures: none; }}
    @media (prefers-reduced-motion: reduce) {{
      .typed-char, .quote-line {{ opacity: 1 !important; }}
      .motion {{ display: none; }}
    }}
  </style>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="{theme['surface']}" stroke="{theme['accent']}"/>
  <path d="M1 45H{width - 1}" stroke="{theme['border']}"/>
  <g fill="{theme['accent']}" aria-hidden="true">
    <circle cx="25" cy="24" r="5"/><circle cx="43" cy="24" r="5"/><circle cx="61" cy="24" r="5"/>
  </g>
  {text(width / 2, 29, 'stack@arch: ~/quotes', theme['text_secondary'], 12, extra='text-anchor="middle"')}
  <path d="M{left} {divider}H{width - left}" stroke="{theme['border']}"/>
  {''.join(content)}
  {terminal_cursor(frames, clock + 1, theme['accent'])}
</svg>
'''
