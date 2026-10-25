-- Scene list for warp.lua: name -> how to get there from a cold boot. RAM and code facts: docs/re/debug.md.
--   chapter, area, heroine: poked into $033B/$033D/$0327 from boot until the stage loader reads them, so the
--     game enters the stage its own way (world map + chapter card when area is 0, then the area's event script).
--     heroine: 0 = Rufu, 1 = Hamusu, 2 = Kairu (script slot order).
--   jump: $96 event-script address the area's main event is sent to once it is past its opening ops
--     (skips the enemy waves; lands on the "03 01" (cutscene on) op before the dialogue's op 05, or on the
--     arena set-up before a boss).
--   arena = x: jump as the loader sets the script (no enemy waves spawn), open the camera and put the player
--     at x+32 px, inside the rect the arena's "08" op waits for; the camera is snapped there too
--     (cam_step = n: moved n px a frame instead; boss 1's area hangs on a jump).--   result: value poked into $0372 (stage result) once the area's events run: 1 = died (GAME OVER, continue
--     screen), 4 = game finished (staff roll).
--   idle = true: no input at all (title attract demo).
--   select_only = true: press Start at the title only (character select screen).
--   arrive: what proves the scene is up: {vm = script scene [, heroine]} (VM entry $83:8960),
--     {mode = n} (sequence dispatcher $82:8000: 0 title, 1 staff roll, 4 continue, 6 world map + chapter card)
--     {events = true} (the area's event script started, $80:B384) or {lz = source} (decompressor $82:D92C
--     unpacks that block: $86:FE87 title logo, $86:8C5C character select).
--   hold: frames to keep shooting after arrival (default 600); shots every SHOT_EVERY (default 60) frames.
local S = {}

-- Idle boot: prologue (vertical Shift-JIS text, $82:8D0C, docs/re/text.md), heroine art, then the title (~f3600).
S.prologue_title = { idle = true, arrive = { lz = 0x86FE87 }, hold = 3300 }
S.select = { select_only = true, arrive = { lz = 0x868C5C }, hold = 600 }

-- World map + chapter card + opening monologue (scenes 10-14; chapter 6 has none), per heroine.
local monologue = { 10, 11, 12, 13, 14 }
for c = 1, 6 do
  for h = 0, 2 do
    S[string.format("ch%d_h%d", c, h)] = { chapter = c - 1, area = 0, heroine = h, arrive = { mode = 6 },
      hold = monologue[c] and 2700 or 1200 }
  end
end

-- Later areas of a chapter (no card).
for _, ca in ipairs({ { 1, 1 }, { 2, 1 }, { 2, 2 }, { 4, 1 }, { 5, 1 }, { 6, 1 } }) do
  S[string.format("ch%d_a%d", ca[1], ca[2])] = { chapter = ca[1] - 1, area = ca[2], heroine = 0,
    arrive = { events = true }, hold = 600 }
end

-- Boss dialogues (scenes 0-5), every heroine: run the area from the boss arena's scroll-limit op "22 xxxx"
-- (followed by "08 rect": wait for the player in the arena) with the player put in that rect; the game then
-- spawns the boss and talks. {scene, chapter, area, jump, arena rect x}.
local bosses = {
  -- boss 1 starts at the op 0E before (x 2688): that object's AI sets $7E:D9D8, which "0D 00" waits for
  -- (off camera here, so warp.lua sets the flag itself)
  { 0, 1, 1, 0x96A9D2, 2984 }, { 1, 2, 2, 0x96AEA8, 1744 }, { 2, 3, 0, 0x96B03D, 2336 },
  { 3, 4, 1, 0x96B66A, 3288 }, { 4, 5, 1, 0x96BDD3, 2336 }, { 5, 6, 0, 0x96C18F, 2336 },
}
for _, b in ipairs(bosses) do
  for h = 0, 2 do
    S[string.format("boss%d_h%d", b[2], h)] = { chapter = b[2] - 1, area = b[3], heroine = h, jump = b[4],
      arena = b[5], cam_step = b[2] == 1 and 8 or nil, arrive = { vm = b[1] }, hold = 1500 }
  end
end

-- Post-boss lines that exist for one heroine only (slots 19, 23, 24).
S.after3_h1 = { chapter = 2, area = 0, heroine = 1, jump = 0x96B072, arrive = { vm = 6 }, hold = 1200 }
S.after4_h2 = { chapter = 3, area = 1, heroine = 2, jump = 0x96B6A9, arrive = { vm = 7 }, hold = 1200 }
S.after5_h0 = { chapter = 4, area = 1, heroine = 0, jump = 0x96BE15, arrive = { vm = 8 }, hold = 1200 }

-- Chapter 4 area 1 mid-stage dialogues with enemy 08 (scenes 15, 16).
for h = 0, 2 do
  S["mid4a_h" .. h] = { chapter = 3, area = 1, heroine = h, jump = 0x96B3D4, arena = 896, arrive = { vm = 15 },
    hold = 1200 }
  S["mid4b_h" .. h] = { chapter = 3, area = 1, heroine = h, jump = 0x96B413, arrive = { vm = 16 }, hold = 900 }
  -- Ending dialogue after the final boss (scene 9), then the rest of the ending.
  S["ending_h" .. h] = { chapter = 5, area = 1, heroine = h, jump = 0x96C2DB, arrive = { vm = 9 }, hold = 3000 }
  -- Profile screens: the title attract demo shows each heroine's profile (scene 28) in turn.
  S["profile_h" .. h] = { idle = true, arrive = { vm = 28, heroine = h }, hold = 400 }
end

S.stageclear = { chapter = 0, area = 1, heroine = 0, jump = 0x96AA14, arrive = { vm = 27 }, hold = 600 }
S.gameover = { chapter = 0, area = 0, heroine = 0, result = 1, arrive = { vm = 26 }, hold = 1500 }
S.staffroll = { chapter = 0, area = 0, heroine = 0, result = 4, arrive = { mode = 1 }, hold = 6000 }

return S
