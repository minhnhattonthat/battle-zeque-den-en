-- Log each entry to the script VM ($83:8960): scene arg (DP $20), heroine ($0327), caller (stack).
--   emu.py ... --script tools/lua/vmentry.lua
L.on_exec(0x838960, 0x838960, function()
  local s = emu.getState()
  local d, sp = s["cpu.d"], s["cpu.sp"]
  local function r(a) return emu.read(a, emu.memType.snesMemory) end
  local function w(a) return r(a) | (r(a + 1) << 8) end
  local ret = {}
  for i = 1, 8 do ret[#ret + 1] = string.format("%02X", r(sp + i)) end
  L.log(string.format("f%d VM scene=%d D=%04X heroine=%d A=%04X stack=%s", L.frame, w(d + 0x20), d,
    r(0x000327), s["cpu.a"], table.concat(ret, " ")))
end)
