-- Trap test: log the first access (PC, address) to each candidate free range, one line per (PC, range).
--   ROM_TRAPS: ROM file ranges nobody may read or execute, e.g. "{{0x1DB7A,0x1FFFF},{0x657B,0x7FBF}}"
--   RAM_TRAPS: WRAM ranges (CPU addresses) nobody may write, e.g. "{{0x7FFF00,0x7FFFFF}}"
--   ALLOW_PC: PCs to ignore (our own code), e.g. "{0x80E580}"
-- A clean run logs nothing but "TRAP armed". Run it across every scene: warp_all.py --lua tools/lua/trap.lua.
local mem = emu.memType.snesMemory
local allow = {}
for _, pc in ipairs(ALLOW_PC or {}) do allow[pc] = true end
local seen = {}
local function watch(kind, lo, hi, cb_type)
  return L.safe(function(addr, value)
    local s = emu.getState()
    local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
    if allow[pc] then return end
    local key = kind .. pc .. ":" .. lo
    if seen[key] then return end
    seen[key] = true
    L.log(string.format("TRAP %s f%d pc=%06X addr=%06X value=%02X", kind, L.frame, pc, addr, value))
  end)
end
local function cpu(off, bank)  -- LoROM file offset -> CPU address in the $00 (bank=0) or $80 mirror
  return ((off >> 15) << 16) + 0x8000 + (off & 0x7FFF) + (bank << 16)
end
for _, r in ipairs(ROM_TRAPS or {}) do
  local lo, hi = r[1], r[2]
  while lo <= hi do  -- split at 32 KB bank edges
    local top = math.min(hi, (lo | 0x7FFF))
    for _, m in ipairs({ 0x00, 0x80 }) do
      emu.addMemoryCallback(watch("read", lo, top), emu.callbackType.read, cpu(lo, m), cpu(top, m),
        emu.cpuType.snes, mem)
    end
    lo = top + 1
  end
end
for _, r in ipairs(RAM_TRAPS or {}) do
  emu.addMemoryCallback(watch("write", r[1], r[2]), emu.callbackType.write, r[1], r[2], emu.cpuType.snes, mem)
end
L.log("TRAP armed")
