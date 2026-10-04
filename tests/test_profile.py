"""Offline checks for configuration, rendering and last-good activity snapshots."""

import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_profile
from profile_config import load_profile, load_theme
import reduce_snake_motion
import render_readme
import render_site
import render_terminal
import render_theme
import update_stats
from svg_motion import static_svg

SVG = "{http://www.w3.org/2000/svg}"
VALID_STATS = f'''<svg xmlns="{SVG[1:-1]}" viewBox="0 0 450 150">
<rect data-testid="card-bg"/><text class="header">Stack</text>
<g data-testid="rank-circle"><text>B</text></g>
<text data-testid="commits">123</text><text data-testid="prs">4</text>
</svg>'''


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = load_profile()
        self.theme = load_theme()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def config_copy(self):
        shutil.copytree(ROOT / "config", self.root / "config")

    def test_config_reports_file_and_field(self):
        self.config_copy()
        path = self.root / "config/theme.json"
        for invalid in ("blue", "#123", None, 42):
            with self.subTest(invalid=invalid):
                theme = {**self.theme, "accent": invalid}
                path.write_text(json.dumps(theme))
                with self.assertRaisesRegex(ValueError, r"theme.json:accent"):
                    load_theme(self.root)

    def test_profile_validates_links_and_enabled_widgets(self):
        self.config_copy()
        path = self.root / "config/profile.json"
        invalid = copy.deepcopy(self.profile)
        invalid["contacts"][0]["url"] = "javascript:alert(1)"
        path.write_text(json.dumps(invalid))
        with self.assertRaisesRegex(ValueError, r"profile.json:contacts\[0\].url"):
            load_profile(self.root)
        invalid = copy.deepcopy(self.profile)
        invalid["widgets"]["spotify"]["enabled"] = True
        path.write_text(json.dumps(invalid))
        with self.assertRaisesRegex(ValueError, r"widgets.spotify.url"):
            load_profile(self.root)

    def test_badge_url_preserves_cplusplus(self):
        item = self.profile["stack"][0]["items"][1]
        badge = render_readme.render_badge(item, self.theme)
        self.assertIn("message=C%2B%2B", badge)
        self.assertIn("color=0F1419", badge)
        self.assertIn("logoColor=088DDC", badge)
        self.assertIn("](https://isocpp.org/)", badge)

    def test_push_messages_require_nonempty_list_of_single_line_strings(self):
        self.config_copy()
        path = self.root / "config/profile.json"
        for messages in (None, [], "a string", [""], [42], ["line\nbreak"]):
            with self.subTest(messages=messages):
                profile = copy.deepcopy(self.profile)
                profile["terminal"]["push_messages"] = messages
                path.write_text(json.dumps(profile))
                with self.assertRaisesRegex(ValueError, r"terminal.push_messages"):
                    load_profile(self.root)

    def test_plain_text_is_escaped_in_markdown_and_html(self):
        self.profile["projects"][0]["name"] = "Demo | [link] <tag>"
        self.profile["quotes"][0]["text"] = "<script> & *not italic*"
        self.profile["description"] = 'A "quote" & <tag>'
        result = render_readme.render(self.profile, self.theme, "About", (ROOT / "templates/README.md.tpl").read_text())
        self.assertIn("Demo | [link] &lt;tag&gt;", result)
        self.assertIn("&lt;script&gt; &amp; *not italic*", result)
        self.assertIn('alt="A &quot;quote&quot; &amp; &lt;tag&gt;"', result)
        self.assertIn('src="assets/quotes.svg"', result)
        self.assertNotIn("<script>", result)

    def test_widgets_are_opt_in(self):
        self.assertEqual("", render_readme.render_widgets(self.profile["widgets"]))
        widget = self.profile["widgets"]["spotify"]
        widget.update(enabled=True, image_url="https://example.com/card.svg", url="https://example.com/music")
        result = render_readme.render_widgets(self.profile["widgets"])
        self.assertIn("## Now Playing", result)
        self.assertIn("card.svg", result)
        self.assertNotIn("Coding Activity", result)

    def test_banner_wraps_long_values_and_escapes_xml(self):
        value = 'Teaching <C> & "Python" with custom tools ' * 8
        self.profile["terminal"]["fields"][0]["value"] = value
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                source = render_terminal.render(mobile, art=["@@", "@@"], profile=self.profile, theme=self.theme)
                root = ET.fromstring(source)
                self.assertEqual("en", root.get("{http://www.w3.org/XML/1998/namespace}lang"))
                values = root.findall(f'{SVG}text[@class="typed"]')
                for node in values:
                    self.assertLess(float(node.get("y")), float(root.get("height")))
                    for span in node.findall(f"{SVG}tspan"):
                        self.assertLess(float(span.get("x")) + float(node.get("font-size")) * .602,
                                        float(root.get("width")) - (24 if mobile else 36) + 1)
                self.assertIn("&lt;", source)
                self.assertNotIn("__CHAR_ANIMATION_", source)
                self.assertNotIn('id="about-heading"', source)
                self.assertNotIn('id="quote-', source)
                self.assertIn("prefers-reduced-motion: reduce", source)

    def test_theme_change_reaches_every_renderer(self):
        theme = {**self.theme, "accent": "#AB1234"}
        self.assertIn("--accent: #AB1234", render_theme.render(theme))
        self.assertIn('stroke="#AB1234"', render_terminal.render(art=["@@"], profile=self.profile, theme=theme))
        self.assertIn("logoColor=AB1234", render_readme.render_badge(self.profile["stack"][0]["items"][0], theme))
        self.assertIn("--cs:#AB1234", reduce_snake_motion.render((ROOT / "assets/contributions/snake.svg").read_text(), theme))
        self.assertIn("#AB1234", update_stats.apply_theme(VALID_STATS, theme))
        params = parse_qs(urlsplit(update_stats.stats_url(self.profile, theme)).query)
        self.assertEqual(["AB1234"], params["ring_color"])

    def test_site_uses_configured_email_and_escaped_identity(self):
        next(item for item in self.profile["contacts"] if item["id"] == "email")["url"] = "mailto:example@example.org"
        self.profile["title"] = 'Stack <&> "Profile"'
        source = render_site.render(self.profile, self.theme, (ROOT / "templates/site.html.tpl").read_text())
        self.assertIn('data-email="example@example.org"', source)
        self.assertIn('href="mailto:example@example.org"', source)
        self.assertIn('Stack &lt;&amp;&gt; &quot;Profile&quot;', source)
        self.assertNotIn("stackctrlz@gmail.com", source)

    def test_snake_postprocessing_is_idempotent_and_preserves_levels(self):
        for suffix, dark in (("", False), ("-dark", True)):
            original = (ROOT / f"assets/contributions/snake{suffix}.svg").read_text()
            first = reduce_snake_motion.render(original, self.theme, dark)
            self.assertEqual(first, reduce_snake_motion.render(first, self.theme, dark))
            before, after = ET.fromstring(original), ET.fromstring(first)
            self.assertEqual([e.attrib for e in before.findall(f"{SVG}rect")],
                             [e.attrib for e in after.findall(f"{SVG}rect")])
            self.assertIsNone(after.find(f'{SVG}style[@id="profile-reduced-motion"]'))
            self.assertTrue(after.findall(f'{SVG}rect[@class="s s0"]'))

    def test_stats_reject_error_cards_even_when_valid_svg(self):
        for source in ("<html>Unavailable</html>", f'<svg xmlns="{SVG[1:-1]}"><text>Something went wrong!</text></svg>', "not XML"):
            with self.subTest(source=source):
                with self.assertRaises((ValueError, ET.ParseError)):
                    update_stats.validate_svg(source)

    def test_static_banners_preserve_all_text_without_smil(self):
        source = render_terminal.render(art=["@@"], profile=self.profile, theme=self.theme)
        animated, static = ET.fromstring(source), ET.fromstring(static_svg(source))
        self.assertEqual("static", static.get("data-motion"))
        self.assertEqual([], static.findall(f".//{SVG}animate"))
        self.assertEqual([], static.findall('.//*[@class="cursor motion"]'))
        for before, after in zip(animated.findall(f"{SVG}text"), static.findall(f"{SVG}text")):
            self.assertEqual("".join(before.itertext()), "".join(after.itertext()))
        snake = static_svg((ROOT / "assets/contributions/snake.svg").read_text(), {"s", "u"})
        snake_root = ET.fromstring(snake)
        self.assertFalse(any({"s", "u"}.intersection(e.get("class", "").split()) for e in snake_root.iter()))
        self.assertTrue(snake_root.findall(f'{SVG}rect[@class="c"]'))

    def test_stats_failure_preserves_last_good_bytes(self):
        target = self.root / "github.svg"
        target.write_text(VALID_STATS)
        original = target.read_bytes()
        for failure in (lambda url: "<html>Rate limited</html>", self.network_failure):
            with redirect_stderr(io.StringIO()):
                self.assertFalse(update_stats.update(self.profile, self.theme, target, fetch=failure))
            self.assertEqual(original, target.read_bytes())

    @staticmethod
    def network_failure(url):
        raise OSError("Network unavailable")

    def test_first_stats_failure_produces_local_fallback(self):
        target = self.root / "stats/github.svg"
        with redirect_stderr(io.StringIO()):
            self.assertFalse(update_stats.update(self.profile, self.theme, target, fetch=self.network_failure))
        root = ET.fromstring(target.read_text())
        self.assertEqual("unavailable", root.get("data-profile-stats"))
        self.assertIn("Statistics are temporarily unavailable", target.read_text())

    def test_stats_success_replaces_fallback_and_is_idempotent(self):
        target = self.root / "stats/github.svg"
        self.assertTrue(update_stats.update(self.profile, self.theme, target, fetch=lambda url: VALID_STATS))
        first = target.read_text()
        self.assertEqual(first, update_stats.apply_theme(first, self.theme))
        update_stats.validate_svg(first)
        self.assertFalse(target.with_suffix(".svg.tmp").exists())
        params = parse_qs(urlsplit(update_stats.stats_url(self.profile, self.theme)).query)
        self.assertIn("commits_year", params)
        self.assertEqual(["false"], params["include_all_commits"])

    def copy_build_inputs(self):
        for name in ("config", "content", "templates", "assets/contributions", "assets/icons"):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copyfile(ROOT / "ascii.txt", self.root / "ascii.txt")

    def snapshot(self):
        return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def test_build_is_deterministic_and_check_never_writes(self):
        self.copy_build_inputs()
        with redirect_stdout(io.StringIO()):
            self.assertTrue(build_profile.build(self.root))
            first = self.snapshot()
            self.assertTrue(build_profile.build(self.root))
            self.assertEqual(first, self.snapshot())
            self.assertTrue(build_profile.build(self.root, check=True))
            (self.root / "content/about.md").write_text("A changed biography.\n")
            before_check = self.snapshot()
            self.assertFalse(build_profile.build(self.root, check=True))
            self.assertEqual(before_check, self.snapshot())

    def test_invalid_configuration_writes_nothing(self):
        self.copy_build_inputs()
        (self.root / "config/theme.json").write_text('{"accent": "bad"}')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            build_profile.build(self.root)
        self.assertEqual(before, self.snapshot())

    def test_default_render_needs_no_third_party_packages(self):
        result = subprocess.run(
            [sys.executable, "-S", "-c", 'import sys; sys.path.insert(0, "scripts"); import render_terminal; print(render_terminal.render(art=["@@"])[:4])'],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("<svg", result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
