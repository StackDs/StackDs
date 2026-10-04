# Maintaining the profile

The profile is published in two places: the repository's `README.md` and the
[web contact card](https://stackds.github.io/StackDs/). Both use the same compact
terminal banners, identity, contact links, and color palette.

## Edit content or colors

1. Edit the relevant source:

   | Source | What to change |
   | --- | --- |
   | `content/about.md` | The About Me paragraphs; Markdown is supported. |
   | `config/profile.json` | Identity, terminal fields, contacts, technology groups, projects, quotes, stats endpoint, and optional widgets. |
   | `config/theme.json` | Shared `#RRGGBB` colors, including the five contribution levels for each snake variant. |
   | `ascii.txt` | Default avatar; preserve spaces and line breaks. |
   | `templates/README.md.tpl` | Section order, headings, separators, and contribution image selection. |
   | `scripts/render_quotes.py` | Closing terminal layout and quote reveal timing. |
   | `scripts/render_project_cards.py` | Static project card layout for desktop and mobile. |
   | `scripts/render_contact_badges.py` | Static contact badge layout. |
   | `scripts/render_tech_badges.py` | Local Java and Kitty badge layout. |
   | `assets/icons/` | Original-color Java and Kitty artwork and source credits. |
   | `scripts/profile_icons.py` | Logo artwork shared by the badges and web card. |
   | `templates/site.html.tpl` | Web card structure and interface copy. |
   | `site/styles.css` | Web layout and spacing; palette values come from generated `site/theme.css`. |

2. Regenerate from the repository root:

   ```sh
   python3 scripts/build_profile.py
   ```

3. Check the generated files:

   ```sh
   python3 -m unittest discover -s tests -v
   python3 scripts/build_profile.py --check
   git diff --check
   ```

4. Include the edited sources and their generated outputs in the same change.

Python **3.11 or newer** is supported. The normal build and offline tests use
only the standard library. No network request is made by `build_profile.py`.
`--check` exits with status 1 for stale or missing outputs and never writes them.
Configuration is validated and all outputs are rendered before any are written.

Generated outputs are `README.md`, `site/index.html`, `site/theme.css`, the
terminal, quote, and contribution SVGs (animated and static), the contact badges
(`assets/contact-NN.svg`), the project cards (`assets/project-NN.svg` and
`assets/project-NN-mobile.svg`), the local Java and Kitty badges (`assets/tech-java.svg`
and `assets/tech-kitty.svg`),
and `assets/stats/github.svg`.
Changes made directly to generated text or banners will be overwritten.
The snake and stats snapshots keep their existing activity data during a local
build; their colors and accessibility styling are reapplied offline.

JSON strings are plain text and are escaped for Markdown or HTML. Use
`content/about.md` and the templates when you want authored Markdown. Templates
use Python's `string.Template`: placeholders look like `$ABOUT`; write `$$` for a
literal dollar sign.

### Add a stack.push message to the opening card

Edit `terminal.push_messages` in `config/profile.json`. Each string produces one
command in the lower section of the card, in list order:

```json
"push_messages": [
  "Last in, first out.",
  "Your next message.",
  "Another message."
]
```

The generator adds `~ $ stack.push("...");` automatically. Enter only the message;
quotes and backslashes are escaped as string literals. Keep at least one nonempty,
single-line message. Long commands wrap and the card grows to fit them on desktop
and mobile. Regenerate with `python3 scripts/build_profile.py` after editing.

`push_messages` replaces the former `footer` and `interests` settings. The checked-in
configuration starts with only `Last in, first out.`; the extra lines above are
examples for adding your own messages.

### Add a technology, project, or quote

Add a technology to the appropriate `stack[].items` list:

```json
{"name": "C++", "logo": "cplusplus", "url": "https://isocpp.org/"}
```

`logo` is a Shields.io / Simple Icons identifier. Use an empty string for a
text-only badge, as with SDL3. `"logo": "java"` and `"logo": "kitty"` select local
badges using the SVG artwork in `assets/icons/`, embedded at 18px with original
colors. Java uses a blue cup with red steam; Kitty uses its upstream cat/terminal
logo on a light tile for contrast. URLs and
names, including `C++`, are encoded automatically. Badges use a flat style, the
shared surface color, and the shared accent for provider-hosted logos.

Add a project to `projects` with `name`, `url`, and a one-line `description`.
Each project becomes a static card with wrapped text and a link to its repository.
Keep the list to two to four projects for readability. Cards are numbered by
their position in the list and have separate desktop and mobile layouts.

Add quotes to `quotes` with separate `text` and `author` fields. They appear in
the final Hall of Fame terminal, in configuration order. The command types once,
then output appears line by line; all quotes remain visible after playback.
Long quotes and authors wrap, and the panel height grows to fit the content.

Contacts use `id`, `label`, and `url`. The README renders a local, static badge
for each contact, with a glyph and label. Unknown IDs use a generic link glyph.
Each badge and project card is wrapped in an ordinary link: links inside an SVG
embedded as an image cannot be clicked individually on GitHub.
The `email` contact's `mailto:` address is
also used by the web card's copy button. The ordinary email link remains usable
when JavaScript or the Clipboard API is unavailable.

The filled PlayStation and Steam paths in `scripts/profile_icons.py` are
vendored from Simple Icons (CC0-1.0); builds do not fetch them. Source snapshots:

- [PlayStation, 16.0.0](https://github.com/simple-icons/simple-icons/blob/16.0.0/icons/playstation.svg)
- [Steam, 16.0.0](https://github.com/simple-icons/simple-icons/blob/16.0.0/icons/steam.svg)

Java and Kitty artwork sources are documented in [`assets/icons/README.md`](assets/icons/README.md).

### README layout and motion

The section order is opening terminal, Contact, About Me, Tech Stack,
Featured Projects, Activity & Contributions, then Hall of Fame.
Horizontal Markdown rules separate the blocks. Enabled optional widgets appear
before Hall of Fame so the quotes always close the profile.

The opening and closing terminals and the contribution snake animate. The opening text repeats this
cycle: type character by character, hold for **4 seconds**, erase in reverse
order, pause for **700 ms**, then start again. Commands, profile fields, and all
`stack.push` messages share the cursor's timeline. The frame and avatar remain
visible; the avatar scan plays once. `HOLD_MS` and `RESTART_PAUSE_MS` in
`scripts/render_terminal.py` control the pauses.
The closing terminal reveals all quotes once, then types
`~ $ Gobernar es Educar - Pedro Aguirre Cerda.` into the final prompt. The phrase
and cursor remain visible after typing. Edit `CLOSING_MESSAGE` in
`scripts/render_quotes.py` to change this closing text.
Both use mobile layouts and static `<picture>` sources for reduced motion.
Static variants show all profile fields and push messages at once.
Animation starts when the browser loads the image; GitHub does not provide a
scroll-triggered playback mechanism for README images.

About Me remains native Markdown. Contact badges, technology
badges, project cards, and statistics are static.
Optional externally hosted widgets control their own motion.

## Regenerate the banner from a photo

The default avatar comes from `ascii.txt`. Photo modes are optional and need Pillow:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/render_terminal.py --photo
```

Use `--random` to choose from compatible images in `assets/images/`; the same
photo is used for both banner sizes. These modes are local previews: the
reproducible full build and CI expect the default ASCII avatar. Run
`python3 scripts/build_profile.py` to return to that version.

The SVG contains text, not an embedded copy of the photograph. Animation uses
SMIL and exposes the complete content in viewers without SMIL support. With
`prefers-reduced-motion: reduce`, the README and web card select `*-static.svg`
through `<picture>`. These variants have no SMIL nodes and disable CSS animation,
so embedded images do not depend on inheriting the host's media preference.
The animated files also include reduced-motion styles for direct viewing.
The avatar's aspect ratio is controlled by
`REFERENCE_ASPECT_RATIO` in `scripts/render_terminal.py`.

## Update activity data

### Contribution snake

`.github/workflows/contributions.yml` runs Platane/snk at **06:23 UTC daily**, on
relevant changes to `main`, and through manual dispatch. It reads the palette
using `scripts/reduce_snake_motion.py --outputs`, then postprocesses the result
with the same script. Postprocessing is idempotent; in reduced-motion mode it
shows the static contribution cells and hides the moving snake and progress bar.

The light and dark SVGs and their static counterparts are stored in
`assets/contributions/`. The README selects the animated snake by default,
uses a static calendar with `prefers-reduced-motion: reduce`, and chooses
its palette with `prefers-color-scheme`. Local generation only restyles those
snapshots; run **Actions → Update contribution snake → Run workflow** to refresh
the contribution data.

### GitHub statistics

Refresh the card locally:

```sh
python3 scripts/update_stats.py
```

`.github/workflows/stats.yml` does this at **06:43 UTC daily**, on relevant
changes to `main`, and through manual dispatch. It requests an English GitHub
Readme Stats card showing rank, commits, and PRs, with explicit shared colors.
By default, `commits_year` is the current UTC calendar year when the card is
fetched; the year remains printed on the cached card. Set
`stats.include_all_commits` to `true` for all-time commits.

The response must be an SVG containing the expected stats and rank elements.
Timeouts, HTML responses, malformed XML, and provider error cards cannot replace
a good snapshot. If there has never been a successful fetch, a local English
unavailable card is generated. The updater reports the problem and exits
successfully so a temporary provider outage does not break publication.

`stats.endpoint` can point at a compatible self-hosted GitHub Readme Stats
instance. Keep any provider credentials in that service's environment or in
GitHub Secrets, rather than in image URLs or this repository.

The two activity workflows share a concurrency group to avoid simultaneous bot
pushes. They use the automatic `GITHUB_TOKEN` and need `contents: write` plus
repository rules that allow their updates to `main`. Schedules can be delayed.
Their commits do not need to trigger a Pages deployment: activity is displayed
in the README, and the web contact card only uses the terminal banners.

## Enable optional music or coding-time cards

Spotify and WakaTime are disabled by default. In `config/profile.json`, update
the corresponding object in `widgets`:

- `enabled`: set to `true` after configuring the provider.
- `image_url`: the public HTTPS URL of an embeddable card image.
- `url`: the HTTPS destination when the card is clicked.
- `title`: section heading.
- `caption`: describe the data, including the measured period for WakaTime.

Spotify requires a separate authorized card provider. Configure it to show the
last track when playback stops, and to use this profile's palette. GitHub caches
images, so a README cannot guarantee live playback updates.

WakaTime requires a public shareable chart or a separate service authorized to
read your stats. Set its time window to match the caption (seven days by default),
apply the shared palette through that provider, and configure its no-data state.
These external cards control their own colors and refresh behavior; the local
generator embeds their URLs. Disabled widgets produce no empty headings.

## Preview the web card

```sh
python3 scripts/build_profile.py
mkdir -p site/assets
cp assets/terminal*.svg site/assets/
python3 -m http.server 8000 --directory site
```

Open <http://localhost:8000/>. The email button uses the Clipboard API on a secure
context such as localhost or GitHub Pages, with an ordinary email link as a fallback.

The Pages workflow copies the terminal banners into the deployment artifact and
publishes `site/`. In **Settings → Pages**, select **GitHub Actions** as the source.
JetBrains Mono is loaded from Google Fonts with local monospace fallbacks.

Review the README on GitHub in light/dark mode and at mobile width. Markdown
text and links follow the reader's GitHub theme; exact palette control applies
to the generated SVGs, badge parameters, and the web card.

## Validation and CI

`.github/workflows/check-profile.yml` runs the offline tests, the freshness check,
and `git diff --check`. Tests cover malformed configuration, escaping, long
banner values, theme propagation, optional widgets, idempotence, read-only
checking, and successful/failed statistics refreshes.

After changes to layout, inspect desktop and mobile banners and project cards,
the beginning and end of both terminal animations, contact and project links,
and reduced-motion mode. For the web card, also check keyboard focus and the
email copy success/failure states.
