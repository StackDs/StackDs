"""Small, self-contained contact glyphs shared by the web card and badges."""

ICONS = {
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle class="icon-fill" cx="17.5" cy="6.8" r="1"/>',
    "psn": '<path d="M12 3.2 16.4 4.4c2.5.7 4.1 2.5 4.1 4.8v8.4c0 1.6-1.2 2.5-2.7 1.8l-3.4-1.6v-2.1l2.5 1.2V9.1c0-1.4-.7-2.3-2.1-2.7L12 5.5v14.9l-3.1-1.1V4.1z"/><path d="m4 16.3 4.5-1.7v2.2l-2.8 1 .9.4 1.9-.7v2.1l-2.1.8c-.7.2-1.4.2-2.1-.1l-1.5-.7c-1.3-.6-1.2-1.6.2-2.1l4.5-1.7"/>',
    "linkedin": '<path class="icon-fill" d="M5.2 3.2a2.1 2.1 0 1 0 0 4.2 2.1 2.1 0 0 0 0-4.2ZM3.4 9h3.7v11.8H3.4zM9.5 9h3.5v1.6h.1A3.8 3.8 0 0 1 16.5 8.7c3.8 0 4.5 2.5 4.5 5.7v6.4h-3.7v-5.7c0-1.4 0-3.2-2-3.2s-2.3 1.5-2.3 3.1v5.8H9.5z"/>',
    "email": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
    "discord": '<path d="M8 5 5 6C3 10 2 14 3 17l5 2 1-2M16 5l3 1c2 4 3 8 2 11l-5 2-1-2M7 7c3-1 7-1 10 0M6 16c4 2 8 2 12 0"/><ellipse cx="8.5" cy="12" rx="1" ry="1.5" class="icon-fill"/><ellipse cx="15.5" cy="12" rx="1" ry="1.5" class="icon-fill"/>',
    "steam": '<circle cx="16.5" cy="7.5" r="5"/><circle cx="16.5" cy="7.5" r="2.5"/><circle cx="7" cy="17" r="3.5"/><path d="m1 13 7 3M1 16l5 3M9 14l3-6M10 18l7-5"/>',
}

LINK = '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-2 2M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l2-2"/>'


def icon_for(identifier):
    return ICONS.get(identifier, LINK)
