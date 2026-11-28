# angelscript-engine

**[English](README.md)** | **[Español](docs/README.es.md)**

Builds any official [AngelScript](https://www.angelcode.com/angelscript/) release, from 2.20 to the latest, with a few compatibility fixes applied to a copy of the sources. [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) uses it to build one executable per engine version.

This is the **legacy support** for older releases. The current release is built by the CLI straight from the official sources; every earlier release goes through here.

## Use it

~~~sh
python scripts/prepare-sdk.py 2.36.1 --out build/sdk        # prints the SDK folder
cmake -S tests/smoke -B build/smoke -DANGELSCRIPT_SDK=<that folder>
cmake --build build/smoke && ctest --test-dir build/smoke
~~~

In your own project:

~~~cmake
set(ANGELSCRIPT_SDK "<sdk folder>")
include(external/angelscript-engine/cmake/AngelScriptEngine.cmake)
target_link_libraries(host PRIVATE angelscript)
~~~

## Supported targets

| Releases | State |
| --- | --- |
| 2.30 and later | Built and smoke-tested in CI on every target |
| 2.20 to 2.29 | Build; the weekly matrix records which tests pass |
| 2.1 to 2.19 | SDK archives only |

Targets: Windows x64 and x86, Linux x64, x86 and arm64, macOS x64 and arm64. The per-release results are in [docs/ENGINE_VERSIONS.md](docs/ENGINE_VERSIONS.md).

## Documentation

- [Usage](docs/USAGE.md) — scripts, the CMake module, pinned releases and how to add one.
- [Engine versions](docs/ENGINE_VERSIONS.md) — what each release supports.
- [CHANGELOG.md](CHANGELOG.md) — release history.

## Roadmap

- Pin every new AngelScript release as it is published.
- Keep the weekly matrix green for 2.20 and later.

## Support

Open an [issue](https://github.com/angelscript-tools/angelscript-engine/issues) for a release that does not build or a wrong pin. Problems with the executable go to [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli/issues).

## Related

| Project | Use |
| --- | --- |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Run, check and debug scripts from the terminal |
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | Editor support for VS Code |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | Debugger core |
| [angelscript-jit](https://github.com/angelscript-tools/angelscript-jit) | Optional JIT compiler |
| [angelscript-debugger-example](https://github.com/angelscript-tools/angelscript-debugger-example) | A host that shows how to use the debugger |

## Credits

| Project | License | Use |
| --- | --- | --- |
| [AngelScript](https://github.com/anjo76/angelscript) by Andreas Jönsson | zlib | The language and its runtime, built by this module |

## License

This repository is licensed under the [MIT License](LICENSE).
