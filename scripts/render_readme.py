"""Render GitHub-compatible Markdown without a runtime template dependency."""

import re
from html import escape
from string import Template
from urllib.parse import quote, urlencode

from render_tech_badges import asset_path
from render_quotes import CLOSING_MESSAGE


def markdown(value):
    """Escape plain config text, including table and blockquote delimiters."""
    value = escape(value, quote=False)
    return re.sub(r"([\\`*_{}\[\]()#!])", r"\\\1", value).replace("|", "&#124;")


def link_url(value):
    return quote(value, safe=":/?&=%@+,-._~#")


def render_badge(item, theme):
    local = asset_path(item)
    if local:
        return f'[![{markdown(item["name"])}]({local})]({link_url(item["url"])})'
    parameters = {
        "style": "flat", "label": "", "message": item["name"],
        "color": theme["surface"].lstrip("#"),
        "logoColor": theme["accent"].lstrip("#"),
    }
    if item["logo"]:
        parameters["logo"] = item["logo"]
    image = "https://img.shields.io/static/v1?" + urlencode(parameters, quote_via=quote)
    return f'[![{markdown(item["name"])}]({image})]({link_url(item["url"])})'


def render_widgets(widgets):
    sections = []
    for widget in widgets.values():
        if widget["enabled"]:
            title = markdown(widget["title"])
            sections.append(
                f'## {title}\n\n[![{title}]({link_url(widget["image_url"])})]'
                f'({link_url(widget["url"])})\n\n{markdown(widget["caption"])}\n')
    return "\n---\n\n" + "\n---\n\n".join(sections) if sections else ""


def render_project(project, index):
    """The outer link stays interactive when GitHub renders the SVG as an image."""
    alt = escape(f'{project["name"]} — {project["description"]}', quote=True)
    base = f"assets/project-{index:02d}"
    return (f'<a href="{escape(link_url(project["url"]), quote=True)}">\n'
            f'  <picture>\n'
            f'    <source media="(max-width: 600px)" srcset="{base}-mobile.svg">\n'
            f'    <img src="{base}.svg" width="100%" alt="{alt}">\n'
            f'  </picture>\n'
            f'</a>')


def render_interest(interest):
    alt = escape(f'{interest["title"]} — {interest["description"]}', quote=True)
    base = f'assets/interest-{interest["id"]}'
    return (f'<picture>\n'
            f'  <source media="(prefers-reduced-motion: reduce) and (max-width: 600px)" srcset="{base}-mobile-static.svg">\n'
            f'  <source media="(prefers-reduced-motion: reduce)" srcset="{base}-static.svg">\n'
            f'  <source media="(max-width: 600px)" srcset="{base}-mobile.svg">\n'
            f'  <img src="{base}.svg" width="100%" alt="{alt}">\n'
            f'</picture>')


def render(profile, theme, about, template):
    contacts = " ".join(
        f'[![{markdown(item["label"])}](assets/contact-{index:02d}.svg)]({link_url(item["url"])})'
        for index, item in enumerate(profile["contacts"], 1))
    stack = "\n\n".join(
        f'**{markdown(group["category"])}**\n\n'
        + " ".join(render_badge(item, theme) for item in group["items"])
        for group in profile["stack"])
    projects = "\n\n".join(render_project(item, index)
                           for index, item in enumerate(profile["projects"], 1))
    interests = "\n\n".join(render_interest(item)
                            for item in profile.get("interests", []))
    quotes_alt = "Hall of Fame. " + " ".join(
        f'{item["text"]} — {item["author"]}.' for item in profile["quotes"])
    quotes_alt += " " + CLOSING_MESSAGE
    if "caption" in profile["stats"]:
        stats_caption = markdown(profile["stats"]["caption"])
    else:
        period = "All-time commits" if profile["stats"]["include_all_commits"] else "Commit year is shown on the card"
        stats_caption = (f"{period}; rank and PR totals are reported by GitHub Readme Stats. "
                         "Updated daily when the provider is available.")
    return Template(template).substitute(
        BANNER_ALT=escape(profile["description"], quote=True), CONTACTS=contacts,
        ABOUT=about.strip(), STACK=stack, PROJECTS=projects,
        INTERESTS=interests,
        QUOTES_ALT=escape(quotes_alt, quote=True),
        GITHUB_URL=f'https://github.com/{profile["username"]}',
        STATS_CAPTION=stats_caption,
        WIDGETS=render_widgets(profile["widgets"]),
    )
