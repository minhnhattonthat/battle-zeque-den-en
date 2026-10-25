-- Log every call of the decompressor $82:D92C: frame, caller-set source ($40/$42), destination ($44/$46), $43 seed.
--   emu.py ... --script tools/lua/lzlog.lua
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function w(a) return rd(a) | rd(a + 1) << 8 end
L.on_exec(0x82D92C, 0x82D92C, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local src = w(d + 0x40) | rd(d + 0x42) << 16
  local dst = w(d + 0x44) | rd(d + 0x46) << 16
  L.log(string.format("lz f%d src=%06X off=%06X dst=%06X seed=%02X", L.frame, src, L.rom_off(src), dst, rd(d + 0x43)))
end)
