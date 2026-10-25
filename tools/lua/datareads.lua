-- SNES (Mesen): log every ROM *data* read (not opcode fetches) in frames FROM..TO, one line per read.
-- Unlike the skill's snes_romreads.lua it does not dedupe, so a text reader shows every byte it walks.
--   emu.py ... --script tools/lua/datareads.lua --var FROM=2241 --var TO=2260 [--var SKIP_BANK=0x96]
local from, to = FROM or 0, TO or math.huge
local skip = SKIP_BANK or -1
local function hook(addr, value)
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if (addr >> 16) & 0x7F == (pc >> 16) & 0x7F and math.abs((addr & 0xFFFF) - (pc & 0xFFFF)) < 4 then return end
  if (addr >> 16) & 0x7F == skip & 0x7F then return end
  L.log(string.format("f%d pc=%06X %06X=%02X", L.frame, pc, addr, value))
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
