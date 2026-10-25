"""Phase-7 ROM-level checks on a fresh English build: every write logged and consistent (romdiff.py --writes),
inside tools/ranges.txt (the dump itself is pinned by rom.sha1), and no branch lands inside a rewritten code span."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import romdiff  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
needs_asar = pytest.mark.skipif(not build.ASAR.is_file(), reason="asar absent")


def ranges():
    out = []
    for line in (ROOT / "tools" / "ranges.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            lo, hi = line.split()[0].split("-")
            out.append((int(lo, 16), int(hi, 16)))
    return out


@pytest.fixture(scope="module")
def built():
    orig = build.ROM.read_bytes()
    return orig, build.build(orig), list(build.WRITES)


@needs_rom
@needs_asar
def test_writes_consistent(built):
    orig, rom, writes = built
    errs, _ = romdiff.check(orig, rom, set(), writes)
    assert not errs, "\n".join(errs[:20])


@needs_rom
@needs_asar
def test_writes_inside_allowed_ranges(built):
    _, _, writes = built
    rs = ranges()
    bad = [f"{off:06X}+{len(new):X} {by}" for off, _, new, by in writes
           if not any(lo <= off and off + len(new) - 1 <= hi for lo, hi in rs)]
    assert not bad, "writes outside tools/ranges.txt:\n" + "\n".join(bad)


HOOKS = [(0x9F01, 0x9F05), (0xA51A, 0xA51B), (0xA561, 0xA5AD)]  # rewritten code spans in bank $83
NOT_CODE = {0x9F7D, 0xA606, 0xA613, 0xA61F}  # operand bytes of ADC #$10B8 / LDA $848000/$848002 (dis65816)


@needs_rom
def test_no_branch_into_hook_spans():
    """Byte scan of the original: any JSR/JMP/branch in bank $83 or JSL/JML to $83 landing strictly inside a
    rewritten span would enter the middle of the new code."""
    rom = build.ROM.read_bytes()
    hits = []
    for o in range(len(rom) - 3):
        op, a = rom[o], (o & 0x7FFF) | 0x8000
        tgts = []
        if 0x18000 <= o < 0x20000:
            if op in (0x20, 0x4C, 0x7C, 0xFC):
                tgts.append(rom[o + 1] | rom[o + 2] << 8)
            if op in (0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0, 0x80):
                tgts.append((a + 2 + (rom[o + 1] ^ 0x80) - 0x80) & 0xFFFF)
            if op == 0x82:
                tgts.append((a + 3 + int.from_bytes(rom[o + 1:o + 3], "little", signed=True)) & 0xFFFF)
        if op in (0x22, 0x5C) and rom[o + 3] in (0x03, 0x83):
            tgts.append(rom[o + 1] | rom[o + 2] << 8)
        for t in tgts:
            if any(lo < t <= hi and not (0x18000 <= o < 0x20000 and lo <= a <= hi) for lo, hi in HOOKS):
                hits.append(a if 0x18000 <= o < 0x20000 else o + 0x10000000)
    assert set(hits) <= NOT_CODE, [hex(h) for h in sorted(set(hits) - NOT_CODE)]
