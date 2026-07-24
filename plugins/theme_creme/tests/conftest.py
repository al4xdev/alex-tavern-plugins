"""Locates the sibling core checkout for coverage tests.

Mirrors the sibling-checkout convention already used by ``check.py`` (``--core-root``,
default ``../roleplay``): this theme is authored and reviewed beside a roleplay
checkout. Nothing from core is imported — the tests only read the core stylesheet
text to keep the override coverage honest.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_HUB_ROOT = Path(__file__).resolve().parents[3]
_CORE_ROOT = (_HUB_ROOT.parent / "roleplay").resolve()


@pytest.fixture(scope="session")
def core_style_css() -> str:
    stylesheet = _CORE_ROOT / "src" / "static" / "style.css"
    if not stylesheet.is_file():
        pytest.skip("core checkout not found beside the hub; coverage checks need it")
    return stylesheet.read_text(encoding="utf-8")
