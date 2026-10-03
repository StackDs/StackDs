#!/usr/bin/env python3
"""Generate all local profile artifacts, or check them without writing files."""

import argparse
import sys
import xml.etree.ElementTree as ET

from profile_config import ROOT, load_profile, load_theme
import reduce_snake_motion
import render_readme
import render_site
import render_terminal
import render_theme
import update_stats
from svg_motion import static_svg


def artifacts(root=ROOT):
    """Render everything before writing anything, so invalid inputs fail early."""
    profile, theme = load_profile(root), load_theme(root)
    def read(name):
        return (root / name).read_text(encoding="utf-8")

    art = read("ascii.txt").splitlines()
    result = {
        "README.md": render_readme.render(profile, theme, read("content/about.md"), read("templates/README.md.tpl")),
        "site/index.html": render_site.render(profile, theme, read("templates/site.html.tpl")),
        "site/theme.css": render_theme.render(theme),
    }
    for suffix, mobile in (("", False), ("-mobile", True)):
        banner = render_terminal.render(mobile, art=art, profile=profile, theme=theme)
        result[f"assets/terminal{suffix}.svg"] = banner
        result[f"assets/terminal{suffix}-static.svg"] = static_svg(banner)
    for suffix, dark in (("", False), ("-dark", True)):
        path = f"assets/contributions/snake{suffix}.svg"
        result[path] = reduce_snake_motion.render(read(path), theme, dark)
        result[f"assets/contributions/snake{suffix}-static.svg"] = static_svg(result[path], {"s", "u"})
    stats = root / "assets/stats/github.svg"
    if stats.is_file():
        source = stats.read_text(encoding="utf-8")
        fallback = ET.fromstring(source).get("data-profile-stats") == "unavailable"
    else:
        fallback = True
    result["assets/stats/github.svg"] = (
        update_stats.render_fallback(profile, theme) if fallback
        else update_stats.apply_theme(source, theme)
    )
    return result


def build(root=ROOT, check=False):
    generated = artifacts(root)
    stale = []
    for name, content in generated.items():
        path = root / name
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        stale.append(name)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f'{"Out of date" if check else "Generated"}: {name}')
    return not stale if check else True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on stale artifacts without writing them")
    args = parser.parse_args()
    try:
        success = build(check=args.check)
    except (OSError, ValueError, KeyError, ET.ParseError) as error:
        print(f"Profile build failed: {error}", file=sys.stderr)
        sys.exit(1)
    if success:
        print("Profile artifacts are up to date.")
    sys.exit(0 if success else 1)
