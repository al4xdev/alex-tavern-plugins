"""Static checks for frontend.js — mirrors the hub's text-assertion style.

The theme is a single injected stylesheet, so the meaningful contract is coverage:
every design-system variable core declares in ``:root`` must be redefined, and every
core rule that hardcodes a dark color (instead of reading a variable) must have an
override selector here. Both checks read the sibling core checkout's ``style.css``,
so they fail — rather than silently shipping a half-dark theme — when core grows a
new variable or a new hardcoded dark rule.
"""

from __future__ import annotations

import re
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]


def _source() -> str:
    return (PACKAGE_DIR / "frontend.js").read_text(encoding="utf-8")


def _theme_css() -> str:
    match = re.search(r"const THEME_CSS = `(.*?)`;", _source(), re.S)
    assert match, "frontend.js must keep the theme in a THEME_CSS template literal"
    return match.group(1)


def test_exports_activate() -> None:
    assert "export function activate(sdk)" in _source()


def test_reaches_document_only_through_the_declared_unsafe_gate() -> None:
    source = _source()
    assert "sdk.unsafe.document" in source
    assert "sdk.observe('unsafe'" in source


def test_reactivation_replaces_instead_of_stacking_style_elements() -> None:
    source = _source()
    assert "doc.getElementById(STYLE_ID)?.remove()" in source
    assert "style.id = STYLE_ID" in source


def test_declares_a_light_color_scheme() -> None:
    assert "color-scheme: light" in _theme_css()


def test_overrides_every_core_root_variable(core_style_css: str) -> None:
    root = re.search(r":root \{(.*?)\n\}", core_style_css, re.S)
    assert root, "core style.css no longer has the expected :root block"
    core_variables = set(re.findall(r"(--[\w-]+):", root.group(1)))
    assert core_variables, "no variables found in core :root"
    themed = set(re.findall(r"(--[\w-]+):", _theme_css()))
    # Radii, fonts, and motion are palette-neutral and intentionally inherited.
    neutral = {v for v in core_variables if re.match(r"--(radius|font|mono|dur|ease)", v)}
    missing = core_variables - neutral - themed
    assert not missing, f"core palette variables without a creme override: {sorted(missing)}"


def test_overrides_every_core_selector_with_hardcoded_dark_colors(core_style_css: str) -> None:
    stripped = re.sub(r"/\*.*?\*/", "", core_style_css, flags=re.S)
    theme = _theme_css()
    missing: list[str] = []
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", stripped):
        selector = " ".join(block.group(1).split())
        if selector.startswith(":root") or selector.startswith(("html", "@", "from", "to")):
            continue
        if re.fullmatch(r"[\d%, ]+", selector):
            continue  # keyframe steps; whole keyframes are re-declared when tinted
        body = block.group(2)
        # Hardcoded colors on dark-only alpha layers or fixed hexes need retinting;
        # pure-white text on accent/danger gradients stays correct and is skipped.
        has_hardcoded = any(
            re.search(r"#[0-9a-fA-F]{3,8}|rgba?\(", declaration)
            and not re.fullmatch(r"\s*color:\s*#fff\s*", declaration)
            and "var(--" not in declaration
            for declaration in body.split(";")
        )
        if has_hardcoded and selector not in theme:
            missing.append(selector)
    allowed_dark = {
        # White-on-accent and semantic-variable rules that stay correct on cream.
        ".toggle input:checked + .toggle-track .toggle-thumb",
        ".session-incompatible-badge",
        ".whisper-popup",
        ".action-btn.whisper-active",
        ".char-id-badge",
        ".compaction-threshold input[type='range']::-webkit-slider-thumb",
        ".compaction-threshold input[type='range']::-moz-range-thumb",
    }
    unexpected = [s for s in missing if s not in allowed_dark]
    assert not unexpected, f"core selectors with dark hardcoded colors lacking overrides: {unexpected}"
