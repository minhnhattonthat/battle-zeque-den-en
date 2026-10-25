# Visual-QA reviewer brief - Battle Zeque Den (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

`$SKILL` = the folder `python tools/skill.py` prints (run from the repo root). Use `"$(python tools/skill.py)"` in
commands; never paste a `plugins/cache/<hash>` path.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ROM's sheets: `work/qa/tour_jp/<id>.png` (same ids, same warp; frame timing can drift a little
  because English pages differ in length). `glossary.md` for names.

## How to look
- Read each sheet whole first. Sheets are full-size frames (256x224) with frame numbers; dialogue text is 8 px
  tall. Where text is small, zoom into it with
  `python -X utf8 "$(python tools/skill.py)/scripts/sheet.py" work/qa/tour/<scene>/f00NNNN.png --crop x,y,w,h --zoom 3 --out work/qa/zoom/<name>.png`
  and read that (the single frames sit beside the sheet in the same folder).
- Sheets keep a frame only when >2% of the screen changed, so the last letters of a page and its finished frame
  with the arrow are often dropped: a page that looks cut off mid-typing on the sheet must be checked in the single
  frames (`work/qa/tour/<scene>/f*.png`, every 20 frames) before it is called an issue.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (kana/kanji in a text box, a card, a name plate, the prologue);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md` (Rufu, Hamusu, Kairu, Seiryu, Koryu, Genbu, Suzaku, Byakko, Totetsu,
  Shumisen / Mount Shumi, Horaku, South Lenben).

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet;
- warp artefacts: no enemies in a stage, the player standing still or placed oddly in an arena, the camera
  jumping, dialogue pages advancing fast (the warp presses A every 40 frames);
- the title logo バトル ZEQUE伝 (title screen, and its pattern in the option-screen background) stays Japanese:
  ruling D5 keeps the original logo;
- the prologue: English in horizontal, left-aligned rows in one colour, scrolling up (the original is vertical
  Japanese in columns); this is the chosen layout;
- staff roll names as credited, e.g. "KATUTOSHI";
- the sixth chapter card reads "Unbound at / Heaven's Edge" on two lines (chosen);
- honorifics such as "Suzaku-sama", "-san" (ruling D1);
- a portrait garbled or sparkling for 1-2 frames when the speaker changes or the box opens (the original does it);
- "Concept&Background Story by" without spaces, and other staff-roll spellings, as in the original;
- one-frame white flashes in the chapter-1 forest (lightning; the original flashes at the same frames, its tour
  shots may miss them) and the ch6 arena white-out;
- Totetsu's lines with no box (the original has none);
- a cry on its own line ("...Suzakuuu...!") where the Japanese gives it its own line too.

Since the phase-8 fix, a finished page stays up with the advance arrow until the press: an empty box with the arrow,
or a page that vanishes before its last words show, is an `issue`.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which frame, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
