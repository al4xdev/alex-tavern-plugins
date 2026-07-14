# Extension points

The authoritative machine-readable list comes from the core `plugin_contract` MCP tool. Current
transactional filters are `turn.input`, `narrator.output`, `character.output`, and
`turn.before_commit`. `turn.after_commit` is an action for effects that must happen only after the
session state is durable.

Filters may mutate their draft and return `None`, or return a replacement. Actions receive their
context. Wrappers receive `(next, context, *args, **kwargs)`. Ordering is a deterministic DAG:
explicit before/after edges first, then descending priority, plugin ID, and registration sequence.

Contribution slots currently include providers, routes, settings, commands, and panels. For an
unanticipated extension, use `context.unsafe` deliberately and document the core object touched.
