"""release.py: build, check and package the patch. Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Steps: build -> tests (tools/check.py) -> smoke -> jp_left (SJIS + font-cell tables, known data runs in
tools/jp_known.txt) -> qa_gate check (and the build's sha1 must equal work/qa/tour.sha1, the build the QA tour
was shot from) -> debug tool off -> BPS patch, re-applied to a clean original and compared -> README -> zip.
Output in release/ (gitignored): Battle_Zeque_Den_EN_v<V>.bps, README.txt, Battle_Zeque_Den_EN_v<V>.zip (patch +
README only). Refuses to overwrite an existing version without --force. The playable image stays build/bzd_en.sfc.
After any rebuild that changes pixels: re-run the tour, qa_gate init, the visual-QA review, then write the new
sha1 to work/qa/tour.sha1.
"""
import argparse
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

import bps
from build import OUT, ROM

ROOT = Path(__file__).resolve().parents[1]
SKILL = subprocess.run([sys.executable, str(ROOT / "tools" / "skill.py")], capture_output=True, text=True,
                       check=True).stdout.strip()
PY = [sys.executable, "-X", "utf8"]
TOUR_SHA1 = ROOT / "work" / "qa" / "tour.sha1"

README = """Battle Zeque Den - English translation v{ver}
==============================================

Unofficial English fan translation of Battle Zeque Den (Super Famicom, 1994; Arsys Software / Asmik).
Source, tools and bug reports: https://github.com/minhnhattonthat/battle-zeque-den-en

Patching
--------
Apply {bps} with any BPS patcher (Floating IPS, beat, Rom Patcher JS: https://www.marcrobledo.com/RomPatcher.js/)
to your own dump of the Japanese game. No ROMs are distributed or will be shared.

Base ROM (No-Intro: Battle Zeque Den (Japan)), no copier header:
  Size:   {size} bytes
  CRC32:  {crc}
  MD5:    {md5}
  SHA-1:  {sha1}
Patched ROM:
  CRC32:  {pcrc}
  SHA-1:  {psha1}

If the patcher complains about the checksum, your dump differs (a 512-byte header, another revision or an
already-patched file).

Notes
-----
- Tested in Mesen 2.2.1 (scripted playthroughs of every chapter, boss, ending, profile, game over and the staff
  roll, from a cold boot). Start from a fresh boot; savestates made on the Japanese game carry its old text.
- Translated: all dialogue, the opening prologue, chapter title cards, heroine names on the select screen and in
  the prologue, and the staff roll's "Charactor Design" typo. The title logo stays as the original (no official
  English logo). Honorifics are kept (Suzaku-sama).
- Dialogue types twice as fast as the original (English needs about three times the letters); holding the button
  still prints a page at once.

Known issues (all in the original game too)
-------------------------------------------
- Portraits briefly garble when the speaker changes.
- Lightning flashes in the chapter-1 forest.
- Staff-roll name spellings are as credited (e.g. "KATUTOSHI").

Credits
-------
Translation, hacking and tools: minhnhattonthat, with extensive AI assistance (Claude by Anthropic).
Corrections are very welcome: open an issue on the GitHub page above.
Battle Zeque Den is (c) Asmik. This patch is not affiliated with or endorsed by them.
"""


def run(name, cmd):
    print(f"== {name}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"release stopped: {name} failed (exit {r.returncode})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing files")
    a = ap.parse_args()
    dist = ROOT / "release"
    stem = f"Battle_Zeque_Den_EN_v{a.version}"
    patch, readme, zipf = dist / f"{stem}.bps", dist / "README.txt", dist / f"{stem}.zip"
    if not a.force and (patch.exists() or zipf.exists()):
        sys.exit(f"{patch.name} / {zipf.name} exist: pass --force to overwrite, or a new --version")

    run("build", PY + ["tools/build.py"])
    run("tests", PY + ["tools/check.py"])
    run("smoke", PY + [f"{SKILL}/scripts/emu.py", str(OUT), "--out", "work/qa/smoke", "--route",
                       "tools/routes/boot.txt", "--smoke"])
    known = ["--orig", str(ROM), "--known", "tools/jp_known.txt"]
    run("jp_left sjis", PY + [f"{SKILL}/scripts/jp_left.py", str(OUT), "--sjis"] + known)
    # font-cell text lives only in bank $83 (dialogue block + free space); elsewhere the table matches graphics/code
    run("jp_left tbl", PY + [f"{SKILL}/scripts/jp_left.py", str(OUT), "--tbl", "tbl/jp.tbl", "--range",
                             "1AA38-20000"] + known)
    run("qa_gate", PY + [f"{SKILL}/scripts/qa_gate.py", "check", "work/qa/manifest.tsv", "work/qa/verdicts"])

    orig, built = ROM.read_bytes(), OUT.read_bytes()
    sha = hashlib.sha1(built).hexdigest()
    toured = TOUR_SHA1.read_text().split()[0] if TOUR_SHA1.exists() else "(none)"
    if sha != toured:
        sys.exit(f"release stopped: build sha1 {sha} != QA tour build {toured} ({TOUR_SHA1.name}): re-run the tour")
    # the debug tool is Lua-only (tools/debug/*.lua, loaded by the emulator): the build must not pull it in
    if "debug" in (ROOT / "tools" / "build.py").read_text(encoding="utf-8").lower():
        sys.exit("release stopped: tools/build.py mentions debug: check no debug code goes into the ROM")
    assert bps.snes_checksum(built)[0] == built, "header checksum not fixed"

    dist.mkdir(exist_ok=True)
    p = bps.make(orig, built)
    again = bps.apply(ROM.read_bytes(), p)  # fresh read of the clean original
    assert again == built, "patch does not reproduce the build"
    patch.write_bytes(p)
    readme.write_text(README.format(
        ver=a.version, bps=patch.name, size=len(orig), crc=f"{zlib.crc32(orig):08X}",
        md5=hashlib.md5(orig).hexdigest(), sha1=hashlib.sha1(orig).hexdigest(),
        pcrc=f"{zlib.crc32(built):08X}", psha1=sha), encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(readme, readme.name)
    with zipfile.ZipFile(zipf) as z:
        assert sorted(z.namelist()) == sorted([patch.name, readme.name]) and z.testzip() is None
        assert bps.apply(orig, z.read(patch.name)) == built
    print(f"{zipf.relative_to(ROOT)}: {zipf.stat().st_size} bytes ({patch.name} {len(p)} bytes + README.txt); "
          f"patched sha1 {sha}")


if __name__ == "__main__":
    main()
