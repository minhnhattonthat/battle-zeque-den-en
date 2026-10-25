# Glossary - Battle Zeque Den

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Name-san). Name order: Western (given name first).
- Romanisation source: official English names (logo, manual, art), else an earlier fan patch, else Hepburn without macrons.
- Credits: English.
- Register / flavour: martial-arts fantasy; plain modern English, each speaker's voice distinct (docs/style-reference.md).
  No archaic "thee/thou"; old or mannered speakers get it through word choice. Grunts/cries (ぐへへ, ウッ, ぐふう)
  as English interjections (Heh heh heh, Ugh, Gwah). Sound effects: none in the dialogue.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', …… / ・・・ -> ... (three dots), ！？ -> ?!, 　(ideographic space)
  -> a space or a sentence break; ー/ァ/ォ vowel stretches -> a stretched word only where it carries tone ("Byakko!"
  for 白虎ォーっ is fine; Hamusu's whine may stretch: "So hooot!").
- 気 (ki) -> aura / presence / energy as the sentence needs ("such an evil aura"); the prologue's 光と闇の二つの気 ->
  "the two forces of light and darkness".
- Voices: see docs/style-reference.md (one table per speaker + approved example pairs).

Names below were proposed in phase 1 from D2 (no official or fan English exists); confirmed in phase 6. The ROM's own
sound-test labels (file 0x11F8D-0x124F9: RUFUU, KAIRU, HAMUSU, SEIRYU(U), KOURYU(U), GENBU, SUZAKU, BYAKKO,
SHUMISEN, TOUTETSU) are developer romanizations, inconsistent with themselves, so Hepburn without macrons wins.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 流風 | Rufu | | heroine (red orb); reading from the script (る・ふ・う); Giant Bomb spelling | Ruhu, Rufuu |
| 波無寿 | Hamusu | | heroine (yellow orb), says ボク; Giant Bomb spelling | |
| 河意留 | Kairu | | heroine (blue orb), polite speech; Giant Bomb spelling | |
| 青龍 | Seiryu | | boss, stage 1 (sound test: SEIRYUU / SEIRYU) | |
| 黄龍 | Koryu | | boss, stage 2 (sound test: KOURYUU / KOURYU; Hepburn Kōryū without macrons) | Oryu |
| (おっちゃん) | Genbu | | stage-3 boss, the river man who knew Hamusu (sound test GENBU; name not in dialogue) | |
| 朱雀 | Suzaku | | boss, fire clan's guardian (stage 4) | |
| 白虎 | Byakko | | boss, Rufu's friend (stage 5) | |
| トウテツ | Totetsu | | final boss, "eater of desire" (饕餮); Hepburn Tōtetsu without macrons (D2) | Toutetsu, Taotie |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| シュミセン / シュミのお山 | Shumisen / Mount Shumi | | the sacred mountain (須弥山, Mt. Sumeru); "Mount Shumisen" or "Shumisen" both fine; Hamusu's childish シュミのお山 = "Mount Shumi" | Sumeru |
| ホウラク京 | Horaku | | capital of the fire clan ("the city of Horaku") | |
| 南レンベン歴 | South Lenben | | profile birthdays: "South Lenben calendar" or "year 742, South Lenben" | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 火の一族 | fire clan | | Hamusu's mangled ヒのイチゾク too | |
| 天地の約束 | pact of heaven and earth | | also the prologue's 天空と大地を支えている約束 | |
| 闘神 | war god | | Suzaku's title | |
| 欲望 | desire | | Totetsu, "the one who devours desire" (欲望を喰らう者) | greed |
| 運命 | fate | | Byakko and Totetsu's key word; keep it "fate" throughout | destiny |
| おっちゃん | Uncle | | Hamusu's name for Genbu (an old family friend, not a relative) | Mister, old man |
| 霊山 / 霊峰 | sacred mountain / sacred peak | | | |

## Decisions from earlier batches
- b001 黄龍のオヤジ -> "that old geezer Koryu" (Genbu mocking; "old man" is reserved-avoid only for おっちゃん lines).
- b001 Genbu's ぐふっ/ぐへっ -> "Heh!"/"Heh..." (laughs); ぐふう -> "Gwah!" for every dying gasp.
- b002 Suzaku's ふふふ -> "Hee hee hee"; everyone else's ふふふ/フフフ -> "Heh heh heh". Kairu's フッ -> "Hmph".
- b002 現実のきびしさを教えてしんぜましょう (Suzaku, B3C5/B6A5) -> "allow me to teach you just how harsh reality can be".
- b002 る・ふ・う (B92D) -> "Ru-fu!".
