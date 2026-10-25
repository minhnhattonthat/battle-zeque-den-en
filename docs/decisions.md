# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-25 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-10-25 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (title logo, manual, art), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-10-25 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-25 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work (wider box, VWF, relocation) before abbreviating; abbreviate only as a flagged last resort. |
| D5 | 2026-10-25 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if it has no official English version. |
| D6 | 2026-10-25 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint; one phase per session, commit + push to main at each phase end. Never `gh release create`, never change repo visibility; the run ends at a built, verified release zip. (Publishing part replaced by D9.) |
| D7 | 2026-10-25 | Existing saves / savestates | user supplies, none | None provided; build the debug tool (phase 2) as usual. |
| D8 | 2026-10-25 | Git identity | ask, preset | Preset by new-game.ps1 (minhnhattonthat); do not change. |
| D9 | 2026-10-25 | Publish v1.0 | keep private, publish | Owner asked: repo made public, `gh release create v1.0` with the verified zip. |
