"""Unit tests for the Dynamic Character Presence backend logic.

Uses a hand-rolled fake ``context`` (not ``src.plugins.sdk.PluginContext``) so these
tests stay pure business-logic checks — no real ``PluginConfig``/filesystem I/O, no
dependency on the host's plugin runtime. Integration with the real hook registry and
manifest is already covered by the core's own loader tests plus ``plugin_validate``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from src.models import Character, CharacterBody, CharacterMind, GameState, Player, Scene

PACKAGE_DIR = Path(__file__).resolve().parents[1]


def _load_backend() -> Any:
    spec = importlib.util.spec_from_file_location(
        "dynamic_character_presence_backend_under_test", PACKAGE_DIR / "backend.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


backend = _load_backend()


class FakeConfig:
    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self._value = dict(initial or {})

    def read(self) -> dict[str, Any]:
        return dict(self._value)

    def write(self, value: dict[str, Any]) -> None:
        self._value = dict(value)


class FakeContext:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = FakeConfig(config)
        self.contributions: list[tuple[str, Any]] = []
        self.filters: dict[str, Any] = {}
        self.events: list[tuple[str, dict[str, Any]]] = []

    def contribute(self, slot: str, value: Any) -> None:
        self.contributions.append((slot, value))

    def filter(self, hook: str, handler: Any, **_order: Any) -> None:
        self.filters[hook] = handler

    def event(self, name: str, **details: Any) -> None:
        self.events.append((name, details))


def _character(name: str) -> Character:
    return Character(
        mind=CharacterMind(name=name, personality="p", knowledge=[], current_mood="calm"),
        body=CharacterBody(name=name, physical_description="", outfit=""),
    )


def _game(ids: list[str], present: list[str], controlled: str) -> GameState:
    characters = {cid: _character(cid) for cid in ids}
    scene = Scene(location="x", time_of_day="day", present_characters=present, physical_facts={})
    return GameState(
        session_id="s1",
        characters=characters,
        player=Player(controlled_character_id=controlled),
        scene=scene,
    )


def _base_schema() -> dict[str, Any]:
    return {"properties": {}, "required": []}


def _rejections(ctx: FakeContext) -> list[tuple[str, dict[str, Any]]]:
    """``setup()`` always emits ``setup_complete`` first; isolate rejection events."""
    return [event for event in ctx.events if event[0] == "presence_update_rejected"]


class TestSetup:
    def test_contributes_settings_descriptor(self) -> None:
        ctx = FakeContext()
        backend.setup(ctx)
        assert ctx.contributions == [("settings", backend.SETTINGS_DESCRIPTOR)]

    def test_registers_exactly_the_three_narrator_hooks(self) -> None:
        ctx = FakeContext()
        backend.setup(ctx)
        assert set(ctx.filters) == {"narrator.schema", "narrator.context", "narrator.result"}

    def test_settings_descriptor_declares_a_boolean_default_true(self) -> None:
        fields = backend.SETTINGS_DESCRIPTOR["fields"]
        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "allow_narrator_presence_changes"
        assert field["type"] == "boolean"
        assert field["default"] is True
        assert field["label"]["en"] and field["label"]["pt-BR"]


class TestNarratorSchema:
    def test_adds_presence_update_when_enabled(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        result = ctx.filters["narrator.schema"](_base_schema(), {})
        assert "presence_update" in result["properties"]
        assert "presence_update" in result["required"]

    def test_omits_presence_update_when_disabled(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": False})
        backend.setup(ctx)
        result = ctx.filters["narrator.schema"](_base_schema(), {})
        assert result == _base_schema()

    def test_defaults_to_enabled_when_config_is_empty(self) -> None:
        ctx = FakeContext({})
        backend.setup(ctx)
        result = ctx.filters["narrator.schema"](_base_schema(), {})
        assert "presence_update" in result["properties"]


class TestNarratorContext:
    def test_mentions_present_and_absent_characters(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "Player"], "C1")
        lines = ctx.filters["narrator.context"]([], {"game": game})
        assert any("C1" in line for line in lines)
        assert any("C2" in line for line in lines)

    def test_returns_unchanged_when_disabled(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": False})
        backend.setup(ctx)
        game = _game(["C1"], ["C1", "Player"], "C1")
        lines = ctx.filters["narrator.context"]([], {"game": game})
        assert lines == []


class TestNarratorResult:
    def test_applies_a_valid_proposal(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        narrator_output = {
            "next_speaker": "Narrator",
            "presence_update": {"present_character_ids": ["C1"]},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "Player"]
        assert _rejections(ctx) == []

    def test_noop_when_no_proposal(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        result = ctx.filters["narrator.result"](game, {"narrator_output": {"next_speaker": "C2"}})
        assert result.scene.present_characters == ["C1", "C2", "Player"]
        assert _rejections(ctx) == []

    def test_noop_when_disabled_even_with_a_proposal(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": False})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        narrator_output = {
            "next_speaker": "Narrator",
            "presence_update": {"present_character_ids": ["C1"]},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "C2", "Player"]

    def test_rejects_removing_the_controlled_character(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        narrator_output = {
            "next_speaker": "C2",
            "presence_update": {"present_character_ids": ["C2"]},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "C2", "Player"]
        rejections = _rejections(ctx)
        assert len(rejections) == 1

    def test_rejects_unknown_character_id(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        narrator_output = {
            "next_speaker": "Narrator",
            "presence_update": {"present_character_ids": ["C1", "C9"]},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "C2", "Player"]
        assert len(_rejections(ctx)) == 1

    def test_rejects_when_next_speaker_would_become_absent(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        narrator_output = {
            "next_speaker": "C2",
            "presence_update": {"present_character_ids": ["C1"]},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "C2", "Player"]
        rejections = _rejections(ctx)
        assert len(rejections) == 1
        assert "next_speaker" in rejections[0][1]["reason"]

    def test_rejects_non_list_present_character_ids(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "C2", "Player"], "C1")
        narrator_output = {
            "next_speaker": "Narrator",
            "presence_update": {"present_character_ids": "C1"},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "C2", "Player"]
        assert len(_rejections(ctx)) == 1

    def test_returning_an_absent_character_is_allowed(self) -> None:
        ctx = FakeContext({"allow_narrator_presence_changes": True})
        backend.setup(ctx)
        game = _game(["C1", "C2"], ["C1", "Player"], "C1")
        narrator_output = {
            "next_speaker": "Narrator",
            "presence_update": {"present_character_ids": ["C1", "C2"]},
        }
        result = ctx.filters["narrator.result"](game, {"narrator_output": narrator_output})
        assert result.scene.present_characters == ["C1", "C2", "Player"]
        assert _rejections(ctx) == []
