# SDK and trust model

Backend entrypoints export `setup(context)`. The context exposes `action`, `filter`, `wrapper`,
`contribute`, executable `command`, plugin-owned atomic config, observable HTTP, structured model calls, events, and the
explicit `unsafe` escape hatch. `context.model.call_json` is the sole model API: it requires JSON
Schema, uses the active provider without exposing secrets, and owns session logging. Read
`model-calls.md` before using it. Frontend entrypoints export `activate(sdk)` and may register
provider adapters, hooks, or mount UI into named slots. They can also reach `window` and `document`
through `unsafe`.

There is no sandbox. Permissions document accesses in the journal and support code review; they do
not block code. A curated artifact is trusted because its complete source was reviewed and its ZIP
hash is fixed. Third-party ZIPs are the installer's responsibility.

Before-commit filters receive a deep draft. If a plugin raises, that draft is discarded, the plugin
is disabled for the rest of the boot, and clean execution continues. Post-commit actions are never
retried. External side effects cannot be rolled back.

## Executable utility commands

`context.command(descriptor, handler)` owns slash tools separately from informational contribution
slots. Names are globally unique; a collision rejects and disables the later plugin during boot.
Descriptors provide `en` and `pt-BR` summary/labels/hints, positional text arguments, typed form
fields (`text`, `textarea`, or `file`), a usage string, and one result kind. The browser builds its
autocomplete and form from this JSON rather than hardcoding plugin identity.

Handlers receive normalized `{arguments, fields, files}` plus a session-bound context containing
`game`, `turn_number`, `runner`, and `operation_id`. File values contain decoded bytes only after
the core has validated Base64 and size. Version 1 commands are utilities: the game is an isolated
snapshot and the command cannot advance narrative history or revision. Model-backed commands pass
that same context to `context.model.call_json` so provider secrets and observability stay in core.

## Generic config UI (`settings` contribution)

`context.contribute("settings", descriptor)` declares one plugin's configuration form — there is no
per-plugin branch anywhere in core or the frontend; the Plugin Center renders whatever schema a
plugin declares. A descriptor is `{"fields": [...]}`, where each field requires `key`, `type` (only
`"boolean"` in schema_version 1), `label` (a dict with at least `en`, optionally `pt-BR`), and
`default`. A malformed descriptor fails the plugin's boot explicitly rather than producing a broken
or silently-skipped form.

The first time a plugin activates, core writes each declared field's `default` into its config
(`context.config`) for any key not already present — so `context.config.read()` is safe to treat as
fully populated from the plugin's very first tick onward. There is no legacy-format fallback: read
whatever key you declared, and if it is missing or the wrong type, that is a bug in the descriptor or
in something that wrote to the config file directly, not a case to paper over silently.

The frontend mirrors this: it fetches the same descriptor from `/plugins` (the `contributions.settings`
list) and the current value from `GET /plugins/{id}/config`, renders one toggle per boolean field
using the shared `.toggle` component, and `PUT`s the whole config object back on change.
