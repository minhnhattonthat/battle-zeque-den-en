"""Phase-7 graphics text: the English build's asset-directory entries decode to what tools/gfx_text.py drew."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import gfx_text  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
needs_asar = pytest.mark.skipif(not build.ASAR.is_file(), reason="asar absent")


@needs_rom
def test_font_glyphs():
    f = gfx_text.font(build.ROM.read_bytes())
    assert len(f) == 95 and all(len(rows) == 16 for rows in f.values())
    assert gfx_text.width("Chapter", f) == 56 and not any(c for r in f[" "] for c in r)


@needs_rom
@needs_asar
def test_built_entries_decode_to_the_drawings():
    orig = build.ROM.read_bytes()
    rom = build.build(orig)
    gfx = build.load("graphics")
    want = {"G4": gfx_text.chapter_card(orig, gfx)}
    _, _, mp, _, chr_, _ = build.entry_blocks(orig, "G3")
    want["G3"] = gfx_text.orb_names(orig, gfx, mp, chr_)
    _, _, mp, _, chr_, _ = build.entry_blocks(orig, "G5")
    want["G5"] = gfx_text.prologue_names(orig, gfx, mp, chr_)[:2]
    for name, (mp, chr_) in want.items():
        _, _, got_mp, _, got_chr, _ = build.entry_blocks(rom, name)
        assert (got_mp, got_chr) == (mp, chr_), name
    assert rom.count(b"Charactor") == 0 and rom.count(b"Character Design") == 2
