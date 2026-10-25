-- Dump PPU state (VRAM/CGRAM/OAM/regs) at each frame in DUMP_AT_LIST, e.g. --var "DUMP_AT_LIST={1100,1740}".
-- Files: <out>/ppu_<frame>.vram.bin etc. (see the skill's L.dump_ppu).
local want = {}
for _, f in ipairs(DUMP_AT_LIST or {}) do want[f] = true end
L.on_frame(function(f)
  if want[f] then L.dump_ppu(string.format("ppu_%06d", f)) end
end)
