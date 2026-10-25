"""Phase-7 text lint over the merged script: every rule of `batches.py check`, plus no untranslated or Japanese
`en`, no one-word stub last lines, and the prologue's English layout."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import build  # noqa: E402
import font  # noqa: E402

ADV = font.advance_map(font.load())
JP = re.compile(r"[぀-ヿ一-鿿！-～]")


def test_dialogue_lint():
    gl = batches.glossary()
    errs = []
    for e in build.load("dialogue"):
        if not e["jp"].removesuffix("{end}"):
            continue
        en = e["en"].removesuffix("{end}")
        if not en or not e["en"].endswith("{end}") or JP.search(en):
            errs.append(f"{e['id']}: en empty, unterminated or Japanese")
            continue
        errs += batches.entry_errors(e, en, ADV, gl)
        for para in en.split("{page}"):
            lines = para.split("{n}")
            last = batches.CODE.sub("", lines[-1]).strip()
            if len(lines) > 1 and len(last) < batches.STUB:
                errs.append(f"{e['id']}: stub last line {last!r}")
    assert not errs, "\n".join(errs)
