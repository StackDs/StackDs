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


def languages_url(profile, theme):
    base = profile.get("stats", {}).get("endpoint", "https://github-readme-stats.vercel.app/api")
    endpoint = urlsplit(base.rstrip("/") + "/top-langs/")
    params = dict(parse_qsl(endpoint.query))
    params.update({
        "username": profile["username"],
        "layout": "compact",
        "card_width": "450",
        "disable_animations": "true",
        "locale": "en",
        "langs_count": str(profile.get("stats", {}).get("langs_count", 6)),
        "bg_color": theme["surface"][1:],
        "title_color": theme["accent"][1:],
        "text_color": theme["text"][1:],
        "border_color": theme["border"][1:],
    })
    return urlunsplit(endpoint._replace(query=urlencode(params)))


def streak_url(profile, theme):
    base = profile.get("stats", {}).get("streak_endpoint", "https://streak-stats.demolab.com")
    endpoint = urlsplit(base)
    params = dict(parse_qsl(endpoint.query))
    params.update({
        "user": profile["username"],
        "disable_animations": "true",
        "background": theme["surface"][1:],
        "border": theme["border"][1:],
        "stroke": theme["accent"][1:],
        "ring": theme["accent"][1:],
        "fire": theme["accent"][1:],
        "currStreakNum": theme["text"][1:],
        "sideNums": theme["text"][1:],
        "currStreakLabel": theme["accent"][1:],
        "sideLabels": theme["accent"][1:],
        "dates": theme["accent_light"][1:],
    })
    return urlunsplit(endpoint._replace(query=urlencode(params)))


def validate_languages_svg(source):
    if len(source.encode("utf-8")) > MAX_BYTES or "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("Invalid or oversized languages response")
    root = ET.fromstring(source)
    if root.tag != f"{{{SVG}}}svg":
        raise ValueError("Languages provider did not return an SVG")
    if "Most Used Languages" not in source and "lang-name" not in source:
        raise ValueError("Languages response is an error card or missing content")
    return root


def validate_streak_svg(source):
    if len(source.encode("utf-8")) > MAX_BYTES or "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("Invalid or oversized streak response")
    root = ET.fromstring(source)
    if root.tag != f"{{{SVG}}}svg":
        raise ValueError("Streak provider did not return an SVG")
    if "Total Contributions" not in source and "Current Streak" not in source:
        raise ValueError("Streak response is missing streak metrics")
    return root


def render_languages_fallback(profile, theme):
    title = escape(f'{profile["display_name"]} — Most Used Languages')
    return f'''<svg xmlns="{SVG}" width="450" height="165" viewBox="0 0 450 165" role="img" aria-labelledby="title desc" data-profile-stats="unavailable">
  <title id="title">{title}</title>
  <desc id="desc">Language statistics are temporarily unavailable.</desc>
  <rect x="0.5" y="0.5" width="449" height="164" rx="8" fill="{theme['surface']}" stroke="{theme['border']}"/>
  <g font-family="DejaVu Sans, sans-serif" font-size="13" fill="{theme['text']}">
    <text x="24" y="34" font-size="18" fill="{theme['accent']}">Most Used Languages</text>
    <text x="24" y="75">Language statistics are temporarily unavailable.</text>
    <text x="24" y="105">View my GitHub profile — automatic updates run daily.</text>
  </g>
</svg>
'''


def render_streak_fallback(profile, theme):
    title = escape(f'{profile["display_name"]} — Contribution Streak')
    return f'''<svg xmlns="{SVG}" width="495" height="195" viewBox="0 0 495 195" role="img" aria-labelledby="title desc" data-profile-stats="unavailable">
  <title id="title">{title}</title>
  <desc id="desc">Contribution streak is temporarily unavailable.</desc>
  <rect x="0.5" y="0.5" width="494" height="194" rx="8" fill="{theme['surface']}" stroke="{theme['border']}"/>
  <g font-family="DejaVu Sans, sans-serif" font-size="13" fill="{theme['text']}">
    <text x="24" y="45" font-size="18" fill="{theme['accent']}">Contribution Streak</text>
    <text x="24" y="95">Streak statistics are temporarily unavailable.</text>
    <text x="24" y="130">View my GitHub profile — automatic updates run daily.</text>
  </g>
</svg>
'''


def apply_languages_theme(source, theme):
    """Recolor the cached languages card offline when the shared theme changes."""
    root = validate_languages_svg(source)
    for old in list(root.findall(f'{{{SVG}}}style[@id="profile-theme"]')):
        root.remove(old)
    background = root.find('.//*[@data-testid="card-bg"]')
    if background is not None:
        background.set("fill", theme["surface"])
        background.set("stroke", theme["border"])
    style = ET.SubElement(root, f"{{{SVG}}}style", {"id": "profile-theme"})
    style.text = (
        f'.header {{ fill: {theme["accent"]} !important; }}'
        f'.lang-name, .stat {{ fill: {theme["text"]} !important; }}'
        '* { animation-duration: 0s !important; animation-delay: 0s !important; }'
    )
    return ET.tostring(root, encoding="unicode") + "\n"


def apply_streak_theme(source, theme):
    """Recolor the cached streak card offline when the shared theme changes."""
    root = validate_streak_svg(source)
    for old in list(root.findall(f'{{{SVG}}}style[@id="profile-theme"]')):
        root.remove(old)
    for rect in root.iter(f"{{{SVG}}}rect"):
        if rect.get("width") in {"494", "495", "100%"}:
            rect.set("fill", theme["surface"])
            rect.set("stroke", theme["border"])
            break
    style = ET.SubElement(root, f"{{{SVG}}}style", {"id": "profile-theme"})
    style.text = '* { animation-duration: 0s !important; animation-delay: 0s !important; }'
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


def update_languages(profile, theme, target, fetch=fetch_svg):
    try:
        result = apply_languages_theme(fetch(languages_url(profile, theme)), theme)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Languages update unavailable: {error}. Keeping the last valid card.", file=sys.stderr)
        if target.is_file():
            try:
                validate_languages_svg(target.read_text(encoding="utf-8"))
                return False
            except (ValueError, ET.ParseError):
                pass
        result = render_languages_fallback(profile, theme)
        success = False
    else:
        success = True
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".svg.tmp")
    temporary.write_text(result, encoding="utf-8")
    temporary.replace(target)
    return success


def update_streak(profile, theme, target, fetch=fetch_svg):
    try:
        result = apply_streak_theme(fetch(streak_url(profile, theme)), theme)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Streak update unavailable: {error}. Keeping the last valid card.", file=sys.stderr)
        if target.is_file():
            try:
                validate_streak_svg(target.read_text(encoding="utf-8"))
                return False
            except (ValueError, ET.ParseError):
                pass
        result = render_streak_fallback(profile, theme)
        success = False
    else:
        success = True
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".svg.tmp")
    temporary.write_text(result, encoding="utf-8")
    temporary.replace(target)
    return success


def update_all(profile, theme, root=ROOT, fetch=fetch_svg):
    target_dir = root / "assets/stats"
    res_github = update(profile, theme, target_dir / "github.svg", fetch=fetch)
    res_languages = update_languages(profile, theme, target_dir / "languages.svg", fetch=fetch)
    res_streak = update_streak(profile, theme, target_dir / "streak.svg", fetch=fetch)
    return {
        "github": res_github,
        "languages": res_languages,
        "streak": res_streak,
    }


if __name__ == "__main__":
    results = update_all(load_profile(), load_theme(), ROOT)
    print(f"Statistics updated: {results}")
