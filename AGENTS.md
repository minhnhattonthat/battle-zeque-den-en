# Battle Zeque Den (SNES) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder. Read its SKILL.md before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/bzd_en.sfc (checks the dump against `rom.sha1` first; written in phase 3)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/bzd_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/bzd_en.sfc --out work/qa/warp/<name> --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 20000` (cold boot; shots from arrival, then stops; scenes: `tools/debug/scenes.lua`, how: `docs/re/debug.md`; never ask the user to play to a scene)
- Warp all: `python -X utf8 tools/debug/warp_all.py [names] --rom build/bzd_en.sfc --sheet [--states]` (`--states` regenerates `work/states/<scene>.mss`; exit 1 if a scene is not reached)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user; phase 9)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Battle Zeque Den (Japan).sfc` (gitignored; 1,572,864 bytes, no header; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip, via `fetch_emu.py mesen`; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/dialogue.json` + `prologue.json` (`tools/extract.py` writes missing files only; build reads `en`, else `jp`). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- RE helpers (phase 1): `tools/gen_tbl.py` (writes `tbl/jp.tbl`), `script_vm.py` (text pointers), `dump_text.py`, `lz.py` (codec), `dump_assets.py`/`render_assets.py`/`lz_scan.py`/`sweep_sheets.py` (graphics), `font_sheet.py`; Lua probes in `tools/lua/`.
- Engine (phase 5): `asm/vwf.asm` (dialogue VWF, assembled by the build with `tools/asar/asar.exe`, asar 1.91 from github.com/RPGHacker/asar/releases, gitignored), font `fonts/vwf.txt` -> `tools/font.py` (writes `tbl/en.tbl`), box budgets `tools/boxes.py` (measure with `tools/textpx.py`), free-space trap probe `tools/lua/trap.lua` (`warp_all.py --lua`).
- Copied from the skill so a clone builds without it: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`. QA tools (`emu.py`, `play.py`, `qa_gate.py`, `jp_left.py`) run through `tools/skill.py`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Guard hook: `.claude/hooks/guard_bash.py` (copied from the skill; the plugin's own hook did not load in this setup).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
