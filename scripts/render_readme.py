"""Render GitHub-compatible Markdown without a runtime template dependency."""

import re
from html import escape
from string import Template
from urllib.parse import quote, urlencode


def markdown(value):
    """Escape plain config text, including table and blockquote delimiters."""
    value = escape(value, quote=False)
    return re.sub(r"([\\`*_{}\[\]()#!])", r"\\\1", value).replace("|", "&#124;")


def link_url(value):
    return quote(value, safe=":/?&=%@+,-._~#")


def render_badge(item, theme):
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
    return "\n" + "\n".join(sections) if sections else ""


def render(profile, theme, about, template):
    contacts = " · ".join(
        f'[{markdown(item["label"])}]({link_url(item["url"])})'
        for item in profile["contacts"])
    stack = "\n\n".join(
        f'**{markdown(group["category"])}**\n\n'
        + " ".join(render_badge(item, theme) for item in group["items"])
        for group in profile["stack"])
    projects = "\n".join(
        f'| [{markdown(item["name"])}]({link_url(item["url"])}) | '
        f'{markdown(item["description"])} |' for item in profile["projects"])
    quotes = "\n\n".join(
        f'> "{markdown(item["text"])}" — *{markdown(item["author"])}*'
        for item in profile["quotes"])
    period = "All-time commits" if profile["stats"]["include_all_commits"] else "Commit year is shown on the card"
    return Template(template).substitute(
        BANNER_ALT=escape(profile["description"], quote=True), CONTACTS=contacts,
        ABOUT=about.strip(), STACK=stack, PROJECTS=projects, QUOTES=quotes,
        GITHUB_URL=f'https://github.com/{profile["username"]}',
        STATS_CAPTION=f"{period}; rank and PR totals are reported by GitHub Readme Stats. "
                      "Updated daily when the provider is available.",
        WIDGETS=render_widgets(profile["widgets"]),
    )
