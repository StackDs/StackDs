#!/usr/bin/env python3
"""Theme Platane/snk SVGs and add an idempotent, static reduced-motion view."""

import re
import xml.etree.ElementTree as ET

from profile_config import ROOT, load_theme
from svg_motion import static_svg

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
MOTION_STYLE = "profile-reduced-motion"


def render(source, theme, dark=False):
    root = ET.fromstring(source)
    if root.tag != f"{{{SVG}}}svg":
        raise ValueError("Expected a contribution SVG")
    palette = theme["snake_dark" if dark else "snake_light"]
    colors = {"cs": theme["accent"], "ce": palette[0], "cb": theme["border"]}
    colors.update({f"c{i}": color for i, color in enumerate(palette)})
    # The original assets already included a simple unmarked reduced-motion rule.
    legacy = "@media(prefers-reduced-motion:reduce){*{animation:none!important;}}"
    for style in list(root.findall(f"{{{SVG}}}style")):
        if style.get("id") == MOTION_STYLE or re.sub(r"\s+", "", style.text or "") == legacy:
            root.remove(style)
    style = root.find(f"{{{SVG}}}style")
    if style is None:
        raise ValueError("Contribution SVG is missing its animation stylesheet")
    css = style.text or ""
    for name, color in colors.items():
        css, count = re.subn(rf"(--{name}:)[^;}}]+", rf"\g<1>{color}", css)
        if count != 1:
            raise ValueError(f"Expected one --{name} color in the Platane/snk SVG")
    style.text = css
    root.set("role", "img")
    root.set("aria-label", "GitHub contribution calendar; animated snake")

    calendar_cells = [
        (idx, child) for idx, child in enumerate(list(root))
        if child.tag == f"{{{SVG}}}rect" and child.get("class", "").split() and child.get("class", "").split()[0] == "c"
    ]
    if calendar_cells:
        existing = {
            (int(child.get("x")), int(child.get("y")))
            for _, child in calendar_cells
        }
        all_xs = sorted(set(x for x, y in existing))
        standard_ys = sorted(set(y for x, y in existing))
        last_idx = calendar_cells[-1][0]
        insert_pos = last_idx + 1
        for x in all_xs:
            for y in standard_ys:
                if (x, y) not in existing:
                    new_rect = ET.Element(f"{{{SVG}}}rect", {
                        "class": "c",
                        "x": str(x),
                        "y": str(y),
                        "rx": "2",
                        "ry": "2",
                    })
                    root.insert(insert_pos, new_rect)
                    insert_pos += 1
                    existing.add((x, y))

    return ET.tostring(root, encoding="unicode") + "\n"


def outputs(theme):
    """The action's outputs input, derived from the same palette as local builds."""
    lines = []
    for suffix, palette in (("", "snake_light"), ("-dark", "snake_dark")):
        options = f'color_snake={theme["accent"]}&color_dots={",".join(theme[palette])}'
        lines.append(f"assets/contributions/snake{suffix}.svg?{options}")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", action="store_true", help="print the Platane/snk outputs input")
    args = parser.parse_args()
    theme = load_theme()
    if args.outputs:
        print(outputs(theme))
    else:
        for suffix in ("", "-dark"):
            path = ROOT / f"assets/contributions/snake{suffix}.svg"
            source = render(path.read_text(encoding="utf-8"), theme, bool(suffix))
            path.write_text(source, encoding="utf-8")
            static_path = path.with_name(f"snake{suffix}-static.svg")
            static_path.write_text(static_svg(source, {"s", "u"}), encoding="utf-8")
            print(path.relative_to(ROOT))
            print(static_path.relative_to(ROOT))
