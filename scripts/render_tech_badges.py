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
    icon.attrib.update(x="4", y="1", width="18", height="18", **{"aria-hidden": "true"})
    artwork = ET.tostring(icon, encoding="unicode")
    backdrop = ('<rect x="4" y="1" width="18" height="18" rx="2" fill="#F4F4F4"/>'
                if item["logo"] == "kitty" else "")
    label = escape(item["name"])
    width = ceil(33 + len(item["name"]) * 6.5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" viewBox="0 0 {width} 20" role="img" aria-labelledby="title" data-motion="static">
  <title id="title">{label}</title>
  <rect width="{width}" height="20" rx="3" fill="{theme['surface']}"/>
  {backdrop}
  {artwork}
  <text x="27" y="14" font-family="Verdana, DejaVu Sans, sans-serif" font-size="11" fill="{theme['text']}">{label}</text>
</svg>
'''
