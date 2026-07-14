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

Before review, run `uv run python check.py --core-root ../roleplay`. It rejects manifest/source,
artifact hash, Experience media, and core-contract drift.
