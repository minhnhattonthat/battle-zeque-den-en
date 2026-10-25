"""Warp to every scene in tools/debug/scenes.lua (or the ones named) from a cold boot, in parallel.

    python -X utf8 tools/debug/warp_all.py [SCENE ..] [--rom build/bzd_en.sfc] [--jobs 4] [--states] [--sheet]

Each scene runs tools/debug/warp.lua into work/qa/warp/<scene>/ (shots <scene>_<frame>.png + final.png).
--states also writes work/states/<scene>.mss at the arrival point (regenerate after code/font/graphics changes).
--sheet makes a contact sheet per scene. Exit 1 if any scene was not reached.
"""
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from skill import SKILL  # noqa: E402

EMU = os.path.join(SKILL, "scripts", "emu.py")
SHEET = os.path.join(SKILL, "scripts", "sheet.py")
WARP = os.path.join(ROOT, "tools", "debug", "warp.lua")


def emu(rom, out, scene, extra=()):
    cmd = [sys.executable, "-X", "utf8", EMU, rom, "--out", out, "--script", WARP, "--var", f"SCENE='{scene}'",
           "--frames", "20000", "--timeout", "600", *extra]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def scene_names(rom):
    out = os.path.join(ROOT, "work", "qa", "warp", "_list")
    emu(rom, out, "list")
    log = open(os.path.join(out, "log.txt"), encoding="utf-8").read()
    return re.search(r"SCENES (.*)", log).group(1).split()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--rom", default=os.path.join(ROOT, "rom", "Battle Zeque Den (Japan).sfc"))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    names = a.scenes or scene_names(a.rom)

    def run(scene):
        out = os.path.join(ROOT, "work", "qa", "warp", scene)
        extra = ["--state-out", os.path.join(ROOT, "work", "states", scene + ".mss")] if a.states else []
        r = emu(a.rom, out, scene, extra)
        log = os.path.join(out, "log.txt")
        text = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
        m = re.search(r"ARRIVED \S+ f(\d+)", text)
        if m and a.sheet:
            subprocess.run([sys.executable, "-X", "utf8", SHEET, out], capture_output=True)
        return scene, r.returncode, m and int(m.group(1))

    bad = 0
    with ThreadPoolExecutor(a.jobs) as pool:
        for scene, code, frame in pool.map(run, names):
            ok = code == 0 and frame is not None
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {scene:14} exit {code}  arrived {frame}", flush=True)
    print(f"{len(names) - bad}/{len(names)} scenes reached")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
