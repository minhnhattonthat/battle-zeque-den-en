# Translation reviewer brief - Battle Zeque Den

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents. Mechanical validity
(ids, control codes, ASCII, width, page length, glossary spellings, honorifics) is already enforced by
`tools/batches.py check` - judge translation quality. Return the report as your final message: subagents cannot write
files, so the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file: every entry as `>> id | speaker | scene | JP` then the English on the next line. ` / ` is a Japanese
  line break; the English is a paragraph the build wraps (`{n}` line break, `{page}` page turn). Read ALL of it.
- `glossary.md` (rulings and style rules at the top), `docs/style-reference.md` (voices, approved pilot),
  `docs/synopsis.md` (who is who), the translator's report (unverified claims).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means. Lines marked "(to Hamusu/Kairu/Rufu)" are shared by all three heroine routes: they must fit any of them.
- Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics per D1 (Kairu-san,
  Suzaku-sama); voice matches the style reference (Rufu rough, Hamusu childish, Kairu composed; Suzaku mannered and
  mocking, Genbu coarse, Totetsu cold and didactic); sentences split across entries read in sequence.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; abbreviated names or terms;
  stock phrases that read awkwardly in English.
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, wrong speaker, broken sentence across entries)
#### Important (clear mistranslation, glossary inconsistency, voice badly off, abbreviation)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
