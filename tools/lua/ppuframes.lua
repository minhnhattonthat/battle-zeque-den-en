-- SNES (Mesen): per frame in [FROM, TO], log forced blank, brightness, BG mode/main screen and a CGRAM checksum
-- (palette uploads show as a changed sum).  --var FROM=3370 --var TO=3400
local from, to = FROM or 0, TO or 0
emu.addEventCallback(function()
  local f = L.frame
  if f < from or f > to then return end
  local s = emu.getState()
  local sum = 0
  for i = 0, 511 do sum = (sum * 31 + emu.read(i, emu.memType.snesCgRam)) % 1000000007 end
  local vram = {}  -- one sum per 8 KB of VRAM
  for k = 0, 7 do
    local v = 0
    for i = k * 0x2000, k * 0x2000 + 0x1FFF do v = (v * 31 + emu.read(i, emu.memType.snesVideoRam)) % 1000003 end
    vram[#vram + 1] = string.format("%06d", v)
  end
  L.log(string.format("f%d blank=%s bright=%s mode=%s main=%s cgram=%d vram=%s", f, tostring(s["ppu.forcedBlank"]),
    tostring(s["ppu.screenBrightness"]), tostring(s["ppu.bgMode"]), tostring(s["ppu.mainScreenLayers"]), sum,
    table.concat(vram, ",")))
end, emu.eventType.endFrame)
