#!/usr/bin/env python3
"""Regenerate self-contained profile banners from the images in assets/images."""

import argparse
import random
from html import escape
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from profile_ascii import ART

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ASPECT_RATIO = 1.0  # Width / height of the supplied square reference.
BACKGROUND = "#0F1419"
ART_BACKGROUND = "#080E14"
TEXT_PRIMARY = "#ECEFF4"
TEXT_SECONDARY = "#D3C6AA"
ACCENT = "#1793D1"
ACCENT_SECONDARY = "#088DDC"
ACCENT_LIGHT = "#6BC5ED"
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
    art_width = width - 2 * left if mobile else 414
    art_padding = 8
    art_x = left + art_padding
    art_y = 108 + art_padding
    art_inner_width = art_width - 2 * art_padding
    cell_width = art_inner_width / columns
    art_size = cell_width / .602
    art_top = 108
    art_height = art_width / REFERENCE_ASPECT_RATIO
    art_inner_height = art_height - 2 * art_padding
    line_height = art_inner_height / len(art)
    art_bottom = ceil(art_top + art_height)
    info_x = left if mobile else 490
    info_y = art_bottom + 40 if mobile else round((art_top + art_bottom) / 2 - 54)
    tagline_y = info_y + 157 if mobile else art_bottom + 24
    divider = tagline_y + 25
    height = divider + 96
    clock = 200
    cursor_frames = {}
    typed_segments = []

    def typed(identifier, x, y, value, fill=TEXT_PRIMARY, size=14,
              speed=34, pause=0, extra=""):
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

    command = typed("command", left, 81, "~ $ fastfetch --Stack", ACCENT, speed=40)
    clock += 200
    scan_start = clock
    info = [typed("profile-name", info_x, info_y, "Stack", size=21,
                  speed=42, extra='font-weight="bold"')]
    for i, (label, value) in enumerate([
        ("os", "Arch Linux"),
        ("role", "Estudiante de informática"),
        ("loc", "Chile"),
    ]):
        y = info_y + 33 + i * 24
        info.append(typed(f"{label}-label", info_x, y, label, TEXT_SECONDARY, pause=160))
        info.append(typed(f"{label}-value", info_x + 52, y, value))
    tagline = typed("tagline", left, tagline_y, "• I'm the son of rage and love  - St. Jimmy", TEXT_SECONDARY,
                    size=13, speed=28, pause=420)
    prompt = typed("footer-command", left, divider + 33,
                   '~ $ stack.push(" Wtf are you looking at? ");', ACCENT, pause=200)
    interests = typed("interests", left, divider + 63,
                      "No sé teoría músical :(", speed=24, pause=140)

    type_end = clock
    erase_start = type_end + 1000
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

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="es">
  <title id="title">Stack / Bryan — Arch Linux</title>
    <desc id="desc">Una terminal con una fotografía convertida a arte ASCII desde {escape(image_name or "el perfil")}. Bryan, estudiante de Ingeniería Civil Informática en Chile. Last in, first out.</desc>
  <style>
    text {{ font-family: 'JetBrains Mono', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
      font-feature-settings: "calt" 1, "liga" 1; font-variant-ligatures: contextual; }}
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
    <linearGradient id="card-neon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{ACCENT}"/>
      <stop offset=".42" stop-color="{ACCENT_SECONDARY}"/>
      <stop offset=".7" stop-color="{ACCENT_LIGHT}"/>
      <stop offset="1" stop-color="{ACCENT}"/>
      <animateTransform attributeName="gradientTransform" type="rotate"
        from="0 .5 .5" to="360 .5 .5" dur="7s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="art-neon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{ACCENT_SECONDARY}"/>
      <stop offset=".45" stop-color="{ACCENT}"/>
      <stop offset=".75" stop-color="{ACCENT_LIGHT}"/>
      <stop offset="1" stop-color="{ACCENT_SECONDARY}"/>
      <animateTransform attributeName="gradientTransform" type="rotate"
        from="0 .5 .5" to="360 .5 .5" dur="5s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="neon-glow" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="2.5"/>
    </filter>
  </defs>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="{BACKGROUND}" stroke="{RULE}"/>
  <path d="M1 45H{width - 1}" stroke="{RULE}"/>
  <g aria-hidden="true">
    <circle cx="25" cy="24" r="5" fill="{ACCENT}"/>
    <circle cx="43" cy="24" r="5" fill="{ACCENT_SECONDARY}"/>
    <circle cx="61" cy="24" r="5" fill="{ACCENT_LIGHT}"/>
  </g>
''']
    parts.append(text(width / 2, 29, "stack@arch: ~", TEXT_SECONDARY, 12,
                      'text-anchor="middle"'))
    parts.append(command)

    parts.append('<g id="ascii-art" aria-hidden="true">')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="{ART_BACKGROUND}" fill-opacity=".48" stroke="{RULE}"/>')
    final_scan_y = art_y + (len(art) - 1) * line_height
    parts.append(f'''<rect class="scanline motion" x="{art_x}" y="{art_y}" width="{art_inner_width}" height="{line_height:.3f}" fill="{ACCENT_SECONDARY}" opacity="0">
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
                f'values="{color};{color};{TEXT_PRIMARY};{ACCENT_SECONDARY};{color}" '
                f'keyTimes="0;{highlight_start:.8f};{highlight_end:.8f};'
                f'{highlight_trail:.8f};1" '
                f'begin="{seconds(scan_start)}" dur="{seconds(scan_duration)}" '
                'repeatCount="indefinite"/></text>')
        parts.append('</g>')
    parts.append('</g>')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="none" stroke="url(#art-neon)" stroke-width="4" opacity=".38" filter="url(#neon-glow)" class="motion"/>')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="none" stroke="url(#art-neon)" stroke-width="1.5" class="motion"/>')

    parts.extend(info)
    parts.append(tagline)
    parts.append(f'<path d="M{left} {divider}H{width-left}" stroke="{RULE}"/>')
    parts.extend([prompt, interests,
                  terminal_cursor(cursor_frames, erase_start, erase_end, cycle_duration)])
    if not mobile:
        parts.append(text(width-left, 81, "I use Arch, btw.", ACCENT, 12,
                          'text-anchor="end"'))
    parts.append(f'<rect x="2.5" y="2.5" width="{width - 5}" height="{height - 5}" rx="10" fill="none" stroke="url(#card-neon)" stroke-width="4" opacity=".28" filter="url(#neon-glow)" class="motion"/>')
    parts.append(f'<rect x="2.5" y="2.5" width="{width - 5}" height="{height - 5}" rx="10" fill="none" stroke="url(#card-neon)" stroke-width="1.5" class="motion"/>')
    parts.append("</svg>\n")
    rendered = "\n".join(parts)
    for marker, animation in animations.items():
        rendered = rendered.replace(marker, animation)
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera el banner ASCII del perfil.")
    parser.add_argument("--random", action="store_true",
                        help="elige al azar una imagen de assets/images (por defecto: bryan.jpeg)")
    args = parser.parse_args()

    (ROOT / "assets").mkdir(exist_ok=True)
    image = choose_image(randomize=args.random)
    columns, rows = photo_grid_size()
    art = image_to_ascii(image, columns, rows)
    print(f"Imagen seleccionada: {image.relative_to(ROOT)}")
    for filename, mobile in [("terminal.svg", False), ("terminal-mobile.svg", True)]:
        target = ROOT / "assets" / filename
        target.write_text(render(mobile, art=art, image_name=image.name), encoding="utf-8")
        print(target.relative_to(ROOT))
