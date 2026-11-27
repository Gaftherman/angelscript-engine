# Changelog

## [0.1.2] - 2026-11-26

### Added

- `engines/versions.json` pins the releases from 2.1.0c to 2.19.2 too (81 pins in total), so `prepare-sdk.py` can fetch every release angelcode.com publishes. They are SDK archives only: angelscript-cli does not build against releases before 2.20.
- The README says which releases build and run, restructured with a dedicated usage guide in `docs/`.
- The weekly matrix reuses the downloaded releases and is skipped when neither this repository nor angelscript-cli changed since the last complete run.

### Changed

- CI skips documentation-only changes, cancels superseded runs and reuses the downloaded release.

---
**Full Changelog**: https://github.com/Gaftherman/angelscript-engine/compare/v0.1.1...v0.1.2

## [0.1.1] - 2026-11-25

### Changed

- The README describes the repository as the legacy support for releases older than the one angelscript-cli bundles. The current release no longer depends on it; the weekly matrix still builds it through `cmake/AngelScriptEngine.cmake`.

---
**Full Changelog**: https://github.com/Gaftherman/angelscript-engine/compare/v0.1.0...v0.1.1

## [0.1.0] - 2026-11-25

### Added

- `scripts/prepare-sdk.py` downloads, verifies, extracts and patches an official AngelScript release, and can write a patched SDK archive.
- `cmake/AngelScriptEngine.cmake` builds that SDK as the `angelscript` target for Windows (x64, x86), Linux (x64, x86, arm64) and macOS (x64, arm64).
- `tests/smoke` host that checks the message callback, native or generic calls, script classes and recursion on each build.
- `scripts/engine-matrix.py`, `scripts/engine-report.py` and `scripts/engine-features.py`, moved from angelscript-cli, with a weekly workflow.
- SHA-256 pins for all 43 releases from 2.20.0 to 2.39.0. A release without a pin is refused unless `--pin` is passed.

### Fixed

- Releases before 2.31 on 64-bit MSVC link `as_callfunc_x64_msvc_asm.asm`, which provides `CallX64` and the `GetReturned*` helpers.
- arm64 releases without a native call convention for the target build in portable mode.
