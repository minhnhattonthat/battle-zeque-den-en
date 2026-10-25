"""Phase-3 identity build: unpack + repack with no edits gives the original ROM; the compressor roundtrips."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402
import build  # noqa: E402
import dump_assets  # noqa: E402
import lz  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")


@needs_rom
def test_identity_build():
    orig = build.ROM.read_bytes()
    assert build.build(orig, identity=True) == orig


@needs_rom
def test_header_checksum_is_mirrored_sum():
    orig = build.ROM.read_bytes()
    assert bps.snes_checksum(orig)[0] == orig


@needs_rom
def test_prologue_unpacks_to_15_lines():
    lines = [ln for ln in build.unpack_prologue(build.ROM.read_bytes()).split("\n") if ln]
    assert len(lines) == 15
    assert lines[0].endswith("[04]…[03]いにしえの予言者は語る") and lines[-1] == "始まると……"


@needs_rom
def test_compress_roundtrips_every_directory_block():
    rom = build.ROM.read_bytes()
    for i, off, typ in dump_assets.entries(rom):
        if typ == 1 or i == 4:
            continue
        mp, end = lz.decompress(rom, off, typ)
        tiles, _ = lz.decompress(rom, end, typ)
        for data, at in ((mp, off), (tiles, end)):
            stride = rom[at + 2] | rom[at + 3] << 8
            blk = lz.compress(data, stride)
            assert lz.decompress(blk, 0, typ) == (data, len(blk)), f"entry {i} block {at:#x}"
