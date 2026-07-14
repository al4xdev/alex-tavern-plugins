"""Reject catalog hash, source, Experience, and exported-contract drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, default=Path("../roleplay"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(args.core_root.resolve(strict=True)))
    from src.plugins.experiences import parse_experience
    from src.plugins.store import validate_package

    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 1:
        raise ValueError("catalog schema_version must be 1")
    seen_releases: set[tuple[str, str]] = set()
    for entry in catalog["plugins"]:
        release = (entry["id"], entry["version"])
        if release in seen_releases:
            raise ValueError(f"Duplicate catalog release for {entry['id']}@{entry['version']}")
        seen_releases.add(release)
        source_name = Path(entry["artifact"]).stem.removesuffix(f"-{entry['version']}")
        source = next(
            path
            for path in (root / "plugins").iterdir()
            if path.name.replace("_", "-").startswith(source_name)
        )
        manifest = validate_package(source)
        if manifest.plugin_id != entry["id"] or manifest.version != entry["version"]:
            raise ValueError(f"Source/catalog drift for {entry['id']}")
        artifact = root / entry["artifact"]
        actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if actual_hash != entry["sha256"]:
            raise ValueError(f"Artifact hash drift for {entry['id']}")
        with tempfile.TemporaryDirectory(prefix="alex-tavern-hub-check-") as temporary:
            extracted = Path(temporary)
            with zipfile.ZipFile(artifact) as archive:
                archive.extractall(extracted)
            artifact_manifest = validate_package(extracted)
        if (
            artifact_manifest.plugin_id != entry["id"]
            or artifact_manifest.version != entry["version"]
        ):
            raise ValueError(f"Artifact/source drift for {entry['id']}")
    for entry in catalog["experiences"]:
        parse_experience(json.loads((root / entry["manifest"]).read_text(encoding="utf-8")))
        if not (root / entry["image"]).is_file():
            raise ValueError(f"Missing Experience image: {entry['image']}")
    print(
        json.dumps(
            {
                "valid": True,
                "plugins": len(catalog["plugins"]),
                "experiences": len(catalog["experiences"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
