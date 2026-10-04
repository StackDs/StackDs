"""Render interactive, responsive interest cards with standalone SVG animations."""

from html import escape
from textwrap import wrap

from profile_config import ROOT


def _pill_badges(tags, start_x, start_y, theme):
    """Render a row of small pill badges for technology / topic tags."""
    pills = []
    x = start_x
    for tag in tags:
        tag_text = escape(tag)
        tag_width = len(tag) * 6.8 + 12
        pills.append(
            f'<rect x="{x:.1f}" y="{start_y:.1f}" width="{tag_width:.1f}" height="18" rx="4" '
            f'fill="{theme["control"]}" stroke="{theme["border"]}"/>\n'
            f'<text x="{x + tag_width / 2:.1f}" y="{start_y + 12.5:.1f}" font-size="10" '
            f'fill="{theme["comment"]}" text-anchor="middle" font-family="DejaVu Sans Mono, monospace">'
            f'{tag_text}</text>'
        )
        x += tag_width + 6
    return "\n    ".join(pills)


def _render_programming_canvas(theme):
    """Canvas content: terminal / editor window typing C code with blinking cursor."""
    accent = theme["accent"]
    accent_light = theme["accent_light"]
    text = theme["text"]
    text_sec = theme["text_secondary"]
    comment = theme["comment"]
    border = theme["border"]

    return f'''
    <style>
      @keyframes prog-type {{
        0%, 10% {{ opacity: 0; }}
        20%, 100% {{ opacity: 1; }}
      }}
      @keyframes prog-run {{
        0%, 55% {{ opacity: 0; transform: translateY(4px); }}
        65%, 100% {{ opacity: 1; transform: translateY(0); }}
      }}
      @keyframes prog-cursor {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0; }}
      }}
      .p-l1 {{ animation: prog-type 6s infinite 0.2s; }}
      .p-l2 {{ animation: prog-type 6s infinite 0.8s; }}
      .p-l3 {{ animation: prog-type 6s infinite 1.4s; }}
      .p-l4 {{ animation: prog-type 6s infinite 2.0s; }}
      .p-l5 {{ animation: prog-type 6s infinite 2.4s; }}
      .p-out {{ animation: prog-run 6s infinite; }}
      .p-cur {{ animation: prog-cursor 0.9s infinite; }}
    </style>
    <!-- Code Editor -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="11">
      <!-- Line 1 -->
      <g class="p-l1">
        <text x="16" y="44"><tspan fill="{comment}">1   </tspan><tspan fill="{accent}">#include </tspan><tspan fill="{accent_light}">&lt;stdio.h&gt;</tspan></text>
      </g>
      <!-- Line 2 -->
      <g class="p-l2">
        <text x="16" y="62"><tspan fill="{comment}">2   </tspan><tspan fill="{accent}">int </tspan><tspan fill="{accent_light}">main</tspan><tspan fill="{text}">(void) {{</tspan></text>
      </g>
      <!-- Line 3 -->
      <g class="p-l3">
        <text x="16" y="80"><tspan fill="{comment}">3     </tspan><tspan fill="{accent_light}">printf</tspan><tspan fill="{text}">(</tspan><tspan fill="{text_sec}">&quot;This shit isn't gonna compile\\n&quot;</tspan><tspan fill="{text}">)</tspan></text>
      </g>
      <!-- Line 4 -->
      <g class="p-l4">
        <text x="16" y="98"><tspan fill="{comment}">4     </tspan><tspan fill="{accent}">return </tspan><tspan fill="{text}">0;</tspan></text>
      </g>
      <!-- Line 5 -->
      <g class="p-l5">
        <text x="16" y="116"><tspan fill="{comment}">5   </tspan><tspan fill="{text}">}}</tspan></text>
      </g>
      <!-- Terminal Execution Divider -->
      <line x1="12" y1="126" x2="348" y2="126" stroke="{border}" stroke-dasharray="3 3"/>
      <!-- Terminal Output -->
      <g class="p-out">
        <text x="16" y="142"><tspan fill="{accent}">~ $ </tspan><tspan fill="{text}">gcc main.c -o And Justice For All</tspan></text>
        <text x="16" y="158" fill="{accent_light}">You forgot a semicolon!... stupid</text>
        <rect class="p-cur" x="240" y="148" width="6" height="12" fill="{accent_light}"/>
      </g>
    </g>
'''


