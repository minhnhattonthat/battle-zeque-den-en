"""boxes.py: width gate data, measured in-game per text box variant (phase 5, docs/re/font.md §Box widths).

px: pen budget per line in pixels (font.text_width of the line must be <= px). lines: rows shown at once; the
dialogue box scrolls after its 3rd row (waits for a button, then scrolls), so longer entries are fine.
measured: the shot that proves it, or "guess".
"""
BOXES = {
    # 22 visible buffer tiles (x 56..231 on screen), portrait left
    "hero": {"px": 176, "lines": 3, "measured": "work/qa/m1/ch1_h0 f001837 (textpx: x 56..231)"},
    # 22 visible buffer tiles (x 24..199), portrait right
    "enemy": {"px": 176, "lines": 3, "measured": "work/qa/m1/boss1_h0 f001297 (textpx: x 24..199)"},
    # no box, text over the arena from x 40: all 23 buffer tiles show (a 182-px line at x 39..220)
    "toutetsu": {"px": 184, "lines": 3, "measured": "work/qa/m1/boss6_h0 f002020 (textpx: x 39..220)"},
    # profile screens: 16-tile buffer rows from x 128 to the screen edge, 9 rows used by the jp text
    "profile": {"px": 128, "lines": 9, "measured": "work/qa/m1/profile_h0 (125-px marker lines from x 127)"},
    # prologue in rows (phase 7, docs/re/text.md §Prologue): 14 16x16 cells per row, 127 cells for all lines
    # (gfx_text.prologue checks both); ~11 rows on screen at once, scrolling up
    "prologue": {"px": 224, "lines": 11, "measured": "work/qa/warp/prologue_title f001440 (block x 40..213)"},
}
