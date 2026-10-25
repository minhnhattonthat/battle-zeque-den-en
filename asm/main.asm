; Engine patches, assembled by tools/build.py (asar 1.91) onto the built ROM. Each file's code continues in the
; $80:E580 free space after the previous one; hooks use pushpc/pullpc.
incsrc vwf.asm
incsrc card.asm
assert pc() <= $80FFC0
