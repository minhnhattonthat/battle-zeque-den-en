# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translate) done 2026-10-25. Next: phase 7 (insert, fit, check).
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
- **Done (phase 6):** all 143 dialogue entries translated and merged into `script/dialogue.json` `en`; build is now
  fully English dialogue (smoke ok, boss-1 and profile warps read correctly).
  - `tools/batches.py`: split -> `work/tl/bNNN.tsv` (speaker/scene from `uses`), check (ids, ASCII, effect codes,
    empty lines, word width, <=3 lines per page or 9 for profiles, glossary + Avoid, honorifics さん/様), merge
    (greedy pixel wrap of paragraph English -> `{n}`), pairs (reviewer file), fit (dry run). `tests/test_batches.py`
    checks every merged `en` fits its box and encodes.
  - Docs: `docs/synopsis.md`, `docs/style-reference.md` (voices + chapter-1 pilot), `docs/translator-brief.md`,
    `docs/reviewer-brief.md`; glossary: register/punctuation rules, terms (fire clan, pact of heaven and earth, war
    god, desire, fate, Uncle, sacred mountain/peak), batch decisions.
  - 2 translator agents (b001 72, b002 71), 1 reviewer over both: Approved, 0 Critical/Important. Applied the
    accuracy Minors; deferred to the phase-9 polish pass: Genbu "darn"/"heck" maybe stronger (AFF0, AF3C), B93C
    "Byakkooo!" vs "Byakko!", B1FD "--" dash style.
  - Prologue English drafted in `script/prologue.json` `en` (15 lines, same blank-line layout, no `[XX]` pacing or
    colour codes yet); `build.py` still packs the jp prologue until phase 7 builds its renderer.
- **Next (phase 7, insert/fit/check):** build lint (width per line from `en`, control codes vs jp, ASCII), `romdiff.py`
  with allowed ranges (text slot, `$83:DB7A+` free space, hook sites, font/VWF code at `$80:E580`); graphics text
  G1-G5 (chapter cards, titles, game over, staff roll typo "Charactor"); English prologue: plan in
  `docs/re/text.md` §Prologue (BG3, 4 tiles per 16x16 glyph, columns right to left, hscroll; the jp has `[04]…[03]`
  pacing and `[03]/[02]` colour codes around 光/闇 to carry over).
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
  - Translation defaults picked in phase 6 (no ruling asked; change in `glossary.md` if wanted): Hamusu's
    おっちゃん -> "Uncle"; 朱雀様 -> "Suzaku-sama" (D1 keeps honorifics); light swearing kept mild ("darn", "heck").
