# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done 2026-10-25. Next: phase 5 (engine spike + marker build).
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
- **Next (phase 5, marker build):** font/VWF decision for the 16x16-cell dialogue font (3 rows/box) and the
  vertical prologue font; English table `tbl/en.tbl`; marker build (`[id]` per string) through `LANG`; trap-test
  free space $83:DB7A-$83:FFFF; measure every box variant (hero/enemy/toutetsu/profile, prologue) in-game.
  `{end}` is part of each `jp` string (tbl terminator): English must keep it.
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
