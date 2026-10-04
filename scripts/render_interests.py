"""Render interactive, responsive interest cards with standalone SVG animations."""

from html import escape
import math
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
      .bn-0 {{ animation: bfs-n0 12s infinite; }}
      .be-1 {{ animation: bfs-e1 12s infinite; }}
      .bn-1 {{ animation: bfs-n1 12s infinite; }}
      .be-2 {{ animation: bfs-e2 12s infinite; }}
      .bn-2 {{ animation: bfs-n2 12s infinite; }}
      .bq-0 {{ animation: bfs-q0 12s infinite; }}
      .bq-1 {{ animation: bfs-q1 12s infinite; }}
      .bq-2 {{ animation: bfs-q2 12s infinite; }}
      .bq-3 {{ animation: bfs-q3 12s infinite; }}
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

    mu = 180.0
    sigma = 42.0
    base_y = 128.0
    peak_y = 50.0
    h_max = base_y - peak_y  # 78.0

    # Mathematically continuous Gaussian bell curve with smooth rounded peak
    path_points = []
    for x_int in range(35, 326, 2):
        x = float(x_int)
        y = base_y - h_max * math.exp(-0.5 * ((x - mu) / sigma) ** 2)
        path_points.append((x, round(y, 2)))

    path_d = "M " + " L ".join(f"{x:.1f},{y:.2f}" for x, y in path_points)
    area_d = f"{path_d} L 325.0,128.0 L 35.0,128.0 Z"

    # Symmetric animated histogram bins rising under the curve
    bin_xs = [180 - 8 + i * 20 for i in range(-5, 6)]
    bin_rects = []
    for idx, bx in enumerate(bin_xs):
        cx = bx + 8.0
        h = max(3.0, round(h_max * math.exp(-0.5 * ((cx - mu) / sigma) ** 2) - 2.0, 1))
        target_y = round(base_y - h, 1)
        bin_rects.append(
            f'<rect class="ds-bin ds-b{idx}" x="{bx}" y="{target_y}" width="16" height="{h}" rx="2" '
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
      <line x1="180" y1="50" x2="180" y2="128"/>
      <line x1="138" y1="81" x2="138" y2="128"/>
      <line x1="222" y1="81" x2="222" y2="128"/>
    </g>
    <!-- Baseline Axis -->
    <line x1="35" y1="128" x2="325" y2="128" stroke="{border}" stroke-width="1.5"/>
    <!-- Axis Ticks & Labels -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="9" fill="{comment}" text-anchor="middle">
      <text x="96" y="140">-2σ</text>
      <text x="138" y="140">-1σ</text>
      <text x="180" y="140" fill="{accent_light}" font-weight="bold">μ</text>
      <text x="222" y="140">+1σ</text>
      <text x="264" y="140">+2σ</text>
    </g>
    <!-- Badge Indicator -->
    <g class="ds-stat" font-family="DejaVu Sans Mono, monospace" font-size="9">
      <rect x="220" y="28" width="105" height="18" rx="4" fill="{control}" stroke="{border}"/>
      <text x="272" y="41" fill="{accent_light}" text-anchor="middle">μ=0.0  σ=1.0</text>
      <rect x="35" y="28" width="100" height="18" rx="4" fill="{control}" stroke="{border}"/>
      <text x="85" y="41" fill="{text_sec}" text-anchor="middle">P(|x|&lt;σ) ≈ 68%</text>
    </g>
'''


def _project_cam(x, y, z, cx=195, cy=96, scale=17.0, theta=0.610865, phi=0.453786):
    """3D camera projection with azimuth theta (35 deg) and elevation phi (26 deg)."""
    x1 = x * math.cos(theta) - y * math.sin(theta)
    y1 = x * math.sin(theta) + y * math.cos(theta)
    z1 = z
    u = cx + scale * x1
    v = cy - scale * (y1 * math.sin(phi) + z1 * math.cos(phi))
    return round(u, 1), round(v, 1)


def _render_mathematics_canvas(theme):
    """Canvas content: 3D hyperbolic paraboloid (saddle point) surface with gradient field & contours."""
    accent = theme["accent"]
    accent_light = theme["accent_light"]
    text = theme["text"]
    text_sec = theme["text_secondary"]
    comment = theme["comment"]
    border = theme["border"]
    control = theme["control"]

    cx, cy = 195, 96
    scale = 17.0
    floor_z = -3.4

    nx, ny = 19, 19
    xs = [-2.6 + i * 5.2 / (nx - 1) for i in range(nx)]
    ys = [-2.6 + j * 5.2 / (ny - 1) for j in range(ny)]

    # Surface: z = (x^2 - y^2) / 2.6
    curves_x = []
    for y in ys:
        pts = []
        for x in xs:
            z = (x**2 - y**2) / 2.6
            u, v = _project_cam(x, y, z, cx=cx, cy=cy, scale=scale)
            pts.append(f"{u},{v}")
        curves_x.append("M " + " L ".join(pts))

    curves_y = []
    for x in xs:
        pts = []
        for y in ys:
            z = (x**2 - y**2) / 2.6
            u, v = _project_cam(x, y, z, cx=cx, cy=cy, scale=scale)
            pts.append(f"{u},{v}")
        curves_y.append("M " + " L ".join(pts))

    # Floor grid
    floor_grid = []
    for val in [-2.6, 0, 2.6]:
        u1, v1 = _project_cam(-2.6, val, floor_z, cx=cx, cy=cy, scale=scale)
        u2, v2 = _project_cam(2.6, val, floor_z, cx=cx, cy=cy, scale=scale)
        floor_grid.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" stroke="{border}" stroke-dasharray="2 2"/>')
        u1, v1 = _project_cam(val, -2.6, floor_z, cx=cx, cy=cy, scale=scale)
        u2, v2 = _project_cam(val, 2.6, floor_z, cx=cx, cy=cy, scale=scale)
        floor_grid.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" stroke="{border}" stroke-dasharray="2 2"/>')

    # Floor contour hyperbolas: x^2 - y^2 = c
    u1, v1 = _project_cam(-2.4, -2.4, floor_z, cx=cx, cy=cy, scale=scale)
    u2, v2 = _project_cam(2.4, 2.4, floor_z, cx=cx, cy=cy, scale=scale)
    asymp1 = f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" stroke="{comment}" stroke-width="0.8" stroke-dasharray="2 2" opacity="0.4"/>'
    u1, v1 = _project_cam(-2.4, 2.4, floor_z, cx=cx, cy=cy, scale=scale)
    u2, v2 = _project_cam(2.4, -2.4, floor_z, cx=cx, cy=cy, scale=scale)
    asymp2 = f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" stroke="{comment}" stroke-width="0.8" stroke-dasharray="2 2" opacity="0.4"/>'

    hyp_pos = []
    for c in [1.6]:
        for sign in [1, -1]:
            pts = []
            for yi in range(-21, 22):
                y_val = yi / 10.0
                radicand = c + y_val**2
                if radicand >= 0:
                    x_val = sign * math.sqrt(radicand)
                    if abs(x_val) <= 2.6:
                        u, v = _project_cam(x_val, y_val, floor_z, cx=cx, cy=cy, scale=scale)
                        pts.append(f"{u},{v}")
            if pts:
                hyp_pos.append(f'<path d="M ' + " L ".join(pts) + '"/>')

    hyp_neg = []
    for c in [-1.6]:
        for sign in [1, -1]:
            pts = []
            for xi in range(-21, 22):
                x_val = xi / 10.0
                radicand = -c + x_val**2
                if radicand >= 0:
                    y_val = sign * math.sqrt(radicand)
                    if abs(y_val) <= 2.6:
                        u, v = _project_cam(x_val, y_val, floor_z, cx=cx, cy=cy, scale=scale)
                        pts.append(f"{u},{v}")
            if pts:
                hyp_neg.append(f'<path d="M ' + " L ".join(pts) + '"/>')

    # 3D Axes
    ox, oy = _project_cam(0, 0, floor_z, cx=cx, cy=cy, scale=scale)
    xx, xy_ = _project_cam(3.1, 0, floor_z, cx=cx, cy=cy, scale=scale)
    yx, yy = _project_cam(0, 3.1, floor_z, cx=cx, cy=cy, scale=scale)
    zx, zy = _project_cam(0, 0, 3.2, cx=cx, cy=cy, scale=scale)

    # Origin saddle critical point (0, 0, 0)
    so_u, so_v = _project_cam(0, 0, 0, cx=cx, cy=cy, scale=scale)

    # Keyframes for particle P(t) on surface
    n_frames = 24
    p_kf = []
    sh_kf = []

    init_px = 1.75
    init_py = 0.0
    init_pz = (init_px**2 - init_py**2) / 2.6
    init_pu, init_pv = _project_cam(init_px, init_py, init_pz, cx=cx, cy=cy, scale=scale)
    init_pfu, init_pfv = _project_cam(init_px, init_py, floor_z, cx=cx, cy=cy, scale=scale)

    for i in range(n_frames + 1):
        pct = round(i * 100.0 / n_frames, 1)
        t = i * 2.0 * math.pi / n_frames
        px = 1.75 * math.cos(t)
        py = 1.35 * math.sin(t)
        pz = (px**2 - py**2) / 2.6
        pu, pv = _project_cam(px, py, pz, cx=cx, cy=cy, scale=scale)
        pfu, pfv = _project_cam(px, py, floor_z, cx=cx, cy=cy, scale=scale)

        p_kf.append(f"{pct}% {{ transform: translate({pu}px, {pv}px); }}")
        sh_kf.append(f"{pct}% {{ transform: translate({pfu}px, {pfv}px); }}")

    p_kf_str = " ".join(p_kf)
    sh_kf_str = " ".join(sh_kf)
    floor_grid_str = " ".join(floor_grid)
    hyp_pos_str = " ".join(hyp_pos)
    hyp_neg_str = " ".join(hyp_neg)
    curves_x_str = " ".join(f'<path d="{d}"/>' for d in curves_x)
    curves_y_str = " ".join(f'<path d="{d}"/>' for d in curves_y)

    return f'''
    <style>
      @keyframes m-surf-pt {{
        {p_kf_str}
      }}
      @keyframes m-surf-sh {{
        {sh_kf_str}
      }}
      @keyframes m-pulse-x {{
        0%, 100% {{ opacity: 0.35; stroke-width: 0.9px; }}
        50% {{ opacity: 0.9; stroke-width: 1.4px; }}
      }}
      @keyframes m-pulse-y {{
        0%, 100% {{ opacity: 0.9; stroke-width: 1.4px; }}
        50% {{ opacity: 0.35; stroke-width: 0.9px; }}
      }}
      @keyframes m-saddle-glow {{
        0%, 100% {{ opacity: 0.55; }}
        50% {{ opacity: 1.0; }}
      }}
      .m-tracer {{ animation: m-surf-pt 9s infinite linear; }}
      .m-shadow {{ animation: m-surf-sh 9s infinite linear; }}
      .m-hyp-x {{ animation: m-pulse-x 4.5s infinite ease-in-out; stroke: {accent_light}; fill: none; }}
      .m-hyp-y {{ animation: m-pulse-y 4.5s infinite ease-in-out; stroke: {accent}; fill: none; }}
      .m-crit {{ animation: m-saddle-glow 2.5s infinite ease-in-out; }}
    </style>

    <!-- Floor Grid & Asymptotes -->
    <g opacity="0.25">
      {floor_grid_str}
    </g>
    {asymp1}
    {asymp2}

    <!-- Pulsing Hyperbolic Contours -->
    <g class="m-hyp-x">
      {hyp_pos_str}
    </g>
    <g class="m-hyp-y">
      {hyp_neg_str}
    </g>

    <!-- 3D Coordinate Axes -->
    <g stroke="{comment}" stroke-width="1" opacity="0.45">
      <line x1="{ox}" y1="{oy}" x2="{xx}" y2="{xy_}"/>
      <line x1="{ox}" y1="{oy}" x2="{yx}" y2="{yy}"/>
      <line x1="{ox}" y1="{oy}" x2="{zx}" y2="{zy}" stroke-dasharray="2 2"/>
    </g>
    <text x="{xx+6}" y="{xy_+3}" font-family="DejaVu Sans Mono" font-size="8" fill="{comment}">x</text>
    <text x="{yx-9}" y="{yy+3}" font-family="DejaVu Sans Mono" font-size="8" fill="{comment}">y</text>
    <text x="{zx}" y="{zy-4}" font-family="DejaVu Sans Mono" font-size="8" fill="{comment}" text-anchor="middle">z</text>

    <!-- Surface Mesh: X-parametric (∂/∂x) & Y-parametric (∂/∂y) Curves -->
    <g fill="none" stroke="{accent}" stroke-width="0.85" opacity="0.72">
      {curves_x_str}
    </g>
    <g fill="none" stroke="{accent_light}" stroke-width="0.85" opacity="0.72">
      {curves_y_str}
    </g>

    <!-- Saddle Critical Point at (0,0,0) -->
    <g class="m-crit">
      <circle cx="{so_u}" cy="{so_v}" r="3.2" fill="none" stroke="{text_sec}" stroke-width="1.2"/>
      <circle cx="{so_u}" cy="{so_v}" r="1.4" fill="{text_sec}"/>
      <text x="{so_u - 38}" y="{so_v + 3}" font-family="DejaVu Sans Mono" font-size="8" fill="{text_sec}">P₀(0,0)</text>
    </g>

    <!-- Static Vertical Projection Line from Surface to Floor -->
    <line x1="{init_pu}" y1="{init_pv}" x2="{init_pfu}" y2="{init_pfv}" stroke="{text_sec}" stroke-dasharray="2 2" stroke-width="1" opacity="0.4"/>

    <!-- Moving Projected Shadow on Floor -->
    <g class="m-shadow" transform="translate({init_pfu}, {init_pfv})">
      <circle cx="0" cy="0" r="2.2" fill="{text_sec}" opacity="0.5"/>
    </g>

    <!-- Moving Point on Surface with Gradient Vector -->
    <g class="m-tracer" transform="translate({init_pu}, {init_pv})">
      <circle cx="0" cy="0" r="3.2" fill="{text}"/>
      <line x1="0" y1="0" x2="10" y2="-7" stroke="{text}" stroke-width="1.8" stroke-linecap="round"/>
      <polygon points="10,-7 6,-10 11,-10" fill="{text}"/>
      <text x="13" y="-9" font-family="DejaVu Sans Mono" font-size="8.5" fill="{text}" font-weight="bold">∇f</text>
    </g>

    <!-- Top Formula Badge -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="9">
      <rect x="226" y="6" width="120" height="16" rx="3" fill="{control}" stroke="{border}"/>
      <text x="286" y="18" fill="{accent_light}" text-anchor="middle">∇f = [∂f/∂x, ∂f/∂y]ᵀ</text>
    </g>

    <!-- Information Badges -->
    <g font-family="DejaVu Sans Mono, monospace" font-size="8.5">
      <rect x="14" y="32" width="128" height="17" rx="3" fill="{control}" stroke="{border}"/>
      <text x="78" y="44" fill="{text_sec}" text-anchor="middle">z = (x² - y²) / 2</text>
      <rect x="14" y="146" width="168" height="16" rx="3" fill="{control}" stroke="{border}"/>
      <text x="98" y="158" fill="{comment}" text-anchor="middle">Hessian: det(H) &lt; 0 (Saddle)</text>
    </g>
'''


CANVAS_RENDERERS = {
    "programming": (_render_programming_canvas, "main.c"),
    "algorithms": (_render_algorithms_canvas, "bfs_graph.py"),
    "data_science": (_render_data_science_canvas, "distribution.py"),
    "mathematics": (_render_mathematics_canvas, "saddle_field.py"),
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
