"""Render the Gambling Phrase terminal: random phrase generator cycling through quotes."""

import random
from html import escape
from textwrap import wrap

CLOSING_MESSAGE = "Gobernar es Educar - Pedro Aguirre Cerda."


def render(profile, theme, mobile=False):
    width, left = (420, 24) if mobile else (880, 36)
    size, line_height = 13.5, 20
    test_advance = 14 * 0.602
    advance = size * 0.602
    columns = min(78, int((width - 2 * left) / test_advance))

    quotes = profile.get("quotes", [])
    total_rounds = len(quotes) if quotes else 1
    round_sec = 6.0
    total_sec = total_rounds * round_sec

    # Deterministic pseudo-random shuffle so ANY number of quotes in profile.json is included.
    # Quote 0 stays in slot 0 to guarantee the static SVG fallback and first playback frame match.
    if total_rounds > 1:
        rng = random.Random(42)
        rest = list(range(1, total_rounds))
        rng.shuffle(rest)
        shuffle_order = [0] + rest
    else:
        shuffle_order = [0]
    time_slots = {quote_idx: slot_idx for slot_idx, quote_idx in enumerate(shuffle_order)}

    css_keyframes = []
    rounds_svg = []

    cmd_text = "~ $ ./gambling_phrase"
    cmd_y = 58 if mobile else 60
    quote_start_y = 80 if mobile else 85
    max_content_y = quote_start_y

    for r_idx, quote in enumerate(quotes):
        slot = time_slots.get(r_idx, r_idx)
        delta_p = 100.0 / total_rounds
        r_start_pct = round(slot * delta_p, 2)
        r_end_pct = round((slot + 1) * delta_p, 2)
        t_in = round(r_start_pct + delta_p * 0.08, 2)
        t_out = round(r_end_pct - delta_p * 0.08, 2)

        css_keyframes.append(f'''
        @keyframes round-{r_idx} {{
          0%, {max(0, r_start_pct - 0.05):.2f}% {{ opacity: 0; visibility: hidden; }}
          {t_in:.2f}%, {t_out:.2f}% {{ opacity: 1; visibility: visible; }}
          {r_end_pct:.2f}%, 100% {{ opacity: 0; visibility: hidden; }}
        }}
        .gp-round-{r_idx} {{
          animation: round-{r_idx} {total_sec:.1f}s infinite;
        }}
        ''')

        y = quote_start_y
        q_lines = wrap(quote["text"], width=columns, break_long_words=True, break_on_hyphens=False)
        quote_elements = []
        author_text = f'— {quote["author"]}'
        spacing = 3

        # Place author inline to the right if it fits on the last line of the quote
        inline_author = bool(q_lines and (len(q_lines[-1]) + spacing + len(author_text) <= columns))

        for idx, ql in enumerate(q_lines):
            quote_elements.append(
                f'<text class="quote-line" x="{left}" y="{y}" fill="{theme["text"]}" font-size="{size}">{escape(ql)}</text>'
            )
            if idx == len(q_lines) - 1 and inline_author:
                author_x = round(left + (len(ql) + spacing) * advance, 2)
                quote_elements.append(
                    f'<text class="quote-author" x="{author_x}" y="{y}" fill="{theme["accent_light"]}" font-size="{size}">{escape(author_text)}</text>'
                )
            y += line_height

        if not inline_author:
            a_lines = wrap(author_text, width=columns, break_long_words=True, break_on_hyphens=False)
            for al in a_lines:
                quote_elements.append(
                    f'<text class="quote-author" x="{left}" y="{y}" fill="{theme["accent_light"]}" font-size="{size}">{escape(al)}</text>'
                )
                y += line_height

        max_content_y = max(max_content_y, y - line_height)

        rounds_svg.append(f'''
    <!-- Round {r_idx + 1}: {escape(quote["author"])} -->
    <g class="gp-round gp-round-{r_idx}" id="round-{r_idx + 1}">
      <g class="quote" id="quote-{r_idx + 1}">
        {"".join(quote_elements)}
      </g>
    </g>''')

    css_block = "\n".join(css_keyframes)
    rounds_block = "\n".join(rounds_svg)

    # Calculate layout offsets and compact height
    std_divider_y = 120 if mobile else 107
    divider_y = max(std_divider_y, max_content_y + 16)
    closing_y = divider_y + 20

    if mobile:
        closing_svg = (
            f'<text id="closing-prompt" class="closing-prompt" font-size="{size}" xml:space="preserve">'
            f'<tspan fill="{theme["accent"]}" x="{left}" y="{closing_y}">~ $ echo </tspan>'
            f'<tspan fill="{theme["text"]}">&quot;Gobernar es Educar </tspan>'
            f'<tspan fill="{theme["text"]}" x="{left + 24}" y="{closing_y + line_height}">- Pedro Aguirre Cerda.&quot;</tspan>'
            f'<tspan class="gp-cursor" fill="{theme["accent"]}"> ▋</tspan>'
            f'</text>'
        )
        height = max(186, closing_y + line_height + 22)
    else:
        closing_svg = (
            f'<text id="closing-prompt" class="closing-prompt" x="{left}" y="{closing_y}" font-size="{size}" xml:space="preserve">'
            f'<tspan fill="{theme["accent"]}">~ $ echo </tspan>'
            f'<tspan fill="{theme["text"]}">&quot;Gobernar es Educar - Pedro Aguirre Cerda.&quot;</tspan>'
            f'<tspan class="gp-cursor" fill="{theme["accent"]}"> ▋</tspan>'
            f'</text>'
        )
        height = max(152, closing_y + 22)

    description = " ".join(f'{quote["text"]} — {quote["author"]}.' for quote in profile["quotes"])
    description += " " + CLOSING_MESSAGE

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="en">
  <title id="title">Gambling Phrase — intercepted transmissions</title>
  <desc id="desc">{escape(description)}</desc>
  <style>
    text {{ font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace; font-variant-ligatures: none; }}
    .gp-round {{ opacity: 0; }}
    #round-1 {{ opacity: 1; }}
    [data-motion="static"] .gp-round {{ opacity: 0 !important; }}
    [data-motion="static"] #round-1 {{ opacity: 1 !important; visibility: visible !important; }}
    [data-motion="static"] .gp-cursor {{ opacity: 1 !important; }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    .gp-cursor {{
      animation: blink 1.2s step-start infinite;
    }}
    {css_block}
    @media (prefers-reduced-motion: reduce) {{
      .gp-round {{ opacity: 0 !important; animation: none !important; }}
      #round-1 {{ opacity: 1 !important; visibility: visible !important; }}
      .gp-cursor {{ opacity: 1 !important; animation: none !important; }}
    }}
  </style>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" fill="{theme['surface']}" stroke="{theme['accent']}"/>
  <!-- Window Header -->
  <path d="M1 38H{width - 1}" stroke="{theme['border']}"/>
  <circle cx="20" cy="19" r="4.5" fill="#EA2D2E"/>
  <circle cx="34" cy="19" r="4.5" fill="#E5C07B"/>
  <circle cx="48" cy="19" r="4.5" fill="#98C379"/>
  <text x="{width / 2:.1f}" y="24" fill="{theme['text_secondary']}" font-size="11" text-anchor="middle">stack@arch: ~/gambling_phrase</text>

  <!-- Fixed Top Command -->
  <text class="terminal-cmd" x="{left}" y="{cmd_y}" fill="{theme['accent']}" font-size="{size}" font-weight="bold">{escape(cmd_text)}</text>

  <!-- Animated Quote Rounds (Only phrases vary) -->
  {rounds_block}

  <!-- Fixed Divider -->
  <line x1="{left}" y1="{divider_y}" x2="{width - left}" y2="{divider_y}" stroke="{theme['border']}" stroke-dasharray="2 2"/>

  <!-- Fixed Bottom Prompt with echo -->
  {closing_svg}
</svg>
'''

