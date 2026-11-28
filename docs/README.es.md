# angelscript-engine

**[English](../README.md)** | **[Español](README.es.md)**

Compila cualquier versión oficial de [AngelScript](https://www.angelcode.com/angelscript/), de la 2.20 a la más reciente, con unas pocas correcciones de compatibilidad aplicadas a una copia de las fuentes. [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) lo usa para compilar un ejecutable por versión del motor.

Es el **soporte heredado** de las versiones antiguas. La CLI compila la versión actual directamente desde las fuentes oficiales; todas las anteriores pasan por aquí.

## Cómo usarlo

~~~sh
python scripts/prepare-sdk.py 2.36.1 --out build/sdk        # imprime la carpeta del SDK
cmake -S tests/smoke -B build/smoke -DANGELSCRIPT_SDK=<esa carpeta>
cmake --build build/smoke && ctest --test-dir build/smoke
~~~

En tu propio proyecto:

~~~cmake
set(ANGELSCRIPT_SDK "<carpeta del SDK>")
include(external/angelscript-engine/cmake/AngelScriptEngine.cmake)
target_link_libraries(host PRIVATE angelscript)
~~~

## Destinos admitidos

| Versiones | Estado |
| --- | --- |
| 2.30 y posteriores | Se compilan y se prueban en CI en todos los destinos |
| 2.20 a 2.29 | Se compilan; la matriz semanal registra qué pruebas pasan |
| 2.1 a 2.19 | Solo los archivos del SDK |

Destinos: Windows x64 y x86, Linux x64, x86 y arm64, macOS x64 y arm64. Los resultados por versión están en [ENGINE_VERSIONS.md](ENGINE_VERSIONS.md).

## Documentación

- [Uso](USAGE.es.md) — scripts, el módulo de CMake, versiones fijadas y cómo añadir una.
- [Versiones del motor](ENGINE_VERSIONS.md) — qué admite cada versión.
- [CHANGELOG.md](../CHANGELOG.md) — historial de versiones.

## Hoja de ruta

- Fijar cada versión nueva de AngelScript cuando se publique.
- Mantener la matriz semanal en verde para la 2.20 y posteriores.

## Soporte

Abre una [incidencia](https://github.com/angelscript-tools/angelscript-engine/issues) si una versión no compila o un hash es incorrecto. Los problemas del ejecutable van a [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli/issues).

## Relacionados

| Proyecto | Uso |
| --- | --- |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Ejecuta, comprueba y depura scripts desde la terminal |
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | Soporte del editor para VS Code |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | Núcleo del depurador |
| [angelscript-jit](https://github.com/angelscript-tools/angelscript-jit) | Compilador JIT opcional |
| [angelscript-debugger-example](https://github.com/angelscript-tools/angelscript-debugger-example) | Una aplicación que muestra cómo usar el depurador |

## Créditos

| Proyecto | Licencia | Uso |
| --- | --- | --- |
| [AngelScript](https://github.com/anjo76/angelscript) by Andreas Jönsson | zlib | El lenguaje y su motor de ejecución, que este módulo compila |

## Licencia

Este repositorio está bajo la [licencia MIT](../LICENSE).
