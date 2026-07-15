# Dynamic Character Presence

Adds a "Na cena" toggle to each character card in setup so the human can choose who starts a scene,
plus a compact control in the active session to add or remove NPCs mid-story. Toggling a character
off never deletes, disables, or resets them — `mind`, `body`, mood, notes, and history all stay
exactly as they were; the character simply stops being pulled into the Narrator's detailed context
and cannot receive an autonomous Character call until they return.

`Scene.present_characters` (core state) is the only source of truth. This plugin does not keep a
mirror list in `plugin_state` or in its own configuration.

The session action `/presence` opens this same mounted roster panel, expands it, refreshes the
canonical session state, and focuses its first available control. It does not add another endpoint
or state path.

## Configuration

One setting, exposed through the generic Plugin Center config form:

- **Narrador pode alterar quem está na cena** (`allow_narrator_presence_changes`, boolean, default
  `true`) — when on, the Narrator's structured turn output may include an optional
  `presence_update.present_character_ids` field declaring the full desired presence list for that
  turn. When off, only the human toggles/mid-session control change presence, and the Narrator's
  schema does not offer the field at all.

## Behavior and limits

- The controlled character can never be toggled off, removed by the Narrator, or dropped from
  `present_character_ids` — the UI blocks it before save/start, and the backend rejects it again
  server-side rather than silently correcting the list.
- A Narrator `presence_update` that references an unknown ID, omits the controlled character, or
  contradicts the same turn's own routing (naming an absent character as `next_speaker`) is discarded
  — the rest of that turn's narration still commits.
- The human mid-session control is administrative: it acquires the same session lock as a turn,
  validates the caller's `expected_revision`, and never generates a turn, calls an LLM, or appends to
  history. Undo is strict LIFO and refuses to overwrite a presence change that happened after it
  (e.g. from a later Narrator `presence_update`).

## Permissions

- `session.state.write` — apply validated presence changes to `Scene.present_characters`.
- `config.read` / `config.write` — the `allow_narrator_presence_changes` setting.
- `frontend.dom.mount` — the per-card toggle, the session roster control, and the config form.
- `frontend.action.register` — expose `/presence` as another entry into the mounted roster control.

No `model.call`, `network`, or `unsafe` — presence changes ride the Narrator's existing structured
turn output; this plugin never calls a model itself.
