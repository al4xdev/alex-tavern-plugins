"""Contract checks for the frontend-only suggestion preloader."""

from __future__ import annotations

import subprocess
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]


def _source() -> str:
    return (PACKAGE_DIR / "frontend.js").read_text(encoding="utf-8")


def test_exports_activate_and_observes_committed_turn_output() -> None:
    source = _source()
    assert "export function activate(sdk)" in source
    assert "sdk.hook('turn.output'" in source
    assert "return data;" in source


def test_preload_runs_off_the_rendering_path_through_supported_sdk_surfaces() -> None:
    source = _source()
    assert "queueMicrotask" in source
    assert "sdk.api.suggest(sessionId)" in source
    assert "sdk.ui.setSuggestionsLoading(true)" in source
    assert "sdk.ui.renderSuggestions(result.suggestions)" in source


def test_stale_and_failed_requests_do_not_replace_native_suggestions() -> None:
    source = _source()
    assert "serial === turnSerial" in source
    assert "context?.state?.sessionId === sessionId" in source
    assert "frontend.suggest.preload-error" in source
    assert "sdk.ui.setSuggestionsLoading(false)" in source


def test_javascript_syntax_is_valid() -> None:
    subprocess.run(
        ["node", "--check", str(PACKAGE_DIR / "frontend.js")],
        check=True,
        capture_output=True,
        text=True,
    )
