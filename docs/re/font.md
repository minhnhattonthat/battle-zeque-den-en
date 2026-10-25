# Fonts

| Font | Where | Format | Use |
|---|---|---|---|
| Dialogue | $84:808C (file 0x2008C), long pointer at $84:8000 | 1bpp, 16x11, 2 bytes/row big-endian (12 px used), 22 bytes/glyph | dialogue boxes, profiles |
| 8x8 | $84:A1E4 (file 0x221E4), pointer $84:8004 | 1bpp 8x8 ASCII | ? (not seen yet) |
| Prologue | $84:A4BC, pointer $84:8008 (`$82:D18C`) | 1bpp 16x16, 32 bytes/glyph | vertical SJIS prologue (`text.md`) |
| HUD | directory entry 27 tile block (compressed) | 2bpp | SCORE, digits, A-Z |

- $84:8000 is a table of 4-byte entries `addr16, bank, flag`: `8C 80 84 01`, `E4 A1 84 01`, `BC A4 84 01`,
  `5C BE 84 00`. (Phase 1 read `$84:8002` as a glyph count 0x0184; it is the bank byte $84 + the flag.)
- Glyph address: `$84:808C + i*22`, carried into the next LoROM bank when it passes $FFFF ($83:9F01).
  **verified** (disassembly + ROM-read trace of き at $84:834C, の at $84:85E0).
- Sheets: `python -X utf8 tools/font_sheet.py OUT.png [--from N --to M --zoom Z]`.

## Dialogue renderer and the VWF (phase 5)

Original `$83:9F01` (A = glyph index): ORs the glyph into a 2bpp tile buffer at **$7F:10B8**, which the game DMAs
whole (0xAA0 bytes) to VRAM $6B00 every frame (`pc=$80:88BF`, `snes_dmalog.lua`). **verified**.
- Glyph rows 0-10 go to both planes (colour 3); a shadow, the glyph shifted 1 px right and 1 row down, goes to
  plane 0 only (colour 1). So each glyph covers 13x12 px.
- Buffer layout, dialogue box (`$7F:003A` = 0): tile rows of 23 tiles (0x170 bytes), text row r = 2 tile rows at
  r * 0x2E0. Profile screens (`$7F:003A` != 0): 16-tile rows (0x100), text row r at r * 0x200, rows up to 15.
- Cursor `$7F:002C`: low nibble = 12-px cell column, bits 4-5 (profile: 4-7) = row. Even cells start on a byte,
  odd cells 4 px further (`$83:A049`). After a glyph the column wraps at 14 to the next row (`$83:A100`).
- Newline `$83:A561` does nothing at column 0 (so no empty lines), else row + 1, column 0. Past row 3: if
  `$7F:002D` (set to 3 by `{page}`) is nonzero it counts down and scrolls (`$83:A3C9`: rows 1-2 up, bottom row
  refilled with the box background AA/55, none for op 06 Totetsu), at 0 it jumps to row 0 without clearing;
  if zero it waits and puts the cursor on row 3 **without scrolling, so the next line overwrites it** (seen in
  the first marker build). `{page}` = newline + wait + counter 3. The jp text never has more than 3 lines before
  a `{page}` (patterns 3 / 2 / 1 / 2+2 / 1+3).
- **Patched (phase 5, `asm/vwf.asm`):** a newline past row 3 waits for a button, clears the 3 rows (3 scrolls) and
  starts a fresh page; `{page}` does the same at once (unless a page just began). So English is a run of lines
  joined by `{n}`, paged by 3 automatically; `{page}` forces a new page. **verified** (`work/qa/m2/ch1_h0`:
  the 4-line torture entry pages after 3; `boss1_h0` AA9E `{page}` starts page 2 at the top).

The VWF (`asm/vwf.asm`, assembled by `tools/build.py` with asar): `$83:9F01` becomes `JSL $80:E580; RTS`. The new
routine keeps the buffer, shadow and row maths, but draws at a pixel pen `$7F:FF00` (reset when the cursor column
is 0), shifting each glyph row through 3 tiles, then adds the glyph's advance (`vwf_widths`, one byte per glyph)
and sets the cursor column to 1 (the game's newline still works; its 14-cell wrap never fires, so the build must
break lines). Scratch `$7F:FF00-$7F:FF13`. Font: `fonts/vwf.txt` (drawn for the project, 95 ASCII glyphs,
caps 8 px, x-height 6, descenders 2) -> glyph slots 0-94 at $84:808C (code = slot + 0x10, `tbl/en.tbl` from
`tools/font.py`). **verified** in the marker build (`work/qa/m1`, all 62 warps).

## Box widths (width gate, `tools/boxes.py`)

Measured with `tools/textpx.py` on full-width marker lines (pen advance budget per line, `font.text_width`):
- hero box (portrait left): 22 buffer tiles visible, text x 56..231 -> 176 px, 3 rows per page;
- enemy box (portrait right): 22 tiles, x 24..199 -> 176 px (the 23rd tile is under the portrait);
- Totetsu (op 06, no box): all 23 tiles, from x 40 -> 184 px (a 182-px line shows whole);
- profile screens: 16-tile rows from x 128 to the screen edge -> 128 px, 9 rows (own reader `$83:9DAC`);
- prologue: own renderer, guess (see `text.md` §Prologue).
The page-wait arrow sits on the box's bottom border, not in a text row, so the last line has the full width.
Glyph torture line (all printable ASCII + double spaces, entry AA38 in the marker build): every glyph shows.
