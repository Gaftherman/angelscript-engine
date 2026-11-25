# Builds an official AngelScript release as the static target `angelscript`.
#
#   set(ANGELSCRIPT_SDK "<folder with angelscript/ and add_on/>")   # see scripts/prepare-sdk.py
#   include(AngelScriptEngine.cmake)
#
# Sets ANGELSCRIPT_ENGINE_NUMBER (23901), ANGELSCRIPT_ENGINE_VERSION ("2.39.1") and ANGELSCRIPT_ENGINE_PORTABLE,
# creates the `angelscript` target and defines two helpers for the targets that compile engine add-ons:
#   angelscript_engine_force_legacy_std(<target>)    releases before 2.31 need std::has_trivial_* traits
#   angelscript_engine_relax_old_sources(<target>)   older sources predate stricter GCC and Clang checks

file(TO_CMAKE_PATH "${ANGELSCRIPT_SDK}" ANGELSCRIPT_SDK)
if(NOT ANGELSCRIPT_SDK OR NOT EXISTS "${ANGELSCRIPT_SDK}/angelscript/include/angelscript.h")
    message(FATAL_ERROR "Set ANGELSCRIPT_SDK to a folder that holds angelscript/include/angelscript.h.")
endif()

set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
set(BUILD_SHARED_LIBS OFF)
set(AS_DISABLE_INSTALL ON)
set(ANGELSCRIPT_ENGINE_DIR "${CMAKE_CURRENT_LIST_DIR}/..")

file(STRINGS "${ANGELSCRIPT_SDK}/angelscript/include/angelscript.h" angelscript_version_line
     REGEX "^#define ANGELSCRIPT_VERSION[ \t]+[0-9]+")
string(REGEX MATCH "[0-9]+$" ANGELSCRIPT_ENGINE_NUMBER "${angelscript_version_line}")
file(STRINGS "${ANGELSCRIPT_SDK}/angelscript/include/angelscript.h" angelscript_version_string_line
     REGEX "^#define ANGELSCRIPT_VERSION_STRING")
string(REGEX MATCH "\"[^\"]+\"" angelscript_version_string "${angelscript_version_string_line}")
string(REPLACE "\"" "" ANGELSCRIPT_ENGINE_VERSION "${angelscript_version_string}")
message(STATUS "Building against AngelScript ${ANGELSCRIPT_ENGINE_VERSION} (${ANGELSCRIPT_ENGINE_NUMBER})")

# The SDK's own CMake project is only dependable from 2.31 on. Earlier releases miss the target or add
# test projects that do not exist in the archive, so the engine sources are built directly.
#
# On arm64 some releases have no native call convention for the target. 2.33 and earlier pick the 32-bit ARM
# assembly (or, on Linux before 2.31, the x86-64 one), 2.35 builds an ELF-only assembly that Apple's assembler
# rejects, and 2.36 predates the Apple silicon port of 2.37. Those builds use the engine's own portable mode
# (AS_MAX_PORTABILITY), which compiles no assembly and calls through the generic convention.
set(ANGELSCRIPT_ENGINE_PORTABLE OFF)
if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm64|aarch64|ARM64)$"
   AND (ANGELSCRIPT_ENGINE_NUMBER LESS 23500
        OR (APPLE AND ANGELSCRIPT_ENGINE_NUMBER LESS 23700)))
    set(ANGELSCRIPT_ENGINE_PORTABLE ON)
    message(STATUS "AngelScript ${ANGELSCRIPT_ENGINE_VERSION} has no native calls on this arm64 target: portable mode")
endif()
if(ANGELSCRIPT_ENGINE_NUMBER GREATER_EQUAL 23100
   AND NOT ANGELSCRIPT_ENGINE_PORTABLE
   AND EXISTS "${ANGELSCRIPT_SDK}/angelscript/projects/cmake/CMakeLists.txt")
    add_subdirectory("${ANGELSCRIPT_SDK}/angelscript/projects/cmake" angelscript)
else()
    file(GLOB angelscript_sources CONFIGURE_DEPENDS "${ANGELSCRIPT_SDK}/angelscript/source/*.cpp")
    add_library(angelscript STATIC ${angelscript_sources})
    find_package(Threads REQUIRED)
    target_link_libraries(angelscript PUBLIC Threads::Threads)
    if(ANGELSCRIPT_ENGINE_PORTABLE)
        target_compile_definitions(angelscript PUBLIC AS_MAX_PORTABILITY)
    elseif(MSVC AND CMAKE_SIZEOF_VOID_P EQUAL 8)
        # The SDK's own CMake adds this MASM file for 64-bit MSVC. Without it CallX64 and the GetReturned*
        # helpers are unresolved in the releases that build from the sources directly (before 2.31).
        enable_language(ASM_MASM)
        if(EXISTS "${ANGELSCRIPT_SDK}/angelscript/source/as_callfunc_x64_msvc_asm.asm")
            target_sources(angelscript PRIVATE "${ANGELSCRIPT_SDK}/angelscript/source/as_callfunc_x64_msvc_asm.asm")
        endif()
    endif()
endif()

set(angelscript_engine_legacy_std_header "${ANGELSCRIPT_ENGINE_DIR}/compat/LegacyStd.h")
function(angelscript_engine_force_legacy_std target)
    if(ANGELSCRIPT_ENGINE_NUMBER LESS 23100)
        if(MSVC)
            target_compile_options(${target} PRIVATE "/FI${angelscript_engine_legacy_std_header}")
        else()
            target_compile_options(${target} PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:SHELL:-include ${angelscript_engine_legacy_std_header}>")
        endif()
    endif()
endfunction()

function(angelscript_engine_relax_old_sources target)
    if(NOT MSVC)
        # C++ only: the arm64 call-convention sources are assembly and have no <cstring>.
        target_compile_options(${target} PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:SHELL:-include cstring>")
        if(ANGELSCRIPT_ENGINE_NUMBER LESS 23100)
            target_compile_options(${target} PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:-fpermissive>")
        endif()
    endif()
endfunction()

angelscript_engine_force_legacy_std(angelscript)
angelscript_engine_relax_old_sources(angelscript)
# Older SDK projects do not export their headers to the targets that link them.
include_directories(SYSTEM "${ANGELSCRIPT_SDK}/angelscript/include")
