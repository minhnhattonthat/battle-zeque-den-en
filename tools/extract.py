"""extract.py: dump the dialogue block and the prologue to script/*.json (phase 4). Never overwrites a file.

    python -X utf8 tools/extract.py

script/dialogue.json: one entry per string of the bank-$83 block, in block order:
  id    "AA38" (CPU address in bank $83, stable)    uses  ["slot:op:portraits", ...] every script op showing it
  box   hero / enemy / toutetsu / profile (from the op, docs/re/text.md)
  heroine  Hamusu / Rufu / Kairu from the low byte of the script's op 01 (guess), "" if shared or none
  jp    decoded with tbl/jp.tbl     en    "" until translated (build falls back to jp)
script/prologue.json: one entry, id "prologue": SJIS text, "\\n" = 0D, other controls as [XX].
"""
import json
import sys
from pathlib import Path

import build
import script_vm
from tbl import Table

SCRIPT = build.ROOT / "script"
BOX = {0x02: "hero", 0x03: "enemy", 0x04: "hero", 0x05: "enemy", 0x06: "toutetsu", 0x17: "profile"}
HEROINE = {0: "Hamusu", 1: "Rufu", 2: "Kairu"}


def uses(rom):
    """{text address: ["slot:op:portraits", ...]}, portraits = the script's last op-01 word ("" if none yet)."""
    out = {}
    for slot, a in script_vm.scripts(rom):
        portraits = ""
        for _, op, arg in script_vm.walk(rom, a):
            if op == 0x01:
                portraits = f"{arg:04X}"
            elif op in script_vm.TEXT_OPS:
                out.setdefault(arg, []).append(f"{slot}:{op:02X}:{portraits}")
    return out


def dialogue(rom):
    refs = uses(rom)
    out = []
    for addr, text in build.unpack_text(rom, Table.load(build.TBL)).items():
        us = refs[addr]
        heroines = {HEROINE.get(int(p[2:], 16), "") if p else "" for p in (u.split(":")[2] for u in us)}
        out.append({"id": f"{addr:04X}", "uses": us, "box": BOX[int(us[0].split(":")[1], 16)],
                    "heroine": heroines.pop() if len(heroines) == 1 else "", "jp": text, "en": ""})
    return out


def prologue(rom):
    return [{"id": "prologue", "jp": build.unpack_prologue(rom), "en": ""}]


def write(path, entries):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    rom = build.ROM.read_bytes()
    SCRIPT.mkdir(exist_ok=True)
    for name, fn in (("dialogue", dialogue), ("prologue", prologue)):
        path = SCRIPT / f"{name}.json"
        if path.exists():
            print(f"{path.relative_to(build.ROOT)} exists, left alone")
            continue
        entries = fn(rom)
        write(path, entries)
        print(f"{path.relative_to(build.ROOT)}: {len(entries)} entries")


if __name__ == "__main__":
    sys.exit(main())
