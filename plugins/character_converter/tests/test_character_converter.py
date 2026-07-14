from __future__ import annotations

import asyncio
import base64
import importlib.util
import json
import struct
import zlib
from pathlib import Path
from typing import Any

import pytest

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend.py"
SPEC = importlib.util.spec_from_file_location("character_converter_backend", BACKEND_PATH)
assert SPEC is not None and SPEC.loader is not None
backend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backend)


def character(name: str = "Lyra") -> dict[str, Any]:
    return {
        "mind": {
            "name": name,
            "personality": "Lyra is observant and guarded.",
            "knowledge": ["Lyra knows the northern roads."],
            "current_mood": "cautious",
        },
        "body": {
            "name": name,
            "physical_description": "Lyra has dark curls and grey eyes.",
            "outfit": "Lyra wears a weathered green cloak.",
        },
    }


class FakeModel:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    async def call_json(self, hook_context, **kwargs):  # noqa: ANN001, ANN202
        self.calls.append({"hook_context": hook_context, **kwargs})
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class FakeContext:
    def __init__(self, responses: list[Any]) -> None:
        self.model = FakeModel(responses)
        self.descriptor = None
        self.handler = None

    def command(self, descriptor, handler):  # noqa: ANN001, ANN202
        self.descriptor = descriptor
        self.handler = handler


def command_for(*responses: Any):
    context = FakeContext(list(responses))
    backend.setup(context)
    assert context.handler is not None
    return context, context.handler


def payload(*, text: str = "", file: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "arguments": {"preset-name": "lyra-nightfall"},
        "fields": {"source-text": text},
        "files": {"source-file": file} if file else {},
    }


def chunk(kind: bytes, data: bytes, *, corrupt: bool = False) -> bytes:
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    if corrupt:
        crc ^= 1
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def card_png(cards: dict[str, dict[str, Any]], *, corrupt: bool = False) -> bytes:
    chunks = []
    for index, (key, value) in enumerate(cards.items()):
        encoded = base64.b64encode(json.dumps(value).encode())
        chunks.append(
            chunk(b"tEXt", key.encode() + b"\0" + encoded, corrupt=corrupt and index == 0)
        )
    return backend.PNG_SIGNATURE + b"".join(chunks) + chunk(b"IEND", b"")


@pytest.mark.parametrize(
    "card, expected",
    [
        ({"name": "Lyra", "description": "A traveler"}, "v1"),
        ({"spec": "chara_card_v2", "spec_version": "2.0", "data": {"name": "Lyra"}}, "v2"),
        ({"spec": "chara_card_v3", "spec_version": "3.0", "data": {"name": "Lyra"}}, "v3"),
    ],
)
def test_json_character_card_versions(card: dict[str, Any], expected: str) -> None:
    context, handler = command_for(character())
    result = asyncio.run(
        handler(
            payload(
                file={
                    "name": "lyra.json",
                    "media_type": "application/json",
                    "data": json.dumps(card).encode(),
                }
            ),
            {"turn_number": 3},
        )
    )
    assert result["source_format"] == expected
    assert result["character"] == character()
    assert len(context.model.calls) == 1


def test_png_prefers_ccv3_over_chara() -> None:
    v1 = {"name": "Old"}
    v3 = {"spec": "chara_card_v3", "spec_version": "3.0", "data": {"name": "Lyra"}}
    _, handler = command_for(character())
    result = asyncio.run(
        handler(
            payload(
                file={
                    "name": "card.png",
                    "media_type": "image/png",
                    "data": card_png({"chara": v1, "ccv3": v3}),
                }
            ),
            {"turn_number": 1},
        )
    )
    assert result["source_format"] == "v3-png-ccv3"


def test_ordinary_png_and_bad_crc_have_clear_errors() -> None:
    _, handler = command_for(character())
    ordinary = backend.PNG_SIGNATURE + chunk(b"IEND", b"")
    with pytest.raises(backend.CommandError, match="ordinary PNG"):
        asyncio.run(
            handler(
                payload(file={"name": "avatar.png", "media_type": "image/png", "data": ordinary}),
                {},
            )
        )

    damaged = card_png({"chara": {"name": "Lyra"}}, corrupt=True)
    with pytest.raises(backend.CommandError, match="checksum"):
        asyncio.run(
            handler(
                payload(file={"name": "card.png", "media_type": "image/png", "data": damaged}), {}
            )
        )


def test_requires_exactly_one_source() -> None:
    _, handler = command_for(character())
    with pytest.raises(backend.CommandError, match="but not both"):
        asyncio.run(handler(payload(), {}))
    with pytest.raises(backend.CommandError, match="but not both"):
        asyncio.run(
            handler(
                payload(
                    text="Lyra",
                    file={"name": "x.json", "media_type": "application/json", "data": b"{}"},
                ),
                {},
            )
        )


def test_semantic_failure_gets_one_correction_call() -> None:
    invalid = character()
    invalid["mind"]["personality"] = "The User's loyal guide."
    context, handler = command_for(invalid, character())
    result = asyncio.run(handler(payload(text="Lyra is a guarded traveler."), {"turn_number": 8}))
    assert result["character"] == character()
    assert len(context.model.calls) == 2
    assert "semantic violations" in context.model.calls[1]["messages"][-1]["content"]


def test_provider_failure_escapes_command_boundary() -> None:
    _, handler = command_for(RuntimeError("provider unavailable"))
    with pytest.raises(RuntimeError, match="provider unavailable"):
        asyncio.run(handler(payload(text="Lyra"), {}))
