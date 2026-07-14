# Alex Tavern Curated Plugins

This is the review and distribution hub for trusted Alex Tavern plugins and Experiences. A plugin
listed here still runs with the same power as the application itself: curation means full-source
review, reproducible packaging, and a fixed SHA-256, not sandboxing.

The framework runtime and SDK live in the main `alex-tavern` repository. This hub contains source,
catalog metadata, authoring documentation, examples, packaged artifacts, and an MCP server designed
for coding agents.

```fish
uv sync
uv run python mcp_server.py --core-root ../roleplay
```

The MCP can read contracts, document structured model calls, scaffold, validate, test, pack, and
inspect plugin traces. Model-backed plugins use the core-owned `context.model.call_json` gateway;
they never handle provider secrets or payloads. The MCP never runs Git commands or publishes
anything.

The curated **Character Converter** demonstrates executable commands. Its
`/convert-character <preset-name>` utility accepts free text or an open Character Card V1/V2/V3
PNG/JSON, validates card metadata locally, and uses the active structured provider to produce a
reviewable native preset draft. It does not use vision, RAG, or automatic persistence.

Before review, run `uv run python check.py --core-root ../roleplay`. It rejects manifest/source,
artifact hash, Experience media, and core-contract drift.

## Plugin ordering and composition

Plugins that use the same hook compose as a deterministic pipeline: the output of one filter is the
input of the next. The manifest's `[order]` table supplies the default relationship for all of a
plugin's registrations:

```toml
[order]
before = []
after = ["dev.example.translator"]
priority = 10
```

Explicit `before`/`after` edges are authoritative. Among registrations without an edge, higher
priority runs first; remaining ties use plugin ID and registration sequence. Cycles are rejected.
Priority controls position, not authority: a later filter can still transform the earlier result.

An unusual plugin may need opposite relationships in different hooks. The backend SDK therefore
lets each registration override the manifest defaults:

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

Prefer manifest-level ordering for the common case. Use per-hook overrides only when the behavior
really differs, and cover that composition in plugin tests and trace review. See
[`docs/hooks.md`](docs/hooks.md) for the detailed execution rules.
