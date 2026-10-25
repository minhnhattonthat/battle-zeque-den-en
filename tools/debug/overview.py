"""One contact sheet with a representative shot per warped scene (work/qa/warp/<scene>/f*.png).

    python -X utf8 tools/debug/overview.py [--out work/qa/overview]

Chapter scenes give two shots (card, monologue), the staff roll two, everything else the 5th shot after arrival.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from skill import SKILL  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "qa", "overview"))
    a = ap.parse_args()
    picks = []
    for d in sorted(glob.glob(os.path.join(ROOT, "work", "qa", "warp", "*"))):
        scene = os.path.basename(d)
        shots = sorted(glob.glob(os.path.join(d, "f*.png")))
        if scene.startswith("_") or not shots:
            continue
        at = [9, 36] if re.match(r"ch\d_h", scene) else [3, 40] if scene == "staffroll" else [4]
        picks += [(scene, shots[min(i, len(shots) - 1)]) for i in at]
    print("\n".join(f"{i:3} {s}" for i, (s, _) in enumerate(picks)))
    os.makedirs(a.out, exist_ok=True)
    sys.exit(subprocess.run([sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "sheet.py"),
                             *[p for _, p in picks], "--cols", "6", "--max", "36", "--changed", "0",
                             "--out", os.path.join(a.out, "sheet.png")]).returncode)


if __name__ == "__main__":
    main()
