-- Write bytes at given frames (or every frame from..to): POKES = {{from, to, addr, value}, ...}.
--   emu.py ... --script tools/lua/poke.lua --var "POKES={{2400,2400,0x7E0372,4}}"
L.on_frame(function(n)
  for _, p in ipairs(POKES or {}) do
    if n >= p[1] and n <= p[2] then emu.write(p[3], p[4], emu.memType.snesMemory) end
  end
end)
