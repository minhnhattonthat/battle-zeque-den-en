# Game flow, stage events and the debug tool (phase 2)

Facts the warp tool (`tools/debug/warp.lua`, scene list `tools/debug/scenes.lua`) builds on. All **verified** by
the warps themselves (each scene's run logs ARRIVED and its shots show the scene) unless marked guess.

## Game state (WRAM, bank $7E / low mirror)

| Address | Meaning | How found |
|---|---|---|
| $0327 | heroine 0 = Rufu, 1 = Hamusu, 2 = Kairu (script slot = scene*3 + heroine) | VM reads it at $83:8987 |
| $033B / $033D | chapter 0-5 / area 0-2; copied to $0341/$0343 at stage start, restored on retry | $80:B395, $80:82CB |
| $0372 | stage result: 0 running, 1 died (GAME OVER, continue), 2/3 retry/next area, 4 game cleared (staff roll) | main loop $80:813D, $80:8396 |
| $03A7 / $03AB | camera left / right limit (event ops 12, 15) | $80:B7C2, $80:B7FF |
| $03B3 / $03B5 | camera x / y (pixels) | event op 09 |
| [$7E:B228] | player object; +$74 x, +$76 y (pixels * 8) | event op 08 |
| $7E:DA94-DAA3 | 8 running event-script pointers (bank $96); slot 0 = the area's main script | $80:B3B2, $80:B414 |
| $7E:D9D8 | flag "0D 00" waits on, set by boss/intro-object AI in bank $81 | $80:B6EF |
| $113D | input playback: 0 off, 1 attract demo from $96:C365, 2 record pad to SRAM $70:0000 (dev leftover) | $80:D9B0 |

## Main loop ($80:812E)

New game ($80:825B: chapter/area 0, sequence 0 = title + character select) -> stage ($80:82A8: if area 0 and no
demo, sequence 6 = world map + chapter card; then $80:8329 runs the stage until $0372 != 0) -> result. Sequence
dispatcher `$82:8000` (A = 0-6): 0 title/select ($82:8027), 1 staff roll ($82:A507), 4 continue ($82:B158),
5 $82:B14E (not seen), 6 world map + chapter card ($82:B448). Chapter 6 (`$033B` = 6 at the title) also runs
the staff roll: guess, from $82:8055.

## Stage event scripts (bank $96)

Area table `$96:A5DE`: 6 chapter words -> 6 area words each (unused = $C364). Areas: ch1 0-1, ch2 0-2, ch3 0,
ch4 0-1, ch5 0-1, ch6 0-1. Loader `$80:B384` puts the area's script in slot 0; runner `$80:B3D8` runs every slot
each frame, op table `$80:B46C` (ops 00-24). Ops used by the debug tool:

| Op | Bytes | Meaning |
|---|---|---|
| 03 | 03 nn | 01 = cutscene on ($7E:D9CC = FFFF), 00 = off |
| 05 | 05 nn | run dialogue script scene nn (VM `$83:895C`, scene in DP $20) |
| 06 | 06 | wait for the dialogue to close |
| 08 | 08 x1 y1 x2 y2 (words) | wait until the player is in the rect (pixels) |
| 0B / 0C / 0E | 12 / 11 / 11 bytes | spawn enemy / boss / object |
| 0D | 0D nn | wait for a flag (00: $7E:D9D8) |
| 12 | 12 lo width | camera window |
| 15 | 15 xx xx | camera right limit |
| 1D / 1E | 1D nn 00 / 1E | start / wait a timer |
| 22 | 22 xx xx | arena limit (followed by an 08 rect) |

Dialogue scenes (VM scene = slot / 3; slots in `docs/re/text.md`):

| Scene | Where (op 05 address) | Text |
|---|---|---|
| 10-14 | ch1-5 area 0 start | opening monologue |
| 0, 1, 2, 3, 4, 5 | ch1 a1 $AA0B, ch2 a2 $AED0, ch3 a0 $B064, ch4 a1 $B696, ch5 a1 $BE02, ch6 a0 $C1B1 | boss |
| 6, 7, 8 | ch3 $B074, ch4 $B6AB, ch5 $BE17 | after the boss; one heroine each (1, 2, 0) |
| 15, 16 | ch4 a1 $B3FC, $B415 | mid-stage, enemy 08 |
| 9 | ch6 a1 $C2E1 | ending dialogue after the final boss |
| 26 | main loop on death ($80:83AC) | GAME OVER (no text) |
| 27 | after each boss | STAGE CLEAR (no text) |
| 28 | attract demo ($80:84E6) | heroine profile screens |
| 17-25 | not called by any op 05 seen | map/effect sequences, no text |

## How the warp works

1. Start every 64 frames until stage entry ($80:82A8), then A every 40 frames (boot timing drifts with Mesen's
   random RAM, so input is by state, not frame).
2. At $80:82A8 poke chapter/area/heroine once (poking during the character select hangs it).
3. Optional `jump`: send slot 0 to an address in the area script once it is past its opening ops (`03 01` before
   the dialogue). Arena scenes (bosses, mid-ch4) jump as the loader stores the script, so no enemy wave spawns,
   pin the player inside the `08` rect and snap the camera ($03B3; chapter 1's area hangs on a jump, so there it is
   stepped 8 px a frame). Boss 1's intro object (op 0E) sits off camera, so the tool sets $7E:D9D8 itself.
4. Optional `result`: poke $0372 (1 game over, 4 staff roll).
5. Arrival: the VM entry for a scene, a sequence number at $82:8000, or a decompressed block ($86:FE87 title logo,
   $86:8C5C character select). Profiles come from the idle attract demo (h0 ~f6500, h2 ~f8700, h1 ~f11200).