def _render_algorithms_canvas(theme):
    """Canvas content: animated Breadth-First Search (BFS) graph traversal."""
    accent = theme["accent"]
    accent_light = theme["accent_light"]
    surface = theme["surface"]
    text = theme["text"]
    comment = theme["comment"]
    border = theme["border"]
    control = theme["control"]

    return f'''
    <style>
      @keyframes bfs-n0 {{
        0% {{ fill: {control}; stroke: {border}; }}
        10%, 92% {{ fill: {accent}; stroke: {accent_light}; }}
        98%, 100% {{ fill: {control}; stroke: {border}; }}
      }}
      @keyframes bfs-e1 {{
        0%, 15% {{ stroke: {border}; stroke-width: 1.5; }}
        25%, 92% {{ stroke: {accent}; stroke-width: 2.5; }}
        98%, 100% {{ stroke: {border}; stroke-width: 1.5; }}
      }}
      @keyframes bfs-n1 {{
        0%, 20% {{ fill: {control}; stroke: {border}; }}
        30%, 45% {{ fill: {surface}; stroke: {accent_light}; }}
        50%, 92% {{ fill: {accent}; stroke: {accent_light}; }}
        98%, 100% {{ fill: {control}; stroke: {border}; }}
      }}
      @keyframes bfs-e2 {{
        0%, 45% {{ stroke: {border}; stroke-width: 1.5; }}
        55%, 92% {{ stroke: {accent}; stroke-width: 2.5; }}
        98%, 100% {{ stroke: {border}; stroke-width: 1.5; }}
      }}
      @keyframes bfs-n2 {{
        0%, 50% {{ fill: {control}; stroke: {border}; }}
        60%, 75% {{ fill: {surface}; stroke: {accent_light}; }}
        80%, 92% {{ fill: {accent}; stroke: {accent_light}; }}
        98%, 100% {{ fill: {control}; stroke: {border}; }}
      }}
      @keyframes bfs-q0 {{
        0%, 5% {{ opacity: 0; }}
        10%, 28% {{ opacity: 1; }}
        30%, 100% {{ opacity: 0; }}
      }}
      @keyframes bfs-q1 {{
        0%, 28% {{ opacity: 0; }}
        30%, 55% {{ opacity: 1; }}
        58%, 100% {{ opacity: 0; }}
      }}
      @keyframes bfs-q2 {{
        0%, 55% {{ opacity: 0; }}
        58%, 85% {{ opacity: 1; }}
        88%, 100% {{ opacity: 0; }}
      }}
      @keyframes bfs-q3 {{
        0%, 85% {{ opacity: 0; }}
        88%, 98% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
      }}
      .bq-0, .bq-1, .bq-2 {{ opacity: 0; }}
      .bq-3 {{ opacity: 1; }}
      .bn-0 {{ animation: bfs-n0 6s infinite; }}
      .be-1 {{ animation: bfs-e1 6s infinite; }}
      .bn-1 {{ animation: bfs-n1 6s infinite; }}
      .be-2 {{ animation: bfs-e2 6s infinite; }}
      .bn-2 {{ animation: bfs-n2 6s infinite; }}
      .bq-0 {{ animation: bfs-q0 6s infinite; }}
      .bq-1 {{ animation: bfs-q1 6s infinite; }}
      .bq-2 {{ animation: bfs-q2 6s infinite; }}
      .bq-3 {{ animation: bfs-q3 6s infinite; }}
    </style>
    <!-- Graph Edges -->
    <g stroke="{border}">
      <!-- Root to Level 1 -->
      <line class="be-1" x1="180" y1="46" x2="110" y2="78"/>
      <line class="be-1" x1="180" y1="46" x2="250" y2="78"/>
      <!-- Level 1 to Level 2 -->
      <line class="be-2" x1="110" y1="78" x2="65" y2="112"/>
      <line class="be-2" x1="110" y1="78" x2="145" y2="112"/>
      <line class="be-2" x1="250" y1="78" x2="215" y2="112"/>
      <line class="be-2" x1="250" y1="78" x2="295" y2="112"/>
    </g>
    <!-- Graph Nodes -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="10" font-weight="bold" text-anchor="middle">
      <!-- Root Node 0 -->
      <circle class="bn-0" cx="180" cy="46" r="11" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="180" y="50" fill="{text}">0</text>
      <!-- Level 1 Nodes -->
      <circle class="bn-1" cx="110" cy="78" r="11" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="110" y="82" fill="{text}">1</text>
      <circle class="bn-1" cx="250" cy="78" r="11" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="250" y="82" fill="{text}">2</text>
      <!-- Level 2 Nodes -->
      <circle class="bn-2" cx="65" cy="112" r="10" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="65" y="116" fill="{text}">3</text>
      <circle class="bn-2" cx="145" cy="112" r="10" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="145" y="116" fill="{text}">4</text>
      <circle class="bn-2" cx="215" cy="112" r="10" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="215" y="116" fill="{text}">5</text>
      <circle class="bn-2" cx="295" cy="112" r="10" fill="{control}" stroke="{border}" stroke-width="2"/>
      <text x="295" y="116" fill="{text}">6</text>
    </g>
    <!-- Queue Status Box -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="10" text-anchor="middle">
      <rect x="35" y="136" width="290" height="22" rx="4" fill="{control}" stroke="{border}"/>
      <text class="bq-0" x="180" y="151" fill="{accent}">Initializing search...</text>
      <text class="bq-1" x="180" y="151" fill="{accent_light}">Searching the best path...</text>
      <text class="bq-2" x="180" y="151" fill="{accent_light}">Drinking a beer...</text>
      <text class="bq-3" x="180" y="151" fill="{accent}">Yep, the liqour store is over here.</text>
    </g>
'''


