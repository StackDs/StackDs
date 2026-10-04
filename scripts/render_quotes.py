"""Render the Gambling Phrase terminal: random phrase generator cycling through quotes."""

from html import escape
from textwrap import wrap

CLOSING_MESSAGE = "Gobernar es Educar - Pedro Aguirre Cerda."


def render(profile, theme, mobile=False):
    width, left = (420, 24) if mobile else (880, 36)
    size, line_height = 13.5, 20
    test_advance = 14 * 0.602
    columns = min(78, int((width - 2 * left) / test_advance))

    quotes = profile.get("quotes", [])
    total_rounds = len(quotes) if quotes else 1
    round_sec = 6.0
    total_sec = total_rounds * round_sec

    # Shuffled order of indices for pseudo-random playback
    if len(quotes) >= 12:
        shuffle_order = [0, 4, 9, 1, 6, 3, 10, 5, 11, 7, 2, 8]
    else:
        shuffle_order = list(range(total_rounds))
    time_slots = {quote_idx: slot_idx for slot_idx, quote_idx in enumerate(shuffle_order)}

    css_keyframes = []
    rounds_svg = []

    cmd_text = "~ $ ./gambling_phrase"
    closing_text = f"~ $ {CLOSING_MESSAGE}"

    max_content_y = 180

    for r_idx, quote in enumerate(quotes):
        slot = time_slots.get(r_idx, r_idx)
        r_start_pct = round(slot * 100.0 / total_rounds, 2)
        r_end_pct = round((slot + 1) * 100.0 / total_rounds, 2)
        r_fade_out = round(r_end_pct - 0.4, 2)

        delta_p = 100.0 / total_rounds
        t_cmd_done = round(r_start_pct + delta_p * 0.18, 2)
        t_quote_in = round(r_start_pct + delta_p * 0.22, 2)
        t_close_p1 = round(r_start_pct + delta_p * 0.45, 2)
        t_close_p2 = round(r_start_pct + delta_p * 0.62, 2)
        t_close_done = round(r_start_pct + delta_p * 0.78, 2)

        css_keyframes.append(f'''
        @keyframes round-{r_idx} {{
          0%, {max(0, r_start_pct - 0.05):.2f}% {{ opacity: 0; visibility: hidden; }}
          {r_start_pct:.2f}%, {r_fade_out:.2f}% {{ opacity: 1; visibility: visible; }}
          {r_end_pct:.2f}%, 100% {{ opacity: 0; visibility: hidden; }}
        }}
        @keyframes quote-reveal-{r_idx} {{
          0%, {t_cmd_done:.2f}% {{ opacity: 0; transform: translateY(3px); }}
          {t_quote_in:.2f}%, 100% {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes close-s1-{r_idx} {{
          0%, {t_quote_in:.2f}% {{ opacity: 0; }}
          {t_close_p1:.2f}%, 100% {{ opacity: 1; }}
        }}
        @keyframes close-s2-{r_idx} {{
          0%, {t_close_p1:.2f}% {{ opacity: 0; }}
          {t_close_p2:.2f}%, 100% {{ opacity: 1; }}
        }}
        @keyframes close-s3-{r_idx} {{
          0%, {t_close_p2:.2f}% {{ opacity: 0; }}
          {t_close_done:.2f}%, 100% {{ opacity: 1; }}
        }}
        .gp-round-{r_idx} {{
          animation: round-{r_idx} {total_sec:.1f}s infinite;
        }}
        .gp-quote-{r_idx} {{
          animation: quote-reveal-{r_idx} {total_sec:.1f}s infinite;
        }}
        .gp-cs1-{r_idx} {{
          animation: close-s1-{r_idx} {total_sec:.1f}s infinite;
        }}
        .gp-cs2-{r_idx} {{
          animation: close-s2-{r_idx} {total_sec:.1f}s infinite;
        }}
        .gp-cs3-{r_idx} {{
          animation: close-s3-{r_idx} {total_sec:.1f}s infinite;
        }}
        ''')

        y = 75
        round_content = []

        # 1. Command
        round_content.append(
            f'<text class="terminal-cmd" x="{left}" y="{y}" fill="{theme["accent"]}" font-size="{size}" font-weight="bold">{escape(cmd_text)}</text>'
        )

        # 2. Quote lines inside an animated group with exact class="quote"
        y += 26
        q_lines = wrap(quote["text"], width=columns, break_long_words=True, break_on_hyphens=False)
        quote_elements = []
        for ql in q_lines:
            quote_elements.append(
                f'<text class="quote-line" x="{left}" y="{y}" fill="{theme["text"]}" font-size="{size}">{escape(ql)}</text>'
            )
            y += line_height

        author_text = f'— {quote["author"]}'
        a_lines = wrap(author_text, width=columns, break_long_words=True, break_on_hyphens=False)
        for al in a_lines:
            quote_elements.append(
                f'<text class="quote-author" x="{left}" y="{y}" fill="{theme["accent_light"]}" font-size="{size}">{escape(al)}</text>'
            )
            y += line_height

        round_content.append(f'<g class="gp-quote-{r_idx}"><g class="quote" id="quote-{r_idx + 1}">{"".join(quote_elements)}</g></g>')
        y += 6

        # Divider
        divider_y = y - 4
        round_content.append(
            f'<line x1="{left}" y1="{divider_y}" x2="{width - left}" y2="{divider_y}" stroke="{theme["border"]}" stroke-dasharray="2 2"/>'
        )

        # 3. Closing prompt
        y += 14
        prompt_id = ' id="closing-prompt"' if r_idx == 0 else f' id="closing-prompt-{r_idx + 1}"'
        c_lines = wrap(closing_text, width=columns, break_long_words=True, break_on_hyphens=False)
        if len(c_lines) == 1:
            p1 = "~ $ Gobernar "
            p2 = "es Educar "
            p3 = "- Pedro Aguirre Cerda."
            closing_svg = (
                f'<text class="closing-prompt"{prompt_id} x="{left}" y="{y}" font-size="{size}" xml:space="preserve">'
                f'<tspan fill="{theme["accent"]}" class="gp-cs1-{r_idx}">{escape(p1)}</tspan>'
                f'<tspan fill="{theme["text_secondary"]}" class="gp-cs2-{r_idx}">{escape(p2)}</tspan>'
                f'<tspan fill="{theme["text_secondary"]}" class="gp-cs3-{r_idx}">{escape(p3)}</tspan>'
                f'</text>'
            )
            round_content.append(closing_svg)
        else:
            closing_svgs = [f'<text class="closing-prompt"{prompt_id} x="{left}" y="{y}" font-size="{size}" xml:space="preserve">']
            for c_idx, cl in enumerate(c_lines):
                cur_y = y + c_idx * line_height
                cls_name = f"gp-cs{min(3, c_idx + 1)}-{r_idx}"
                fill_color = theme["accent"] if c_idx == 0 else theme["text_secondary"]
                space = " " if c_idx < len(c_lines) - 1 else ""
                closing_svgs.append(
                    f'<tspan class="{cls_name}" x="{left}" y="{cur_y}" fill="{fill_color}">{escape(cl + space)}</tspan>'
                )
            closing_svgs.append('</text>')
            round_content.append("".join(closing_svgs))
            y += (len(c_lines) - 1) * line_height

        max_content_y = max(max_content_y, y)

        rounds_svg.append(f'''
    <!-- Round {r_idx + 1}: {escape(quote["author"])} -->
    <g class="gp-round gp-round-{r_idx}" id="round-{r_idx + 1}">
      {' '.join(round_content)}
    </g>''')

    css_block = "\n".join(css_keyframes)
    rounds_block = "\n".join(rounds_svg)

    # Dynamic height if quotes require more space, else standard compact height
    default_height = 270 if mobile else 230
    height = max(default_height, max_content_y + 35)

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
    [data-motion="static"] #round-1 {{ opacity: 1 !important; }}
    [data-motion="static"] .gp-cs1-0, [data-motion="static"] .gp-cs2-0, [data-motion="static"] .gp-cs3-0, [data-motion="static"] .gp-quote-0 {{ opacity: 1 !important; transform: none !important; }}
    {css_block}
    @media (prefers-reduced-motion: reduce) {{
      .gp-round {{ opacity: 0 !important; animation: none !important; }}
      #round-1 {{ opacity: 1 !important; visibility: visible !important; }}
      .gp-cs1-0, .gp-cs2-0, .gp-cs3-0, .gp-quote-0 {{ opacity: 1 !important; animation: none !important; }}
    }}
  </style>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" fill="{theme['surface']}" stroke="{theme['accent']}"/>
  <!-- Window Header -->
  <path d="M1 38H{width - 1}" stroke="{theme['border']}"/>
  <circle cx="20" cy="19" r="4.5" fill="#EA2D2E"/>
  <circle cx="34" cy="19" r="4.5" fill="#E5C07B"/>
  <circle cx="48" cy="19" r="4.5" fill="#98C379"/>
  <text x="{width / 2:.1f}" y="24" fill="{theme['text_secondary']}" font-size="11" text-anchor="middle">stack@arch: ~/gambling_phrase</text>

  <!-- Animated Rounds -->
  {rounds_block}
</svg>
'''

