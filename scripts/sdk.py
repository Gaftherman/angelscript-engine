"""Downloads, verifies and patches the official AngelScript SDK releases.

Every release is pinned by SHA-256 in engines/versions.json. The fixes are applied only to the extracted copy
of a release, never to the download.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINES = ROOT / "engines"
BASE = "https://www.angelcode.com/angelscript"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url, timeout=120):
    # angelcode.com rejects requests that do not look like a browser.
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def version_key(version):
    return [int(part) if part.isdigit() else part for part in re.split(r"[.]|(?<=\d)(?=[a-z])", version)]


def official_versions():
    html = fetch(f"{BASE}/downloads.html").decode("utf-8", "replace")
    found = set(re.findall(r"/angelscript/sdk/files/angelscript_([0-9][0-9.]*[0-9a-z]?)\.zip", html))
    return sorted(found, key=version_key)


def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def download(version, cache, pins, pin=False):
    archive = cache / f"angelscript_{version}.zip"
    if not archive.exists():
        cache.mkdir(parents=True, exist_ok=True)
        archive.write_bytes(fetch(f"{BASE}/sdk/files/angelscript_{version}.zip"))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    pinned = pins.get(version)
    if pinned and pinned != digest:
        raise SystemExit(f"SHA-256 of angelscript_{version}.zip changed: pinned {pinned}, got {digest}")
    if not pinned:
        if not pin:
            raise SystemExit(f"angelscript_{version}.zip has no pin in engines/versions.json (sha256 {digest}); pass --pin to record it")
        pins[version] = digest
    return archive, digest


def extract(archive, destination):
    if destination.exists():
        shutil.rmtree(destination)
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(destination)
    for candidate in (destination / "sdk", *destination.glob("*/sdk")):
        if (candidate / "angelscript" / "include" / "angelscript.h").exists():
            return candidate
    # The oldest layouts have no sdk/ folder: find the include directory and take the folder above angelscript/.
    for header in destination.rglob("angelscript.h"):
        if header.parent.name == "include" and header.parent.parent.name == "angelscript":
            return header.parent.parent.parent
    raise RuntimeError("no sdk/angelscript/include/angelscript.h in the archive")


# Fixes applied to the extracted copy of a release, never to the repository or the download. Each one is a
# one-line change that a current compiler requires and that does not alter behaviour.
SDK_FIXES = [
    # scriptarray.cpp of 2.24 and 2.25 compares a function pointer with >= 0.
    ("add_on/scriptarray/scriptarray.cpp", "cache->cmpFunc >= 0", "cache->cmpFunc != 0"),
    # angelscript.h of 2.20 and 2.21 returns 0 where an asSFuncPtr is expected in a template that is never used.
    (
        "angelscript/include/angelscript.h",
        r"(ERROR_UnsupportedMethodPtr\[N-100\];\s*)return 0;",
        r"\1return asSFuncPtr();",
    ),
    # as_compiler.cpp of 2.20.2 passes false where an object type pointer is expected.
    ("angelscript/source/as_compiler.cpp", "&funcPtr, node, true, true, false);", "&funcPtr, node, true, true, 0);"),
    # as_callfunc_x64_gcc.cpp before 2.39 defines global asm labels that clash on Clang/macOS; 2.39 prefixes them with L.
    ("angelscript/source/as_callfunc_x64_gcc.cpp", "jle endstack \\n", "jle Lendstack \\n"),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", '"loopstack: \\n', '"Lloopstack: \\n'),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", "jne loopstack \\n", "jne Lloopstack \\n"),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", '"endstack: \\n', '"Lendstack: \\n'),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", "je intret \\n", "je Lintret \\n"),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", "jmp endcall \\n", "jmp Lendcall \\n"),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", '"intret: \\n', '"Lintret: \\n'),
    ("angelscript/source/as_callfunc_x64_gcc.cpp", '"endcall: \\n', '"Lendcall: \\n'),
    # aswrappedcall.h of 2.35 uses AS_METHOD_AMBIGUITY_CAST inside a template, which Clang rejects; 2.36.0 added this branch.
    # The unindented #define only exists before 2.36, where the same line sits inside the #if.
    (
        "add_on/autowrapper/aswrappedcall.h",
        r"(?m)^(#define WRAP_MFN_PR\(ClassType, name, Parameters, ReturnType\) asFUNCTION\(.*AS_METHOD_AMBIGUITY_CAST.*)$",
        "#if defined(__clang__)\n"
        "#define WRAP_MFN_PR(ClassType, name, Parameters, ReturnType) "
        "asFUNCTION((::gw::Wrapper<ReturnType (ClassType::*)Parameters>::TMPL f< &ClassType::name >))\n"
        "#else\n"
        r"\1"
        "\n#endif",
    ),
]


# Source files that an official release replaced in the next point release to fix a crash or a wrong result.
# They are copied from that release into the extracted copy of the older one (the engine stays the official one).
SDK_BORROW = {
    "2.22.0": ("2.23.1", ["angelscript/source/as_callfunc.h", "angelscript/source/as_callfunc_x64_gcc.cpp"]),
    "2.22.1": ("2.23.1", ["angelscript/source/as_callfunc.h", "angelscript/source/as_callfunc_x64_gcc.cpp"]),
    "2.22.2": ("2.23.1", ["angelscript/source/as_callfunc.h", "angelscript/source/as_callfunc_x64_gcc.cpp"]),
    "2.23.0": ("2.23.1", ["angelscript/source/as_callfunc_x64_gcc.cpp"]),
    "2.26.0": ("2.26.2", ["angelscript/source/as_callfunc_x64_gcc.cpp"]),
    "2.26.1": ("2.26.2", ["angelscript/source/as_callfunc_x64_gcc.cpp"]),
}


def borrow_sources(sdk, version, cache, pins, pin=False):
    donor, files = SDK_BORROW.get(version, (None, []))
    applied = []
    if not donor:
        return applied
    archive, _ = download(donor, cache, pins, pin)
    with zipfile.ZipFile(archive) as bundle:
        for relative in files:
            member = next((n for n in bundle.namelist() if n.endswith("/" + relative) or n == relative), None)
            if member:
                (sdk / relative).write_bytes(bundle.read(member))
                applied.append(f"{relative}: taken from {donor}")
    return applied


def apply_sdk_fixes(sdk, version=None, cache=None, pins=None, pin=False):
    applied = borrow_sources(sdk, version, cache, pins, pin) if version and cache is not None else []
    for relative, old, new in SDK_FIXES:
        path = sdk / relative
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            changed = re.sub(old, new, text) if old.startswith("(") else text.replace(old, new)
            if changed != text:
                path.write_text(changed, encoding="utf-8", errors="surrogateescape", newline="")
                applied.append(f"{relative}: {old} -> {new}")
    return applied


def run(command, cwd, log):
    with log.open("a", encoding="utf-8", errors="replace") as out:
        out.write("$ " + " ".join(map(str, command)) + "\n")
        out.flush()
        return subprocess.run(command, cwd=cwd, stdout=out, stderr=subprocess.STDOUT).returncode


def first_error(log):
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    for line in text.splitlines():
        if re.search(r"\b(error|Error|FAILED|undefined reference)\b", line):
            return line.strip()[:300]
    return ""
