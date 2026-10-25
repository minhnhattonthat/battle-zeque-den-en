"""Walk the cutscene script VM in bank $83 and list every text pointer it uses (docs/re/text.md).

    python -X utf8 tools/script_vm.py            # scripts, ops and text pointers

Script table: 87 words at $83:BE33 (0 = unused slot). Each op is one byte; its handler reads its arguments,
then reads the next op byte ($83:9443). Op 00 ends the script.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
BANK = 0x18000 - 0x8000          # file offset = BANK + CPU address in bank $83
TABLE, TABLE_END = 0xBE33, 0xBEE1
ARGS = {0x00: 0, 0x01: 2, 0x02: 2, 0x03: 2, 0x04: 2, 0x05: 2, 0x06: 2, 0x07: 1, 0x08: 1, 0x09: 1, 0x0A: 1,
        0x0B: 0, 0x0C: 0, 0x0D: 0, 0x0E: 0, 0x0F: 0, 0x10: 0, 0x11: 0, 0x12: 1, 0x13: 0, 0x14: 0, 0x15: 0,
        0x16: 1, 0x17: 2}
TEXT_OPS = {0x02, 0x03, 0x04, 0x05, 0x06, 0x17}  # word argument = text pointer in bank $83


def scripts(rom):
    """Yield (slot, address) for each used slot of the script table."""
    for slot in range((TABLE_END - TABLE) // 2):
        a = rom[BANK + TABLE + 2 * slot] | rom[BANK + TABLE + 2 * slot + 1] << 8
        if a:
            yield slot, a


def walk(rom, addr):
    """Ops of one script as (address, op, arg) up to and including op 00."""
    out = []
    while True:
        op = rom[BANK + addr]
        if op not in ARGS:
            raise ValueError(f"unknown op {op:02X} at ${addr:04X}")
        n = ARGS[op]
        arg = int.from_bytes(rom[BANK + addr + 1:BANK + addr + 1 + n], "little") if n else None
        out.append((addr, op, arg))
        addr += 1 + n
        if op == 0x00:
            return out


def text_pointers(rom):
    """{text address: [(slot, op address), ...]} over all scripts."""
    refs = {}
    for slot, a in scripts(rom):
        for at, op, arg in walk(rom, a):
            if op in TEXT_OPS:
                refs.setdefault(arg, []).append((slot, at))
    return refs


def main():
    rom = ROM.read_bytes()
    for slot, a in scripts(rom):
        ops = " ".join(f"{op:02X}" + (f":{arg:0{2 * ARGS[op]}X}" if arg is not None else "")
                       for _, op, arg in walk(rom, a))
        print(f"slot {slot:2d} ${a:04X}: {ops}")
    refs = text_pointers(rom)
    print(f"{len(refs)} distinct text pointers, ${min(refs):04X}-${max(refs):04X}")


if __name__ == "__main__":
    sys.exit(main())
