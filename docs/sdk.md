# SDK and trust model

Backend entrypoints export `setup(context)`. The context exposes `action`, `filter`, `wrapper`,
`contribute`, plugin-owned atomic config, observable HTTP, events, and the explicit `unsafe` escape
hatch. Frontend entrypoints export `activate(sdk)` and may register provider adapters, hooks, or mount
UI into named slots. They can also reach `window` and `document` through `unsafe`.

There is no sandbox. Permissions document accesses in the journal and support code review; they do
not block code. A curated artifact is trusted because its complete source was reviewed and its ZIP
hash is fixed. Third-party ZIPs are the installer's responsibility.

Before-commit filters receive a deep draft. If a plugin raises, that draft is discarded, the plugin
is disabled for the rest of the boot, and clean execution continues. Post-commit actions are never
retried. External side effects cannot be rolled back.
