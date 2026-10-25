# Compression (graphics and tilemaps)

One codec for all compressed graphics: decompressor `$82:D92C` (long entry `JSL $82D928`). Caller sets source in
`$40-$42` (24-bit), destination in `$44-$46`; `$43` (the high byte of the source word pair) seeds the delta ops.
Python: `tools/lz.py` (`decompress(data, off, init) -> (bytes, end)`), selftest in `tests/test_recon.py`.
**verified**: every directory entry's map and tile block decode to their header size and each tile block's stream
ends exactly at the next entry (0x23E5C-0x46374, `test_directory_blocks_are_back_to_back`).

## Format

Header: u16 output size, u16 stride (0x40 for 32-wide tilemaps, 0x08/0x200 for tiles). Then commands; high nibble
= op, `n = low nibble + 1`, until the output reaches the size.

| Op | Effect |
|---|---|
| 0 | n zero bytes |
| 1 / 2 / 3 | repeat the last byte / word / dword n times |
| 4 / 5 | n / n+16 literal bytes |
| 6 / 7 | one byte: last += n-17 / n-1 ("last" = last literal or delta byte; starts as the seed) |
| 8 / 9 | copy n bytes from out-stride / out-2*stride |
| A / B | n words: word at out-stride +0x10 / -0x10 |
| C / D | n words counting up / down from the previous word |
| E | u16 off: the next n+3 *stream* bytes are read from block_start+off |
| F | u8 b, u16 off: the next ((n-1)<<8 \| b)+4 stream bytes are read from block_start+off |

E/F replay earlier compressed bytes (commands included), so a recompressor can ignore them: literals (op 5) plus
runs are enough, at some size cost. Free space and repointing decide that in phase 5.

## Where blocks are

- **Asset directory** at $84:8000 (file 0x20000): 35 entries of (u24 address, u8 type). Type 01 = raw (fonts,
  entries 0-2); others: a tilemap block followed directly by its tile block (the loader decompresses both;
  `tools/dump_assets.py OUTDIR` dumps them, `tools/render_assets.py OUTDIR` draws each map with its tiles).
  Entry 4 has a zero-size header; 0x25A62-0x2665E after it is not yet identified.
- Loader for directory entries: `$83:A124` (reads entry 3), `$83:8231`, `$83:8C76`; stage loader in bank $82
  (`$82:D828`, table via `[$48],y`) loads stage tiles, e.g. the stage-1 chain 0x78781-0x7CC39 (7 blocks).
- `tools/lua/lzlog.lua` logs every decompressor call (source, destination, seed) during a run.
- `tools/lz_scan.py` finds back-to-back block chains anywhere in the ROM (4 s for the whole ROM). Result: the
  directory chain plus 12 stage chains of 7 blocks each, 0x78781-0xAE6E7 (first block = scenery tiles, stride
  0x200; the rest stride 8). Nothing compressed elsewhere. The decompressor raises on a self-referencing E/F
  loop, which only garbage contains.
