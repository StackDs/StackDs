"""Content, layout and playback contracts for the README's SVG panels."""

import copy
import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from profile_config import load_profile, load_theme
import build_profile
import render_contact_badges
import render_project_cards
import render_quotes
import render_readme
import render_terminal
import render_tech_badges
from svg_motion import static_svg

SVG = "{http://www.w3.org/2000/svg}"


def visible_text(root):
    return ["".join(node.itertext()) for node in root.iter(f"{SVG}text")]


class TerminalPanelTests(unittest.TestCase):
    def setUp(self):
        self.profile = load_profile()
        self.theme = load_theme()

    def assert_single_reveal(self, root):
        animations = list(root.iter(f"{SVG}animate"))
        self.assertTrue(animations)
        for animation in animations:
            self.assertNotEqual("indefinite", animation.get("repeatCount"))
            if animation.get("attributeName") == "opacity" and animation.get("values"):
                # The scanline may disappear; text and cursor must stay visible.
                if animation.get("class") == "reveal":
                    values = list(map(float, animation.get("values").split(";")))
                    self.assertEqual(sorted(values), values)
                    self.assertEqual(1, values[-1])

    def test_intro_cycles_through_typing_hold_reverse_erasure_and_restart(self):
        for mobile in (False, True):
            root = ET.fromstring(render_terminal.render(
                mobile, art=["@@"], profile=self.profile, theme=self.theme))
            chars = root.findall(f'.//{SVG}tspan[@class="typed-char"]')
            reveals, erasures, durations = [], [], set()
            for char in chars:
                animation = char.find(f"{SVG}animate")
                self.assertEqual("indefinite", animation.get("repeatCount"))
                self.assertEqual("0;1;0;0", animation.get("values"))
                self.assertEqual("remove", animation.get("fill"))
                duration = float(animation.get("dur")[:-1])
                durations.add(duration)
                events = [float(t) * duration for t in animation.get("keyTimes").split(";")]
                reveals.append(events[1])
                erasures.append(events[2])
            self.assertEqual(1, len(durations))
            self.assertEqual(sorted(reveals), reveals)
            self.assertEqual(sorted(erasures, reverse=True), erasures)
            # Erasure begins after a 4s hold, with one character tick to delete.
            self.assertAlmostEqual(4.017, min(erasures) - max(reveals), places=5)
            self.assertAlmostEqual(.7, duration - max(erasures), places=5)
            cursor = root.find(f'{SVG}rect[@id="terminal-cursor"]')
            for animation in cursor.findall(f"{SVG}animate"):
                self.assertEqual("indefinite", animation.get("repeatCount"))
                self.assertEqual(duration, float(animation.get("dur")[:-1]))
            opacity = cursor.find(f'{SVG}animate[@attributeName="opacity"]')
            self.assertEqual("0.000", opacity.get("values").split(";")[-1])
            static = ET.fromstring(static_svg(ET.tostring(root, encoding="unicode")))
            self.assertEqual(visible_text(root), visible_text(static))
            self.assertFalse(list(static.iter(f"{SVG}animate")))

    def test_push_messages_are_escaped_wrapped_and_rendered_in_order(self):
        messages = ['Last in, first out.', 'Quoted "value" & <C++> \\ path ' * 8]
        self.profile["terminal"]["push_messages"] = messages
        for mobile in (False, True):
            source = render_terminal.render(mobile, art=["@@"], profile=self.profile, theme=self.theme)
            root = ET.fromstring(source)
            groups = root.findall(f'{SVG}g[@class="push-command"]')
            self.assertEqual(len(messages), len(groups))
            for message, group in zip(messages, groups):
                self.assertEqual(f'~ $ stack.push({json.dumps(message, ensure_ascii=False)});',
                                 "".join(visible_text(group)))
                for line in group.findall(f"{SVG}text"):
                    self.assertLess(float(line.get("y")), float(root.get("height")) - 20)
                    for span in line.findall(f"{SVG}tspan"):
                        self.assertLess(float(span.get("x")) + 14 * .602,
                                        float(root.get("width")) - (24 if mobile else 36) + 1)
            self.assertNotIn("Learn. Teach. Build.", source)
            self.assertNotIn("Code / Guitar / Bass", source)

    def test_quotes_preserve_order_and_all_content_in_static_variants(self):
        for mobile in (False, True):
            source = render_quotes.render(self.profile, self.theme, mobile)
            root, static = ET.fromstring(source), ET.fromstring(static_svg(source))
            self.assert_single_reveal(root)
            self.assertEqual(visible_text(root), visible_text(static))
            self.assertFalse(list(static.iter(f"{SVG}animate")))
            self.assertIsNone(static.find('.//*[@id="terminal-cursor"]'))
            closing = root.find(f'{SVG}text[@id="closing-prompt"]')
            self.assertEqual("~ $ Gobernar es Educar - Pedro Aguirre Cerda.",
                             "".join(closing.itertext()))
            final_quote_time = max(float(node.get("dur")[:-1])
                                   for node in root.findall(f'.//{SVG}g[@class="quote"]//{SVG}animate'))
            closing_times = [float(node.get("dur")[:-1]) for node in closing.iter(f"{SVG}animate")]
            self.assertGreater(min(closing_times), final_quote_time)
            self.assertEqual(sorted(set(closing_times)), closing_times)
            for span in closing.findall(f"{SVG}tspan"):
                self.assertLess(float(span.get("x")) + 14 * .602,
                                float(root.get("width")) - (24 if mobile else 36))
            groups = root.findall(f'{SVG}g[@class="quote"]')
            self.assertEqual(len(self.profile["quotes"]), len(groups))
            for quote, group in zip(self.profile["quotes"], groups):
                lines = visible_text(group)
                self.assertEqual(quote["text"], " ".join(lines[:-1]))
                self.assertEqual("— " + quote["author"], lines[-1])

    def test_quotes_wrap_long_text_and_authors_without_xml_injection(self):
        profile = copy.deepcopy(self.profile)
        profile["quotes"] = [{"text": '<script> & "quotes" ' * 20,
                              "author": "Author " * 40}]
        for mobile in (False, True):
            source = render_quotes.render(profile, self.theme, mobile)
            root = ET.fromstring(source)
            self.assertNotIn("<script>", source)
            margin = 24 if mobile else 36
            width, height = float(root.get("width")), float(root.get("height"))
            lines = root.findall(f'.//{SVG}g[@class="quote"]/{SVG}text')
            self.assertGreater(len(lines), 4)
            for line in lines:
                self.assertLess(float(line.get("y")), height - 20)
                end = float(line.get("x")) + len("".join(line.itertext())) * 14 * .602
                self.assertLessEqual(end, width - margin)

    def test_project_cards_wrap_names_and_descriptions_and_are_static(self):
        project = {"name": 'Very-long-project-<&>-name' * 6,
                   "description": 'A description with <C++> & "Python". ' * 15}
        for mobile in (False, True):
            source = render_project_cards.render(project, self.theme, mobile)
            root = ET.fromstring(source)
            self.assertEqual("static", root.get("data-motion"))
            self.assertFalse(list(root.iter(f"{SVG}animate")))
            self.assertNotIn("<C++>", source)
            title = root.find(f"{SVG}title")
            self.assertEqual(project["name"], title.text)
            lines = list(root.iter(f"{SVG}text"))
            self.assertEqual(project["name"], "".join(
                line.text for line in lines if line.get("font-size") == "18"))
            margin = 24 if mobile else 36
            for line in lines:
                end = float(line.get("x")) + len(line.text) * float(line.get("font-size")) * .602
                self.assertLessEqual(end, float(root.get("width")) - margin)
                self.assertLess(float(line.get("y")), float(root.get("height")) - 20)

    def test_contact_badges_are_local_static_and_support_unknown_contacts(self):
        contacts = self.profile["contacts"] + [{"id": "custom", "label": '<&> "New"'}]
        for contact in contacts:
            root = ET.fromstring(render_contact_badges.render(contact, self.theme))
            self.assertEqual(contact["label"], root.find(f"{SVG}title").text)
            self.assertEqual("static", root.get("data-motion"))
            self.assertFalse(list(root.iter(f"{SVG}animate")))
            self.assertFalse(list(root.iter(f"{SVG}image")))

    def test_java_and_kitty_badges_embed_local_artwork(self):
        java = next(item for group in self.profile["stack"] for item in group["items"]
                    if item["name"] == "Java")
        self.assertEqual('[![Java](assets/tech-java.svg)](https://dev.java/)',
                         render_readme.render_badge(java, self.theme))
        theme = {**self.theme, "accent": "#ABCDEF"}
        source = render_tech_badges.render(java, theme)
        root = ET.fromstring(source)
        self.assertEqual("Java", root.find(f"{SVG}title").text)
        colors = {node.get("fill") for node in root.iter(f"{SVG}path")}
        self.assertIn("#0074BD", colors)
        self.assertIn("#EA2D2E", colors)
        self.assertEqual("18", root.find(f"{SVG}svg").get("height"))
        self.assertFalse(list(root.iter(f"{SVG}image")))
        kitty = next(item for group in self.profile["stack"] for item in group["items"]
                     if item["name"] == "Kitty")
        self.assertEqual('[![Kitty](assets/tech-kitty.svg)](https://sw.kovidgoyal.net/kitty/)',
                         render_readme.render_badge(kitty, self.theme))
        root = ET.fromstring(render_tech_badges.render(kitty, self.theme))
        self.assertIsNotNone(root.find(f'{SVG}rect[@fill="#F4F4F4"]'))
        self.assertTrue(list(root.find(f"{SVG}svg").iter(f"{SVG}path")))
        self.assertFalse(list(root.iter(f"{SVG}image")))

    def test_readme_preserves_links_and_quotes_are_last_even_with_widgets(self):
        self.profile["widgets"]["spotify"].update(
            enabled=True, url="https://example.org/music", image_url="https://example.org/card.svg")
        source = render_readme.render(self.profile, self.theme, "A biography.",
                                     (ROOT / "templates/README.md.tpl").read_text())
        headings = re.findall(r"^## (.+)$", source, re.MULTILINE)
        self.assertEqual([
            "Contact", "About Me", "Tech Stack", "Featured Projects",
            "Activity & Contributions", "Now Playing", "Hall of Fame",
        ], headings)
        for index, contact in enumerate(self.profile["contacts"], 1):
            self.assertIn(f'[![{contact["label"]}](assets/contact-{index:02d}.svg)]({contact["url"]})', source)
        for index, project in enumerate(self.profile["projects"], 1):
            self.assertIn(f'<a href="{project["url"]}">', source)
            self.assertIn(f'src="assets/project-{index:02d}.svg"', source)
            self.assertIn(f'srcset="assets/project-{index:02d}-mobile.svg"', source)
        self.assertIn("A biography.", source)
        self.assertIn("snake-static.svg", source)
        self.assertIn("snake-dark-static.svg", source)
        self.assertIn('src="assets/contributions/snake.svg"', source)
        self.assertIn('media="(prefers-color-scheme: dark)" srcset="assets/contributions/snake-dark.svg"', source)
        self.assertIn('media="(prefers-reduced-motion: reduce)" srcset="assets/contributions/snake-static.svg"', source)
        self.assertNotIn("Code Philosophy", source)
        self.assertNotIn("opening_brace_on_same_line", source)
        self.assertIn("Gobernar es Educar - Pedro Aguirre Cerda.", source)
        self.assertEqual(7, source.count("\n---\n"))
        self.assertTrue(source.rstrip().endswith("</picture>"))
        self.assertNotIn("<details>", source)

    def test_build_generates_all_linked_panels_and_propagates_theme(self):
        artifacts = build_profile.artifacts()
        readme = artifacts["README.md"]
        paths = re.findall(r'(?:src|srcset)="(assets/[^"]+)"|\]\((assets/[^)]+)\)', readme)
        for candidates in paths:
            self.assertIn(next(path for path in candidates if path), artifacts)
        theme = {**self.theme, "accent": "#AB1234", "accent_light": "#FEDCBA"}
        for source in (
            render_quotes.render(self.profile, theme),
            render_project_cards.render(self.profile["projects"][0], theme),
            render_contact_badges.render(self.profile["contacts"][0], theme),
        ):
            self.assertIn("#FEDCBA", source)
        for name, source in artifacts.items():
            if name.startswith(("assets/contact-", "assets/project-", "assets/quotes")):
                ET.fromstring(source)


if __name__ == "__main__":
    unittest.main()
