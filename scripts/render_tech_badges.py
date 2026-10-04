"""Local technology badges for logos unavailable from the badge provider."""

from html import escape
from math import ceil
import xml.etree.ElementTree as ET

from profile_config import ROOT

LOCAL_LOGOS = {"java", "kitty"}
ET.register_namespace("", "http://www.w3.org/2000/svg")


def asset_path(item):
    if item["logo"] in LOCAL_LOGOS:
        return f'assets/tech-{item["logo"]}.svg'
    return None


def render(item, theme, source=None):
    if item["logo"] not in LOCAL_LOGOS:
        raise ValueError(f'No local logo for {item["logo"]}')
    if source is None:
        source = (ROOT / "assets" / "icons" / f'{item["logo"]}.svg').read_text(encoding="utf-8")
    icon = ET.fromstring(source)
    svg_ns = "{http://www.w3.org/2000/svg}"
    accent = theme["accent"]
    accent_light = theme.get("accent_light", accent)
    surface = theme["surface"]

    if item["logo"] == "java":
        for path in icon.iter(f"{svg_ns}path"):
            fill = path.get("fill")
            if fill == "#EA2D2E":
                path.set("fill", accent_light)
            else:
                path.set("fill", accent)
    elif item["logo"] == "kitty":
        for g in icon.findall(f".//{svg_ns}g"):
            for rect in list(g.findall(f"{svg_ns}rect")):
                g.remove(rect)
        for p in icon.iter(f"{svg_ns}path"):
            style = p.get("style", "")
            d = p.get("d", "")
            if "M67.896" in d:
                p.set("style", f"fill:{accent};stroke-width:1.4")
            elif "#784421" in style:
                p.set("style", f"fill:{accent};clip-rule:evenodd;fill-rule:evenodd")
            elif "#2b1100" in style:
                p.set("style", f"fill:{surface};clip-rule:evenodd;fill-rule:evenodd")
            elif "#483737" in style:
                p.set("style", f"fill:{surface};clip-rule:evenodd;fill-rule:evenodd")
            elif "#c0c81f" in style:
                p.set("style", f"fill:{accent_light};clip-rule:evenodd;fill-rule:evenodd")

    icon.attrib.update(x="4", y="1", width="18", height="18", **{"aria-hidden": "true"})
    artwork = ET.tostring(icon, encoding="unicode")
    label = escape(item["name"])
    width = ceil(33 + len(item["name"]) * 6.5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" viewBox="0 0 {width} 20" role="img" aria-labelledby="title" data-motion="static">
  <title id="title">{label}</title>
  <rect width="{width}" height="20" rx="3" fill="{theme['surface']}"/>
  {artwork}
  <text x="27" y="14" font-family="Verdana, DejaVu Sans, sans-serif" font-size="11" fill="{theme['text']}">{label}</text>
</svg>
'''
