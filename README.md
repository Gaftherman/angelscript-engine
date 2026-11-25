# angelscript-engine

Builds any official [AngelScript](https://www.angelcode.com/angelscript/) release, from 2.20 to the latest, with a few compatibility fixes applied to a copy of the sources. [angelscript-cli](https://github.com/Gaftherman/angelscript-cli) uses it to build one executable per engine version.

## What it does

- **`scripts/prepare-sdk.py <version> --out <dir>`** downloads the release from angelcode.com, checks its SHA-256 against `engines/versions.json`, extracts it and patches the copy. It never touches the download. `--tarball <dir>` also writes `angelscript-sdk-<version>-patched.tar.gz`.
- **`cmake/AngelScriptEngine.cmake`** builds that SDK as the static target `angelscript`:
  - Releases before 2.31 are built from their sources, because their own CMake project is unreliable. On 64-bit MSVC it adds the MASM call convention file.
  - arm64 targets without a native call convention (Linux before 2.35, Apple before 2.37) use the engine's portable mode (`AS_MAX_PORTABILITY`).
  - It defines `angelscript_engine_force_legacy_std()` (the `std::has_trivial_*` traits of 2.30 and earlier) and `angelscript_engine_relax_old_sources()` for targets that compile add-ons.
- **`scripts/engine-matrix.py`** builds and tests the CLI against every release and records `engines/matrix.json`. `scripts/engine-report.py` turns it into [docs/ENGINE_VERSIONS.md](docs/ENGINE_VERSIONS.md).

The fixes are listed in `scripts/sdk.py` (`SDK_FIXES` and `SDK_BORROW`). Each one is a one-line change that a current compiler requires.

## Use it

```sh
python scripts/prepare-sdk.py 2.36.1 --out build/sdk        # prints the SDK folder
cmake -S tests/smoke -B build/smoke -DANGELSCRIPT_SDK=<that folder>
cmake --build build/smoke && ctest --test-dir build/smoke
```

In your own project:

```cmake
set(ANGELSCRIPT_SDK "<sdk folder>")
include(external/angelscript-engine/cmake/AngelScriptEngine.cmake)
target_link_libraries(host PRIVATE angelscript)
```

The module sets `ANGELSCRIPT_ENGINE_NUMBER` (for example 23600), `ANGELSCRIPT_ENGINE_VERSION` and `ANGELSCRIPT_ENGINE_PORTABLE`.

## Supported targets

CI builds and runs `tests/smoke` for 2.30.2, 2.33.0, 2.35.1, 2.36.1, 2.37.0 and 2.38.0 on Windows x64 and x86, Linux x64, x86 and arm64, and macOS x64 and arm64. The weekly workflow tests every release from 2.20.0 with the full CLI test suite.

A new release needs its SHA-256 in `engines/versions.json`: run `prepare-sdk.py <version> --pin`.

## License

[MIT](LICENSE). AngelScript is distributed under the zlib license by Andreas Jönsson.
