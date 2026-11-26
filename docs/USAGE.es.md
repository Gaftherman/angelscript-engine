# Uso

**[English](USAGE.md)** | **[Español](USAGE.es.md)**

## Qué hace

- **`scripts/prepare-sdk.py <versión> --out <carpeta>`** descarga la versión desde angelcode.com, comprueba su SHA-256 con `engines/versions.json`, la extrae y parchea la copia. Nunca modifica la descarga. `--tarball <carpeta>` escribe además `angelscript-sdk-<versión>-patched.tar.gz`.
- **`cmake/AngelScriptEngine.cmake`** compila ese SDK como el destino estático `angelscript`:
  - Las versiones anteriores a la 2.31 se compilan desde sus fuentes, porque su propio proyecto de CMake no es fiable. En MSVC de 64 bits añade el archivo MASM de la convención de llamadas.
  - Los destinos arm64 sin convención de llamadas nativa (Linux antes de la 2.35, Apple antes de la 2.37) usan el modo portátil del motor (`AS_MAX_PORTABILITY`).
  - Define `angelscript_engine_force_legacy_std()` (los rasgos `std::has_trivial_*` de la 2.30 y anteriores) y `angelscript_engine_relax_old_sources()` para los destinos que compilan add-ons.
- **`scripts/engine-matrix.py`** compila y prueba la CLI con cada versión y registra `engines/matrix.json`. `scripts/engine-report.py` lo convierte en [ENGINE_VERSIONS.md](ENGINE_VERSIONS.md).

Las correcciones están en `scripts/sdk.py` (`SDK_FIXES` y `SDK_BORROW`). Cada una es un cambio de una línea que exige un compilador actual.

El módulo define `ANGELSCRIPT_ENGINE_NUMBER` (por ejemplo 23600), `ANGELSCRIPT_ENGINE_VERSION` y `ANGELSCRIPT_ENGINE_PORTABLE`.

## Qué versiones

`engines/versions.json` fija todas las versiones 2.x que publica angelcode.com, de la 2.1.0c a la actual (81 hashes SHA-256), así que `prepare-sdk.py` puede descargar cualquiera.

| Versiones | Qué funciona |
| --- | --- |
| 2.30 y posteriores | Se compilan y se prueban en CI en todos los destinos. Son las versiones que distribuye angelscript-cli. |
| 2.20 a 2.29 | Se compilan con este módulo; `engines/matrix.json` registra qué pruebas de la CLI pasan. La 2.20.0 y la 2.20.1 fallan en cerca de la mitad. |
| 2.1 a 2.19 | Solo los archivos del SDK. Los add-ons de estas versiones suponen un `size_t` de 32 bits y la API del contexto no tiene pila de llamadas por nivel, así que angelscript-cli no compila con ellas. |

## Papel

La CLI instala una versión de AngelScript cada vez. [angelscript-cli](https://github.com/Gaftherman/angelscript-cli) compila la versión actual desde su submódulo `external/angelscript`, porque no necesita parches. La matriz semanal también compila la versión actual con este módulo, para que una regresión del módulo se vea antes de que una versión antigua la necesite. Las versiones que ofrece la CLI están en `scripts/plan-engine-builds.py` de angelscript-cli.

## Destinos en CI

`tests/smoke` se ejecuta para 2.30.2, 2.33.0, 2.35.1, 2.36.1, 2.37.0 y 2.38.0 en Windows x64 y x86, Linux x64, x86 y arm64, y macOS x64 y arm64. El flujo semanal prueba cada versión desde la 2.20.0 con el conjunto completo de pruebas de la CLI.

## Añadir una versión

Una versión nueva necesita su SHA-256 en `engines/versions.json`: ejecuta `prepare-sdk.py <versión> --pin`.
