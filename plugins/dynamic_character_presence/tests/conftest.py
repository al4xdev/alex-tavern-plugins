"""Makes the core repo's ``src`` package importable for this plugin's tests.

Mirrors the sibling-checkout convention already used by ``check.py`` (``--core-root``,
default ``../roleplay``): this plugin is authored and tested beside a roleplay checkout,
never inside ``.data/plugins/hub``. Only pure, side-effect-free core modules
(``src.models``) are imported here — nothing touches ``src.paths``/the real ``.data/``
directory, so no data-root isolation is needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HUB_ROOT = Path(__file__).resolve().parents[3]
_CORE_ROOT = (_HUB_ROOT.parent / "roleplay").resolve()
if _CORE_ROOT.is_dir() and str(_CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CORE_ROOT))