def _render_data_science_canvas(theme):
    """Canvas content: statistical normal distribution bell curve with dynamic histogram."""
    accent = theme["accent"]
    accent_light = theme["accent_light"]
    text = theme["text"]
    text_sec = theme["text_secondary"]
    comment = theme["comment"]
    border = theme["border"]
    control = theme["control"]

    # Pre-calculated Gaussian curve coordinates (width 300, centered at 180, peak at y=48, baseline y=128)
    path_points = [
        (45, 127), (65, 126), (85, 124), (105, 118), (120, 111),
        (135, 99), (150, 83), (165, 65), (180, 48), (195, 65),
        (210, 83), (225, 99), (240, 111), (255, 118), (275, 124),
        (295, 126), (315, 127)
    ]
    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in path_points)
    area_d = f"{path_d} L 315.0,128 L 45.0,128 Z"

    # Animated histogram bins rising under the curve
    bins = [
        (60, 4, 124), (82, 8, 120), (104, 16, 112), (126, 32, 96),
        (148, 52, 76), (170, 74, 54), (192, 74, 54), (214, 52, 76),
        (236, 32, 96), (258, 16, 112), (280, 8, 120),
    ]
    bin_rects = []
    for idx, (bx, target_h, target_y) in enumerate(bins):
        bin_rects.append(
            f'<rect class="ds-bin ds-b{idx}" x="{bx}" y="{target_y}" width="16" height="{target_h}" rx="2" '
            f'fill="{control}" stroke="{border}"/>'
        )

    bin_elements = "\n      ".join(bin_rects)

    return f'''
    <style>
      @keyframes ds-sample {{
        0%, 10% {{ opacity: 0.2; transform: scaleY(0.1); transform-origin: 0 128px; }}
        40%, 88% {{ opacity: 0.85; transform: scaleY(1.0); transform-origin: 0 128px; }}
        96%, 100% {{ opacity: 0.2; transform: scaleY(0.1); transform-origin: 0 128px; }}
      }}
      @keyframes ds-curve {{
        0% {{ stroke-dashoffset: 600; opacity: 0.4; }}
        35%, 88% {{ stroke-dashoffset: 0; opacity: 1; }}
        96%, 100% {{ stroke-dashoffset: 0; opacity: 0.4; }}
      }}
      @keyframes ds-pulse {{
        0%, 100% {{ opacity: 0.4; }}
        50% {{ opacity: 1; }}
      }}
      .ds-bin {{ animation: ds-sample 6s ease-out infinite; }}
      .ds-line {{
        stroke-dasharray: 600;
        animation: ds-curve 6s ease-in-out infinite;
      }}
      .ds-stat {{ animation: ds-pulse 3s ease-in-out infinite; }}
    </style>
    <defs>
      <linearGradient id="bell-grad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{accent_light}" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="{accent}" stop-opacity="0.04"/>
      </linearGradient>
    </defs>
    <!-- Histogram Bars -->
    <g>
      {bin_elements}
    </g>
    <!-- Area Under Curve -->
    <path d="{area_d}" fill="url(#bell-grad)"/>
    <!-- Gaussian Bell Curve -->
    <path class="ds-line" d="{path_d}" fill="none" stroke="{accent_light}" stroke-width="2.5" stroke-linecap="round"/>
    <!-- Standard Deviation Vertical Guides -->
    <g stroke="{accent}" stroke-dasharray="2 2" stroke-width="1" opacity="0.6">
      <line x1="180" y1="48" x2="180" y2="128"/>
      <line x1="135" y1="99" x2="135" y2="128"/>
      <line x1="225" y1="99" x2="225" y2="128"/>
    </g>
    <!-- Baseline Axis -->
    <line x1="35" y1="128" x2="325" y2="128" stroke="{border}" stroke-width="1.5"/>
    <!-- Axis Ticks & Labels -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="9" fill="{comment}" text-anchor="middle">
      <text x="95" y="140">-2σ</text>
      <text x="135" y="140">-1σ</text>
      <text x="180" y="140" fill="{accent_light}" font-weight="bold">μ</text>
      <text x="225" y="140">+1σ</text>
      <text x="265" y="140">+2σ</text>
    </g>
    <!-- Badge Indicator -->
    <g class="ds-stat" font-family="DejaVu Sans Mono, monospace" font-size="9">
      <rect x="220" y="28" width="105" height="18" rx="4" fill="{control}" stroke="{border}"/>
      <text x="272" y="41" fill="{accent_light}" text-anchor="middle">μ=0.0  σ=1.0</text>
      <rect x="35" y="28" width="100" height="18" rx="4" fill="{control}" stroke="{border}"/>
      <text x="85" y="41" fill="{text_sec}" text-anchor="middle">P(|x|&lt;σ) ≈ 68%</text>
    </g>
'''


