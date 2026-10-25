-- Text coverage: log each distinct text-byte address the game reads (bank $83 text slot + overflow space).
-- tools/textcover.py turns the logs of a warp_all run into the list of strings shown / never shown.
--   warp_all.py --rom build/bzd_en.sfc --out cover --lua tools/lua/textcover.lua
local seen = {}
local function hook(addr)
  local a = addr & 0xFFFF
  if seen[a] then return end
  seen[a] = true
  L.log(string.format("TEXT %04X f%d", a, L.frame))
end
for _, bank in ipairs({ 0x03, 0x83 }) do
  for _, r in ipairs({ { 0xAA38, 0xBE32 }, { 0xDB7A, 0xFFFF } }) do
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | r[1], (bank << 16) | r[2],
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
