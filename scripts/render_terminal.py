#!/usr/bin/env python3
"""Render compact, self-contained profile banners from shared configuration."""

import argparse
import json
import random
from html import escape
from math import ceil
from pathlib import Path
from textwrap import wrap

from profile_config import load_profile, load_theme
from svg_motion import static_svg

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ASPECT_RATIO = 1.0  # Width / height of the supplied square reference.
DEFAULT_IMAGE = "Final.jpeg"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DENSITY_RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_RAMP = DENSITY_RAMP[::-1]
PHOTO_GRID_COLUMNS = 320
PHOTO_CELL_ASPECT = .5  # Cell width / line height; square art needs half as many rows.
PHOTO_COOL_TONES = 5
PHOTO_SKIN_TONES = 3
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
    return PHOTO_GRID_COLUMNS, round(
        PHOTO_GRID_COLUMNS / REFERENCE_ASPECT_RATIO * PHOTO_CELL_ASPECT)


_IMAGE_CACHE = {}


def get_avatar_image(root=None):
    """Load and base64-encode the original avatar image from assets/images.
    Crops the outer black border frame if PIL is available, and resizes for crisp rendering.
    Falls back to reading raw image bytes without any third-party dependencies.
    """
    base_root = Path(root) if root is not None else ROOT
    key = str(base_root)
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]

    target = base_root / "assets" / "images" / DEFAULT_IMAGE
    if not target.is_file():
        target = ROOT / "assets" / "images" / DEFAULT_IMAGE
    if not target.is_file():
        for candidate in ("Final.jpeg", "bryan.jpeg"):
            t = base_root / "assets" / "images" / candidate
            if t.is_file():
                target = t
                break
            t = ROOT / "assets" / "images" / candidate
            if t.is_file():
                target = t
                break
    if not target.is_file():
        return None

    import base64
    try:
        from PIL import Image
        import io
        with Image.open(target) as im:
            sw, sh = im.size
            spix = im.load()
            if sum(spix[0, 0][:3]) < 30 and sum(spix[sw - 1, sh - 1][:3]) < 30:
                x_in, y_in = 0, 0
                while x_in < sw // 8 and sum(spix[x_in, sh // 2][:3]) < 30:
                    x_in += 1
                while y_in < sh // 8 and sum(spix[sw // 2, y_in][:3]) < 30:
                    y_in += 1
                x_out, y_out = sw - 1, sh - 1
                while x_out > 7 * sw // 8 and sum(spix[x_out, sh // 2][:3]) < 30:
                    x_out -= 1
                while y_out > 7 * sh // 8 and sum(spix[sw // 2, y_out][:3]) < 30:
                    y_out -= 1
                if x_out > x_in and y_out > y_in:
                    im = im.crop((x_in + 2, y_in + 2, x_out - 1, y_out - 1))
            im = im.resize((800, 800), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=88, optimize=True)
            result = base64.b64encode(buf.getvalue()).decode("ascii")
            _IMAGE_CACHE[key] = result
            return result
    except ImportError:
        result = base64.b64encode(target.read_bytes()).decode("ascii")
        _IMAGE_CACHE[key] = result
        return result


