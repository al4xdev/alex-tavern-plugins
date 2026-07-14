from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
from typing import Any

import pytest

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend.py"
SPEC = importlib.util.spec_from_file_location("grammar_tools_backend", BACKEND_PATH)
assert SPEC is not None and SPEC.loader is not None
backend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backend)


class FakeModel:
    def __init__(self, response: dict[str, str] | BaseException) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    async def call_json(self, hook_context, **kwargs):  # noqa: ANN001, ANN202
        self.calls.append({"hook_context": hook_context, **kwargs})
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


class FakeContext:
    def __init__(self, response: dict[str, str] | BaseException) -> None:
        self.model = FakeModel(response)
        self.handler = None

    def filter(self, hook, handler):  # noqa: ANN001, ANN202
        assert hook == "turn.input"
        self.handler = handler


def handler_for(response: dict[str, str] | BaseException):
    context = FakeContext(response)
    backend.setup(context)
    assert context.handler is not None
    return context, context.handler


def test_corrects_all_fields_with_one_strict_json_call() -> None:
    corrected = {
        "speech": "Eu vou abrir a porta.",
        "thought": "Ela parece preocupada.",
        "action": "Eu observo o rosto dela.",
    }
    context, handler = handler_for(corrected)
    original = {
        "speech": "eu vai abrir a porta",
        "thought": "ela parece preocupado",
        "action": "eu observa o rosto dela",
        "force_speaker": "C2",
        "narrator_hint": "",
        "skip": False,
    }

    result = asyncio.run(handler(original.copy(), {"turn_number": 4}))

    assert {field: result[field] for field in backend.FIELDS} == corrected
    assert result["force_speaker"] == "C2"
    assert len(context.model.calls) == 1
    call = context.model.calls[0]
    assert call["json_schema"] == backend.GRAMMAR_SCHEMA
    assert call["use_configured_language"] is False
    assert "player" not in call["messages"][1]["content"].lower()


def test_empty_character_fields_skip_model_call() -> None:
    context, handler = handler_for({field: "unexpected" for field in backend.FIELDS})
    value = {
        "speech": "",
        "thought": "",
        "action": "",
        "force_speaker": None,
        "narrator_hint": "A storm begins.",
        "skip": False,
    }

    assert asyncio.run(handler(value.copy(), {})) == value
    assert context.model.calls == []


@pytest.mark.parametrize(
    "response, message",
    [
        ({"speech": "Invented", "thought": "", "action": ""}, "populated empty field"),
        ({"speech": "", "thought": "", "action": ""}, "erased non-empty field"),
    ],
)
def test_rejects_cross_field_or_erased_content(response: dict[str, str], message: str) -> None:
    _, handler = handler_for(response)
    value = {
        "speech": "",
        "thought": "segredo",
        "action": "",
        "force_speaker": None,
        "narrator_hint": "",
        "skip": False,
    }

    with pytest.raises(ValueError, match=message):
        asyncio.run(handler(value, {}))


def test_model_failure_escapes_to_runtime_containment() -> None:
    _, handler = handler_for(RuntimeError("provider unavailable"))
    value = {
        "speech": "texto",
        "thought": "",
        "action": "",
        "force_speaker": None,
        "narrator_hint": "",
        "skip": False,
    }

    with pytest.raises(RuntimeError, match="provider unavailable"):
        asyncio.run(handler(value, {}))
