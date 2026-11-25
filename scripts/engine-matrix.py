#!/usr/bin/env python3
"""Builds and tests angelscript-cli against official AngelScript releases.

  python scripts/engine-matrix.py --cli ../angelscript-cli --list
  python scripts/engine-matrix.py --cli ../angelscript-cli --versions 2.38.0,2.37.0 --work build/matrix
  python scripts/engine-matrix.py --cli ../angelscript-cli --from 2.20.0 --work build/matrix

Each run records, per version, whether the CLI builds, whether CTest passes and the first error in
engines/matrix.json. A version without a pin in engines/versions.json is refused unless --pin is passed.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

from sdk import ENGINES, ROOT, apply_sdk_fixes, download, extract, first_error, load, official_versions, run, save, version_key


def test_version(version, cli, work, cache, pins, jobs, pin):
    started = time.time()
    archive, digest = download(version, cache, pins, pin)
    sdk_dir = extract(archive, work / "sdk" / version)
    apply_sdk_fixes(sdk_dir, version, cache, pins, pin)
    build = work / "build" / version
    log = work / "logs" / f"{version}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.unlink(missing_ok=True)
    if build.exists():
        shutil.rmtree(build)
    result = {
        "version": version,
        "sha256": digest,
        "configure": False,
        "builds": False,
        "tests": {"passed": 0, "total": 0},
        "error": "",
    }
    configure = [
        "cmake",
        "-S",
        str(cli),
        "-B",
        str(build),
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        f"-DANGELSCRIPT_SDK={sdk_dir}",
        f"-DANGELSCRIPT_ENGINE_DIR={ROOT}",
    ]
    if os.environ.get("ASDEBUGGER_DIR"):
        configure.append(f"-DASDEBUGGER_DIR={os.environ['ASDEBUGGER_DIR']}")
    if run(configure, cli, log) == 0:
        result["configure"] = True
        if run(["cmake", "--build", str(build), "--parallel", str(jobs)], cli, log) == 0:
            result["builds"] = True
            run(["ctest", "--test-dir", str(build), "--output-on-failure"], cli, log)
            summary = re.findall(
                r"(\d+)% tests passed, (\d+) tests failed out of (\d+)",
                log.read_text(encoding="utf-8", errors="replace"),
            )
            if summary:
                _, failed, total = map(int, summary[-1])
                result["tests"] = {"passed": total - failed, "total": total}
    if not result["builds"]:
        result["error"] = first_error(log)
    result["seconds"] = round(time.time() - started)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="print the official versions and exit")
    parser.add_argument("--versions", help="comma separated versions")
    parser.add_argument("--from", dest="start", help="every official version from this one up")
    parser.add_argument("--cli", required=True, help="checkout of angelscript-cli to build against each release")
    parser.add_argument("--pin", action="store_true", help="record the hash of a release that has no pin yet")
    parser.add_argument("--work", default="build/matrix")
    parser.add_argument("--cache", default=None)
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--out", default=str(ENGINES / "matrix.json"))
    args = parser.parse_args()

    if args.list:
        print("\n".join(official_versions()))
        return 0
    if args.versions:
        versions = args.versions.split(",")
    elif args.start:
        versions = [v for v in official_versions() if version_key(v) >= version_key(args.start)]
    else:
        parser.error("pass --versions, --from or --list")

    work = Path(args.work).resolve()
    cache = Path(args.cache) if args.cache else work / "cache"
    pins_path = ENGINES / "versions.json"
    pins = load(pins_path, {})
    out = Path(args.out)
    matrix = {row["version"]: row for row in load(out, [])}
    for version in versions:
        print(f"== AngelScript {version}", flush=True)
        try:
            row = test_version(version, Path(args.cli).resolve(), work, cache, pins, args.jobs, args.pin)
        except Exception as exc:  # a missing archive or a broken zip is a result, not a crash
            row = {
                "version": version,
                "configure": False,
                "builds": False,
                "tests": {"passed": 0, "total": 0},
                "error": f"{type(exc).__name__}: {exc}",
            }
        matrix[version] = row
        print(json.dumps(row), flush=True)
        save(pins_path, pins)
        save(out, sorted(matrix.values(), key=lambda r: version_key(r["version"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