CANVAS_RENDERERS = {
    "programming": (_render_programming_canvas, "main.c"),
    "algorithms": (_render_algorithms_canvas, "bfs_graph.py"),
    "data_science": (_render_data_science_canvas, "distribution.py"),
}


def render(interest, theme, mobile=False):
    """Render an interest card in desktop or mobile layout."""
    interest_id = interest["id"]
    renderer_tuple = CANVAS_RENDERERS.get(interest_id, (_render_programming_canvas, "terminal"))
    canvas_fn, filename = renderer_tuple

    width = 420 if mobile else 880
    height = 360 if mobile else 220
    surface = theme["surface"]
    border = theme["border"]
    background = theme["background"]
    accent = theme["accent"]
    accent_light = theme["accent_light"]
    text_color = theme["text"]
    comment = theme["comment"]

    title = escape(interest.get("title", ""))
    subtitle = escape(interest.get("subtitle", "").upper())
    description = interest.get("description", "")
    tags = interest.get("tags", [])

    if mobile:
        # Mobile stacked layout
        # Top text section
        text_left = 22
        subtitle_y = 30
        title_y = 52
        desc_start_y = 72
        desc_lines = wrap(description, width=44, break_long_words=True, break_on_hyphens=False)
        desc_svg = "\n    ".join(
            f'<text x="{text_left}" y="{desc_start_y + idx * 16}" font-size="12" fill="{text_color}">{escape(line)}</text>'
            for idx, line in enumerate(desc_lines)
        )
        tag_y = desc_start_y + len(desc_lines) * 16 + 6
        pills_svg = _pill_badges(tags[:4], text_left, tag_y, theme)

        # Bottom visual canvas
        canvas_x = 22
        canvas_y = 175
        canvas_width = 376
        canvas_height = 170

    else:
        # Desktop 2-column side-by-side layout
        text_left = 32
        subtitle_y = 36
        title_y = 62
        desc_start_y = 86
        desc_lines = wrap(description, width=46, break_long_words=True, break_on_hyphens=False)
        desc_svg = "\n    ".join(
            f'<text x="{text_left}" y="{desc_start_y + idx * 18}" font-size="13" fill="{text_color}">{escape(line)}</text>'
            for idx, line in enumerate(desc_lines)
        )
        tag_y = desc_start_y + len(desc_lines) * 18 + 12
        pills_svg = _pill_badges(tags[:5], text_left, tag_y, theme)

        # Right visual canvas
        canvas_x = 490
        canvas_y = 20
        canvas_width = 358
        canvas_height = 180

    canvas_inner = canvas_fn(theme)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}: {escape(description)}" xml:lang="en">
  <title>{title}</title>
  <desc>{escape(description)}</desc>
  <!-- Card Background -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" fill="{surface}" stroke="{border}"/>

  <!-- Text & Information Column -->
  <g font-family="DejaVu Sans Mono, Liberation Mono, monospace">
    <text x="{text_left}" y="{subtitle_y}" font-size="11" fill="{accent}" font-weight="bold">// {subtitle}</text>
    <text x="{text_left}" y="{title_y}" font-size="19" fill="{accent_light}" font-weight="bold">{title}</text>
    {desc_svg}
    {pills_svg}
  </g>

  <!-- Interactive Visual Canvas -->
  <g transform="translate({canvas_x}, {canvas_y})">
    <!-- Sub-window Frame -->
    <rect width="{canvas_width}" height="{canvas_height}" rx="6" fill="{background}" stroke="{border}"/>
    <!-- Sub-window Header -->
    <circle cx="14" cy="13" r="3.5" fill="#EA2D2E"/>
    <circle cx="25" cy="13" r="3.5" fill="#E5C07B"/>
    <circle cx="36" cy="13" r="3.5" fill="#98C379"/>
    <text x="50" y="17" font-family="DejaVu Sans Mono, monospace" font-size="11" fill="{comment}">{filename}</text>
    <line x1="0" y1="26" x2="{canvas_width}" y2="26" stroke="{border}"/>

    <!-- Canvas Animation Content -->
    {canvas_inner}
  </g>
</svg>
'''
