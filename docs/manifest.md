# Plugin manifest

Every package has one `plugin.toml` at its root. The current format is deliberately strict and
forward-only. Required top-level fields are `schema_version = 1`, `id`, `name`, semantic `version`,
`description`, `license`, non-empty `authors`, observational `permissions`, `dependencies`, and the
`entrypoints`, `order`, and `python` tables.

IDs are stable lowercase dotted or dashed identifiers. Entrypoints are package-relative files.
Dependencies are plugin IDs with a version expression and optional flag. `order.before` and
`order.after` refer to plugin IDs; cycles reject the registration. `python.dependencies` are uv
requirement strings used to rebuild the environment for the exact active set.

Run `plugin_validate` through the MCP before packing. Unknown fields are errors.

Declare `model.call` when backend code uses `context.model.call_json`. This documents cost-bearing
access for review; the SDK still owns provider selection, secrets, schema validation, and logging.
