# Fonts

| Font | Where | Format | Use |
|---|---|---|---|
| Dialogue | $84:808C (file 0x2008C), 388 glyphs (count word at $84:8002 = 0x0184) | 1bpp, 16x11, 2 bytes/row big-endian (12 px used), 22 bytes/glyph | dialogue boxes, profiles |
| 8x8 | $84:A1E4 (file 0x221E4), directory entry 1 | 1bpp 8x8 ASCII | ? (not seen yet) |
| HUD | directory entry 27 tile block (compressed) | 2bpp | SCORE, digits, A-Z |

- Glyph address: `$84:808C + i*22`, carried into the next LoROM bank when it passes $FFFF ($83:9F01).
  **verified** (disassembly + ROM-read trace of き at $84:834C, の at $84:85E0).
- The dialogue glyph is drawn into a 1bpp->tile buffer per cell; the cursor column is a 4-bit field (16 cells per line),
  3 rows per box. A VWF goes here (phase 5).
- Sheets: `python -X utf8 tools/font_sheet.py OUT.png [--from N --to M --zoom Z]`.
