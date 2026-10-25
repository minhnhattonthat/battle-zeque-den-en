"""Phase-5 engine: VWF font data, tbl/en.tbl in sync, marker build layout and the $83:9F01 hook."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import boxes  # noqa: E402
import build  # noqa: E402
import font  # noqa: E402
import script_vm  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
needs_asar = pytest.mark.skipif(not build.ASAR.is_file(), reason="asar absent")


def test_font_is_printable_ascii_in_order():
    glyphs = font.load()
    assert "".join(ch for ch, _, _ in glyphs) == "".join(map(chr, range(0x20, 0x7F)))
    assert len(font.glyph_bytes(glyphs)) == 22 * len(glyphs)
    for ch, rows, adv in glyphs:
        assert len(rows) == font.ROWS and 1 < adv <= 16, ch


def test_en_tbl_is_current():
    expected = "\n".join(font.tbl_lines(font.load())) + "\n"
    assert font.EN_TBL.read_text(encoding="utf-8") == expected, "run tools/font.py"


def test_en_tbl_roundtrips_ascii():
    t = Table.load(font.EN_TBL)
    s = "".join(map(chr, range(0x20, 0x7F))) + "{n}x{page}y{end}"
    b = t.encode(s)
    assert b[0] == 0x10 and t.decode(b, 0) == (s, len(b))


def test_markers_fit_their_buffer_rows():
    adv = font.advance_map(font.load())
    full = build.full_markers(build.load("dialogue"))
    for e in build.load("dialogue"):
        for line in build.marker(e, adv, e["id"] in full).removesuffix("{end}").replace("{page}", "{n}").split("{n}"):
            line = line.replace("{c04}", "")
            assert font.text_width(line, adv) <= build.BUF_PX.get(e["box"], 184), (e["id"], line)


def test_box_budgets_fit_the_buffer():
    for name, b in boxes.BOXES.items():
        if name != "prologue":
            assert b["px"] <= build.BUF_PX.get(name, 184)


@needs_rom
@needs_asar
def test_marker_build_hooks_and_text_pointers():
    orig = build.ROM.read_bytes()
    rom = build.build(orig)
    assert rom[0x19F01:0x19F06] == bytes.fromhex("2280E58060")  # JSL $80:E580; RTS
    assert rom[0x1A51A] == 0x4C and rom[0x1A561:0x1A563] == bytes.fromhex("E220")  # {page} -> JMP, newline rewritten
    assert rom[0x1A4F9:0x1A4FB] == orig[0x1A4F9:0x1A4FB]  # control-code jump table untouched
    t = Table.load(font.EN_TBL)
    en = {int(e["id"], 16): e["en"] for e in build.load("dialogue")}
    for addr, uses in script_vm.text_pointers(orig).items():
        for _, at in uses:
            ptr = int.from_bytes(rom[script_vm.BANK + at + 1:script_vm.BANK + at + 3], "little")
            text, _ = t.decode(rom, ptr + script_vm.BANK)
            if en[addr]:  # every pointer reaches its own entry: the translation, else its marker
                assert text == en[addr], hex(addr)
            else:
                assert text.replace("{c04}", "").startswith(f"[{addr:04X}]") or addr == 0xAA38, (hex(addr), text[:20])
