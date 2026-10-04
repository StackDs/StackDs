#!/usr/bin/env python3
"""Generate all local profile artifacts, or check them without writing files."""

import argparse
import sys
import xml.etree.ElementTree as ET

from profile_config import ROOT, load_profile, load_theme
import reduce_snake_motion
import render_readme
import render_contact_badges
import render_project_cards
import render_quotes
import render_site
import render_terminal
import render_theme
import render_tech_badges
import render_interests
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
        banner = render_terminal.render(mobile, art=art, profile=profile, theme=theme, root=root)
        result[f"assets/terminal{suffix}.svg"] = banner
        result[f"assets/terminal{suffix}-static.svg"] = static_svg(banner)
        quotes = render_quotes.render(profile, theme, mobile)
        result[f"assets/quotes{suffix}.svg"] = quotes
        result[f"assets/quotes{suffix}-static.svg"] = static_svg(quotes)
        for index, project in enumerate(profile["projects"], 1):
            result[f"assets/project-{index:02d}{suffix}.svg"] = render_project_cards.render(
                project, theme, mobile)
        for interest in profile.get("interests", []):
            card = render_interests.render(interest, theme, mobile)
            result[f"assets/interest-{interest['id']}{suffix}.svg"] = card
            result[f"assets/interest-{interest['id']}{suffix}-static.svg"] = static_svg(card)
    for index, contact in enumerate(profile["contacts"], 1):
        result[f"assets/contact-{index:02d}.svg"] = render_contact_badges.render(contact, theme)
    for group in profile["stack"]:
        for item in group["items"]:
            path = render_tech_badges.asset_path(item)
            if path:
                result[path] = render_tech_badges.render(item, theme, read(f'assets/icons/{item["logo"]}.svg'))
    for suffix, dark in (("", False), ("-dark", True)):
        path = f"assets/contributions/snake{suffix}.svg"
        result[path] = reduce_snake_motion.render(read(path), theme, dark)
        result[f"assets/contributions/snake{suffix}-static.svg"] = static_svg(result[path], {"s", "u"})
    for name, applier, fallback_gen in (
        ("github.svg", update_stats.apply_theme, update_stats.render_fallback),
        ("languages.svg", update_stats.apply_languages_theme, update_stats.render_languages_fallback),
        ("streak.svg", update_stats.apply_streak_theme, update_stats.render_streak_fallback),
    ):
        target = root / f"assets/stats/{name}"
        if target.is_file():
            source = target.read_text(encoding="utf-8")
            fallback = ET.fromstring(source).get("data-profile-stats") == "unavailable"
        else:
            fallback = True
        result[f"assets/stats/{name}"] = (
            fallback_gen(profile, theme) if fallback
            else applier(source, theme)
        )
    return result


def build(root=ROOT, check=False):
    generated = artifacts(root)
    stale = []
    for name, content in generated.items():
        path = root / name
        if isinstance(content, bytes):
            is_same = path.is_file() and path.read_bytes() == content
            if not is_same:
                stale.append(name)
                if not check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
        else:
            is_same = path.is_file() and path.read_text(encoding="utf-8") == content
            if not is_same:
                stale.append(name)
                if not check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
        if not is_same:
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
