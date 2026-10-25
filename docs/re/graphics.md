# Graphics-text survey

Sources: cold-boot tours of the original ROM (`work/qa/tour1`, `opt`, `ch1`; routes `tools/routes/boot.txt`,
`option.txt`), every asset-directory entry decompressed and drawn (`tools/dump_assets.py` +
`tools/render_assets.py`), and a static sweep of every ROM bank as raw 2bpp and 4bpp tiles
(`tools/sweep_sheets.py`, read by reviewer subagents; flagged spots re-checked at 4x).

## Japanese graphics text (to translate unless noted)

| # | Element | Screen | Layer | Source | Notes |
|---|---|---|---|---|---|
| G1 | Title logo バトル ZEQUE伝 | title | BG | dir 17 ($86:FE87 map + tiles), compressed | **keep Japanese** (D5: no official English logo exists) |
| G2 | Logo pattern in the option-screen background (バトル ZEQUE伝 + ॐ glyph) | option select | BG | dir 16 ($86:EE21), compressed | part of the logo; keep with G1 |
| G3 | Heroine names on the select orbs: 流風 / 波無寿 / 河意留 | character select | sprites? (VRAM $0000 area) | dir 13 ($86:9B16, type 04) tile block, compressed | Rufu / Hamusu / Kairu (glossary); 2-3 kanji per orb, ~40 px wide |
| G4 | Chapter cards: 第 / 章 + 一..六 and six titles 樹木騒擾, 地氣鳴動, 奔流喧轟, 火焔盛衰, 砂塵空漠, 天涯?束 (3rd kanji unclear: 抜/技?) | chapter intro (map + text) | BG3 (2bpp, chr $A000, map $F800 in VRAM) | dir 11 ($85:F90F, type 08) tile block at 0x2FA16, compressed | 16x16 cells; title row 4 cells (64 px) - English needs more width or a smaller font |
| G5 | Vertical heroine names 流風 / 波無寿 / 河意留 (4bpp, large) | not seen yet (ending / profile screen?) | ? | dir 09 ($85:C16A) tile block, compressed | find the screen in phase 2 (profile scripts slots 84-86) |

## Already English (no work)

START / OPTION (dir 25/26), © 1994 ASMIK / ... / ARSYS SOFTWARE (dir 24), option screen text, HUD (SCORE,
digits, A-Z; dir 27), GAME OVER (dir 28), STAGE CLEAR (dir 32), CONTINUE? YES NO (dir 33), GO-arrow and
LEVEL/UP effect sprites (bank $97, file 0xB8000), Asmik logo (dir 5).

- **Staff roll is English already**: ASCII strings at file 0x12C9E-0x130xx ("The Crew", "Directed by", names...;
  control bytes 09 = position, 0C = new page, 00 = line end), drawn with the 8x16 ASCII font (dir entry 4).
  Original typos: "Charactor Design" x2, "KATUTOSHI". D3 (credits in English) needs no work; fixing the typos is optional.
- Option screen and sound-test names are ASCII strings at file 0x11EFF-0x124F9 (English).

## Fonts with Japanese that are not shown anywhere seen so far

- 8x8 font, dir entry 1 (file 0x221E4): ASCII + half-width katakana. No screen using it found yet (probably the
  option screen's ASCII; the katakana half may be unused).
- 8x16 ASCII font, dir entry 4 (raw 2bpp, file 0x25A5E-0x2665D, 4-byte zero header + 3072 bytes): staff roll.

## Static sweep result (done-when: every Japanese element is a known string or a row above)

- Every bank $80-$AF drawn as raw 2bpp and 4bpp (`work/sweep2`, `work/sweep4`), read by four reviewer subagents:
  no Japanese except the known dialogue font in bank $84. Their low-confidence spots (banks $97, $A9, $AB, $AC) were
  re-checked at 4x: English effect sprites (GO arrow, LEVEL/UP) and literal runs inside compressed data.
- Every compressed block: `tools/lz_scan.py` finds all back-to-back chains: the directory (0x23E5C-0x46374, drawn
  map+tiles above) and 12 stage chains of 7 blocks (0x78781-0xAE6E7, two per chapter). All 84 stage blocks drawn as
  2bpp/4bpp tiles and read by a reviewer: scenery only, no lettering. Two tiny 2-block "chains" at 0xC64BA and
  0x1666E8 are false positives inside raw data (covered by the raw sweep).
- Sprites stream raw from banks $97-$9A by DMA (`snes_dmalog.lua` during stage 1) - covered by the raw sweep.
- Skipped on purpose (grey in the raw sweep): text block 0x1AA38-0x1BE33, directory blocks 0x23E5C-0x46374,
  stage-1 chain 0x78781-0x7CC39; all three are covered by decoding instead.

## Not reached yet in a tour (phase 2 debug tool must reach and shoot these)

Chapters 2-6 cards (tiles already in G4), ending, profile screens (text slots 84-86, maybe G5), world map
(sound test lists WORLD MAP). The static sweep found no other Japanese graphics, so these should show only G4/G5
and font text; confirm with shots.
