"""Full-size contact sheets for a warp tour, one set per scene: work/qa/<tour>/<scene>/sheet*.png (phase-8 QA).

    python -X utf8 tools/qa_sheets.py tour tour_jp

Frames are kept at 1x (dialogue text is 8 px) and only when the screen changed, so a held page costs one tile.
Then: qa_gate.py init work/qa/manifest.tsv work/qa/tour (docs/visual-qa-brief.md).
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from skill import SKILL  # noqa: E402

for tour in sys.argv[1:]:
    for d in sorted(glob.glob(os.path.join(ROOT, "work", "qa", tour, "*", ""))):
        for old in glob.glob(os.path.join(d, "sheet*.png")):
            os.remove(old)
        if glob.glob(os.path.join(d, "f*.png")):
            subprocess.run([sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "sheet.py"), d, "--div", "1",
                            "--changed", "0.02", "--max", "16", "--out", os.path.join(d, "sheet.png")], check=True,
                           stdout=subprocess.DEVNULL)
    print(tour, len(glob.glob(os.path.join(ROOT, "work", "qa", tour, "*", "sheet*.png"))), "sheets")
