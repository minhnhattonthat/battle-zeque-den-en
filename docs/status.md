# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done 2026-10-25: v1.0 zip built and verified, not published.
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
  - Prologue English drafted in `script/prologue.json` `en` (15 lines, same blank-line layout).
- **Done (phase 7):** build green: lint clean, control codes matched, every write logged and inside `tools/ranges.txt`.
  - Lint (`batches.entry_errors`, `tests/test_lint.py`): ASCII, unknown codes, effect-code parity, widths, stub last
    lines (balanced re-wrap), glossary across line breaks.
  - `build.py` logs every write (`put` -> `build/writes.txt`); `tests/test_romdiff.py`: `romdiff.py --writes` clean,
    writes inside `tools/ranges.txt`, no branch into rewritten bank-$83 hook spans (bank-$82 `D054` span scanned by
    hand: no entry).
  - Graphics text (`tools/gfx_text.py`, `script/graphics.json`, `tests/test_gfx.py`): G4 chapter cards (new layout,
    `asm/card.asm`), G3 select-orb names, G5 prologue heroine names + sprite lists; staff-roll "Charactor" fixed.
    G1/G2 logo kept (D5). `lz.compress` now has stride/count ops: edited blocks fit in place.
  - English prologue: the drawer's dormant horizontal mode, finished by 5 small patches; VWF lines pre-drawn into the
    prologue font slots, rows scroll up ~f960-f2060, cleared before the eyes scene (`docs/re/text.md` §Prologue,
    `tests/test_gfx.py::test_prologue_lines_read_back`). Old jp prologue text blanked (`jp_left --sjis`: only noise).
  - Warp sweep on the final build: 62/62 reached, states regenerated (`work/states/`). New probes in `tools/lua/`:
    `writes.lua` (WRAM write log; IO registers are not caught), `execs.lua`, `ramdumps_at.lua`.
- **Done (phase 8):** QA tour = all 62 warps (`warp_all.py --rom build/bzd_en.sfc --out tour --var
  SHOT_EVERY_W=20`), full-size sheets `tools/qa_sheets.py tour` (also `tour_jp` from the original), gate
  `work/qa/manifest.tsv` + `work/qa/verdicts/` (289 sheets), brief `docs/visual-qa-brief.md` (game's standing
  non-bugs listed). 3 rounds of visual-qa agents; `qa_gate.py check` exits 0 on the final build (sha1 185e1f70...,
  smoke ok, states regenerated). Fixed:
  - **Page wait (critical, from phase 5):** `$83:9DE7` is a per-frame state machine; `vwf_newpage` scrolled after its
    first call, so every page cleared the moment it was typed and the arrow waited on an empty box. Clear now deferred
    to the next glyph (`docs/re/font.md` §Dialogue renderer). Verified frame by frame (boss1_h0, ch2_h2).
  - **Text speed:** a glyph every 4 frames (was 8; English pages have ~3x the glyphs, ~12 s a page).
  - **One-word last lines** ("power.", "Suzaku?", 18 entries): `batches.stub()` = one word or < 6 chars, re-wrapped by
    `wrap`, checked by `tests/test_lint.py`; merged again from `work/tl/b00{1,2}.out.tsv`.
  - **Prologue:** 41 rows (was 42): at 42 the group art after the Kairu card flashed 2-3 frames in the old palette
    (a timing race, the scenes ran 47 frames late); 41 is clean at every frame.
  - Not ours: ch1 forest lightning flashes, portrait garble at speaker swaps, staff-roll spellings (original).
  - Zoomed checks (`work/qa/zoom/cards.png`, `prologue.png`, `prologue_names.png`, `staff.png`): all six chapter cards,
    prologue text + Rufu/Hamusu/Kairu names, select orbs, GAME OVER/CONTINUE (original English; the BG logo pattern is
    G2, kept by D5), staff roll incl. "Character Design": English.
  - New: `tools/qa_sheets.py`, `tools/lua/ppuframes.lua` (per-frame blank/brightness/CGRAM/VRAM sums). Gotcha: the
    skill's `snes_dmalog.lua` logged nothing here (IO-register writes aren't caught, as with `writes.lua`).
- **Done (phase 9):** `tools/release.py` (build -> tests -> smoke -> `jp_left` SJIS + font-cell bank $83 ->
  `qa_gate check` -> build sha1 == `work/qa/tour.sha1` (the toured build) -> debug off -> BPS made, re-applied to a
  fresh read of the original, zip re-read and re-applied). All green: `release/Battle_Zeque_Den_EN_v1.0.zip` (16 KB:
  .bps 24386 B + README.txt with base CRC32 8CAC063C / MD5 / SHA-1, patched CRC32 6B4E4534, SHA-1 185e1f70...).
  Independently re-applied with the skill's `bps.py`: same sha1. Refuses to overwrite without `--force`.
  - `tools/jp_known.txt`: the 8 jp_left hits, all data (ASCII "SCORE", ascending curve tables, code bytes). A whole-ROM
    `--tbl` scan is noise (10k runs in graphics/code); font-cell text exists only in bank $83 (phases 1/4).
  - Polish pass: kept as is. "darn"/"heck" = the mild-swearing default; "Byakkooo!" matches 白虎ォーっ; the one "--"
    (B1FD) kept, since changing pixels would void the phase-8 QA gate for a Minor.
- **Next:** nothing; the run ends here. Publishing (`gh release create`) is the owner's call.
- **After any change that alters pixels:** rebuild, re-run the tour (phase-8 command), `qa_gate.py init`, visual-QA
  the changed sheets, write the new build sha1 to `work/qa/tour.sha1`, then `tools/release.py --version 1.1`.
- **Open bugs:** none.
- **Notes for later phases:**
  - Regenerate states with `warp_all.py --rom build/bzd_en.sfc --states` after any code/font/graphics change.
  - The machine may be shared with another project's emulators: tours then take ~3x longer.
- **Waiting on the user:**
  - Not verified: the Mesen GUI in `tools/mesen/` taking keyboard input (headless scripted input works). Owner: open
    `tools/mesen/Mesen.exe` once and check the arrow keys/Z/X work.
  - Staff roll typos: "Charactor" -> "Character" done (phase 7); "KATUTOSHI" left as credited.
  - Sixth chapter title 天涯抜束 drawn as "Unbound at / Heaven's Edge" (two lines; "Breaking Free..." was 1 px
    too wide). Change in `script/graphics.json` if wanted.
  - Prologue layout default (phase 7): horizontal rows, left-aligned, scrolling up, one colour (the jp's
    `[04]…` pacing and the 光/闇 colour accents are not carried over: this drawer mode has one colour).
  - Translation defaults picked in phase 6 (no ruling asked; change in `glossary.md` if wanted): Hamusu's
    おっちゃん -> "Uncle"; 朱雀様 -> "Suzaku-sama" (D1 keeps honorifics); light swearing kept mild ("darn", "heck").
  - Text speed default (phase 8): dialogue types twice as fast as the original (a glyph every 4 frames; holding the
    button still prints instantly). `asm/vwf.asm` `org $83916E`: `and #$01` = faster, `#$07` = original.
