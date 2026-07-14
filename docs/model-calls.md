# Structured model calls

Model-backed plugins use `await context.model.call_json(hook_context, ...)`. This is the only
public plugin model API. It always delegates to the active server-side provider, shared HTTP
client, ProviderAdapter, JSON Schema validator, retry policy, timeout, and debug log. It never
returns provider configuration, transport objects, or API keys to plugin code.

The hook context must contain `game`, `turn_number`, and `runner`. The SDK derives `session_id`
from the game and records every attempt as `agent = "plugin:<plugin_id>"`. Declare `model.call` in
`permissions`; permissions are observational review metadata, not a sandbox.

```python
result = await context.model.call_json(
    hook_context,
    messages=[
        {"role": "system", "content": "Return the requested structured result."},
        {"role": "user", "content": source_text},
    ],
    json_schema={
        "name": "example_result",
        "schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    max_tokens=512,
    use_configured_language=True,
)
```

`json_schema` is mandatory and must use the subset exported and validated by the current core.
`max_tokens` must be positive. `use_configured_language=True` injects the application's configured
story language; use `False` only when the operation must preserve the input language verbatim.
Provider-specific payloads, response parsing, schema adaptation, retries, and secret handling stay
inside the core.

Do not import `src.llm.*`, read `runner.client` or `runner.config`, call provider HTTP endpoints,
accept raw keys in plugin config, omit `hook_context`, or implement regex/markdown parsing as a
substitute for the structured result. Let failures escape from pre-commit filters: the runtime
discards the plugin draft, disables the plugin for the boot, and continues with the clean input.

Before authoring, call `plugin_contract` and inspect `services.model.call_json`. Then run
`plugin_validate`, `plugin_test`, `plugin_pack`, and `plugin_trace` through this MCP. A model-backed
plugin should test success, invalid schema output, empty input, provider failure, and that private
fields never migrate into public fields.
