# AngelScript engine versions

angelscript-cli builds against any official release from [angelcode.com](https://www.angelcode.com/angelscript/downloads.html). This table is the result of `scripts/engine-matrix.py`, which downloads each release, checks its SHA-256 against `engines/versions.json`, builds the CLI on Linux x64 and runs the test suite.

- **Full**: runs, checks and debugs scripts. The debugger needs the context and function introspection of 2.36 and later.
- **Run and check**: runs and checks scripts. `--dap-port` reports that debugging needs 2.36.0 or later. Releases before 2.33 skip the tests for the `filesystem` and `datetime` add-ons, whose API differs.
- **Partial**: builds, but some of the CLI's tests fail on that release. Prefer the nearest newer release listed as Run and check or Full.
- **Unsupported**: the release does not build. Releases before 2.22 run through the function-id API, and two one-line fixes are applied to the extracted copy of 2.20 to 2.21 and 2.24 to 2.25 (see `scripts/sdk.py`).

2.22.0 to 2.22.2, 2.23.0, 2.26.0 and 2.26.1 return wrong float results or crash on Linux x64 because of their `as_callfunc_x64_gcc.cpp`. The extracted copy takes that file (and `as_callfunc.h` for 2.22) from the next point release, 2.23.1 or 2.26.2, and nothing else, so the engine stays the official one. 2.20.0, 2.20.1 and 2.31.0 crash in other places of the engine and are not patched; use 2.20.2, 2.21.0 or later, and 2.31.1.

2.35.1 does not build with Clang (macOS, Linux with clang) because of `WRAP_MFN_PR` in its `aswrappedcall.h`. The extracted copy gets the Clang branch that 2.36.0 added to that macro, and nothing else.

On arm64, releases up to 2.33 (and 2.35 and 2.36 on macOS, which predate the Apple silicon port of 2.37) build in the engine's portable mode (`AS_MAX_PORTABILITY`): no assembly, generic calls only. The `filesystem` and `datetime` add-ons are left out of those builds when the release has no portable registration for them.

`angelscript --dump-predefined` needs 2.39.0 or later.

| AngelScript | Support | Builds | Tests | Debugger (DAP) | Note |
| --- | --- | --- | --- | --- | --- |
| 2.39.0 | Full | yes | 25/25 | yes |  |
| 2.38.0 | Full | yes | 25/25 | yes |  |
| 2.37.0 | Full | yes | 25/25 | yes |  |
| 2.36.1 | Full | yes | 25/25 | yes |  |
| 2.36.0 | Full | yes | 25/25 | yes |  |
| 2.35.1 | Run and check | yes | 24/24 | no |  |
| 2.35.0 | Run and check | yes | 24/24 | no |  |
| 2.34.0 | Run and check | yes | 24/24 | no |  |
| 2.33.0 | Run and check | yes | 24/24 | no |  |
| 2.32.0 | Run and check | yes | 21/21 | no |  |
| 2.31.2 | Run and check | yes | 21/21 | no |  |
| 2.31.1 | Run and check | yes | 21/21 | no |  |
| 2.31.0 | Partial | yes | 19/21 | no | the engine crashes (segmentation fault) in 2 tests; fixed in 2.31.1 |
| 2.30.2 | Run and check | yes | 21/21 | no |  |
| 2.30.1 | Run and check | yes | 21/21 | no |  |
| 2.30.0 | Run and check | yes | 21/21 | no |  |
| 2.29.2 | Run and check | yes | 21/21 | no |  |
| 2.29.1 | Run and check | yes | 21/21 | no |  |
| 2.29.0 | Run and check | yes | 21/21 | no |  |
| 2.28.2 | Run and check | yes | 21/21 | no |  |
| 2.28.1 | Run and check | yes | 21/21 | no |  |
| 2.28.0 | Run and check | yes | 21/21 | no |  |
| 2.27.1 | Run and check | yes | 21/21 | no |  |
| 2.27.0 | Run and check | yes | 21/21 | no |  |
| 2.26.3 | Run and check | yes | 21/21 | no |  |
| 2.26.2 | Run and check | yes | 21/21 | no |  |
| 2.26.1 | Run and check | yes | 21/21 | no |  |
| 2.26.0 | Run and check | yes | 21/21 | no |  |
| 2.25.2 | Run and check | yes | 21/21 | no |  |
| 2.25.1 | Run and check | yes | 21/21 | no |  |
| 2.25.0 | Run and check | yes | 21/21 | no |  |
| 2.24.1 | Run and check | yes | 21/21 | no |  |
| 2.24.0a | Run and check | yes | 21/21 | no |  |
| 2.23.1 | Run and check | yes | 21/21 | no |  |
| 2.23.0 | Run and check | yes | 21/21 | no |  |
| 2.22.2 | Partial | yes | 20/21 | no | 1 test fails: this release lacks a script feature the test uses |
| 2.22.1 | Partial | yes | 20/21 | no | 1 test fails: this release lacks a script feature the test uses |
| 2.22.0 | Partial | yes | 20/21 | no | 1 test fails: this release lacks a script feature the test uses |
| 2.21.0 | Partial | yes | 20/21 | no | 1 test fails: this release lacks a script feature the test uses |
| 2.20.3 | Partial | yes | 18/21 | no | 3 tests fail: this release lacks script features the tests use (global initializers with calls, add-on join) |
| 2.20.2 | Partial | yes | 18/21 | no | 3 tests fail: this release lacks script features the tests use (global initializers with calls, add-on join) |
| 2.20.1 | Partial | yes | 10/21 | no | the engine crashes (segmentation fault) in 11 tests |
| 2.20.0 | Partial | yes | 10/21 | no | the engine crashes (segmentation fault) in 11 tests |

Only versions that appear in the table were tested. Run `python scripts/engine-matrix.py --cli <angelscript-cli checkout> --versions X.Y.Z` to test another one, and `python scripts/engine-report.py` to refresh this page.
