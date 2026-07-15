# Character Converter

Adds `/convert-character` to Alex Tavern. Its typed tool card shows the preset name and accepts
either plain text or one open
Character Card V1/V2/V3 PNG/JSON, calls the active structured model provider, and returns a native
character preset draft for review. It never saves a preset automatically.

PNG parsing is local and strict: every chunk CRC is checked, `ccv3` takes precedence over `chara`,
and ordinary avatar PNGs receive a clear metadata error. Character.AI images, JPEG/WebP, ZIP,
CHARX, vision inference, and RAG are intentionally outside version 1.1. The tool is session-bound,
and the palette explains that an adventure must be open before it can run.

Explain behavior, permissions, configuration, and failure modes.
