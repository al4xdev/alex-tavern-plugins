"""MCP server for AI-assisted Alex Tavern plugin authorship."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)
MUTATING = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=False,
)


def create_server(core_root: Path, hub_root: Path) -> FastMCP:
    resolved_core = core_root.resolve(strict=True)
    resolved_hub = hub_root.resolve(strict=True)
    sys.path.insert(0, str(resolved_core))
    from src.plugins.contracts import exported_contract
    from tools.plugin_author import (
        pack_plugin,
        scaffold_plugin,
        test_plugin,
        trace_plugin,
        validate_plugin,
    )

    server = FastMCP(
        "Alex Tavern Plugin Author",
        instructions=(
            "Create trusted in-process Alex Tavern plugins. Read the contract before choosing hooks. "
            "No tool performs Git operations or publication."
        ),
    )

    @server.tool(annotations=READ_ONLY)
    def plugin_docs(document: str = "sdk") -> str:
        """Read one authoring document: manifest, sdk, hooks, or mcp."""
        if document not in {"manifest", "sdk", "hooks", "mcp"}:
            raise ValueError("document must be manifest, sdk, hooks, or mcp")
        return (resolved_hub / "docs" / f"{document}.md").read_text(encoding="utf-8")

    @server.tool(annotations=READ_ONLY)
    def plugin_contract() -> dict[str, Any]:
        """Return the exact hooks, contexts, permissions, and crash semantics from core."""
        return exported_contract()

    @server.tool(annotations=MUTATING)
    def plugin_scaffold(
        destination: str,
        plugin_id: str,
        name: str,
        backend: bool = True,
        frontend: bool = False,
    ) -> dict[str, Any]:
        """Create a new plugin package with current manifest and entrypoint skeletons."""
        return scaffold_plugin(
            Path(destination), plugin_id, name, backend=backend, frontend=frontend
        )

    @server.tool(annotations=READ_ONLY)
    def plugin_validate(package: str) -> dict[str, Any]:
        """Validate manifest, entrypoints, and Python/JavaScript syntax against core."""
        return validate_plugin(Path(package))

    @server.tool(annotations=READ_ONLY)
    def plugin_test(package: str) -> dict[str, Any]:
        """Run contract checks and plugin-local pytest tests when present."""
        return test_plugin(Path(package))

    @server.tool(annotations=MUTATING)
    def plugin_pack(package: str, output: str) -> dict[str, Any]:
        """Build a deterministic ZIP and report its version and SHA-256."""
        return pack_plugin(Path(package), Path(output))

    @server.tool(annotations=READ_ONLY)
    def plugin_trace(plugin_id: str, limit: int = 200) -> list[dict[str, Any]]:
        """Read observable runtime events for one plugin from the core data directory."""
        return trace_plugin(plugin_id, limit)

    return server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, default=Path("../roleplay"))
    args = parser.parse_args()
    create_server(args.core_root, Path(__file__).resolve().parent).run(transport="stdio")


if __name__ == "__main__":
    main()
