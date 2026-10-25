-- Log WRAM bytes PEEK_LO..PEEK_HI (default 16 bytes) at frames PEEK_AT (list) or every PEEK_EVERY frames.
--   emu.py ... --script tools/lua/peek.lua --var PEEK_LO=0x7EDA94 [--var PEEK_HI=0x7EDAA3] --var "PEEK_AT={600,2200}"
local lo = assert(PEEK_LO, "set --var PEEK_LO=0x...")
local hi = PEEK_HI or lo + 15
local at = {}
for _, f in ipairs(PEEK_AT or {}) do at[f] = true end
L.on_frame(function(n)
  if not (at[n] or (PEEK_EVERY and n % PEEK_EVERY == 0)) then return end
  local t = {}
  for a = lo, hi do t[#t + 1] = string.format("%02X", emu.read(a, emu.memType.snesMemory)) end
  L.log(string.format("f%d %06X: %s", n, lo, table.concat(t, " ")))
end)
