"""Render the web card using the same identity and links as the README."""

from html import escape
from string import Template

from profile_icons import icon_for


def render(profile, theme, template):
    contacts = []
    for item in profile["contacts"]:
        icon = icon_for(item["id"])
        svg = f'<svg class="link-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{icon}</svg>'
        contacts.append(f'            <a class="link-item" href="{escape(item["url"], quote=True)}">'
                        f'{svg}<span>{escape(item["label"])}</span></a>')
        if item["id"] == "email" and item["url"].startswith("mailto:"):
            address = escape(item["url"][7:], quote=True)
            contacts.append(f'            <button class="link-item email-button" id="copy-email" '
                            f'type="button" data-email="{address}">{svg}<span>Copy email</span></button>')
    return Template(template).substitute(
        SURFACE=theme["surface"], TITLE=escape(profile["title"], quote=True),
        DESCRIPTION=escape(profile["description"], quote=True), CONTACTS="\n".join(contacts))
