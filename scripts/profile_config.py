"""Validated, shared inputs for the profile's local generators and workflows."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
COLOR_KEYS = (
    "background", "surface", "accent", "accent_light", "text", "text_secondary",
    "comment", "border", "control", "control_hover", "photo_shadow", "photo_mid",
    "photo_light",
)


def _require(condition, location, message):
    if not condition:
        raise ValueError(f"{location}: {message}")


def _string(value, location, empty=False):
    _require(isinstance(value, str) and (empty or bool(value.strip())),
             location, "expected a non-empty string" if not empty else "expected a string")
    _require(not any(ord(c) < 32 for c in value), location, "use a single line of text")


def _url(value, location, mail=False):
    _string(value, location)
    parsed = urlsplit(value)
    valid = parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
    if mail and parsed.scheme == "mailto":
        valid = bool(re.fullmatch(r"[^\s@?]+@[^\s@?]+\.[^\s@?]+", parsed.path))
    _require(valid and not any(c.isspace() for c in value), location,
             "expected an HTTPS URL" + (" or mailto address" if mail else ""))


def _object(value, location):
    _require(isinstance(value, dict), location, "expected an object")


def _list(value, location):
    _require(isinstance(value, list) and bool(value), location, "expected a non-empty list")


def _read(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"{path}: {error}") from error
    _object(data, str(path))
    return data


def load_theme(root=ROOT):
    path = root / "config/theme.json"
    theme = _read(path)
    for key in COLOR_KEYS + ("snake_dark", "snake_light"):
        value = theme.get(key)
        if key.startswith("snake_"):
            _require(isinstance(value, list) and len(value) == 5,
                     f"{path}:{key}", "expected five colors, from empty to highest activity")
            colors = value
        else:
            colors = [value]
        for color in colors:
            _require(isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color),
                     f"{path}:{key}", "expected #RRGGBB colors")
    return theme


def load_profile(root=ROOT):
    path = root / "config/profile.json"
    profile = _read(path)
    for key in ("username", "display_name", "title", "description"):
        _string(profile.get(key), f"{path}:{key}")
    _require(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", profile["username"]),
             f"{path}:username", "expected a GitHub username")
    terminal = profile.get("terminal")
    _object(terminal, f"{path}:terminal")
    for key in ("title", "command", "aside"):
        _string(terminal.get(key), f"{path}:terminal.{key}")
    _list(terminal.get("push_messages"), f"{path}:terminal.push_messages")
    for i, value in enumerate(terminal["push_messages"]):
        _string(value, f"{path}:terminal.push_messages[{i}]")

    collections = [
        ("terminal.fields", terminal.get("fields"), ("label", "value")),
        ("contacts", profile.get("contacts"), ("id", "label", "url")),
        ("projects", profile.get("projects"), ("name", "url", "description")),
        ("quotes", profile.get("quotes"), ("text", "author")),
    ]
    _list(profile.get("stack"), f"{path}:stack")
    for i, group in enumerate(profile["stack"]):
        _object(group, f"{path}:stack[{i}]")
        _string(group.get("category"), f"{path}:stack[{i}].category")
        collections.append((f"stack[{i}].items", group.get("items"), ("name", "logo", "url")))
    for name, items, keys in collections:
        _list(items, f"{path}:{name}")
        for i, item in enumerate(items):
            location = f"{path}:{name}[{i}]"
            _object(item, location)
            for key in keys:
                _string(item.get(key), f"{location}.{key}", empty=key == "logo")
            if "url" in keys:
                _url(item["url"], f"{location}.url", mail=name == "contacts")
    ids = [item["id"] for item in profile["contacts"]]
    _require(len(ids) == len(set(ids)), f"{path}:contacts", "IDs must be unique")
    stats = profile.get("stats")
    _object(stats, f"{path}:stats")
    _url(stats.get("endpoint"), f"{path}:stats.endpoint")
    _require(isinstance(stats.get("include_all_commits"), bool),
             f"{path}:stats.include_all_commits", "expected a boolean")
    widgets = profile.get("widgets")
    _object(widgets, f"{path}:widgets")
    for name in ("spotify", "wakatime"):
        widget = widgets.get(name)
        location = f"{path}:widgets.{name}"
        _object(widget, location)
        _require(isinstance(widget.get("enabled"), bool), location + ".enabled", "expected a boolean")
        for key in ("title", "caption"):
            _string(widget.get(key), f"{location}.{key}")
        for key in ("url", "image_url"):
            value = widget.get(key)
            _string(value, f"{location}.{key}", empty=not widget["enabled"])
            if value:
                _url(value, f"{location}.{key}")
    return profile
