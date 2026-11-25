# Changelog

## [0.1.1]

### Changed

- The README describes the repository as the legacy support for releases older than the one angelscript-cli bundles. The current release no longer depends on it; the weekly matrix still builds it through `cmake/AngelScriptEngine.cmake`.

## [0.1.0]

### Added

- `scripts/prepare-sdk.py` downloads, verifies, extracts and patches an official AngelScript release, and can write a patched SDK archive.
- `cmake/AngelScriptEngine.cmake` builds that SDK as the `angelscript` target for Windows (x64, x86), Linux (x64, x86, arm64) and macOS (x64, arm64).
- `tests/smoke` host that checks the message callback, native or generic calls, script classes and recursion on each build.
- `scripts/engine-matrix.py`, `scripts/engine-report.py` and `scripts/engine-features.py`, moved from angelscript-cli, with a weekly workflow.
- SHA-256 pins for all 43 releases from 2.20.0 to 2.39.0. A release without a pin is refused unless `--pin` is passed.

### Fixed

- Releases before 2.31 on 64-bit MSVC link `as_callfunc_x64_msvc_asm.asm`, which provides `CallX64` and the `GetReturned*` helpers.
- arm64 releases without a native call convention for the target build in portable mode.
