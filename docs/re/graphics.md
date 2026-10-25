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
| G3 | Heroine names on the select orbs: 流風 / 波無寿 / 河意留 | character select (warp `select`) | sprites, 16x16, VRAM $0000 | dir 12 ($86:8C5C) | **English (phase 7)**: three 64x32 blocks (tile rows 0-3 cols 0-7, rows 0-3 cols 8-15, rows 4-7 cols 0-7), colours 15 ink / 7 edge / 1 shadow |
| G4 | Chapter cards: 第 / 章 + 一..六 and six titles 樹木騒擾, 地氣鳴動, 奔流喧轟, 火焔盛衰, 砂塵空漠, 天涯抜束 | chapter intro (warp `chN_hH`) | BG3 (2bpp, chr $A000, map $F800 in VRAM) | dir 11 ($85:F90F) | **English (phase 7)**: new layout, `asm/card.asm` (hook $82:B585) |
| G5 | Heroine names 流風 (horizontal) / 波無寿 / 河意留 (vertical) | prologue heroine-art screens (warp `prologue_title`, ~f3072/3192/3252) | sprites 16x16, VRAM $0000 | dir 09 ($85:C16A) + sprite lists in the prologue sequence script | **English (phase 7)**: twice-size 8x16 font; Hamusu/Kairu turned to read top to bottom in the original 32x96 columns |

How the loaders work (verified with PPU dumps, phase 7): a directory entry's map is drawn with its tiles into VRAM
tiles, map cell (r, c) -> VRAM tile 16r+c (dir 12, dir 9: sprite sheets) or 16r+c+1 (dir 11, BG3). Map and tiles
are decompressed to `$7F:0600+` first (`tools/lua/lzlog.lua`; dir 13 fills it to `$7F:5220`).
- G4: the card routine `$82:B57E` wrote 3x4-tile cells (第 at tile $01, 章 $04, numeral $41+64c, title $44+64c..)
  into the BG3 map at rows 14-17 / 22-25. English (`tools/gfx_text.py chapter_card`, `asm/card.asm`): "Chapter"
  in tiles $01-$08/$11-$18, digits 1-6 in $21-$26/$31-$36, chapter c's title (1-2 lines, <= 120 px each) in the
  4x15 tiles from $41+64c; map rows 15-16 cols 11-19 and rows 22-25 cols 8-22, centred on x 124 like the original.
- G5: sprite lists in the prologue sequence script, count byte then (x, y, tile, attr) per 16x16 sprite: Rufu
  0x10FA7 (8), Hamusu 0x10FC9 (12), Kairu 0x10FFB (12); names were 32x32 kanji cells. The build rewrites them.
- Lettering font for all three: the game's 8x16 staff-roll font (dir entry 4, raw 2bpp at 0x25A5E, copied to VRAM
  as is: char c top tile 32*((c-0x20)//16) + c%16, bottom +16), drawn proportionally.

## Already English (no work)

START / OPTION (dir 25/26), © 1994 ASMIK / ... / ARSYS SOFTWARE (dir 24), option screen text, HUD (SCORE,
digits, A-Z; dir 27), GAME OVER (dir 28), STAGE CLEAR (dir 32), CONTINUE? YES NO (dir 33), GO-arrow and
LEVEL/UP effect sprites (bank $97, file 0xB8000), Asmik logo (dir 5).

- **Staff roll is English already**: ASCII strings at file 0x12C9E-0x130xx ("The Crew", "Directed by", names...;
  control bytes 09 = position, 0C = new page, 00 = line end), drawn with the 8x16 ASCII font (dir entry 4).
  Original typos: "Charactor Design" x2 (0x12D48, 0x12D72; the build writes "Character"), "KATUTOSHI" (a name,
  left as credited).
- Option screen and sound-test names are ASCII strings at file 0x11EFF-0x124F9 (English).

## Fonts with Japanese that are not shown anywhere seen so far

- 8x8 font, dir entry 1 (file 0x221E4): ASCII + half-width katakana. No screen using it found yet (probably the
  option screen's ASCII; the katakana half may be unused).
- 8x16 ASCII font, dir entry 4 (raw 2bpp, file 0x25A5E-0x2665D, 3072 bytes; no header): staff roll; also the
  lettering of G3-G5 (phase 7).

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

## Reached in phase 2 (`tools/debug/scenes.lua`)

All chapter cards with the world map (G4; the 6th title reads 天涯放束 in the card shot), ending dialogue, profile
screens (dialogue-font text over the attract demo), continue screen, staff roll, stage clear. Only G4/G5 and font
text showed. **Missed in phase 1:** the idle-boot prologue, vertical Shift-JIS text drawn with its own font
(`text.md` §Prologue), then G5.
