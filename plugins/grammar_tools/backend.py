"""Grammar-only cleanup for the controlled character's submitted text."""

from __future__ import annotations

import json

FIELDS = ("speech", "thought", "action")
GRAMMAR_SCHEMA = {
    "name": "grammar_cleanup",
    "schema": {
        "type": "object",
        "properties": {field: {"type": "string"} for field in FIELDS},
        "required": list(FIELDS),
        "additionalProperties": False,
    },
}


def setup(context) -> None:  # noqa: ANN001
    async def polish(turn_input, hook_context):  # noqa: ANN001, ANN202
        original = {field: str(turn_input[field]) for field in FIELDS}
        if not any(value.strip() for value in original.values()):
            return turn_input

        corrected = await context.model.call_json(
            hook_context,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Correct only grammar, spelling, agreement, and punctuation in each "
                        "roleplay character field. Preserve its language, meaning, voice, person, "
                        "tense, facts, and intent. Do not embellish, summarize, translate, move "
                        "content between fields, or mention an operator, user, or player. Return "
                        "only the required JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(original, ensure_ascii=False),
                },
            ],
            json_schema=GRAMMAR_SCHEMA,
            max_tokens=1024,
            use_configured_language=False,
        )
        for field in FIELDS:
            value = corrected.get(field)
            if not isinstance(value, str):
                raise ValueError(f"Grammar result {field} must be a string")
            if not original[field] and value:
                raise ValueError(f"Grammar result populated empty field {field}")
            if original[field].strip() and not value.strip():
                raise ValueError(f"Grammar result erased non-empty field {field}")
            turn_input[field] = value
        return turn_input

    context.filter("turn.input", polish)
