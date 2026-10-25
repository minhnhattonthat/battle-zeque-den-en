-- SNES (Mesen): count executions of each address in PCS per frame window; log the first frame each one runs and
-- how often, plus A/X/Y at the first MAX hits.  --var "PCS={0x82C1FF,0x80DB48}" [--var FROM=600 --var MAX=5]
local from, max = FROM or 0, MAX or 5
local count = {}
for _, pc in ipairs(PCS) do
  count[pc] = 0
  L.on_exec(pc, pc, function()
    if L.frame < from then return end
    count[pc] = count[pc] + 1
    if count[pc] <= max then
      local s = emu.getState()
      L.log(string.format("f%d %06X A=%04X X=%04X Y=%04X", L.frame, pc, s["cpu.a"], s["cpu.x"], s["cpu.y"]))
    end
  end)
end
L.on_frame(function(f)
  if f % 500 == 0 then
    local parts = {}
    for _, pc in ipairs(PCS) do parts[#parts + 1] = string.format("%06X:%d", pc, count[pc]) end
    L.log(string.format("f%d counts %s", f, table.concat(parts, " ")))
  end
end)
