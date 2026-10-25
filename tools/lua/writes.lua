-- SNES (Mesen): log every CPU write to WRAM addresses LO..HI in frames FROM..TO (pc, address, value), at most MAX lines.
--   emu.py ... --script tools/lua/writes.lua --var LO=0x7E03CB --var HI=0x7E03CC [--var FROM=700 --var TO=900]
local from, to, max, n = FROM or 0, TO or math.huge, MAX or 2000, 0
L.on_write(LO, HI or LO, function(addr, value)
  if L.frame < from or L.frame > to or n >= max then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("f%d pc=%02X%04X %06X=%02X", L.frame, s["cpu.k"], s["cpu.pc"], addr, value))
end)
