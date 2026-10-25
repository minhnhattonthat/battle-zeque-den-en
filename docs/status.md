# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done 2026-10-25. Next: phase 3 (identity build). No build yet.
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
  Phase 4 must extract it (13 lines) and phase 5 must handle its font. G5 (heroine names) shows in the
  prologue's art screens.
- **Next (phase 3, identity build):** `tools/build.py` that checks `rom.sha1`, unpacks (text block, script
  table, prologue text, G3/G4/G5 blocks via `lz.py`) and repacks with no edits -> byte-identical ROM, as a test.
- **Open bugs:** none.
- **Notes for later phases:**
  - Warp shots are every 60 frames and the warp mashes A every 40, so a dialogue page can fall between shots; for
    phase-8 QA pass `--var SHOT_EVERY_W=20` or slow the mash.
  - Regenerate states with `warp_all.py --rom build/bzd_en.sfc --states` after any code/font/graphics change.
- **Waiting on the user:**
  - Not verified: the Mesen GUI in `tools/mesen/` taking keyboard input (headless scripted input works). Owner: open
    `tools/mesen/Mesen.exe` once and check the arrow keys/Z/X work.
  - Staff roll is already English but has original typos ("Charactor Design", "KATUTOSHI"). Default: fix
    "Charactor" -> "Character" in phase 7, leave personal names as written.
  - Sixth chapter title: the card shot (warp `ch6_h0`) reads 天涯放束; translator to confirm from the zoomed card.
