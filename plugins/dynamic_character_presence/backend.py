"""Dynamic Character Presence plugin.

Presence is core state (`Scene.present_characters`) — this plugin never keeps a mirror
list in `plugin_state` or in its own configuration. It only:

1. declares a generic config field (`allow_narrator_presence_changes`) through the
   `settings` contribution, so the Plugin Center renders its form without core knowing
   this plugin exists;
2. optionally extends the Narrator's structured turn output with `presence_update`,
   validated through the same `validate_present_characters` contract the core boundary
   and the human mid-session control both use.

The human toggle (setup) and the mid-session roster control live in `frontend.js` and
call the core `/session/{id}/presence` endpoints directly — no backend code is needed
for that path.
"""

from __future__ import annotations

from typing import Any

from src.models import validate_present_characters

SETTINGS_DESCRIPTOR = {
    "fields": [
        {
            "key": "allow_narrator_presence_changes",
            "type": "boolean",
            "label": {
                "en": "Narrator can change who is in the scene",
                "pt-BR": "Narrador pode alterar quem está na cena",
            },
            "default": True,
        },
    ],
}

PRESENCE_UPDATE_SCHEMA = {
    "type": ["object", "null"],
    "properties": {
        "present_character_ids": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["present_character_ids"],
    "additionalProperties": False,
    "description": (
        "Optional: the complete list of present character IDs for this turn (never "
        "include the internal Player marker). Use null when presence does not change. "
        "The controlled character can never be removed."
    ),
}


def setup(context) -> None:  # noqa: ANN001
    """Register hooks and contributions through the Alex Tavern SDK."""
    context.contribute("settings", SETTINGS_DESCRIPTOR)

    def allow_narrator_changes() -> bool:
        config = context.config.read()
        return bool(config.get("allow_narrator_presence_changes", True))

    def extend_schema(schema, hook_context):  # noqa: ANN001, ANN202, ARG001
        if not allow_narrator_changes():
            return schema
        schema["properties"]["presence_update"] = PRESENCE_UPDATE_SCHEMA
        schema["required"].append("presence_update")
        return schema

    def add_context(lines, hook_context):  # noqa: ANN001, ANN202
        if not allow_narrator_changes():
            return lines
        game = hook_context["game"]
        present = [cid for cid in game.characters if cid in game.scene.present_characters]
        absent = [cid for cid in game.characters if cid not in present]
        lines.append(
            "You may set presence_update to move characters in or out of the scene. "
            f"Currently present: {', '.join(present) or '(none)'}. "
            f"Available elsewhere: {', '.join(absent) or '(none)'}. "
            "The controlled character can never be removed; leave presence_update null "
            "when nothing changes."
        )
        return lines

    def apply_presence(game, hook_context):  # noqa: ANN001, ANN202
        if not allow_narrator_changes():
            return game
        narrator_output: dict[str, Any] = hook_context["narrator_output"]
        proposal = narrator_output.get("presence_update")
        if not proposal:
            return game

        ids = proposal.get("present_character_ids")
        if not isinstance(ids, list):
            context.event("presence_update_rejected", reason="present_character_ids must be a list")
            return game

        controlled_id = game.player.controlled_character_id
        try:
            validated = validate_present_characters(
                [*ids, "Player"], game.characters, controlled_id
            )
        except ValueError as error:
            context.event("presence_update_rejected", reason=str(error))
            return game

        # The character call for this turn (if any) already ran against the OLD
        # presence — a proposal that would make that already-chosen speaker absent
        # contradicts what just happened in the same response and is discarded whole,
        # rather than silently applied alongside an inconsistent turn.
        next_speaker = narrator_output.get("next_speaker")
        if next_speaker not in (None, "Narrator") and next_speaker not in validated:
            context.event(
                "presence_update_rejected",
                reason=f"next_speaker {next_speaker} would be absent under the proposed presence",
            )
            return game

        game.scene.present_characters = validated
        return game

    context.filter("narrator.schema", extend_schema)
    context.filter("narrator.context", add_context)
    context.filter("narrator.result", apply_presence)
    context.event("setup_complete")
