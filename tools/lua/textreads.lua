-- Log each read of the dialogue block ($83:AA38-$83:BE32) with the reading PC: finds the text reader.
--   emu.py ... --script tools/lua/textreads.lua
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local key = pc .. ":" .. addr
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d pc=%06X %06X=%02X", L.frame, pc, addr, value))
end
for _, bank in ipairs({0x03, 0x83}) do
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0xAA38, (bank << 16) | 0xBE32,
    emu.cpuType.snes, emu.memType.snesMemory)
end
