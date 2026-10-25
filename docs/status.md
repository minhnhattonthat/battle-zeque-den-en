# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done 2026-10-25. Next: phase 6 (translate).
- **Done (phase 1):** all in `docs/re/` (index `docs/re/README.md`), facts pinned by `tests/test_recon.py`.
  - ROM: LoROM FastROM 1.5 MB, header says 2 MB; free-space candidates listed, none trap-tested (`rom.md`).
  - Dialogue: one block in bank $83 (0x1AA38-0x1BE33, 143 strings, font-cell encoding), script VM table
    $83:BE33 (87 slots), `tbl/jp.tbl` (`text.md`, `font.md`). Compression codec `tools/lz.py` (`compression.md`).
  - Graphics text G1-G5 (`graphics.md`); glossary names proposed.
- **Done (phase 2):** `tools/debug/warp.lua` + `scenes.lua` reach 62 scenes from a cold boot, each with shots
  (`python -X utf8 tools/debug/warp_all.py --sheet`: 62/62 on the original ROM; `tools/debug/overview.py` makes
  one sheet of them). Covered: prologue + title, character select, world map + card + opening monologue for
  chapters 1-6 x 3 heroines, later areas, all 6 boss dialogues x 3 heroines, post-boss lines (scenes 6-8),
  mid-chapter-4 dialogues, ending dialogue x 3, profiles x 3, game over + continue, stage clear, staff roll.
  How it works and the RAM/event-script facts: `docs/re/debug.md`; `tests/test_debug.py` checks the jump
  addresses against the ROM. Lua probes added in `tools/lua/` (vmentry, events, pctrace, peek, poke, player).
- **Phase-1 gap found:** the idle-boot **prologue** is a second text system: vertical Shift-JIS text inline in a
  bank-$82 sequence script at file 0x10D0C, own font + SJIS lookup lists at 0x15281 (`text.md` §Prologue).
  Phase 4 must extract it (15 lines) and phase 5 must handle its font. G5 (heroine names) shows in the
  prologue's art screens.
- **Done (phase 3):** `tools/build.py` checks `rom.sha1`, unpacks + repacks the dialogue block (strings back to
  back, every script pointer rewritten), the prologue (SJIS, `[XX]` controls, `\n` = 0D; must fit its slot
  0x10D0C-0x10E22), G3/G4/G5 tile blocks (unchanged -> original bytes, else `lz.compress`), fixes the header
  checksum -> `build/bzd_en.sfc`, 0 bytes differ, smoke ok. `tests/test_build.py`: identity, compressor roundtrip
  over every directory block. `bps.snes_checksum` fixed for 1.5 MB (mirrored sum; the plain sum was wrong).
- **Done (phase 4):** `tools/extract.py` -> `script/dialogue.json` (143 entries: id = $83 address, `uses`
  "slot:op:portraits", `box` hero/enemy/toutetsu/profile, `heroine` from op-01 low byte (guess), `jp`, `en`) and
  `script/prologue.json` (1 entry, `\n` = 0D, `[XX]` controls). Never overwrites. `build.py` reads JSON (`LANG`
  field, else `jp`); identity still 0 bytes differ, smoke ok. `tests/test_extract.py`: JSON == fresh dump, jp
  re-encodes to the whole block with no gap, prologue re-encodes to its slot. ROM-wide SJIS scan: prologue is the
  only SJIS text; `$82:D0F9` has no other caller (`text.md`).
- **Done (phase 5):** dialogue VWF + marker build (`docs/re/font.md` §Dialogue renderer, §Box widths).
  - `asm/vwf.asm` (asar 1.91 in `tools/asar/`, gitignored; `build.py` errors with the URL if missing): `$83:9F01`
    -> `JSL $80:E580` pixel-pen renderer into the game's own 2bpp text buffer `$7F:10B8` (shadow kept); newline
    and `{page}` rewritten so >3 lines page automatically (the original overwrote row 3). Font `fonts/vwf.txt`
    (95 ASCII glyphs, drawn here) -> `tools/font.py` -> slots 0-94, `tbl/en.tbl` (code = slot + 0x10).
  - `build.py`: `build(orig, identity=True)` = phase-3 identity; default = English: `en` text, else a marker
    `[id] p.l The quick brown fox...` per jp line (first 2 entries per box type fill the whole line), AA38 = glyph
    torture line. Text packs into the slot, then `$83:DB7A+`.
  - Trap-tested (`tools/lua/trap.lua`, 62 warps): ROM 0x1DB7A-0x1FFFF, 0x657B-0x7FBF unread; `$7F:FE00+` unwritten.
  - Width gate `tools/boxes.py`: hero 176 px, enemy 176, Totetsu 184, profile 128 (9 rows), 3 rows per page;
    measured from pixels (`tools/textpx.py`). Prologue: **guess** (208 px), its renderer is phase-7 work.
  - Coverage: `tools/lua/textcover.lua` + `tools/textcover.py`: all 143 strings displayed in warps
    (`warp_all.py --out cover --var HOLD_W=9000 --lua tools/lua/textcover.lua`). `warp.lua` got `HOLD_W`,
    `warp_all.py` got `--lua/--var/--out`.
- **Next (phase 6, translate):** translator brief: lines joined by `{n}` (no empty lines: a newline at column 0 is
  ignored), each line <= the box's px budget (`font.text_width`), pages of 3 lines are automatic, `{page}` forces
  a new page, keep `{c04}` where the jp has it and the final `{end}`. ASCII only (add glyphs to `fonts/vwf.txt`
  for anything else, e.g. é or curly quotes). `[XX]` with two hex digits is a hex escape in tbl.py: avoid.
  Consider letting the build wrap plain text by width instead of translators placing `{n}` (phase 7 lint either way).
- **Prologue (phase 7):** English needs its own layout: plan in `docs/re/text.md` §Prologue (BG3, 4 tiles per
  16x16 glyph, columns right to left, hscroll). Until then the build keeps the jp prologue (its font is separate,
  so it still shows Japanese).
- **Open bugs:** none.
- **Notes for later phases:**
  - `lz.compress` (no stride copies / replays) is 5-9% bigger than the game's blocks (G3 13905 vs 12785 slot,
    G4 4900 vs 4678, G5 2420 vs 2305), so an edited block won't fit in place. Either add op 8/9 matching or move
    the entry (map + its tile block, which follows the map stream) to free space and repoint the directory entry.
  - Warp shots are every 60 frames and the warp mashes A every 40, so a dialogue page can fall between shots; for
    phase-8 QA pass `--var SHOT_EVERY_W=20` or slow the mash.
  - Regenerate states with `warp_all.py --rom build/bzd_en.sfc --states` after any code/font/graphics change.
- **Waiting on the user:**
  - Not verified: the Mesen GUI in `tools/mesen/` taking keyboard input (headless scripted input works). Owner: open
    `tools/mesen/Mesen.exe` once and check the arrow keys/Z/X work.
  - Staff roll is already English but has original typos ("Charactor Design", "KATUTOSHI"). Default: fix
    "Charactor" -> "Character" in phase 7, leave personal names as written.
  - Sixth chapter title: the card shot (warp `ch6_h0`) reads 天涯放束; translator to confirm from the zoomed card.
