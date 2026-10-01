#!/usr/bin/env python3
"""Keep the contribution calendar still when reduced motion is requested."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ('<style id="reduced-motion">'
         '@media (prefers-reduced-motion: reduce) {'
         '* { animation: none !important; }'
         '}</style>')

if __name__ == "__main__":
    for name in ("snake.svg", "snake-dark.svg"):
        path = ROOT / "assets" / "contributions" / name
        svg = path.read_text(encoding="utf-8")
        if 'id="reduced-motion"' not in svg:
            if "</svg>" not in svg:
                raise ValueError(f"Invalid SVG: {path}")
            path.write_text(svg.replace("</svg>", STYLE + "</svg>"), encoding="utf-8")
