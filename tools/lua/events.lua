-- Log each stage-event op the event runner ($80:B441) executes: frame, $96:xxxx pointer, op, next bytes.
--   emu.py ... --script tools/lua/events.lua
local last = {}
L.on_exec(0x80B441, 0x80B441, function()
  local x = emu.getState()["cpu.x"]
  if last[x] == L.frame - 1 or last[x] == L.frame then last[x] = L.frame return end
  last[x] = L.frame
  local t = {}
  for i = 0, 7 do t[#t + 1] = string.format("%02X", emu.read(0x960000 + x + i, emu.memType.snesMemory)) end
  L.log(string.format("f%d ev $96:%04X %s", L.frame, x, table.concat(t, " ")))
end)
