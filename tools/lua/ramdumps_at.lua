-- SNES (Mesen): dump all of WRAM ($7E0000-$7FFFFF, 128 KB) at each frame of DUMP_AT_LIST: <out>/ram_<frame>.bin.
--   --var "DUMP_AT_LIST={1100,1300}"   (search them with the skill's ramsearch.py)
local want = {}
for _, f in ipairs(DUMP_AT_LIST or {}) do want[f] = true end
L.on_frame(function(f)
  if want[f] then L.dump_ram(string.format("ram_%06d.bin", f)) end
end)
