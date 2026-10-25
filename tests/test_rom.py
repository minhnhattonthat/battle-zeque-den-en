import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402

ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"


@pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")
def test_rom_matches_sha1():
    check_rom.check()
