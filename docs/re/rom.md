# ROM header, map, free space

- File: 1,572,864 bytes (12 Mbit), no copier header. Internal name `BATTLE ZEQUE DEN`.
- Header at $00:FFC0 (file 0x7FC0): map mode $30 = **LoROM, FastROM** (code runs in $80+ banks); cart type $00
  (ROM only, no SRAM); size byte $0B (claims 2 MB, the file is 1.5 MB); region $00 (Japan); version 0;
  checksum complement $4F3C / checksum $B0C3. **verified** (read from the dump in `rom.sha1`).
- File offset = `((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)`.
- Banks: $80-$83 code (+ option/sound-test/staff-roll ASCII at $82:9EFF-$82:B0xx, text, script, palettes in $83),
  $84-$88 fonts + asset directory blocks (file 0x20000-0x46374), $88-$8F 0x47000-0x78781 not identified (no
  compressed chains, no graphics in the sweep; likely sound/level data), $8F-$95 compressed stage chains
  (0x78781-0xAE6E7), $96-$AF raw sprite graphics (DMA'd from ROM). (layout from the sweep and traces)

## Free-space candidates (runs of 00, >= 256 bytes)

**Trap-tested (phase 5):** `tools/lua/trap.lua` over all 62 warps (`warp_all.py --out trap --lua tools/lua/trap.lua
--var "ROM_TRAPS={{0x1DB7A,0x1FFFF},{0x657B,0x7FBF}}" --var "RAM_TRAPS={{0x7FFE00,0x7FFFFF}}"`) on the original
ROM: no read of either ROM range; the only write to `$7F:FE00-FFFF` is the boot WRAM clear (`$80:8125`, frame 23).
In use: `$80:E580+` VWF code, `$83:DB7A+` overflow text, `$7F:FF00-FF13` VWF scratch. The rest are untested.

| File range | CPU | Bytes |
|---|---|---|
| 0x0657B-0x07FBF | $80:E57B | 6,725 (stops at the header) |
| 0x0FD5C-0x0FFFF | $81:FD5C | 676 |
| 0x1641F-0x17FFF | $82:E41F | 7,137 |
| 0x1DB7A-0x1FFFF | $83:DB7A | 9,350 (only text-bank space) |
| 0x46374-0x46FFF | $88:E374 | 3,212 |
| 0x77DBB-0x77FFF | $8E:FDBB | 581 |
| 0xAE6E6-0xAFFFF | $95:E6E6 | 6,426 |
| 0xB5B37-0xB8002 | $96:DB37 | 9,420 |
| 0xBF2A0-0xBFFFF | $97:F2A0 | 3,424 |
| 0x14E53D-0x14E67C, 0x14F1CD-0x14F390 | $A9 | 320, 452 |
| 0x167EE5-0x167FFF | $AC:FEE5 | 283 |
| 0x16F8A4-0x170001 | $AD:F8A4 | 1,886 |
| 0x177246-0x177FFF | $AE:F246 | 3,514 |
| 0x17932B-0x17FFFF | $AF:932B | 27,861 |

Expansion to 2 MB (banks $B0-$BF, file 0x180000-0x1FFFFF) is free by construction; the header already says 2 MB.