def image_to_ascii(path, columns, rows, theme=None):
    """Map luminance to glyph density, with separate general and skin palettes.

    Contain the complete composition, rather than cropping the hands or instrument.
    The renderer uses a 1:2 cell grid so the original proportions are preserved.
    """
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert("RGBA")
        # Crop outer black border frame if present (e.g. Final.jpeg)
        sw, sh = source.size
        spix = source.load()
        if sum(spix[0, 0][:3]) < 30 and sum(spix[sw - 1, sh - 1][:3]) < 30:
            x_in, y_in = 0, 0
            while x_in < sw // 8 and sum(spix[x_in, sh // 2][:3]) < 30:
                x_in += 1
            while y_in < sh // 8 and sum(spix[sw // 2, y_in][:3]) < 30:
                y_in += 1
            x_out, y_out = sw - 1, sh - 1
            while x_out > 7 * sw // 8 and sum(spix[x_out, sh // 2][:3]) < 30:
                x_out -= 1
            while y_out > 7 * sh // 8 and sum(spix[sw // 2, y_out][:3]) < 30:
                y_out -= 1
            if x_out > x_in and y_out > y_in:
                source = source.crop((x_in + 2, y_in + 2, x_out - 1, y_out - 1))

        working_size = 1280
        contained = ImageOps.contain(source, (working_size, working_size),
                                     method=Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (working_size, working_size), (0, 0, 0, 0))
        canvas.alpha_composite(
            contained,
            ((working_size - contained.width) // 2,
             (working_size - contained.height) // 2),
        )
        source = canvas

        # Keep the original luminance before making the backdrop transparent.
        grayscale = source.convert("RGB").convert(
            "L", (.2126, .7152, .0722, 0))
        # The backdrop darkens toward the bottom: sample exposed side edges too,
        # rather than leaving gradient bands behind after a top-corner flood.
        # Avoid the headstock at the left edge and the sleeve at the bottom right.
        last = working_size - 1
        seeds = [(0, 0), (last, 0)]
        seeds.extend((0, y) for y in range(working_size // 2, working_size, 16))
        seeds.extend((last, y) for y in range(0, working_size * 3 // 5, 16))
        for seed in seeds:
            red, green, blue, opacity = source.getpixel(seed)
            if opacity and blue - red > 12 and green - red > 3 and blue - green > 5:
                ImageDraw.floodfill(source, seed, (0, 0, 0, 0), thresh=42)

        sample_size = (columns, rows)
        rgb_pixels = source.convert("RGB").resize(
            sample_size, Image.Resampling.LANCZOS).load()
        alpha = source.getchannel("A")
        if Path(path).name == DEFAULT_IMAGE:
            # Keep only the connected portrait (face, body, hands and bass).
            # JPEG texture can otherwise leave detached blue specks in the sky.
            silhouette = alpha.point(lambda value: 255 if value >= 128 else 0)
            face_seed = (round(working_size * .53), round(working_size * .39))
            ImageDraw.floodfill(silhouette, face_seed, 128, thresh=0)
            alpha = silhouette.point(lambda value: 255 if value == 128 else 0)
        alpha = alpha.resize(sample_size, Image.Resampling.LANCZOS)
        grayscale = ImageOps.autocontrast(grayscale, cutoff=.5)
        # Lift hoodie/hair detail without clipping the face into a solid white mass.
        grayscale = grayscale.point([round(255 * (i / 255) ** .8) for i in range(256)])
        grayscale = grayscale.resize(sample_size, Image.Resampling.LANCZOS)
        grayscale = grayscale.filter(ImageFilter.UnsharpMask(
            radius=.65, percent=140, threshold=2))
        # Resolve eyes, glasses, nose and lips locally, without sharpening the
        # background or flattening the skin's midtones across the whole portrait.
        # Keep the mask centered on facial features to prevent harsh jawline shadows.
        face_mask = Image.new("L", sample_size, 0)
        ImageDraw.Draw(face_mask).ellipse(
            (columns * .38, rows * .23, columns * .68, rows * .48), fill=255)
        face_mask = face_mask.filter(ImageFilter.GaussianBlur(radius=rows * .02))
        face_detail = ImageEnhance.Contrast(grayscale).enhance(1.08)
        face_detail = face_detail.filter(ImageFilter.UnsharpMask(
            radius=.75, percent=130, threshold=2))
        grayscale = Image.composite(face_detail, grayscale, face_mask)
        gray_pixels = grayscale.load()
        alpha_pixels = alpha.load()
        is_default_portrait = Path(path).name == DEFAULT_IMAGE
        art = []
        for y in range(rows):
            layers = [[] for _ in range(PHOTO_COOL_TONES + PHOTO_SKIN_TONES)]
            for x in range(columns):
                luminance = gray_pixels[x, y] / 255
                tone = -1
                if alpha_pixels[x, y] >= 128:
                    red, green, blue = rgb_pixels[x, y]
                    # Use the illustration's peach/red chroma, not brightness:
                    # white eyes/logo and blue instrument must stay cool.
                    skin = (red >= 105 and red - green >= 22
                            and red - blue >= 32 and green >= blue - 12)
                    if skin:
                        eff_lum = luminance
                        # Soften the harsh neck/jawline shadow from cheek to chin
                        if is_default_portrait and int(rows * .45) <= y <= int(rows * .57) and int(columns * .50) <= x <= int(columns * .65):
                            if 0.35 < eff_lum < 0.88:
                                eff_lum = min(0.95, eff_lum + 0.30)
                            elif 0.05 < eff_lum <= 0.35:
                                eff_lum = 0.50
                        character = DENSITY_RAMP[round(eff_lum * (len(DENSITY_RAMP) - 1))]
                        tone = PHOTO_COOL_TONES + (0 if eff_lum < .55
                                                   else 1 if eff_lum < .80 else 2)
                    else:
                        character = DENSITY_RAMP[round(luminance * (len(DENSITY_RAMP) - 1))]
                        tone = min(int(luminance * PHOTO_COOL_TONES), PHOTO_COOL_TONES - 1)
                else:
                    character = DENSITY_RAMP[round(luminance * (len(DENSITY_RAMP) - 1))]
                for index, layer in enumerate(layers):
                    layer.append(character if index == tone else " ")
            art.append(tuple("".join(layer) for layer in layers))
        return art


def render(mobile=False, art=None, image_name="", profile=None, theme=None, root=None, use_image=True):
    profile = profile if profile is not None else load_profile()
    theme = theme if theme is not None else load_theme()
    terminal = profile["terminal"]
    BACKGROUND = theme["surface"]
    ART_BACKGROUND = "#000000"
    TEXT_PRIMARY = theme["text"]
    TEXT_SECONDARY = theme["text_secondary"]
    ACCENT = theme["accent"]
    RULE = theme["border"]
    PHOTO_SHADOW, PHOTO_MID, PHOTO_COLOR = (
        theme["photo_shadow"], theme["photo_mid"], theme["photo_light"])
    PHOTO_DEEP = theme.get("photo_deep", "#2276A0")
    PHOTO_WHITE = theme.get("photo_white", "#FFFFFF")
    PHOTO_TONES = (PHOTO_DEEP, PHOTO_SHADOW, PHOTO_MID, PHOTO_COLOR, PHOTO_WHITE,
                   theme["photo_skin_shadow"], theme["photo_skin_mid"], theme["photo_skin_light"])

    image_b64 = None
    if use_image:
        image_b64 = get_avatar_image(root)

    if not image_b64:
        if art is None:
            art = (ROOT / "ascii.txt").read_text(encoding="utf-8").splitlines()
        if not art or not any(art):
            raise ValueError("ASCII artwork must not be empty")
        _NUM_TONES = len(PHOTO_TONES)
        _ramp_len = len(DENSITY_RAMP)
        _band = max(_ramp_len // PHOTO_COOL_TONES, 1)
        _CHAR_TONE = {}
        for _idx, _ch in enumerate(ASCII_RAMP):
            _CHAR_TONE[_ch] = min(_idx // _band, PHOTO_COOL_TONES - 1)
        parsed_art = []
        for row in art:
            if isinstance(row, (tuple, list)) and len(row) in (PHOTO_COOL_TONES, len(PHOTO_TONES)):
                parsed_art.append(tuple(row) + (" " * len(row[0]),) * (_NUM_TONES - len(row)))
            else:
                layers = [[] for _ in range(_NUM_TONES)]
                for ch in row:
                    tone = _CHAR_TONE.get(ch, -1)
                    if tone < 0:
                        for layer in layers:
                            layer.append(" ")
                    else:
                        for t, layer in enumerate(layers):
                            layer.append(ch if t == tone else " ")
                parsed_art.append(tuple("".join(layer) for layer in layers))
        art = parsed_art
        columns = max(len(layer) for row in art for layer in row)

    width = 420 if mobile else 880
    left = 24 if mobile else 36
    command_y = 81
    art_width = width - 2 * left if mobile else 414
    art_padding = 8
    art_x = left + art_padding
    art_y = command_y + 27 + art_padding
    art_inner_width = art_width - 2 * art_padding
    art_top = command_y + 27
    art_height = art_width / REFERENCE_ASPECT_RATIO
    art_inner_height = art_height - 2 * art_padding
    art_bottom = ceil(art_top + art_height)
    info_x = left if mobile else 490
    info_y = art_bottom + 40 if mobile else art_top + 33

    if not image_b64:
        cell_width = art_inner_width / columns
        line_height = art_inner_height / len(art)
        art_size = cell_width / .602
    else:
        columns = cell_width = line_height = art_size = 0

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
        f"an avatar based on {escape(image_name)}"
        if image_name else "Bryan's portrait"
    )
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="en">
  <title id="title">{escape(profile["title"])}</title>
    <desc id="desc">A terminal with {avatar_description}. {escape(profile["description"])}</desc>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300&amp;400&amp;500&amp;600&amp;700&amp;display=swap');
    text {{ font-family: 'JetBrains Mono', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
      font-weight: 400; font-feature-settings: "calt" 1, "liga" 1;
      font-variant-ligatures: contextual; }}
    .ascii-shade {{ font-weight: 700; font-variant-ligatures: none; font-feature-settings: "calt" 0, "liga" 0; }}
    @media (prefers-reduced-motion: reduce) {{
      .typed-char {{ opacity: 1 !important; }}
      .tone-0 {{ fill: {PHOTO_DEEP} !important; }}
      .tone-1 {{ fill: {PHOTO_SHADOW} !important; }}
      .tone-2 {{ fill: {PHOTO_MID} !important; }}
      .tone-3 {{ fill: {PHOTO_COLOR} !important; }}
      .tone-4 {{ fill: {PHOTO_WHITE} !important; }}
      .motion {{ display: none; }}
    }}
  </style>
  <defs>
    <filter id="neon-glow" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="2.5"/>
    </filter>
    <linearGradient id="scanline-beam" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{ACCENT}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="art-clip">
      <rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8"/>
    </clipPath>
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
    parts.append(f'<rect x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" rx="8" fill="{ART_BACKGROUND}" stroke="{ACCENT}"/>')
    if image_b64:
        parts.append(
            f'<image href="data:image/jpeg;base64,{image_b64}" xlink:href="data:image/jpeg;base64,{image_b64}" '
            f'x="{left}" y="{art_top}" width="{art_width}" height="{art_height}" '
            f'clip-path="url(#art-clip)" preserveAspectRatio="xMidYMid slice"/>')
    beam_h = 16
    scan_start_y = art_top - beam_h
    scan_end_y = art_bottom
    scan_dur = 4.0
    parts.append(f'''<g class="scanline-group motion" clip-path="url(#art-clip)" aria-hidden="true">
      <rect class="scanline" x="{left}" y="{scan_start_y}" width="{art_width}" height="{beam_h}" fill="url(#scanline-beam)">
        <animate attributeName="y" values="{scan_start_y};{scan_end_y}" keyTimes="0;1" dur="{scan_dur}s" repeatCount="indefinite"/>
      </rect>
      <line x1="{left}" y1="{scan_start_y + beam_h // 2}" x2="{left + art_width}" y2="{scan_start_y + beam_h // 2}" stroke="{ACCENT}" stroke-width="1.5" opacity="0.65" filter="url(#neon-glow)">
        <animate attributeName="y1" values="{scan_start_y + beam_h // 2};{scan_end_y + beam_h // 2}" keyTimes="0;1" dur="{scan_dur}s" repeatCount="indefinite"/>
        <animate attributeName="y2" values="{scan_start_y + beam_h // 2};{scan_end_y + beam_h // 2}" keyTimes="0;1" dur="{scan_dur}s" repeatCount="indefinite"/>
      </line>
    </g>''')
    if not image_b64 and art:
        for i, layers in enumerate(art):
            parts.append(f'<g class="ascii-row" data-row="{i}">')
            for tone, line in enumerate(layers):
                ink = [(column, character) for column, character in enumerate(line)
                       if character != " "]
                if not ink:
                    continue
                # Anchor each glyph: SVG textLength can redistribute whitespace
                # differently across sparse layers, misaligning facial details.
                positions = " ".join(f"{art_x + column * cell_width:.3f}"
                                     for column, _ in ink)
                color = PHOTO_TONES[tone]
                parts.append(
                    f'<text class="ascii-shade tone-{tone}" x="{positions}" '
                    f'y="{art_y + (line_height + art_size * .7) / 2 + i * line_height:.3f}" '
                    f'fill="{color}" font-size="{art_size:.3f}" xml:space="preserve">'
                    f'{escape("".join(character for _, character in ink))}</text>')
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
        source = render(mobile, art=art, image_name=image_name, profile=profile,
                        theme=theme, use_image=False)
        target.write_text(source, encoding="utf-8")
        static_target = target.with_name(target.stem + "-static.svg")
        static_target.write_text(static_svg(source), encoding="utf-8")
        print(target.relative_to(ROOT))
        print(static_target.relative_to(ROOT))
