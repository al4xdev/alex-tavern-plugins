# Agent authoring MCP

The stdio MCP exposes documentation, the live exported contract, scaffolding, validation, local
tests, deterministic ZIP packing, and filtered observability traces. Mutating tools only write below
the requested destination. The server has no Git, GitHub, publishing, or installation tool.

Use `plugin_docs(document="model-calls")` for the structured LLM gateway. The live
`plugin_contract` response exports the same API under `services.model.call_json`.

Set `ALEX_TAVERN_ROOT` or pass `--core-root`. The core checkout is the source of truth, so the MCP
does not maintain a second implementation of manifest or hook validation.
