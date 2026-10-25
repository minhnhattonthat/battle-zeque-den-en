-- Warp from a cold boot to a scene in tools/debug/scenes.lua, shoot it, stop. RAM/code facts: docs/re/debug.md.
--   emu.py ROM --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='boss1_h0'" --frames 20000
-- Optional: --var SHOT_EVERY_W=30 (shot cadence after arrival, default 60), --var NOSTOP=1 (run to --frames),
--   --var "SCENES_FILE='abs/path/scenes.lua'".
-- Logs "ARRIVED <scene> f<frame>"; fails (exit 2) if --frames ends first.
local scenes = dofile(SCENES_FILE or "../debug/scenes.lua")  -- Mesen runs with cwd = tools/mesen
if SCENE == "list" then
  local names = {}
  for k in pairs(scenes) do names[#names + 1] = k end
  table.sort(names)
  L.log("SCENES " .. table.concat(names, " "))
  L.finish(0)
  return
end
local sc = assert(scenes[SCENE or ""], "unknown SCENE '" .. tostring(SCENE) .. "' (see tools/debug/scenes.lua)")
local every = SHOT_EVERY_W or 60
local mem = emu.memType.snesMemory
local function r8(a) return emu.read(a, mem) end
local function r16(a) return r8(a) | (r8(a + 1) << 8) end
local function w8(a, v) emu.write(a, v, mem) end
local function w16(a, v) w8(a, v & 0xFF); w8(a + 1, v >> 8) end

local arrived, stage_started, jumped, result_done = nil, false, false, false
local function arrive(what)
  if arrived then return end
  arrived = L.frame + 1  -- hooks run mid-frame; the frame counter steps at its end
  L.log(string.format("ARRIVED %s f%d (%s)", SCENE, L.frame, what))
  if STATE_OUT then L.save_state(STATE_OUT) end  -- --state-out: a state at the arrival point
end

-- Input by state, not frame counts (boot timing drifts with Mesen's random RAM): Start every 64 frames until the
-- character select is up (select_only) or the stage is entered, then A every 40 frames (attacks, pages text).
local poked, select_up = false, false
if not sc.idle then
  emu.addEventCallback(L.safe(function()
    local n = L.frame
    if not (poked or (sc.select_only and select_up)) then
      if n >= 300 and n % 64 < 6 then emu.setInput({ start = true }, 0) end
    elseif poked then
      emu.setInput({ a = n % 40 < 6 }, 0)
    end
  end), emu.eventType.inputPolled)
end

-- Decompressor $82:D92C source ($40-$42): title logo $86:FE87, character select $86:8C5C.
L.on_exec(0x82D92C, 0x82D92C, function()
  local d = emu.getState()["cpu.d"]
  local src = r16(d + 0x40) | (r8(d + 0x42) << 16)
  if src == 0x868C5C then select_up = true end
  if sc.arrive.lz == src then arrive(string.format("lz %06X", src)) end
end)

-- Poke chapter/area/heroine once at stage entry ($80:82A8, before the chapter card); poking during the
-- character select hangs it. The stage loader ($80:B384) then sets slot 0 of the event list.
L.on_exec(0x8082A8, 0x8082A8, function()
  if not sc.chapter or poked then return end
  poked = true
  w8(0x7E033B, sc.chapter); w8(0x7E033D, sc.area); w8(0x7E0327, sc.heroine)
end)
L.on_exec(0x80B384, 0x80B384, function()
  if not stage_started then
    stage_started = L.frame
    L.log(string.format("stage loader f%d chapter %d area %d heroine %d", L.frame, r8(0x7E033B), r8(0x7E033D),
      r8(0x7E0327)))
  end
end)

-- Arena scenes: replace the area script as the loader stores it ($80:B3B6, after STA $7EDA94), so none of the
-- area's enemy waves spawn; then open the camera's right limit ($03AB, event ops 12/15) and put the player
-- (object at [$7E:B228], x*8 at +$74) inside the arena rect the script waits for.
-- The stage intro resets the player's position, so pin it inside the rect every frame until the main event is
-- past the "08 x1 y1 x2 y2" op (pixels; the object keeps them *8).
if sc.arena then
  local rect
  for i = 0, 40 do
    if r8(sc.jump + i) == 0x08 and r16(sc.jump + i + 1) == sc.arena then rect = sc.jump + i; break end
  end
  assert(rect, "no '08' rect op with x1 = arena after the jump address")
  local x, y1, y2 = sc.arena + 32, r16(rect + 3), r16(rect + 7)
  L.on_exec(0x80B3B6, 0x80B3B6, function()
    if jumped then return end
    jumped = true
    w16(0x7EDA94, sc.jump & 0xFFFF)
    L.log(string.format("event jump at load f%d -> %06X (rect op %06X)", L.frame, sc.jump, rect))
  end)
  local pinned = false
  local target = sc.arena - 72
  L.on_frame(function(n)
    local p = r16(0x7EB228)
    if not jumped or arrived or p == 0 then return end
    -- camera x ($03B3): else it scrolls from the area start (~2 px/frame) first. Boss 1's area hangs on a
    -- jump, so there (cam_step) it is stepped toward the arena a few pixels a frame instead.
    local cam = r16(0x7E03B3)
    if sc.cam_step and cam < target then w16(0x7E03B3, math.min(target, cam + sc.cam_step)) end
    local ptr = 0x960000 | r16(0x7EDA94)
    if ptr > rect then
      -- "0D 00" waits for $7E:D9D8, set by an intro object's AI that may sit off camera (boss 1): set it
      -- (only the one before the boss-spawn op 0C; the next "0D 00" waits for the boss itself)
      if r8(ptr) == 0x0D and r8(ptr + 1) == 0 and r8(ptr + 2) == 0x0C then w16(0x7ED9D8, 0xFFFF) end
      if not pinned then L.log(string.format("in arena f%d", n)) end
      pinned = true
      return
    end
    if pinned then return end
    w16(0x7E03AB, 0x7FFF)
    if not sc.cam_step then w16(0x7E03B3, target) end
    w16(0x7E0000 | (p + 0x74), x * 8)
    local y = r16(0x7E0000 | (p + 0x76)) >> 3
    if y < y1 or y >= y2 then w16(0x7E0000 | (p + 0x76), (y2 - 24) * 8) end
  end)
end

-- Event runner reads slot X ($7E:DA94..) at $80:B41F: redirect the main event once past its opening ops.
local function script_start()
  local t = r16(0x96A5DE + 2 * r8(0x7E033B)) | 0x960000
  return r16(t + 2 * r8(0x7E033D)) | 0x960000
end
L.on_exec(0x80B41F, 0x80B41F, function()
  if not stage_started then return end
  if sc.arrive.events then arrive("events") end
  if emu.getState()["cpu.x"] ~= 0xDA94 then return end
  local ptr = 0x960000 | r16(0x7EDA94)
  local start = script_start()
  -- area scripts that open with a monologue: 15 xx xx 03 01 04 05 nn 06 03 00; wait until past it
  local skip = (r8(start + 3) == 3 and r8(start + 5) == 4 and r8(start + 6) == 5) and 11 or 3
  if ptr < start + skip then return end
  if sc.jump and not jumped and not sc.arena then
    jumped = true
    w16(0x7EDA94, sc.jump & 0xFFFF)
    L.log(string.format("event jump f%d %06X -> %06X", L.frame, ptr, sc.jump))
  end
  if sc.result and not result_done then
    result_done = true
    w8(0x7E0372, sc.result)
    L.log(string.format("stage result %d f%d", sc.result, L.frame))
  end
end)

-- Arrival hooks.
if sc.arrive.vm then
  L.on_exec(0x838960, 0x838960, function()
    local scene = r16(emu.getState()["cpu.d"] + 0x20)
    if scene == sc.arrive.vm and (sc.arrive.heroine == nil or r8(0x7E0327) == sc.arrive.heroine) then
      arrive("vm scene " .. scene)
    end
  end)
end
if sc.arrive.mode then
  L.on_exec(0x828000, 0x828000, function()
    if (emu.getState()["cpu.a"] & 0x0F) == sc.arrive.mode then arrive("mode " .. sc.arrive.mode) end
  end)
end

L.on_frame(function(n)
  if arrived then
    local k = n - arrived
    if k % every == 0 then L.shot(string.format("f%06d.png", n)) end
    if k == (sc.hold or 600) and not NOSTOP then
      L.shot("final.png")
      L.finish(0)
    end
  elseif FRAMES and n >= FRAMES - 1 then
    L.fail(string.format("scene %s not reached in %d frames", SCENE, FRAMES))
  end
end)
