-- Ring buffer of the last 400 executed PCs; dump it when TARGET runs (default the script VM entry $83:8960).
--   emu.py ... --script tools/lua/pctrace.lua [--var TARGET=0x838960] [--var FROM=2000]
local target = TARGET or 0x838960
local from = FROM or 0
local ring, n, done = {}, 0, false
L.on_exec(0x800000, 0x83FFFF, function(addr)
  if done or L.frame < from then return end
  n = n + 1
  ring[n % 400] = addr
  if addr == target then
    local out = {}
    for i = n - 399, n do
      local a = ring[i % 400]
      if a and a ~= out[#out] then out[#out + 1] = a end
    end
    local s = {}
    for _, a in ipairs(out) do s[#s + 1] = string.format("%06X", a) end
    L.log("trace before " .. string.format("%06X", target) .. ": " .. table.concat(s, " "))
    done = true
  end
end)
