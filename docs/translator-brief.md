# Translator brief - Battle Zeque Den (Super Famicom, 1994)

You translate part of the Japanese script of Battle Zeque Den into English for a fan patch. Side-scrolling martial-arts
beat 'em up: three teenage heroines (Rufu, Hamusu, Kairu) each climb toward the sacred Mount Shumisen, trading words
with a boss at the end of every chapter. Short, punchy lines; each speaker has a distinct voice.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - voices per speaker and the approved chapter-1 pilot. Ids in its pilot table: copy
   that English verbatim.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table and style rules in `glossary.md`).
3. `docs/synopsis.md` - plot, who is who, the ending reveal.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>scene<TAB>limit<TAB>Japanese`. ` / ` separates the lines of one Japanese box: translate the box as
one utterance, don't mirror its line breaks. `speaker` names who talks; "(to Hamusu/Kairu/Rufu)" means the line is
shared by every heroine route, so it must suit any of the three (all girls). Lines are in story order per route; one
boss scene's lines often continue a sentence across entries (AAD2 -> AAF7): make them read in sequence.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs,
no `{}` or `[]` except the codes below, no Japanese or fullwidth characters.
- Write each entry as one paragraph: the build wraps it to the box width (pixels, variable-width font). `{n}` forces
  a line break (profile screens, or a deliberate beat); never two in a row.
- A box shows 3 lines (about 30-34 characters each). Longer entries need `{page}` at a sentence break where the
  page should turn; the check fails a page that wraps to 4+ lines. Keep `{page}` where the Japanese has one, unless
  the English fits in one page and reads better unbroken.
- Copy effect codes exactly (`{c04}` at the start of two Totetsu lines). Don't write `{end}`; the tool adds it.
- Dry-run a line: `python -X utf8 tools/batches.py fit hero "Your English here"` (box = hero, enemy, toutetsu, profile).
- Profile screens (box profile, 128 px, max 9 lines): one field per line with `{n}`, e.g.
  `Name: Rufu{n}Birthday: April 30,{n}742, South Lenben{n}Age: 17{n}Height: 163 cm{n}Bust: 82{n}Waist: 56{n}Hips: 84{n}Blood type: A`.

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Wordplay keeps its punch (no translator notes).
- Names and terms exactly as in the glossary. Never abbreviate to fit; if a line can't fit without losing meaning,
  use `{page}` instead.
- Honorifics kept (D1): 河意留さん -> Kairu-san, 朱雀様 -> Suzaku-sama. お嬢さん is not an honorific ("young lady").
  Western name order.
- Punctuation: 「」 -> "...", …… -> `...`, ！？ -> `?!`; the ideographic space is a pause (comma, dash or new sentence).
- Grunts and cries become English interjections (ぐへへ "Heh heh heh", ウッ "Ugh!", ぐふう "Gwah!"); a dying cry
  like 朱雀ゥ……！ can stretch the name ("Suzakuuu...!") or not, but stays readable.
- Totetsu's speech is a sustained argument across many entries (fate -> desire -> humanity creates Totetsu): keep the
  key words "fate" and "desire" consistent so the logic carries.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
