# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done 2026-10-25. Next: phase 1 (research and recon). No build yet.
- **Done:**
  - Template files in place; `AGENTS.md`, `rom.sha1`, `docs/decisions.md` (D1-D8), glossary rulings filled.
  - `tools/skill.py` (prints skill path), `tools/{tbl,bps,romdiff}.py` copied; `tools/check.py` runs `tests/`; pre-commit hook in `.git/hooks/` runs it (a failing test was rejected).
  - Guard hook `.claude/hooks/guard_bash.py` wired in `.claude/settings.json`; canary `sed -i` blocked.
  - MesenCE 2.2.1 in `tools/mesen/`; smoke on the original ROM passes (`tools/routes/boot.txt`: Asmik logo -> title -> Start -> mode-select screen with two Japanese buttons); `tools/lua/probe_hello.lua` log line lands in log.txt. Settings copy in `tools/emu-config/mesen-settings.json`.
- **Next (phase 1):** prior work (web search: a Spanish patch by Traducciones Magno exists; English patch unconfirmed, a LaunchBox list hints one - check romhacking.net / superfamicom.org), header/map, compression, text encoding, pointers, control codes, free space, graphics-text survey (title logo "バトル ZEQUE伝" is graphics; mode buttons on the post-title screen too). Record in `docs/re/`. Fill README title/publisher/year.
- **Open bugs:** none.
- **Waiting on the user:**
  - Not verified: the Mesen GUI in `tools/mesen/` taking keyboard input (headless scripted input works; settings have `ConfigUpgrade` so defaults load on first GUI start). Owner: open `tools/mesen/Mesen.exe` once and check the arrow keys/Z/X work.
