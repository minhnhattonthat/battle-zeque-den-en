# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [rom.md](rom.md) | header, mapping, bank layout, free-space candidates | header verified, free space candidates only |
| [text.md](text.md) | encoding, control codes, script VM, text pointers, text free space | verified (op meanings partly guessed) |
| [font.md](font.md) | dialogue 16x11 font, 8x8 font, HUD font | verified |
| [compression.md](compression.md) | graphics/tilemap codec, asset directory, block locations | verified |
| [graphics.md](graphics.md) | graphics-text survey (tour + static sweep) | see file |
| [debug.md](debug.md) | game state RAM, main loop, stage event scripts, how the warp tool works | verified by warps |
| [prior-work.md](prior-work.md) | earlier patches and documentation | searched |
