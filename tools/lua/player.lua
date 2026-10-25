-- Log the player object (pointer $7E:B228; +$74 x, +$76 y, +$1A ?) and camera ($03B3/$03B5) every 60 frames.
--   emu.py ... --script tools/lua/player.lua
local function r8(a) return emu.read(a, emu.memType.snesMemory) end
local function r16(a) return r8(a) | (r8(a + 1) << 8) end
L.on_frame(function(n)
  if n % 60 ~= 0 then return end
  local p = r16(0x7EB228)
  if p == 0 then return end
  local o = 0x7E0000 | p
  L.log(string.format("f%d obj=%04X x=%d y=%d cam=%d,%d D9D8=%d D9DA=%d", n, p, r16(o + 0x74), r16(o + 0x76),
    r16(0x7E03B3), r16(0x7E03B5), r16(0x7ED9D8), r16(0x7ED9DA)))
end)
