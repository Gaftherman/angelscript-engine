#!/usr/bin/env python3
"""Prepares an official AngelScript release for building.

  python scripts/prepare-sdk.py 2.38.0 --out build/sdk
  python scripts/prepare-sdk.py 2.30.2 --out build/sdk --cache build/cache --tarball dist

The release is downloaded from angelcode.com (or taken from --cache), checked against the SHA-256 in
engines/versions.json, extracted to <out>/<version> and patched. The last line printed is the SDK folder,
the one that holds angelscript/ and add_on/. --tarball also writes angelscript-sdk-<version>-patched.tar.gz.
"""

import argparse
import sys
import tarfile
from pathlib import Path

import sdk


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version")
    parser.add_argument("--out", required=True, help="folder that receives <version>/")
    parser.add_argument("--cache", help="folder with angelscript_<version>.zip (default <out>/cache)")
    parser.add_argument("--tarball", help="folder that receives angelscript-sdk-<version>-patched.tar.gz")
    parser.add_argument("--pin", action="store_true", help="record the hash of a release that has no pin yet")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    cache = Path(args.cache).resolve() if args.cache else out / "cache"
    pins_path = sdk.ENGINES / "versions.json"
    pins = sdk.load(pins_path, {})
    archive, _ = sdk.download(args.version, cache, pins, args.pin)
    root = sdk.extract(archive, out / args.version)
    for change in sdk.apply_sdk_fixes(root, args.version, cache, pins, args.pin):
        print(f"compatibility fix in the extracted copy: {change}", file=sys.stderr)
    if args.pin:
        sdk.save(pins_path, pins)
    if args.tarball:
        destination = Path(args.tarball).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        asset = destination / f"angelscript-sdk-{args.version}-patched.tar.gz"
        with tarfile.open(asset, "w:gz") as bundle:
            bundle.add(root, arcname="sdk")
        print(f"wrote {asset}", file=sys.stderr)
    print(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
