#!/usr/bin/env python3
"""Fetch a validated GitHub Readme Stats snapshot; retain the last good card."""

import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import escape
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from profile_config import ROOT, load_profile, load_theme

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
MAX_BYTES = 1_000_000


def stats_url(profile, theme):
    endpoint = urlsplit(profile["stats"]["endpoint"])
    params = dict(parse_qsl(endpoint.query))
    params.update({
        "username": profile["username"], "show_icons": "true", "hide_rank": "false",
        "hide": "stars,issues,contribs", "include_all_commits": str(profile["stats"]["include_all_commits"]).lower(),
        "disable_animations": "true", "locale": "en", "card_width": "450",
        "custom_title": f'{profile["display_name"]} — GitHub Stats',
        "bg_color": theme["surface"][1:], "title_color": theme["accent"][1:],
        "icon_color": theme["accent"][1:], "ring_color": theme["accent"][1:],
        "text_color": theme["text"][1:], "border_color": theme["border"][1:],
    })
    if not profile["stats"]["include_all_commits"]:
        params["commits_year"] = str(datetime.now(timezone.utc).year)
    else:
        params.pop("commits_year", None)
    return urlunsplit(endpoint._replace(query=urlencode(params)))


def validate_svg(source):
    if len(source.encode("utf-8")) > MAX_BYTES or "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("Invalid or oversized statistics response")
    root = ET.fromstring(source)
    if root.tag != f"{{{SVG}}}svg":
        raise ValueError("Statistics provider did not return an SVG")
    ids = {element.get("data-testid") for element in root.iter()}
    if not {"commits", "prs", "rank-circle", "card-bg"}.issubset(ids):
        raise ValueError("Statistics response is an error card or is missing commits, PRs, or rank")
    for stat in ("commits", "prs"):
        node = root.find(f'.//*[@data-testid="{stat}"]')
        if not "".join(node.itertext()).strip():
            raise ValueError(f"Statistics response has no {stat} value")
    return root


def render_fallback(profile, theme):
    title = escape(f'{profile["display_name"]} — GitHub Stats')
    return f'''<svg xmlns="{SVG}" width="450" height="128" viewBox="0 0 450 128" role="img" aria-labelledby="title desc" data-profile-stats="unavailable">
  <title id="title">{title}</title>
  <desc id="desc">Statistics are temporarily unavailable. Follow the link to the GitHub profile.</desc>
  <rect x="0.5" y="0.5" width="449" height="127" rx="8" fill="{theme['surface']}" stroke="{theme['border']}"/>
  <g font-family="DejaVu Sans, sans-serif" font-size="13" fill="{theme['text']}">
    <text x="24" y="34" font-size="18" fill="{theme['accent']}">{title}</text>
    <text x="24" y="67">Statistics are temporarily unavailable.</text>
    <text x="24" y="94">View my GitHub profile — automatic updates run daily.</text>
  </g>
</svg>
'''


def apply_theme(source, theme):
    """Recolor the cached card offline when the shared theme changes."""
    root = validate_svg(source)
    for old in list(root.findall(f'{{{SVG}}}style[@id="profile-theme"]')):
        root.remove(old)
    background = root.find('.//*[@data-testid="card-bg"]')
    background.set("fill", theme["surface"])
    background.set("stroke", theme["border"])
    style = ET.SubElement(root, f"{{{SVG}}}style", {"id": "profile-theme"})
    style.text = (
        f'.header, .icon {{ fill: {theme["accent"]}; }}'
        f'.stat, .rank-text {{ fill: {theme["text"]}; }}'
        f'.rank-circle, .rank-circle-rim {{ stroke: {theme["accent"]}; }}'
        '* { animation-duration: 0s !important; animation-delay: 0s !important; }'
    )
    return ET.tostring(root, encoding="unicode") + "\n"


def fetch_svg(url):
    request = Request(url, headers={"User-Agent": "StackDs-profile", "Accept": "image/svg+xml"})
    with urlopen(request, timeout=30) as response:
        if response.headers.get_content_type() != "image/svg+xml":
            raise ValueError("Statistics provider did not send image/svg+xml")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Statistics response exceeds 1 MB")
    return data.decode("utf-8")


def update(profile, theme, target, fetch=fetch_svg):
    try:
        result = apply_theme(fetch(stats_url(profile, theme)), theme)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Statistics update unavailable: {error}. Keeping the last valid card.", file=sys.stderr)
        if target.is_file():
            try:
                validate_svg(target.read_text(encoding="utf-8"))
                return False
            except (ValueError, ET.ParseError):
                pass
        result = render_fallback(profile, theme)
        success = False
    else:
        success = True
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".svg.tmp")
    temporary.write_text(result, encoding="utf-8")
    temporary.replace(target)
    return success


if __name__ == "__main__":
    success = update(load_profile(), load_theme(), ROOT / "assets/stats/github.svg")
    print("Statistics updated." if success else "Using a cached card or the local unavailable state.")
