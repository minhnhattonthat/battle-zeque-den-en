"""Phase-1 recon facts as tests (docs/re/): table roundtrip, text coverage, script pointers, decompressor."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import dump_assets  # noqa: E402
import gen_tbl  # noqa: E402
import lz  # noqa: E402
import script_vm  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
TEXT_LO, TEXT_HI = 0x1AA38, 0x1BE33  # file offsets of the dialogue block in bank $83
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


def test_tbl_is_generated():
    assert (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines() == gen_tbl.lines()


def test_lz_selftest():
    lz.selftest()


@needs_rom
def test_text_block_roundtrip_and_coverage():
    rom = ROM.read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    o, starts = TEXT_LO, []
    while o < TEXT_HI:
        text, used = t.decode(rom, o)
        assert "[" not in text, f"undecoded byte at {o:#x}: {text}"
        assert t.encode(text) == rom[o:o + used]
        starts.append(o)
        o += used
    assert o == TEXT_HI
    assert len(starts) == 143
    refs = script_vm.text_pointers(rom)
    assert sorted(script_vm.BANK + a for a in refs) == starts  # every string is reached, nothing else


@needs_rom
def test_directory_blocks_are_back_to_back():
    rom = ROM.read_bytes()
    ents = list(dump_assets.entries(rom))
    for (i, off, typ), nxt in zip(ents, ents[1:] + [(None, 0x46374, None)]):
        if typ == 1 or i == 4:  # raw fonts; entry 4 is an empty header followed by other data
            continue
        _, end = lz.decompress(rom, off, typ)
        _, end = lz.decompress(rom, end, typ)
        assert end == nxt[1], f"entry {i}: tile block ends {end:#x}, next entry {nxt[1]:#x}"
