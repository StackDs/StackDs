#!/usr/bin/env python3
"""Regenerate self-contained profile banners from the images in assets/images."""

import argparse
import random
from html import escape
from math import ceil
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from profile_ascii import ART

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ASPECT_RATIO = 1.0  # Width / height of the supplied square reference.
BACKGROUND = "#0F1419"
ART_BACKGROUND = "#080E14"
TEXT_PRIMARY = "#ECEFF4"
TEXT_SECONDARY = "#D3C6AA"
ACCENT = "#088DDC"
COMMENT = "#5c6370"
PHOTO_COLOR = "#A5F3FC"
PHOTO_SHADOW = "#3FAFE0"
PHOTO_MID = "#7ED7F0"
ART_BACKGROUND_RGB = tuple(int(ART_BACKGROUND[i:i + 2], 16) for i in (1, 3, 5))
RULE = "#2B3A45"
DEFAULT_IMAGE = "bryan.jpeg"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DENSITY_RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_RAMP = DENSITY_RAMP[::-1]
PHOTO_TONES = (PHOTO_SHADOW, PHOTO_MID, PHOTO_COLOR)
PHOTO_GRID_SCALE = 1.25
ABOUT_ME_TEXT = "I'm a Computer Engineering student with a passion for teaching. I enjoy teaching math and computer science, always guided by the philosophy that the best way to learn is by teaching. I love programming, although with AI around, I don't do it as much anymore XD. I like designing systems and tools for various topics, and I'm obsessed with customization because I use Arch, btw. AFK, I'm a musician and play several instruments. I definitely have more hours logged in video games than touching grass. I also love playing basketball because you have to move your ass every once in a while, and I'm a bit of an alcoholic, but what engineer isn't?"
ABOUT_ME_WRAP = 40
ABOUT_ME_PADDING_RIGHT = 24
ABOUT_ME_LINE_HEIGHT = 20
QUOTES = (
"  • I'm the son of rage and love  - St. Jimmy",
"  • You can't get a hangover if you don't stop drinking - Lemmy Kilmister",
"  • Talk is cheap. Show me the code - Linus Torvalds",
"  • A wrong decision is better than indecision - Tony Soprano",
"  • Yeah, Mr. White! Yeah, science! - Jesse Pinkman",
"  • Wubba lubba dub dub! - Rick Sanchez",
"  • What's in the box? - Se7en",
"  • Cadia stands, and we shall not fall - Imperial Creed",
"  • War. War never changes. - Fallout",
"  • Forget about Freeman - Half-Life",
"  • The cake is a lie - Portal",
"  • Praise the sun! - Solaire of Astora",
"  • Would you kindly? - Atlas",
"  • How's your sister? - Cayde-6",
"  • In a world withouh gold, we might've been heroes - BlackBeard",
"  • SIC PARVIS MAGNA - Sir Francis Drake",
"  • Kept you waiting, huh? - Big Boss",
"  • It can't be for nothing  -Ellie"
)


def text(x, y, value, fill=TEXT_PRIMARY, size=15, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'{extra}>{escape(value)}</text>')


def seconds(milliseconds):
    return f"{milliseconds / 1000:.3f}s"


def discrete_animation(attribute, events, duration, repeat=False):
    """Use absolute timeline events, collapsing unchanged values."""
    changes = []
    for time, value in sorted(events):
        if not changes or changes[-1][1] != value:
            changes.append((time, value))
    if changes[0][0] != 0:
        changes.insert(0, (0, changes[0][1]))
    if changes[-1][0] != duration:
        changes.append((duration, changes[-1][1]))
    values = ";".join(f"{value:.3f}" for _, value in changes)
    times = ";".join(f"{time / duration:.8f}" for time, _ in changes)
    repeat_attribute = 'repeatCount="indefinite"' if repeat else ""
    return (f'<animate attributeName="{attribute}" values="{values}" '
            f'keyTimes="{times}" calcMode="discrete" begin="0s" '
            f'dur="{seconds(duration)}" fill="remove" '
            f'{repeat_attribute}/>')


