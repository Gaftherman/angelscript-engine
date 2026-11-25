#!/usr/bin/env python3
"""Finds the first official release that declares each asEP_* engine property.

  python scripts/engine-features.py --cache <dir with angelscript_<ver>.zip> [--out engines/properties.json]

The LSP uses the result to tell a project that sets an engine property newer than its engine profile.
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def key(version):
    return [int(p) if p.isdigit() else p for p in re.split(r"[.]|(?<=\d)(?=[a-z])", version)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "engines" / "properties.json"))
    args = parser.parse_args()
    archives = {}
    for path in Path(args.cache).glob("angelscript_*.zip"):
        archives[path.stem.split("_", 1)[1]] = path
    first = {}
    for version in sorted(archives, key=key):
        with zipfile.ZipFile(archives[version]) as bundle:
            name = next((n for n in bundle.namelist() if n.endswith("angelscript/include/angelscript.h")), None)
            if not name:
                continue
            text = bundle.read(name).decode("utf-8", "replace")
        for prop in re.findall(r"\b(asEP_[A-Z0-9_]+)\b", text):
            if prop != "asEP_LAST_PROPERTY":
                first.setdefault(prop, version)
    result = {"properties": dict(sorted(first.items())), "versions": sorted(archives, key=key)}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    for prop, version in sorted(first.items(), key=lambda kv: (key(kv[1]), kv[0])):
        print(f"{version:8} {prop}")


if __name__ == "__main__":
    main()
