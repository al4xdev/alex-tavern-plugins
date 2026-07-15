"""Static checks for frontend.js — mirrors the core repo's text-assertion style.

A full DOM-driven behavioral test would need a browser/jsdom, which this hub's test
setup doesn't carry; these checks instead pin the accessibility and wiring contract:
native checkbox semantics (keyboard/touch operable for free), an explicit aria-label
(so the accessible name survives the core's small-screen ``.toggle-label { display:
none }`` rule), and registration against the generic hooks/slot core exposes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]


def _source() -> str:
    return (PACKAGE_DIR / "frontend.js").read_text(encoding="utf-8")


def test_exports_activate() -> None:
    assert "export function activate(sdk)" in _source()


def test_registers_the_three_generic_setup_hooks() -> None:
    source = _source()
    assert "sdk.hook('setup.charCardHead'" in source
    assert "sdk.hook('setup.presentCharacters'" in source
    assert "sdk.hook('setup.restorePresence'" in source


def test_mounts_into_the_generic_session_tools_slot() -> None:
    assert "sdk.mount('session.tools'" in _source()


def test_registers_session_presence_action_that_opens_and_focuses_existing_panel() -> None:
    source = _source()
    assert "sdk.registerAction({" in source
    assert "name: 'presence'" in source
    assert "scope: 'session'" in source
    assert "panel.openAndFocus()" in source
    assert "list.querySelector('input:not(:disabled)')" in source


def test_toggle_uses_native_checkbox_semantics_with_explicit_aria_label() -> None:
    source = _source()
    assert "input.type = 'checkbox'" in source
    assert source.count("setAttribute('aria-label'") >= 2  # card toggle + roster rows


def test_reuses_the_core_toggle_component_not_a_bespoke_control() -> None:
    source = _source()
    assert "'toggle char-presence-toggle'" in source
    assert "'toggle-track'" in source
    assert "'toggle-thumb'" in source


def test_labels_come_from_core_i18n_not_hardcoded_strings() -> None:
    source = _source()
    assert "import { t } from '/i18n.js';" in source
    assert "t('character.inScene')" in source


def test_present_characters_hook_always_keeps_the_player_marker() -> None:
    source = _source()
    assert "[...present, 'Player']" in source


def test_javascript_syntax_is_valid() -> None:
    subprocess.run(
        ["node", "--check", str(PACKAGE_DIR / "frontend.js")],
        check=True,
        capture_output=True,
        text=True,
    )