def terminal_cursor(frames, erase_start, erase_end, duration):
    """One cursor follows the typing/deletion cycle and blinks in the pause."""
    start = min(frames)
    first = frames[start]
    parts = [f'<rect id="terminal-cursor" class="cursor motion" '
             f'x="{first[0]:.3f}" y="{first[1]:.3f}" '
             f'width="{first[2]:.3f}" height="{first[3]:.3f}" '
             f'fill="{ACCENT}" opacity="0" aria-hidden="true">']
    for i, attribute in enumerate(("x", "y", "width", "height")):
        parts.append(discrete_animation(
            attribute, [(time, frame[i]) for time, frame in frames.items()], duration,
            repeat=True))
    parts.append(discrete_animation("opacity", [
        (0, 0), (start, 1), (erase_start, 1), (erase_end, 0),
        (duration, 0),
    ], duration, repeat=True))
    parts.append("</rect>")
    return "\n".join(parts)


def choose_image(randomize=False):
    image_dir = ROOT / "assets" / "images"
    images = sorted(path for path in image_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise FileNotFoundError(f"No hay imágenes compatibles en {image_dir}")
    if randomize:
        return random.choice(images)
    default = image_dir / DEFAULT_IMAGE
    if not default.is_file():
        raise FileNotFoundError(f"No se encontró la imagen predeterminada: {default}")
    return default


def photo_grid_size():
    columns = round(max(map(len, ART)) * PHOTO_GRID_SCALE)
    rows = round(columns / REFERENCE_ASPECT_RATIO * .5)
    return columns, rows


def image_to_ascii(path, columns, rows):
    """Convert a photo into preserved-whitespace SVG text rows.

    The grid has twice as many columns as rows because terminal glyph cells are
    roughly half as wide as their line height; this keeps square portraits square.
    Transparent pixels remain spaces, so PNG alpha is preserved in the ASCII.
    """
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert("RGBA")
        source = ImageOps.fit(source, (720, 720), method=Image.Resampling.LANCZOS,
                              centering=(.5, .48))

        # Bryan's JPEG has a white field outside the circular illustration.
        # Remove edge-connected white only; keep white details inside the art.
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            for seed in ((0, 0), (719, 0), (0, 719), (719, 719)):
                ImageDraw.floodfill(source, seed, (*ART_BACKGROUND_RGB, 0), thresh=28)

        alpha = source.getchannel("A").resize(
            (columns, rows), Image.Resampling.LANCZOS)
        backdrop = Image.new("RGBA", source.size, (*ART_BACKGROUND_RGB, 255))
        grayscale = Image.alpha_composite(backdrop, source).convert("L")
        grayscale = grayscale.resize((columns, rows), Image.Resampling.LANCZOS)
        grayscale = ImageOps.autocontrast(grayscale, cutoff=1)
        grayscale = ImageEnhance.Contrast(grayscale).enhance(1.35)

        # Give the upper-center focal area a restrained local clarity boost.
        # The feathered oval covers facial features in both supplied portraits
        # without creating a visible boundary in the surrounding image.
        face_mask = Image.new("L", (720, 720), 0)
        ImageDraw.Draw(face_mask).ellipse(
            (int(.16 * 720), int(.08 * 720), int(.96 * 720), int(.76 * 720)),
            fill=255,
        )
        face_mask = face_mask.filter(ImageFilter.GaussianBlur(radius=48)).resize(
            (columns, rows), Image.Resampling.LANCZOS)
        face_detail = ImageEnhance.Contrast(grayscale).enhance(1.10)
        face_detail = face_detail.filter(ImageFilter.UnsharpMask(
            radius=.65, percent=190, threshold=1))
        grayscale = Image.composite(face_detail, grayscale, face_mask)
        grayscale = grayscale.filter(ImageFilter.UnsharpMask(
            radius=.8, percent=160, threshold=2))
        edges = ImageOps.invert(grayscale.filter(ImageFilter.FIND_EDGES))
        grayscale = Image.blend(grayscale, edges, .10)
        grayscale = ImageOps.autocontrast(grayscale, cutoff=1)

        art = []
        pixels = grayscale.load()
        alpha_pixels = alpha.load()
        for y in range(rows):
            tones = [[], [], []]
            for x in range(columns):
                if alpha_pixels[x, y] < 72:
                    for line in tones:
                        line.append(" ")
                    continue
                brightness = pixels[x, y]
                luminance = brightness / 255
                index = round((1 - luminance) * (len(ASCII_RAMP) - 1))
                character = ASCII_RAMP[index]
                tone = 0 if luminance < .28 else 1 if luminance < .68 else 2
                for layer, line in enumerate(tones):
                    line.append(character if layer == tone else " ")
            art.append(tuple("".join(line) for line in tones))
        return art


def render(mobile=False, art=None, image_name=""):
    art = art or ART
    photo_art = image_name != ""
    if not photo_art:
        art = [(line, " " * len(line), " " * len(line)) for line in art]
    columns = max(len(layer) for row in art for layer in row)
    width = 420 if mobile else 880
    left = 24 if mobile else 36
    command_y = 81
    art_width = width - 2 * left if mobile else 414
    art_padding = 8
    art_x = left + art_padding
    art_y = command_y + 27 + art_padding
    art_inner_width = art_width - 2 * art_padding
    cell_width = art_inner_width / columns
    art_size = cell_width / .602
    art_top = command_y + 27
    art_height = art_width / REFERENCE_ASPECT_RATIO
    art_inner_height = art_height - 2 * art_padding
    line_height = art_inner_height / len(art)
    art_bottom = ceil(art_top + art_height)
    quote_column_count = 1 if mobile else 2
    quote_column_gap = 14 if quote_column_count == 2 else 0
    quote_content_width = art_width - 2 * art_padding
    quote_column_width = (
        quote_content_width - quote_column_gap * (quote_column_count - 1)
    ) / quote_column_count
    quote_width = max(12, int(quote_column_width / (12 * .602)))
    quote_layout = []
    quote_column_y = [art_bottom + 20] * quote_column_count
    ordered_quotes = sorted(
        enumerate(QUOTES),
        key=lambda item: (len(item[1].strip().removeprefix("•").strip()), item[0]))
    for order_index, (quote_index, quote) in enumerate(ordered_quotes):
        column_index = order_index % quote_column_count
        quote_x = (left + art_padding
                   + column_index * (quote_column_width + quote_column_gap))
        quote_text = quote.strip().removeprefix("•").strip()
        quote_body, separator, quote_author = quote_text.rpartition(" -")
        if separator:
            quote_body = quote_body.rstrip()
            quote_attribution = f" - {quote_author.strip()}"
        else:
            quote_body = quote_text
            quote_attribution = ""
        quote_lines = wrap(quote_body, width=quote_width,
                           initial_indent="• ", subsequent_indent="  ",
                           break_long_words=True, break_on_hyphens=False) or ["• "]
        for line_index, line in enumerate(quote_lines):
            is_last_line = line_index == len(quote_lines) - 1
            attribution = quote_attribution if is_last_line else ""
            if attribution and len(line) + len(attribution) > quote_width:
                attribution = ""
            quote_layout.append((quote_index, line_index, quote_x,
                                 quote_column_y[column_index], line, attribution))
            quote_column_y[column_index] += 17
        if quote_attribution and not quote_layout[-1][-1]:
            quote_layout.append((quote_index, len(quote_lines), quote_x,
                                 quote_column_y[column_index], "",
                                 f"  - {quote_author.strip()}"))
            quote_column_y[column_index] += 17
        quote_column_y[column_index] += 4
    quote_bottom = max(quote_column_y) - 4
    info_x = left if mobile else 490
    info_y = quote_bottom + 40 if mobile else art_top + 33
    clock = 200
    cursor_frames = {}
    typed_segments = []

    def typed(identifier, x, y, value, fill=TEXT_PRIMARY, size=14,
              speed=17, pause=0, extra=""):
        """Reveal whole characters on one shared millisecond timeline.

        Each character is visible by default. SMIL hides it only until its
        reveal time, so unsupported animation and reduced motion remain useful.
        """
        nonlocal clock
        clock += pause
        advance = size * .602
        spans = []
        cursor_frames[clock] = (x + 1.5, y - size * .85, advance * .8, size + 2)
        for i, character in enumerate(value):
            reveal = clock + (i + 1) * speed
            cursor_frames[reveal] = (
                x + (i + 1) * advance + 1.5, y - size * .85, advance * .8, size + 2,
            )
            spans.append(
                f'<tspan class="typed-char" x="{x + i * advance:.3f}">'
                f'{escape(character)}__CHAR_ANIMATION_{len(typed_segments)}_{i}__</tspan>')
        typed_segments.append({
            "id": identifier, "value": value, "start": clock,
            "speed": speed, "advance": advance, "x": x, "y": y, "size": size,
        })
        clock += len(value) * speed
        return (f'<text id="{identifier}" class="typed" x="{x}" y="{y}" '
                f'fill="{fill}" font-size="{size}" xml:space="preserve" '
                f'{extra}>{"".join(spans)}</text>')

    command = typed("command", left, command_y, "~ $ fastfetch --Stack", ACCENT,
                    speed=20, extra='font-weight="bold"')
    clock += 200
    scan_start = clock
    quote_items = []
    for quote_index, line_index, x, y, line, attribution in quote_layout:
        if line:
            quote_items.append(typed(
                f"quote-{quote_index}-{line_index}", x, y, line,
                TEXT_PRIMARY, size=12, speed=13, pause=60,
            ))
        if attribution:
            attribution_x = x + len(line) * 12 * .602 if line else x
            quote_items.append(typed(
                f"quote-author-{quote_index}-{line_index}", attribution_x, y,
                attribution, COMMENT, size=12, speed=13,
                pause=0 if line else 60,
            ))
    profile_fields = [
        ("name", "Bryan Aguirre"),
        ("age", "21"),
        ("role", "Informatic Engineering Student"),
        ("school", "Udec (Unfortunately)"),
        ("loc", "Chile"),
        ("os", "Arch Linux"),
        ("contact", "stackctrlz@gmail.com"),
    ]
    info = [typed("profile-name", info_x, info_y, "Stack", ACCENT, size=21,
                  speed=21, extra='font-weight="bold"')]
    # One shared value_x gives the personal data a stable two-column grid.
    label_width = ceil(max(len(label) * 14 * .602 for label, _ in profile_fields) + 16)
    value_x = info_x + label_width
    right_edge = width - left
    value_chars = max(10, int((right_edge - value_x) / (14 * .602)))
    row_y = info_y + 33
    for label, value in profile_fields:
        value_lines = wrap(value, width=value_chars, break_long_words=True,
                           break_on_hyphens=False) or [""]
        info.append(typed(f"{label}-label", info_x, row_y, label,
                          TEXT_SECONDARY, pause=160))
        for line_index, line in enumerate(value_lines):
            info.append(typed(f"{label}-value-{line_index}", value_x,
                              row_y + line_index * 20, line))
        row_y += max(24, len(value_lines) * 20 + 4)

    about_title_y = row_y + 12
    info.append(typed("about-heading", info_x, about_title_y, "about me",
                      ACCENT, size=14, pause=260,
                      extra='font-weight="bold"'))
    about_width = min(
        ABOUT_ME_WRAP,
        max(12, int((right_edge - info_x - ABOUT_ME_PADDING_RIGHT) / (13 * .602))),
    )
    about_lines = wrap(ABOUT_ME_TEXT, width=about_width, break_long_words=True,
                       break_on_hyphens=False) or [""]
    about_start_y = about_title_y + 23
    for line_index, line in enumerate(about_lines):
        info.append(typed(f"about-text-{line_index}", info_x,
                           about_start_y + line_index * ABOUT_ME_LINE_HEIGHT, line,
                          TEXT_SECONDARY, size=13, speed=15,
                          pause=100 if line_index else 160,
                          extra='text-anchor="start"'))
    about_end_y = about_start_y + (len(about_lines) - 1) * ABOUT_ME_LINE_HEIGHT

    divider = max(art_bottom, about_end_y, quote_bottom) + 32
    parts_width = max(12, int((width - 2 * left) / (14 * .602)))
    command_lines = wrap('~ $ stack.push(" Wtf are you looking at? ");',
                         width=parts_width, break_long_words=True,
                         break_on_hyphens=False)
    prompt = []
    for line_index, line in enumerate(command_lines):
        prompt.append(typed(f"footer-command-{line_index}", left,
                            divider + 27 + line_index * 19, line,
                            ACCENT, pause=200 if line_index == 0 else 80,
                            extra='font-weight="bold"'))
    interests_lines = []
    for interest in ("O(log n)", "vibecoder (not really)"):
        interests_lines.extend(wrap(interest, width=parts_width,
                                    break_long_words=True,
                                    break_on_hyphens=False))
    interest_start = divider + 27 + len(command_lines) * 19 + 17
    interests = []
    for line_index, line in enumerate(interests_lines):
        interests.append(typed(f"interests-{line_index}", left,
                               interest_start + line_index * 19, line,
                               ACCENT,
                               speed=12, pause=140 if line_index == 0 else 80))
    height = interest_start + len(interests_lines) * 19 + 30

    type_end = clock
    erase_start = type_end + 4000
    erase_clock = erase_start
    erase_times = {}
    for segment_index in range(len(typed_segments) - 1, -1, -1):
        segment = typed_segments[segment_index]
        value = segment["value"]
        speed = segment["speed"]
        for char_index in range(len(value) - 1, -1, -1):
            erase_clock += speed
            erase_times[(segment_index, char_index)] = erase_clock
            cursor_frames[erase_clock] = (
                segment["x"] + char_index * segment["advance"] + 1.5,
                segment["y"] - segment["size"] * .85,
                segment["advance"] * .8, segment["size"] + 2,
            )
        erase_clock += 120
    erase_end = erase_clock
    cycle_duration = erase_end + 700
    scan_duration = 8000

    # Each glyph types in, holds, then erases in reverse order. All segments
    # share one repeat interval so the cursor and text restart in sync.
    animations = {}
    for segment_index, segment in enumerate(typed_segments):
        for char_index in range(len(segment["value"])):
            reveal_at = segment["start"] + (char_index + 1) * segment["speed"]
            erase_at = erase_times[(segment_index, char_index)]
            animations[f"__CHAR_ANIMATION_{segment_index}_{char_index}__"] = (
                f'<animate class="motion" attributeName="opacity" '
                f'values="0;1;0;0" keyTimes="0;{reveal_at / cycle_duration:.8f};'
                f'{erase_at / cycle_duration:.8f};1" calcMode="discrete" '
                f'begin="0s" dur="{seconds(cycle_duration)}" '
                'repeatCount="indefinite" fill="remove"/>')

    avatar_description = (
        f"avatar ASCII basado en {escape(image_name)}"
        if image_name else "avatar ASCII personalizado"
    )
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="es">
  <title id="title">Stack / Bryan — Arch Linux</title>
    <desc id="desc">Una terminal con {avatar_description}. Bryan, estudiante de Ingeniería Civil Informática en Chile. Last in, first out.</desc>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300&amp;400&amp;500&amp;600&amp;700&amp;display=swap');
    text {{ font-family: 'JetBrains Mono', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
      font-weight: 400; font-feature-settings: "calt" 1, "liga" 1;
      font-variant-ligatures: contextual; }}
    .ascii-shade {{ font-variant-ligatures: none; font-feature-settings: "calt" 0, "liga" 0; }}
    @media (prefers-reduced-motion: reduce) {{
      .typed-char {{ opacity: 1 !important; }}
      .tone-0 {{ fill: {PHOTO_SHADOW} !important; }}
      .tone-1 {{ fill: {PHOTO_MID} !important; }}
      .tone-2 {{ fill: {PHOTO_COLOR} !important; }}
      .motion {{ display: none; }}
    }}
  </style>
  <defs>
    <filter id="neon-glow" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="2.5"/>
    </filter>
  </defs>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="{BACKGROUND}" stroke="{ACCENT}"/>
  <path d="M1 45H{width - 1}" stroke="{RULE}"/>
  <g aria-hidden="true">
    <circle cx="25" cy="24" r="5" fill="{ACCENT}"/>
    <circle cx="43" cy="24" r="5" fill="{ACCENT}"/>
    <circle cx="61" cy="24" r="5" fill="{ACCENT}"/>
  </g>
''']
    parts.append(text(width / 2, 29, "stack@arch: ~", TEXT_SECONDARY, 12,
                      'text-anchor="middle"'))
    parts.append(command)

    parts.append('<g id="ascii-art" aria-hidden="true">')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="{ART_BACKGROUND}" fill-opacity=".48" stroke="{ACCENT}"/>')
    final_scan_y = art_y + (len(art) - 1) * line_height
    parts.append(f'''<rect class="scanline motion" x="{art_x}" y="{art_y}" width="{art_inner_width}" height="{line_height:.3f}" fill="{ACCENT}" opacity="0">
      <animate attributeName="y" values="{art_y};{art_y};{final_scan_y:.3f};{final_scan_y:.3f}" keyTimes="0;.02;.96;1" begin="{seconds(scan_start)}" dur="{seconds(scan_duration)}" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;.14;.14;0" keyTimes="0;.025;.96;1" begin="{seconds(scan_start)}" dur="{seconds(scan_duration)}" repeatCount="indefinite"/>
    </rect>''')
    for i, layers in enumerate(art):
        # Keep one cell width across every row, including spaces. Fitting each
        # row independently to the full width would distort the supplied art.
        highlight_start = .02 + i * .94 / len(art)
        highlight_end = highlight_start + .65 / len(art)
        highlight_trail = min(highlight_end + .01, .985)
        parts.append(f'<g class="ascii-row" data-row="{i}">')
        for tone, line in enumerate(layers):
            color = PHOTO_TONES[tone]
            parts.append(
                f'<text class="ascii-shade tone-{tone}" x="{art_x}" '
                f'y="{art_y + art_size + i * line_height:.3f}" '
                f'fill="{color}" font-size="{art_size:.3f}" xml:space="preserve" '
                f'textLength="{columns * cell_width:.3f}" lengthAdjust="spacingAndGlyphs">'
                f'{escape(line)}<animate class="motion" attributeName="fill" '
                f'values="{color};{color};{TEXT_PRIMARY};{ACCENT};{color}" '
                f'keyTimes="0;{highlight_start:.8f};{highlight_end:.8f};'
                f'{highlight_trail:.8f};1" '
                f'begin="{seconds(scan_start)}" dur="{seconds(scan_duration)}" '
                'repeatCount="indefinite"/></text>')
        parts.append('</g>')
    parts.append('</g>')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="none" stroke="{ACCENT}" stroke-width="4" opacity=".38" filter="url(#neon-glow)" class="motion"/>')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="none" stroke="{ACCENT}" stroke-width="1.5" class="motion"/>')

    parts.extend(quote_items)
    parts.extend(info)
    parts.append(f'<path d="M{left} {divider}H{width-left}" stroke="{RULE}"/>')
    parts.extend(prompt)
    parts.extend(interests)
    parts.append(terminal_cursor(cursor_frames, erase_start, erase_end, cycle_duration))
    if not mobile:
        parts.append(text(width-left, command_y, "I use Arch, btw.", ACCENT, 12,
                          'text-anchor="end"'))
    parts.append(f'<rect x="2.5" y="2.5" width="{width - 5}" height="{height - 5}" rx="10" fill="none" stroke="{ACCENT}" stroke-width="4" opacity=".28" filter="url(#neon-glow)" class="motion"/>')
    parts.append(f'<rect x="2.5" y="2.5" width="{width - 5}" height="{height - 5}" rx="10" fill="none" stroke="{ACCENT}" stroke-width="1.5" class="motion"/>')
    parts.append("</svg>\n")
    rendered = "\n".join(parts)
    for marker, animation in animations.items():
        rendered = rendered.replace(marker, animation)
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera el banner ASCII del perfil.")
    image_mode = parser.add_mutually_exclusive_group()
    image_mode.add_argument("--photo", action="store_true",
                            help="usa la fotografía predeterminada en lugar de ascii.txt")
    image_mode.add_argument("--random", action="store_true",
                            help="elige al azar una imagen de assets/images")
    args = parser.parse_args()

    (ROOT / "assets").mkdir(exist_ok=True)
    image_name = ""
    if args.photo or args.random:
        image = choose_image(randomize=args.random)
        columns, rows = photo_grid_size()
        art = image_to_ascii(image, columns, rows)
        image_name = image.name
        print(f"Imagen seleccionada: {image.relative_to(ROOT)}")
    else:
        avatar = ROOT / "ascii.txt"
        art = avatar.read_text(encoding="utf-8").splitlines()
        if not art or not any(art):
            raise ValueError(f"El avatar ASCII está vacío: {avatar}")
        print(f"Avatar seleccionado: {avatar.relative_to(ROOT)}")

    for filename, mobile in [("terminal.svg", False), ("terminal-mobile.svg", True)]:
        target = ROOT / "assets" / filename
        target.write_text(render(mobile, art=art, image_name=image_name), encoding="utf-8")
        print(target.relative_to(ROOT))
