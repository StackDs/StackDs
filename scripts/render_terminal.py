#!/usr/bin/env python3
"""Render compact, self-contained profile banners from shared configuration."""

import argparse
import json
import random
from html import escape
from math import ceil
from pathlib import Path
from textwrap import wrap

from profile_ascii import ART
from profile_config import load_profile, load_theme
from svg_motion import static_svg

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ASPECT_RATIO = 1.0  # Width / height of the supplied square reference.
DEFAULT_IMAGE = "bryan.jpeg"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DENSITY_RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_RAMP = DENSITY_RAMP[::-1]
PHOTO_GRID_SCALE = 1.25
HOLD_MS = 4000
RESTART_PAUSE_MS = 700


def text(x, y, value, fill, size=15, extra=""):
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
    repeating = ' repeatCount="indefinite"' if repeat else ""
    return (f'<animate attributeName="{attribute}" values="{values}" '
            f'keyTimes="{times}" calcMode="discrete" begin="0s" '
            f'dur="{seconds(duration)}" fill="remove"{repeating}/>')


def terminal_cursor(frames, duration, accent, repeat=False, hide_at=None):
    """Follow the shared timeline; optionally hide after erasing and repeat."""
    start = min(frames)
    final = frames[max(frames)]
    parts = [f'<rect id="terminal-cursor" class="cursor motion" '
             f'x="{final[0]:.3f}" y="{final[1]:.3f}" '
             f'width="{final[2]:.3f}" height="{final[3]:.3f}" '
             f'fill="{accent}" opacity="{0 if repeat else 1}" aria-hidden="true">']
    for i, attribute in enumerate(("x", "y", "width", "height")):
        parts.append(discrete_animation(
            attribute, [(time, frame[i]) for time, frame in frames.items()], duration, repeat))
    visibility = [(0, 0), (start, 1)]
    if hide_at is not None:
        visibility.append((hide_at, 0))
    parts.append(discrete_animation("opacity", visibility, duration, repeat))
    parts.append("</rect>")
    return "\n".join(parts)


