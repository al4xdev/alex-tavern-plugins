# Extension points

The authoritative machine-readable list comes from the core `plugin_contract` MCP tool. Current
transactional filters are `turn.input`, `narrator.context`, `narrator.schema`, `narrator.result`,
`narrator.output`, `character.output`, and `turn.before_commit`. `turn.after_commit` is an action for
effects that must happen only after the session state is durable.

`turn.input` receives the complete input draft plus `game`, `turn_number`, and `runner` in its hook
context. It runs after the raw `turn_input` marker and before authoritative history. Model-backed
filters must pass that hook context to `context.model.call_json` so logging metadata is automatic.

## Extending the Narrator without replacing the call

`narrator.call` is a wrapper — it can replace, surround, or bypass the entire Narrator operation, but
that is overkill for a plugin that only wants to add one optional output field. Three narrower filters
compose instead:

- `narrator.context` — value is `list[str]`; each registered plugin appends its own read-only lines,
  rendered as a `PLUGIN CONTEXT:` block in the Narrator's prompt.
- `narrator.schema` — value is `{"properties": {...}, "required": [...]}`; a plugin merges in its own
  JSON Schema property (with its own `description` — that is what the model reads to understand the
  field, not prose in core). Leave `properties`/`required` untouched to contribute nothing this turn,
  e.g. when the plugin's own config disables the feature.
- `narrator.result` — value is the same-turn `GameState` draft, run after `scene_update`/`mood_updates`
  are applied and before `turn.before_commit`. The hook context carries `narrator_output` (the
  validated Narrator dict) so the handler can read back whatever key it declared via `narrator.schema`,
  validate it, and apply it to the draft.

A plugin that finds its own `narrator_output` proposal invalid (bad ID, contradicts routing, etc.)
must return the draft **unchanged** rather than raise. Raising trips the shared crash policy — the
plugin is disabled for the rest of the boot — which is for genuine bugs, not routine "the model
proposed something invalid" outcomes. Journal the rejection yourself via `context.event(...)` if you
want it auditable; the rest of that turn's narration still commits normally either way.

Filters may mutate their draft and return `None`, or return a replacement. Actions receive their
context. Wrappers receive `(next, context, *args, **kwargs)`. Ordering is a deterministic DAG:
explicit before/after edges first, then descending priority, plugin ID, and registration sequence.

## Ordering defaults and per-hook overrides

`plugin.toml` defines the default order for every registration made by that plugin:

```toml
[order]
before = []
after = ["dev.example.translator"]
priority = 10
```

For filters, execution is sequential: each successful result becomes the next filter's input. Two
plugins writing the same value are therefore not automatically a conflict; they may be an intended
composition. `before` and `after` express required relationships. Priority only orders registrations
that are currently unconstrained by the DAG, and a higher number runs earlier.

The manifest order is a default, not a forced global order. `context.action`, `context.filter`, and
`context.wrapper` accept `before`, `after`, and `priority` for one registration:

```python
def setup(context):
    context.filter(
        "turn.input",
        correct_text,
        after=("dev.example.translator",),
        priority=10,
    )
    context.filter(
        "turn.before_commit",
        validate_state,
        before=("dev.example.translator",),
        priority=100,
    )
```

This permits a plugin to run after another plugin for input transformation but before it for state
validation. Prefer manifest defaults when one relationship is sufficient. Curated review should
require tests for per-hook inversions and inspect the effective order with `plugin_trace`. A cycle
is rejected rather than resolved by priority.

Contribution slots currently include providers, routes, settings, commands, and panels. For an
unanticipated extension, use `context.unsafe` deliberately and document the core object touched.
