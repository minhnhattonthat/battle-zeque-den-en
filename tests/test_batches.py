"""Phase-6 batch tool: wrapping, glossary parsing, and every merged `en` fitting its box."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import font  # noqa: E402
from boxes import BOXES  # noqa: E402
from tbl import Table  # noqa: E402

ADV = font.advance_map(font.load())


def test_wrap_greedy_and_explicit_breaks():
    text = "aaaa " * 20
    out = batches.wrap(text.strip(), 60, ADV)  # "aaaa" = 24 px, space 4: two words per 60-px line
    assert out.split("{n}") == ["aaaa aaaa"] * 10
    assert batches.wrap("{c04}Hi there{n}You{page}Me", 176, ADV) == "{c04}Hi there{n}You{page}Me"


def test_glossary_rows():
    rows = {jp: en for jp, en, _ in batches.glossary()}
    assert rows["流風"] == ["Rufu"] and rows["シュミのお山"] == ["Mount Shumi"]


def test_merged_text_fits():
    t = Table.load(font.EN_TBL)
    for e in batches.load():
        if not e["en"]:
            continue
        box = BOXES[e["box"]]
        assert e["en"].endswith("{end}") and t.encode(e["en"])
        assert not re.search(r"\[[0-9A-Fa-f]{2}\]", e["en"]), e["id"]  # would encode as a hex escape
        pages = e["en"].removesuffix("{end}").split("{page}")
        for page in pages:
            lines = page.split("{n}")
            assert len(lines) <= box["lines"], e["id"]
            assert all(batches.width(ln, ADV) <= box["px"] for ln in lines), e["id"]