def choose_image(randomize=False):
    image_dir = ROOT / "assets" / "images"
    images = sorted(path for path in image_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise FileNotFoundError(f"No supported images in {image_dir}")
    if randomize:
        return random.choice(images)
    default = image_dir / DEFAULT_IMAGE
    if not default.is_file():
        raise FileNotFoundError(f"Default image not found: {default}")
    return default


def photo_grid_size():
    columns = round(max(map(len, ART)) * PHOTO_GRID_SCALE)
    rows = round(columns / REFERENCE_ASPECT_RATIO * .5)
    return columns, rows


def image_to_ascii(path, columns, rows, theme=None):
    """Convert a photo into preserved-whitespace SVG text rows.

    The grid has twice as many columns as rows because terminal glyph cells are
    roughly half as wide as their line height; this keeps square portraits square.
    Transparent pixels remain spaces, so PNG alpha is preserved in the ASCII.
    """
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

    background = (theme or load_theme())["background"]
    background_rgb = tuple(int(background[i:i + 2], 16) for i in (1, 3, 5))
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert("RGBA")
        source = ImageOps.fit(source, (720, 720), method=Image.Resampling.LANCZOS,
                              centering=(.5, .48))

        # Bryan's JPEG has a white field outside the circular illustration.
        # Remove edge-connected white only; keep white details inside the art.
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            for seed in ((0, 0), (719, 0), (0, 719), (719, 719)):
                ImageDraw.floodfill(source, seed, (*background_rgb, 0), thresh=28)

        alpha = source.getchannel("A").resize(
            (columns, rows), Image.Resampling.LANCZOS)
        backdrop = Image.new("RGBA", source.size, (*background_rgb, 255))
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


def render(mobile=False, art=None, image_name="", profile=None, theme=None):
    profile = profile if profile is not None else load_profile()
    theme = theme if theme is not None else load_theme()
    terminal = profile["terminal"]
    BACKGROUND = theme["surface"]
    ART_BACKGROUND = theme["background"]
    TEXT_PRIMARY = theme["text"]
    TEXT_SECONDARY = theme["text_secondary"]
    ACCENT = theme["accent"]
    RULE = theme["border"]
    PHOTO_SHADOW, PHOTO_MID, PHOTO_COLOR = (
        theme["photo_shadow"], theme["photo_mid"], theme["photo_light"])
    PHOTO_TONES = (PHOTO_SHADOW, PHOTO_MID, PHOTO_COLOR)
    if art is None:
        art = (ROOT / "ascii.txt").read_text(encoding="utf-8").splitlines()
    if not art or not any(art):
        raise ValueError("ASCII artwork must not be empty")
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
    info_x = left if mobile else 490
    info_y = art_bottom + 40 if mobile else art_top + 33
    clock = 200
    cursor_frames = {}
    typed_segments = []

    def typed(identifier, x, y, value, fill=TEXT_PRIMARY, size=14,
              speed=17, pause=0, extra=""):
        """Reveal whole characters on one shared millisecond timeline.

        Each character is visible by default. SMIL controls its visibility
        during playback, so unsupported animation and reduced motion remain useful.
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

    command = typed("command", left, command_y, terminal["command"], ACCENT,
                    speed=20, extra='font-weight="bold"')
    clock += 200
    scan_start = clock
    profile_fields = [(field["label"], field["value"]) for field in terminal["fields"]]
    info = [typed("profile-name", info_x, info_y, profile["display_name"], ACCENT, size=21,
                  speed=21, extra='font-weight="bold"')]
    # One shared value_x gives the personal data a stable two-column grid.
    label_width = ceil(max(len(label) * 14 * .602 for label, _ in profile_fields) + 16)
    value_x = info_x + label_width
    right_edge = width - left
    value_chars = max(10, int((right_edge - value_x) / (14 * .602)))
    row_y = info_y + 33
    for field_index, (label, value) in enumerate(profile_fields):
        value_lines = wrap(value, width=value_chars, break_long_words=True,
                           break_on_hyphens=False) or [""]
        info.append(typed(f"field-{field_index}-label", info_x, row_y, label,
                          TEXT_SECONDARY, pause=160))
        for line_index, line in enumerate(value_lines):
            info.append(typed(f"field-{field_index}-value-{line_index}", value_x,
                              row_y + line_index * 20, line))
        row_y += max(24, len(value_lines) * 20 + 4)

    divider = max(art_bottom, row_y) + 24
    parts_width = max(12, int((width - 2 * left) / (14 * .602)))
    prompt = []
    push_y = divider + 27
    for index, message in enumerate(terminal["push_messages"]):
        command_value = f'~ $ stack.push({json.dumps(message, ensure_ascii=False)});'
        command_lines = wrap(command_value, width=parts_width, break_long_words=True,
                             break_on_hyphens=False, drop_whitespace=False)
        prompt.append(f'<g class="push-command" id="push-command-{index}">')
        for line_index, line in enumerate(command_lines):
            prompt.append(typed(f"push-{index}-line-{line_index}", left, push_y, line,
                                ACCENT, pause=200 if line_index == 0 else 80,
                                extra='font-weight="bold"'))
            push_y += 19
        prompt.append('</g>')
        push_y += 10
    height = push_y + 20

    erase_clock = clock + HOLD_MS
    erase_times = {}
    for segment_index in reversed(range(len(typed_segments))):
        segment = typed_segments[segment_index]
        for char_index in reversed(range(len(segment["value"]))):
            erase_clock += segment["speed"]
            erase_times[segment_index, char_index] = erase_clock
            cursor_frames[erase_clock] = (
                segment["x"] + char_index * segment["advance"] + 1.5,
                segment["y"] - segment["size"] * .85,
                segment["advance"] * .8, segment["size"] + 2,
            )
        if segment_index:
            erase_clock += 120
    duration = erase_clock + RESTART_PAUSE_MS
    scan_duration = 8000

    # Every glyph shares one cycle: type, hold, erase in reverse, pause.
    # Base text stays visible in viewers without SMIL and in static variants.
    animations = {}
    for segment_index, segment in enumerate(typed_segments):
        for char_index in range(len(segment["value"])):
            reveal_at = segment["start"] + (char_index + 1) * segment["speed"]
            erase_at = erase_times[segment_index, char_index]
            animations[f"__CHAR_ANIMATION_{segment_index}_{char_index}__"] = (
                f'<animate class="typing-cycle" attributeName="opacity" '
                f'values="0;1;0;0" keyTimes="0;{reveal_at / duration:.8f};{erase_at / duration:.8f};1" '
                f'calcMode="discrete" begin="0s" dur="{seconds(duration)}" '
                'repeatCount="indefinite" fill="remove"/>')

    avatar_description = (
        f"an ASCII avatar based on {escape(image_name)}"
        if image_name else "a custom ASCII avatar"
    )
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="en">
  <title id="title">{escape(profile["title"])}</title>
    <desc id="desc">A terminal with {avatar_description}. {escape(profile["description"])}</desc>
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
    parts.append(text(width / 2, 29, terminal["title"], TEXT_SECONDARY, 12,
                      'text-anchor="middle"'))
    parts.append(command)

    parts.append('<g id="ascii-art" aria-hidden="true">')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="{ART_BACKGROUND}" fill-opacity=".48" stroke="{ACCENT}"/>')
    final_scan_y = art_y + (len(art) - 1) * line_height
    parts.append(f'''<rect class="scanline motion" x="{art_x}" y="{art_y}" width="{art_inner_width}" height="{line_height:.3f}" fill="{ACCENT}" opacity="0">
      <animate attributeName="y" values="{art_y};{art_y};{final_scan_y:.3f};{final_scan_y:.3f}" keyTimes="0;.02;.96;1" begin="{seconds(scan_start)}" dur="{seconds(scan_duration)}"/>
      <animate attributeName="opacity" values="0;.14;.14;0" keyTimes="0;.025;.96;1" begin="{seconds(scan_start)}" dur="{seconds(scan_duration)}"/>
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
                'fill="remove"/></text>')
        parts.append('</g>')
    parts.append('</g>')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="none" stroke="{ACCENT}" stroke-width="4" opacity=".38" filter="url(#neon-glow)" class="motion"/>')
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="none" stroke="{ACCENT}" stroke-width="1.5" class="motion"/>')

    parts.extend(info)
    parts.append(f'<path d="M{left} {divider}H{width-left}" stroke="{RULE}"/>')
    parts.extend(prompt)
    parts.append(terminal_cursor(cursor_frames, duration, ACCENT,
                                 repeat=True, hide_at=erase_clock))
    if not mobile:
        parts.append(text(width-left, command_y, terminal["aside"], ACCENT, 12,
                          'text-anchor="end"'))
    parts.append(f'<rect x="2.5" y="2.5" width="{width - 5}" height="{height - 5}" rx="10" fill="none" stroke="{ACCENT}" stroke-width="4" opacity=".28" filter="url(#neon-glow)" class="motion"/>')
    parts.append(f'<rect x="2.5" y="2.5" width="{width - 5}" height="{height - 5}" rx="10" fill="none" stroke="{ACCENT}" stroke-width="1.5" class="motion"/>')
    parts.append("</svg>\n")
    rendered = "\n".join(parts)
    for marker, animation in animations.items():
        rendered = rendered.replace(marker, animation)
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the profile's ASCII banners.")
    image_mode = parser.add_mutually_exclusive_group()
    image_mode.add_argument("--photo", action="store_true",
                             help="use the default photo instead of ascii.txt")
    image_mode.add_argument("--random", action="store_true",
                             help="choose a random image from assets/images")
    args = parser.parse_args()

    profile, theme = load_profile(), load_theme()
    image_name = ""
    if args.photo or args.random:
        image = choose_image(randomize=args.random)
        columns, rows = photo_grid_size()
        art = image_to_ascii(image, columns, rows, theme)
        image_name = image.name
        print(f"Selected image: {image.relative_to(ROOT)}")
    else:
        avatar = ROOT / "ascii.txt"
        art = avatar.read_text(encoding="utf-8").splitlines()
        if not art or not any(art):
            raise ValueError(f"ASCII avatar is empty: {avatar}")
        print(f"Selected avatar: {avatar.relative_to(ROOT)}")

    for filename, mobile in [("terminal.svg", False), ("terminal-mobile.svg", True)]:
        target = ROOT / "assets" / filename
        source = render(mobile, art=art, image_name=image_name, profile=profile, theme=theme)
        target.write_text(source, encoding="utf-8")
        static_target = target.with_name(target.stem + "-static.svg")
        static_target.write_text(static_svg(source), encoding="utf-8")
        print(target.relative_to(ROOT))
        print(static_target.relative_to(ROOT))
