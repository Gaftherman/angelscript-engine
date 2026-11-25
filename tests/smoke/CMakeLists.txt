cmake_minimum_required(VERSION 3.21)
project(angelscript-engine-smoke LANGUAGES CXX)

# cmake -S tests/smoke -B build -DANGELSCRIPT_SDK=<sdk folder from scripts/prepare-sdk.py>
include("${CMAKE_CURRENT_LIST_DIR}/../../cmake/AngelScriptEngine.cmake")

add_executable(smoke main.cpp)
target_link_libraries(smoke PRIVATE angelscript)
angelscript_engine_force_legacy_std(smoke)
set_target_properties(smoke PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

enable_testing()
add_test(NAME smoke COMMAND smoke)
