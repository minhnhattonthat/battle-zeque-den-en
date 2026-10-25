"""textcover.py: which dialogue strings a warp run displayed (logs of tools/lua/textcover.lua).

    python -X utf8 tools/textcover.py work/qa/cover [--rom build/bzd_en.sfc]

A string counts as shown when the game read its first byte. Prints the ids never shown, with their script uses;
exit 1 if any.
"""
import argparse
import re
import sys
from pathlib import Path

import build
import script_vm


def starts(rom, orig):
    """{id (original $83 address): address of the string in rom} through the script ops that point at it."""
    out = {}
    for addr, uses in script_vm.text_pointers(orig).items():
        _, at = uses[0]
        out[addr] = int.from_bytes(rom[script_vm.BANK + at + 1:script_vm.BANK + at + 3], "little")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", type=Path)
    ap.add_argument("--rom", type=Path, default=build.OUT)
    a = ap.parse_args()
    read = {int(m, 16) for log in a.logs.glob("*/log.txt")
            for m in re.findall(r"^TEXT ([0-9A-F]{4})", log.read_text(encoding="utf-8"), re.M)}
    orig = build.ROM.read_bytes()
    st = starts(a.rom.read_bytes(), orig)
    uses = {int(e["id"], 16): e["uses"] for e in build.load("dialogue")}
    missing = sorted(i for i, at in st.items() if at not in read)
    for i in missing:
        print(f"never shown: {i:04X} uses {' '.join(uses[i])}")
    print(f"{len(st) - len(missing)}/{len(st)} strings shown")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
