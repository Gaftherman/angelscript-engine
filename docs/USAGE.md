# Usage

**[English](USAGE.md)** | **[Español](USAGE.es.md)**

## What it does

- **`scripts/prepare-sdk.py <version> --out <dir>`** downloads the release from angelcode.com, checks its SHA-256 against `engines/versions.json`, extracts it and patches the copy. It never touches the download. `--tarball <dir>` also writes `angelscript-sdk-<version>-patched.tar.gz`.
- **`cmake/AngelScriptEngine.cmake`** builds that SDK as the static target `angelscript`:
  - Releases before 2.31 are built from their sources, because their own CMake project is unreliable. On 64-bit MSVC it adds the MASM call convention file.
  - arm64 targets without a native call convention (Linux before 2.35, Apple before 2.37) use the engine's portable mode (`AS_MAX_PORTABILITY`).
  - It defines `angelscript_engine_force_legacy_std()` (the `std::has_trivial_*` traits of 2.30 and earlier) and `angelscript_engine_relax_old_sources()` for targets that compile add-ons.
- **`scripts/engine-matrix.py`** builds and tests the CLI against every release and records `engines/matrix.json`. `scripts/engine-report.py` turns it into [ENGINE_VERSIONS.md](ENGINE_VERSIONS.md).

The fixes are listed in `scripts/sdk.py` (`SDK_FIXES` and `SDK_BORROW`). Each one is a one-line change that a current compiler requires.

The module sets `ANGELSCRIPT_ENGINE_NUMBER` (for example 23600), `ANGELSCRIPT_ENGINE_VERSION` and `ANGELSCRIPT_ENGINE_PORTABLE`.

## Which releases

`engines/versions.json` pins every 2.x release angelcode.com publishes, from 2.1.0c to the current one (81 SHA-256 hashes), so `prepare-sdk.py` can fetch any of them.

| Releases | What works |
| --- | --- |
| 2.30 and later | Built and smoke-tested on every target in CI. These are the releases angelscript-cli ships. |
| 2.20 to 2.29 | Build through this module; `engines/matrix.json` records which tests of the CLI pass. 2.20.0 and 2.20.1 crash in about half of them. |
| 2.1 to 2.19 | The SDK archives only. The add-ons of these releases assume a 32-bit `size_t` and the context API has no call stack by level, so angelscript-cli does not build against them. |

## Role

The CLI installs one AngelScript release at a time. The current release is built by [angelscript-cli](https://github.com/Gaftherman/angelscript-cli) from its `external/angelscript` submodule, because it needs no patches. The weekly matrix still builds the current release through this module too, so a regression in the module shows up before an older release needs it. The releases the CLI offers are listed in `scripts/plan-engine-builds.py` of angelscript-cli.

## Targets in CI

`tests/smoke` runs for 2.30.2, 2.33.0, 2.35.1, 2.36.1, 2.37.0 and 2.38.0 on Windows x64 and x86, Linux x64, x86 and arm64, and macOS x64 and arm64. The weekly workflow tests every release from 2.20.0 with the full CLI test suite.

## Add a release

A new release needs its SHA-256 in `engines/versions.json`: run `prepare-sdk.py <version> --pin`.
